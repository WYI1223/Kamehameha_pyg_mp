import queue
from loguru import logger
from mediapipe import *
from sklearn.linear_model import LinearRegression
import math


class tpose_detector:
    def __init__(self):
        pass

    def detect(self):
        pass






class attack_detector:
    _logger = None
    def set_logger(logger_):
        attack_detector._logger = logger_

    def __init__(self,model):
        self.queue = queue.Queue()
        self.intialize()
        self.model = model
        self.push_counter = 0
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
                         body: 11-left_shoulder, 12-right_shoulder, 13-left_elbow, 14-right_elbow, 15-left_wrist, 16-right_wrist
        Output: 1-前推, 0-其他

        logic: 计算手腕和肩膀的深度差，如果手腕在肩膀前面的一定数值，则认为是前推动作
        """

        # 1. 获得手腕,手肘,肩膀的坐标
        try:
            left_shoulder = self.model.results.pose_landmarks.landmark[11]
            right_shoulder = self.model.results.pose_landmarks.landmark[12]
            left_elbow = self.model.results.pose_landmarks.landmark[13]
            right_elbow = self.model.results.pose_landmarks.landmark[14]
            left_wrist = self.model.results.pose_landmarks.landmark[15]
            right_wrist = self.model.results.pose_landmarks.landmark[16]
        except:
            return False



        # 2. 计算手肘的角度
        left_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)

        # 3. 判断是否前推
        if left_angle > 135 and right_angle > 135:
            self.push_counter += 1
            if self.push_counter > 10:
                print("前推")
                self.push_counter = 0
                print("left_angle:{}, right_angle:{}".format(left_angle, right_angle))
                return True
        else:
            self.push_counter = 0
            return False
        return False



        # logger.info("execute action3")
    def calculate_angle(self,landmark1, landmark2, landmark3):
            # 获取坐标
        x1, y1, z1 = landmark1.x, landmark1.y, landmark1.z
        x2, y2, z2 = landmark2.x, landmark2.y, landmark2.z
        x3, y3, z3 = landmark3.x, landmark3.y, landmark3.z

            # 计算向量
        vector1 = [x2 - x1, y2 - y1, z2 - z1]
        vector2 = [x2 - x3, y2 - y3, z2 - z3]

            # 计算向量的点积
        dot_product = sum(a * b for a, b in zip(vector1, vector2))

            # 计算向量的模长
        magnitude1 = math.sqrt(sum(a * a for a in vector1))
        magnitude2 = math.sqrt(sum(a * a for a in vector2))

            # 计算角度
        angle = math.acos(dot_product / (magnitude1 * magnitude2))

            # 将角度从弧度转换为度
        angle = math.degrees(angle)

        return angle

        # 示例：计算肩膀、肘部和手腕之间的角度
        # 你需要从MediaPipe的输出中提供这些关键点的坐标
        # angle = calculate_angle(shoulder_landmark, elbow_landmark, wrist_landmark)


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

