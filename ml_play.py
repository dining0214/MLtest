"""
The template of the main script of the machine learning process
"""
import pickle
import numpy as np
import random
from sklearn import svm

from mlgame.communication import ml as comm
import os.path as path


def ml_loop(side: str):
    """
    The main loop of the machine learning process
    This loop is run in a separate process, and communicates with the game process.
    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    if side == "1P":
        filename = path.join(path.dirname(__file__),"clf_KMeans_PingPong.pickle")
    else:
        filename = path.join(path.dirname(__file__),"clf_KMeans_PingPong_p2.pickle")
    with open(filename, 'rb') as file:
        clf_p1 = pickle.load(file)
    

    s = [93,93]
    def get_direction(ball_x,ball_y,ball_pre_x,ball_pre_y):
        VectorX = ball_x - ball_pre_x
        VectorY = ball_y - ball_pre_y
        if(VectorX>=0 and VectorY>=0):
            return 0
        elif(VectorX>0 and VectorY<0):
            return 1
        elif(VectorX<0 and VectorY>0):
            return 2
        elif(VectorX<0 and VectorY<0):
            return 3

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()
    
    
        

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.recv_from_game()
        feature = []
        if side == '1P':
            feature.append(scene_info["platform_1P"][0])
        else:
            feature.append(scene_info["platform_2P"][0])
        feature.append(scene_info["blocker"][0])
        feature.append(scene_info["ball_speed"][0])
        feature.append(scene_info["ball_speed"][1])
        if side == '1P':
            if scene_info["ball_speed"][1] > 0 : # 球正在向下 # ball goes down
                x = ( scene_info["platform_1P"][1]-scene_info["ball"][1] ) // scene_info["ball_speed"][1] # 幾個frame以後會需要接  # x means how many frames before catch the ball
                pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)  # 預測最終位置 # pred means predict ball landing site 
                bound = pred // 200 # Determine if it is beyond the boundary
                if (bound > 0): # pred > 200 # fix landing position
                    if (bound%2 == 0) : 
                        pred = pred - bound*200                    
                    else :
                        pred = 200 - (pred - 200*bound)
                elif (bound < 0) : # pred < 0
                    if (bound%2 ==1) :
                        pred = abs(pred - (bound+1) *200)
                    else :
                        pred = pred + (abs(bound)*200)
            else : # 球正在向上 # ball goes up
                pred = 100
        elif side == '2P':
            if scene_info["ball_speed"][1] < 0 : # 球正在向下 # ball goes down
                x = ( scene_info["platform_2P"][1]+30-scene_info["ball"][1] ) // scene_info["ball_speed"][1] 
                pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x) 
                bound = pred // 200 
                if (bound > 0):
                    if (bound%2 == 0):
                        pred = pred - bound*200 
                    else :
                        pred = 200 - (pred - 200*bound)
                elif (bound < 0) :
                    if bound%2 ==1:
                        pred = abs(pred - (bound+1) *200)
                    else :
                        pred = pred + (abs(bound)*200)
            else : # 球正在向上 # ball goes up
                pred = 100
        feature.append(pred)
        
        feature = np.array(feature)
        feature = feature.reshape((-1,5))
        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            if random.randrange(0,2) == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            else:
                comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_RIGHT"})
            ball_served = True
        else:
            y = clf_p1.predict(feature)
            if y == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
                print('NONE')
            elif y == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                print('LEFT')
            elif y == 2:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                print('RIGHT')
