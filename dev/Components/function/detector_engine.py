import queue
from loguru import logger
from mediapipe import *
from sklearn.linear_model import LinearRegression
import math
import numpy as np


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
        self.isSuccess1 = False
        try:
            #详见handlandmark.jpg
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

        Left_X = np.array(left_X).reshape(-1, 1)
        Right_X = np.array(right_X).reshape(-1, 1)
        Left_y = np.array(left_y).reshape(-1, 1)
        Right_y = np.array(right_y).reshape(-1, 1)

        L_model = LinearRegression()
        R_model = LinearRegression()

        L_model.fit(Left_X, Left_y)
        R_model.fit(Right_X,Right_y)

        """
        # 左右手小拇指点拟合直线斜率
        print("the slope of L:", L_model.coef_)
        print("the slope of R:", R_model.coef_)
        """

        # z轴小拇指与大拇指的坐标差值
        diff = self.model.results.left_hand_landmarks.landmark[17].z - self.model.results.left_hand_landmarks.landmark[3].z

        # 判断小拇指是否到达指定斜率
        if L_model.coef_ > -0.1 and L_model.coef_ < 0:
            return True

        """
        暂定动作一逻辑由拟合直线斜率和z轴坐标来定，斜率需要测试，z轴坐标主要体现在大拇指与小拇指距离差上
            若右手是负值则是小拇指在前，则是动作一
            反之则到了动作二
        """


    def action2(self):
        logger.info("execute action2")
        self.isSuccess2 = False
        pass



    """
        动作3：前推检测
        Input: 双手关键点, hand : 0-Wrist,4-Thumb,8-Index,12-Middle,16-Ring,20-Pinky
                         body: 11-left_shoulder, 12-right_shoulder, 13-left_elbow, 14-right_elbow, 15-left_wrist, 16-right_wrist
        Output: 1-前推, 0-其他

        logic: 计算手腕和肩膀的深度差，如果手腕在肩膀前面的一定数值，则认为是前推动作
    """
    def action3(self):

        # 1. 获得手腕,手肘,肩膀的坐标
        hand_push = False
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
            hand_push = True
        # ------------------------------------------------------------------这里需要加入log，这里判断的是手臂伸直，所以应该有个info，手臂伸直的log
        else:
            self.push_counter = 0
            return False
        """
        动作3-2：手掌张开检测
        Input: 双手关键点, hand : 0 - Wrist
                                2,3,4 - Thump_MCP, Thump_IP, Thump_TIP
                                6,7,8 - Index
                                10,11,12 - Middle
                                14,15,16 - Ring
                                18,19,20 - Pinky
        Output: 1-张开,0-其他
        
        logic: 计算手指三个关键点的角度是否在180左右，全部满足则返回True
        """
        # 1. 获得手掌关键点
        try:
            # 左手关键点
            left_hand_Wrist = self.model.results.left_hand_landmarks.landmark[0]
            left_hand_Thump = [left_hand_Wrist,
                               self.model.results.left_hand_landmarks.landmark[2],
                               self.model.results.left_hand_landmarks.landmark[4]]
            left_hand_Middle = [left_hand_Wrist,
                                self.model.results.left_hand_landmarks.landmark[10],
                                self.model.results.left_hand_landmarks.landmark[12]]
            left_hand_Ring = [left_hand_Wrist,
                              self.model.results.left_hand_landmarks.landmark[14],
                              self.model.results.left_hand_landmarks.landmark[16]]
            # 右手关键点
            right_hand_Wrist = self.model.results.right_hand_landmarks.landmark[0]
            right_hand_Thump = [right_hand_Wrist,
                               self.model.results.right_hand_landmarks.landmark[2],
                               self.model.results.right_hand_landmarks.landmark[4]]
            right_hand_Middle = [right_hand_Wrist,
                                self.model.results.right_hand_landmarks.landmark[10],
                                self.model.results.right_hand_landmarks.landmark[12]]
            right_hand_Ring = [right_hand_Wrist,
                              self.model.results.right_hand_landmarks.landmark[14],
                              self.model.results.right_hand_landmarks.landmark[16]]
        except:
            return False
        # 2. 计算手指角度
        #  左手
        left_hand_Thump_angle = self.calculate_angle(left_hand_Thump[0],left_hand_Thump[1],left_hand_Thump[2])
        left_hand_Middle_angle = self.calculate_angle(left_hand_Middle[0], left_hand_Middle[1], left_hand_Middle[2])
        left_hand_Ring_angle = self.calculate_angle(left_hand_Ring[0], left_hand_Ring[1], left_hand_Ring[2])
        #  右手
        right_hand_Thump_angle = self.calculate_angle(right_hand_Thump[0],right_hand_Thump[1],right_hand_Thump[2])
        right_hand_Middle_angle = self.calculate_angle(right_hand_Middle[0], right_hand_Middle[1], right_hand_Middle[2])
        right_hand_Ring_angle = self.calculate_angle(right_hand_Ring[0], right_hand_Ring[1], right_hand_Ring[2])

        # 3. 判断是否张开手指
        hand_open = False
        if left_hand_Thump_angle > 135 and left_hand_Middle_angle > 135 and left_hand_Ring_angle > 135:
            if right_hand_Thump_angle > 135 and right_hand_Middle_angle > 135 and right_hand_Ring_angle > 135:
                self.push_counter += 1
                if self.push_counter > 10:
                    print("left_hand_Thump_angle:{}, left_hand_Middle_angle:{}, left_hand_Ring_angle:{}".format(
                        left_hand_Thump_angle, left_hand_Middle_angle, left_hand_Ring_angle))

                    print("right_hand_Thump_angle:{}, right_hand_Middle_angle:{}, right_hand_Ring_angle:{}".format(
                        right_hand_Thump_angle, right_hand_Middle_angle, right_hand_Ring_angle))

                    print("action3 done")
                    # ---------------------------这里是判断是否手掌张开并伸直，所以这里要加log，info，手臂伸直并手掌打开，action3动作完成。
                    self.push_counter = 0
                    return (True and hand_push)
            return False
        else:
            self.push_counter = 0
            return False


        # logger.info("execute action3")

    """
    计算三点之间的角度
    Input: x,y,z of landmark1, landmark2, landmark3
    output: 三点之间夹角度数
    
    logic: 余弦函数
    """
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

