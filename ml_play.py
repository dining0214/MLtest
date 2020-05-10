"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import pickle
import numpy as np
import os

def ml_loop(side: str):
    """
    The main loop for the machine learning process
    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```
    @param side The side which this script is executed for. Either "1P" or "2P".
    """
    path = os.getcwd()
    with open(os.path.join(path,'games','pingpong','ml','save','decisiontree_300_slice.pickle'), 'rb') as f:
        decisiontree = pickle.load(f)
    with open(os.path.join(path,'games','pingpong','ml','save','decisiontree_300_slice_for_1P.pickle'), 'rb') as f:
        decisiontree_1P = pickle.load(f)
    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    def move_to(player, pred) : #move platform to predicted position to catch ball 
        if player == '1P':
            if scene_info["platform_1P"][0]+20  > (pred-10) and scene_info["platform_1P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_1P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20  > (pred-10)and scene_info["platform_2P"][0]+20 < (pred+10):
                if scene_info["platform_2P"][1]+30-scene_info["ball_speed"][1] > scene_info["ball"][1] :
                    return 0
                    #if scene_info["ball"][0] > scene_info["platform_2P"][0]+20 and scene_info["ball_speed"][0] > 0:
                    #    return 1
                    #elif scene_info["ball"][0] > scene_info["platform_2P"][0]+20 and scene_info["ball_speed"][0] < 0:
                    #    return 1
                else :
                    return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left

    def ml_loop_for_1P(): 
        # print ("blocker : %s, ball : %s"%(scene_info["blocker"],scene_info["ball"]))
        if scene_info["ball_speed"][1] > 0 :
            if scene_info["ball_speed"][0] > 0:
                direction = 0
            else :
                direction = 1
        else :
            if scene_info["ball_speed"][0] > 0:
                direction = 2
            else:
                direction = 3
        X = [scene_info["ball"][0], scene_info["ball"][1], direction, scene_info["blocker"][0]]
        X = np.array(X).reshape((1,-1))
        pred = decisiontree_1P.predict(X)
        return move_to(player = '1P',pred = pred)



    def ml_loop_for_2P():  # as same as 1P
        # print ("blocker : %s, ball : %s"%(scene_info["blocker"],scene_info["ball"]))
        if scene_info["ball_speed"][1] > 0 :
            if scene_info["ball_speed"][0] > 0:
                direction = 0
            else :
                direction = 1
        else :
            if scene_info["ball_speed"][0] > 0:
                direction = 2
            else:
                direction = 3
        X = [scene_info["ball"][0], scene_info["ball"][1], direction, scene_info["blocker"][0]]
        X = np.array(X).reshape((1,-1))
        pred = decisiontree.predict(X)
        return move_to(player = '2P',pred = pred)
    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_RIGHT"})
            ball_served = True
        else:
            if side == "1P":
                command = ml_loop_for_1P()
            else:
                command = ml_loop_for_2P()

            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else :
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
