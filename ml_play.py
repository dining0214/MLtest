class MLPlay:
    def __init__(self, player):
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        self.car_vel = 0
        self.car_pos = (0,0)
        self.car_lane = self.car_pos[0] // 70
        self.lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center

        self.coin_num = 0
        self.computer_cars = []
        self.coins_pos = []    

    def update(self, scene_info: dict):
        """
        Generate the command according to the received scene information
        """
        """
        9 grid relative position
        |    |    |    |
        |  1 |  2 |  3 |
        |    |  5 |    |
        |  4 |  c |  6 |
        |    |    |    |
        |  7 |  8 |  9 |
        |    |    |    |       
        """
        """
        5 coin grid relative position                      
         1 | 2 | 3 | 4 | 5
           | 6 | 8 | 7 |
           |   |   |   |
           |   | c |   |
         - | - | - | - | -
         - | - | - | - | -         
        """
        def check_grid():
            #print(self.coins_pos)
            grid = set()       
            coin_grid = set()     
            speed_ahead = 100

            if self.car_lane == 0: # left bound
                grid.add(1)
                grid.add(4)
                grid.add(7)
            elif self.car_lane == 8: # right bound
                grid.add(3)
                grid.add(6)
                grid.add(9)

            for car in scene_info["cars_info"]:
                if car["id"] != self.player_no:                    
                    y = self.car_pos[1] - car["pos"][1] # y relative position
                    lanes = car["pos"][0] // 70 # car lane
                    
                    if self.car_lane == lanes :      
                        if y > 0 and y < 300:
                            grid.add(2)
                            if y < 200:
                                speed_ahead = car["velocity"]
                                grid.add(5) 
                        elif y < 0 and y > -200:
                            grid.add(8)
                    if self.car_lane + 1 == lanes :
                        if y > 80 and y < 250:                            
                            grid.add(3)
                        elif y < -80 and y > -200:
                            grid.add(9)
                        elif y < 80 and y > -80:
                            grid.add(6)
                    if self.car_lane - 1 == lanes:
                        if y > 80 and y < 250:                            
                            grid.add(1)
                        elif y < -80 and y > -200:
                            grid.add(7)
                        elif y < 80 and y > -80:
                            grid.add(4)
            
            for coin in self.coins_pos:
                if coin[1] < self.car_pos[1]:    
                    y = self.car_pos[1] - coin[1]
                    lanes = coin[0] // 70 #coin lane

                    if(self.car_lane > lanes):# left side
                        if(self.car_lane - lanes == 1):
                            if y > 200:
                                coin_grid.add(2)
                            else:
                                coin_grid.add(6)
                        else:
                            coin_grid.add(1)
                    if(self.car_lane == lanes):
                        coin_grid.add(3)    
                        if y < 200:
                            coin_grid.add(8)                    
                    if(self.car_lane < lanes): # right side                        
                        if(lanes - self.car_lane == 1):    
                            if y > 200:                        
                                coin_grid.add(4)
                            else:
                                coin_grid.add(7)
                        else:
                            coin_grid.add(5)
            return move(grid = grid, coin_grid = coin_grid, speed_ahead = speed_ahead)
        
        def move(grid, coin_grid, speed_ahead): 
            if len(grid) == 0:            
                if len(coin_grid) == 0:
                    return ["SPEED"]
                else:
                    if(3 in coin_grid):
                        return["SPEED"]
                    elif(2 in coin_grid) or (1 in coin_grid) or (6 in coin_grid):
                        return["MOVE_LEFT", "SPEED"]
                    elif(4 in coin_grid) or (5 in coin_grid) or (7 in coin_grid):
                        return["MOVE_RIGHT", "SPEED"]                                                    
            else:
                if (2 not in grid): # Check forward                                                      
                    # Back to lane center
                    if(8 in coin_grid):
                        if self.car_pos[0] > self.lanes[self.car_lane]:
                            return ["SPEED", "MOVE_LEFT"]
                        elif self.car_pos[0] < self.lanes[self.car_lane]:
                            return ["SPEED", "MOVE_RIGHT"]
                        else:
                            return["SPEED"]
                    # left has coin
                    if(6 in coin_grid) and (1 not in grid) and (4 not in grid):
                        return ["SPEED", "MOVE_LEFT"]
                    # right has coin
                    if(7 in coin_grid) and (3 not in grid) and (6 not in grid):
                        return ["SPEED", "MOVE_RIGHT"]
                    # Back to lane center
                    if(3 in coin_grid):
                        if self.car_pos[0] > self.lanes[self.car_lane]:
                            return ["SPEED", "MOVE_LEFT"]
                        elif self.car_pos[0] < self.lanes[self.car_lane]:
                            return ["SPEED", "MOVE_RIGHT"]
                        else:
                            return["SPEED"]
                    # left has coin
                    if(2 in coin_grid) and (1 not in grid) and (4 not in grid):
                        return ["SPEED", "MOVE_LEFT"]
                    # right has coin
                    if(4 in coin_grid) and (3 not in grid) and (6 not in grid):
                        return ["SPEED", "MOVE_RIGHT"]
                    # left far has coin
                    if(1 in coin_grid) and (1 not in grid) and (4 not in grid):
                        return ["SPEED", "MOVE_LEFT"]    
                    # right far has coin
                    if(5 in coin_grid) and (3 not in grid) and (6 not in grid):
                        return ["SPEED", "MOVE_RIGHT"]                                           
                    # no coin # Back to lane center
                    if self.car_pos[0] > self.lanes[self.car_lane]:
                        return ["SPEED", "MOVE_LEFT"]
                    elif self.car_pos[0] < self.lanes[self.car_lane]:
                        return ["SPEED", "MOVE_RIGHT"]
                    else:
                        return ["SPEED"]   
                else:
                    # 5 in grid
                    if (5 in grid): # NEED to BRAKE
                        if (6 not in grid) and (3 not in grid): # turn right
                            if self.car_vel < speed_ahead:
                                return ["SPEED", "MOVE_RIGHT"]
                            else:
                                return ["BRAKE", "MOVE_RIGHT"]
                        if (4 not in grid) and (1 not in grid): # turn left
                            if self.car_vel < speed_ahead:
                                return ["SPEED", "MOVE_LEFT"]
                            else:
                                return ["BRAKE", "MOVE_LEFT"]
                        if (6 not in grid): # turn right
                            if self.car_vel < speed_ahead:
                                return ["SPEED", "MOVE_RIGHT"]
                            else:
                                return ["BRAKE", "MOVE_RIGHT"]
                        if (4 not in grid): # turn left
                            if self.car_vel < speed_ahead:
                                return ["SPEED", "MOVE_LEFT"]
                            else:
                                return ["BRAKE", "MOVE_LEFT"] 
                        if self.car_vel < speed_ahead:  # BRAKE
                            return ["SPEED"]
                        else:
                            return ["BRAKE"]                                                           
                    # 5 is not in grid
                    # forward has coin
                    if(8 in coin_grid) and (6 not in coin_grid) and (7 not in coin_grid):                                                              
                        if self.car_vel < speed_ahead:  # BRAKE
                            return ["SPEED"]
                        else:
                            return ["BRAKE"]
                    # left has coin
                    if(6 in coin_grid) and (1 not in grid) and (4 not in grid):
                        return ["SPEED", "MOVE_LEFT"]
                    # right has coin
                    if(7 in coin_grid) and (3 not in grid) and (6 not in grid):                    
                        return ["SPEED", "MOVE_RIGHT"]
                    # left has coin
                    if(2 in coin_grid) and (1 not in grid) and (4 not in grid):
                        return ["SPEED", "MOVE_LEFT"]
                    # right has coin
                    if(4 in coin_grid) and (1 not in grid) and (6 not in grid):
                        return ["SPEED", "MOVE_RIGHT"]
                    # left far has coin
                    if(1 in coin_grid) and (1 not in grid) and (4 not in grid):
                        return ["SPEED", "MOVE_LEFT"]    
                    # right far has coin
                    if(5 in coin_grid) and (3 not in grid) and (6 not in grid):
                        return ["SPEED", "MOVE_RIGHT"]     

                    if (3 not in grid) and (6 not in grid) and (9 not in grid): # turn right
                        return ["SPEED", "MOVE_RIGHT"]
                    if (1 not in grid) and (4 not in grid) and (7 not in grid): # turn left 
                        return ["SPEED", "MOVE_LEFT"]
                    if (3 not in grid) and (6 not in grid): # turn right
                        return ["SPEED", "MOVE_RIGHT"]
                    if (1 not in grid) and (4 not in grid): # turn left 
                        return ["SPEED", "MOVE_LEFT"]
                                  

        if len(scene_info[self.player]) != 0:
            self.car_pos = scene_info[self.player]
        
        for car in scene_info["cars_info"]:
            if car["id"]==self.player_no:
                self.car_vel = car["velocity"]
                self.coin_num = car["coin_num"]

        self.computer_cars = scene_info["computer_cars"]
        if scene_info.__contains__("coins"):
            self.coins_pos = scene_info["coins"]

        if scene_info["status"] != "ALIVE":
            return "RESET"

        self.car_lane = self.car_pos[0] // 70
        return check_grid()        

    def reset(self):
        """
        Reset the status
        """
        print("reset ml script")
        pass
