import queue
from loguru import logger
from mediapipe import *
from sklearn.linear_model import LinearRegression

class attack_detector:
    _logger = None
    def set_logger(logger_):
        attack_detector._logger = logger_

    def __init__(self,model):
        self.queue = queue.Queue()
        self.intialize()
        self.model = model
        pass

    def intialize(self):
        pass



    def action1(self):
        logger.info("execute action1")
        self.isSuccess = False
        try:
            left_pinky_mcp = [self.model.results.left_hand_landmarks.landmark[17].x,
                              self.model.results.left_hand_landmarks.landmark[17].y]
            left_pinky_pip = [self.model.results.left_hand_landmarks.landmark[18].x,
                              self.model.results.left_hand_landmarks.landmark[18].y]
            left_pinky_dip = [self.model.results.left_hand_landmarks.landmark[19].x,
                              self.model.results.left_hand_landmarks.landmark[19].y]
            left_pinky_tip = [self.model.results.left_hand_landmarks.landmark[20].x,
                              self.model.results.left_hand_landmarks.landmark[20].y]
            right_pinky_mcp = [self.model.results.right_hand_landmarks.landmark[17].x,
                              self.model.results.right_hand_landmarks.landmark[17].y]
            right_pinky_pip = [self.model.results.right_hand_landmarks.landmark[18].x,
                              self.model.results.right_hand_landmarks.landmark[18].y]
            right_pinky_dip = [self.model.results.right_hand_landmarks.landmark[19].x,
                              self.model.results.right_hand_landmarks.landmark[19].y]
            right_pinky_tip = [self.model.results.right_hand_landmarks.landmark[20].x,
                              self.model.results.right_hand_landmarks.landmark[20].y]
        except:
            print("no hand detected")
            return

        left_X = [left_pinky_mcp[0], left_pinky_pip[0], left_pinky_dip[0], left_pinky_tip[0]]
        right_X = [right_pinky_mcp[0], right_pinky_pip[0], right_pinky_dip[0], right_pinky_tip[0]]
        left_y = [left_pinky_mcp[1], left_pinky_pip[1], left_pinky_dip[1], left_pinky_tip[1]]
        right_y = [right_pinky_mcp[1], right_pinky_pip[1], right_pinky_dip[1], right_pinky_tip[1]]

        L_model = LinearRegression()
        R_model = LinearRegression()

        L_model.fit(left_X, left_y)
        R_model.fit(right_X,right_y)

        print("the slope of L:", L_model.coef_)
        print("the slope of R:", R_model.coef_)



    def action2(self):
        logger.info("execute action2")
        pass

    def action3(self):
        """
        动作3：前推检测
        Input: 双手关键点, hand : 0-Wrist,4-Thumb,8-Index,12-Middle,16-Ring,20-Pinky
                         body: 11-left_shoulder, 12-right_shoulder,15-left_wrist,16-right_wrist
        Output: 1-前推, 0-其他

        logic: 计算手腕和肩膀的深度差，如果手腕在肩膀前面的一定数值，则认为是前推动作
        """

        # 1. 获得手腕与肩膀的z轴数据
        try:
            left_shoulder = self.model.results.pose_landmarks.landmark[11].z
            right_shoulder = self.model.results.pose_landmarks.landmark[12].z
            left_wrist = self.model.results.pose_landmarks.landmark[15].z
            right_wrist = self.model.results.pose_landmarks.landmark[16].z
        except:
            print("no pose_landmarks")
            return

        # 2. 计算手腕与肩膀的深度差
        left_diff = left_wrist - left_shoulder
        right_diff = right_wrist - right_shoulder

        print("left_diff: ", left_diff)
        print("right_diff: ", right_diff)


        # logger.info("execute action3")

class jump_detector:

    def __init__(self):
        pass

    def intialize(self):
        pass

logger.info("")
logger.debug("")
class sit_detector:

    def __init__(self):
        pass

    def intialize(self):
        pass

