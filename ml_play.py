"""
The template of the main script of the machine learning process
"""

class MLPlay:
    def __init__(self):
        """
        Constructor
        """
        self.ball_served = False
        self.previous_ball = (0, 0)
        self.pred = 100

    def update(self, scene_info):
        """
        Generate the command according to the received `scene_info`.
        """
        # Make the caller to invoke `reset()` for the next round.
        if (scene_info["status"] == "GAME_OVER" or
            scene_info["status"] == "GAME_PASS"):
            return "RESET"

        if not self.ball_served:
            self.ball_served = True
            self.previous_ball = scene_info["ball"]
            command = "SERVE_TO_RIGHT" # 發球
            
        else:
            # rule code
            self.pred = 100
            if self.previous_ball[1]-scene_info["ball"][1] > 0: # 球正在往上
                pass
            else :  # 球正在往下，判斷球的落點
                self.pred = scene_info["ball"][0] + ((400 - scene_info["ball"][1]) // 7 ) * (scene_info["ball"][0]- self.previous_ball[0])
            
            # 調整predict值
            if self.pred > 400:
                self.pred = self.pred - 400
            elif self.pred < 400 and self.pred >200 :
                self.pred = 200 - (self.pred -200 )
            elif self.pred < -200:
                self.pred = 200 - (abs(self.pred) - 200)
            elif self.pred > -200 and self.pred < 0 :
                self.pred = abs(self.pred)

            # 判斷command
            if scene_info["platform"][0]+20 - 5 > self.pred :
                command = "MOVE_LEFT"
            elif scene_info["platform"][0]+20 + 5 < self.pred : 
                command = "MOVE_RIGHT"
            else :
                command = "NONE"

        self.previous_ball = scene_info["ball"]
        return command

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
