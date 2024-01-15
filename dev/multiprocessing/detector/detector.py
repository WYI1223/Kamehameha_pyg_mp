import time
from loguru import logger
from sklearn.linear_model import LinearRegression
import math
import cv2
import numpy as np


class attack_detector:
    """
        该类用于检测游戏所需动作是否完成
            a. 动作一：左手在上大拇指在后
            b. 动作二：右手在上大拇指在后
            c. 动作三：前推以及手掌张开
        Input : mediapipe_holistic_engine类的数据 (使用到pose_landmarks, left_hand_landmarks, right_hand_landmarks)
        Output : True or False (成功或者失败)        

        Function:   initialize_model(self,model), 
                    detect(self), 
                    action1(self), 
                    action2(self), 
                    action3(self), 
                    calculate_angle(self) 
    """

    def __init__(self):
        # self.queue = queue.Queue()

        # 目前action状态机，如果为空，则判断action1，成功则+1，并判断下一个动作
        self.state_machine = 0
        # 需要一个数组来短暂的储存最近几次检测到的动作, 来避免一只手检测另一只手没有检测到后来又检测到的情况
        self.Lslope = [] * 10
        self.Lslope_b = [] * 10
        self.Rslope = [] * 10
        self.Rslope_b = [] * 10

        self.sit_down = False
        
        self.pose_landmarks = None
        self.left_hand_landmark = None
        self.right_hand_landmark = None
        self.last_time = time.time()

    def datainput(self, pose_landmark, left_hand_landmark, right_hand_landmark):
        
        self.pose_landmarks = pose_landmark
        self.left_hand_landmark = left_hand_landmark
        self.right_hand_landmark = right_hand_landmark



    """
    统筹整个class，作为class判断的入口
    Input: None
    Output: True, or False

    Logic: 
        目前action状态机，如果为空，则判断action1，成功则+1，并判断下一个动作
        当state_machine不为0时，开始计时，超过10s则将state_machine归0
    """

    def detect(self):
        if self.state_machine == 0:
            if self.action1():
                self.state_machine += 1
                self.last_time = time.time()
                logger.debug("Action1 done -- {}".format(time.time()))
                return 1
            pass

        if self.state_machine == 1:
            if self.action2():
                self.state_machine += 1
                self.last_time = time.time()
                logger.debug("Action2 done -- {}".format(time.time()))
                return 2
            pass

        if self.state_machine == 2:
            if self.action3():
                self.state_machine = 0
                logger.debug("Action3 done -- {}".format(time.time()))
                return 3
            pass

        # print(self.state_machine, " ", time.time() - self.last_time)
        # 5s 后状态机归0
        if self.state_machine != 0 and time.time() - self.last_time > 10:
            logger.debug("Action reset")
            self.state_machine = 0
        return False

    def action1(self):
        try:
            # 详见handlandmark.jpg
            left_pinky_mcp = [self.left_hand_landmark.landmark[17].x,
                              self.left_hand_landmark.landmark[17].y]
            left_pinky_pip = [self.left_hand_landmark.landmark[18].x,
                              self.left_hand_landmark.landmark[18].y]
            left_pinky_dip = [self.left_hand_landmark.landmark[19].x,
                              self.left_hand_landmark.landmark[19].y]
            left_pinky_tip = [self.left_hand_landmark.landmark[20].x,
                              self.left_hand_landmark.landmark[20].y]
            left_X = [left_pinky_mcp[0], left_pinky_pip[0], left_pinky_dip[0], left_pinky_tip[0]]
            left_y = [left_pinky_mcp[1], left_pinky_pip[1], left_pinky_dip[1], left_pinky_tip[1]]
            Left_X = np.array(left_X).reshape(-1, 1)
            Left_y = np.array(left_y).reshape(-1, 1)
            L_model = LinearRegression()
            L_model.fit(Left_X, Left_y)

            diff = (self.left_hand_landmark.landmark[17].z -
                    self.left_hand_landmark.landmark[3].z)
            if len(self.Lslope_b) < 10:
                self.Lslope_b.append(diff)
            else:
                self.Lslope_b.pop(0)

            if len(self.Lslope) < 10:
                self.Lslope.append(np.abs(L_model.coef_))
            else:
                self.Lslope.pop(0)
        except:
            if len(self.Lslope) == 0:
                return False

        try:
            right_pinky_mcp = [self.right_hand_landmark.landmark[17].x,
                               self.right_hand_landmark.landmark[17].y]
            right_pinky_pip = [self.right_hand_landmark.landmark[18].x,
                               self.right_hand_landmark.landmark[18].y]
            right_pinky_dip = [self.right_hand_landmark.landmark[19].x,
                               self.right_hand_landmark.landmark[19].y]
            right_pinky_tip = [self.right_hand_landmark.landmark[20].x,
                               self.right_hand_landmark.landmark[20].y]

            right_X = [right_pinky_mcp[0], right_pinky_pip[0], right_pinky_dip[0], right_pinky_tip[0]]
            right_y = [right_pinky_mcp[1], right_pinky_pip[1], right_pinky_dip[1], right_pinky_tip[1]]

            Right_X = np.array(right_X).reshape(-1, 1)
            Right_y = np.array(right_y).reshape(-1, 1)

            R_model = LinearRegression()
            R_model.fit(Right_X, Right_y)

            diff = (self.right_hand_landmark.landmark[17].z -
                    self.right_hand_landmark.landmark[3].z)

            if len(self.Rslope_b) < 10:
                self.Rslope_b.append(diff)
            else:
                self.Rslope_b.pop(0)

            if len(self.Rslope) < 10:
                self.Rslope.append(np.abs(R_model.coef_))
            else:
                self.Rslope.pop(0)
        except:
            if len(self.Rslope) == 0:
                return False
        """
        # 左右手小拇指点拟合直线斜率
        print("the slope of L:", L_model.coef_)
        print("the slope of R:", R_model.coef_) 
        """
        # diff = self.left_hand_landmark.landmark[17].z - self.left_hand_landmark.landmark[3].z
        # print(self.Rslope, " ", self.Lslope, " ", self.Rslope_b, " ", self.Lslope_b)
        for i in range(len(self.Lslope)):
            for n in range(len(self.Rslope)):
                diff1 = self.Rslope_b[n]
                diff2 = self.Lslope_b[i]
                if self.Rslope[n] < 0.25 and self.Lslope[i] < 0.25 and diff1 > 0 and diff2 < 0:
                    print(time.time(), " ", self.Rslope[n], " ", self.Lslope[i], " ", diff1, " ", diff2, "action1")
                    self.Rslope.clear()
                    self.Lslope.clear()
                    self.Rslope_b.clear()
                    self.Lslope_b.clear()
                    return True
        self.Rslope.pop(0)
        self.Lslope.pop(0)

        self.Rslope_b.pop(0)
        self.Lslope_b.pop(0)
        # # z轴小拇指与大拇指的坐标差值
        # diff = self.left_hand_landmark.landmark[17].z - self.left_hand_landmark.landmark[3].z
        #
        # # 判断小拇指是否到达指定斜率(动作一左手在上大拇指在后)
        # if L_model.coef_ > -0.25 and L_model.coef_ < 0 and diff > 0:
        #     logger.info("Action1 done")
        #     return True

        """
        暂定动作一逻辑由拟合直线斜率和z轴坐标来定，斜率需要测试，z轴坐标主要体现在大拇指与小拇指距离差上
            若右手是负值则是小拇指在前，则是动作一
            反之则到了动作二
        """

    def action2(self):
        try:
            # 详见handlandmark.jpg
            left_pinky_mcp = [self.left_hand_landmark.landmark[17].x,
                              self.left_hand_landmark.landmark[17].y]
            left_pinky_pip = [self.left_hand_landmark.landmark[18].x,
                              self.left_hand_landmark.landmark[18].y]
            left_pinky_dip = [self.left_hand_landmark.landmark[19].x,
                              self.left_hand_landmark.landmark[19].y]
            left_pinky_tip = [self.left_hand_landmark.landmark[20].x,
                              self.left_hand_landmark.landmark[20].y]
            left_X = [left_pinky_mcp[0], left_pinky_pip[0], left_pinky_dip[0], left_pinky_tip[0]]
            left_y = [left_pinky_mcp[1], left_pinky_pip[1], left_pinky_dip[1], left_pinky_tip[1]]
            Left_X = np.array(left_X).reshape(-1, 1)
            Left_y = np.array(left_y).reshape(-1, 1)
            L_model = LinearRegression()
            L_model.fit(Left_X, Left_y)

            diff = (self.left_hand_landmark.landmark[17].z -
                    self.left_hand_landmark.landmark[3].z)
            if len(self.Lslope_b) < 10:
                self.Lslope_b.append(diff)
            else:
                self.Lslope_b.pop(0)

            if len(self.Lslope) < 10:
                self.Lslope.append(np.abs(L_model.coef_))
            else:
                self.Lslope.pop(0)
        except:
            if len(self.Lslope) == 0:
                return False

        try:
            right_pinky_mcp = [self.right_hand_landmark.landmark[17].x,
                               self.right_hand_landmark.landmark[17].y]
            right_pinky_pip = [self.right_hand_landmark.landmark[18].x,
                               self.right_hand_landmark.landmark[18].y]
            right_pinky_dip = [self.right_hand_landmark.landmark[19].x,
                               self.right_hand_landmark.landmark[19].y]
            right_pinky_tip = [self.right_hand_landmark.landmark[20].x,
                               self.right_hand_landmark.landmark[20].y]

            right_X = [right_pinky_mcp[0], right_pinky_pip[0], right_pinky_dip[0], right_pinky_tip[0]]
            right_y = [right_pinky_mcp[1], right_pinky_pip[1], right_pinky_dip[1], right_pinky_tip[1]]

            Right_X = np.array(right_X).reshape(-1, 1)
            Right_y = np.array(right_y).reshape(-1, 1)

            R_model = LinearRegression()
            R_model.fit(Right_X, Right_y)

            diff = self.right_hand_landmark.landmark[17].z - \
                   self.right_hand_landmark.landmark[3].z

            if len(self.Rslope_b) < 10:
                self.Rslope_b.append(diff)
            else:
                self.Rslope_b.pop(0)

            if len(self.Rslope) < 10:
                self.Rslope.append(np.abs(R_model.coef_))
            else:
                self.Rslope.pop(0)
        except:
            if len(self.Rslope) == 0:
                return False
        """
        # 左右手小拇指点拟合直线斜率
        print("the slope of L:", L_model.coef_)
        print("the slope of R:", R_model.coef_)
        """

        for i in range(len(self.Lslope)):
            for n in range(len(self.Rslope)):
                diff1 = self.Rslope_b[n]
                diff2 = self.Lslope_b[i]
                if self.Rslope[n] < 0.25 and self.Lslope[i] < 0.25 and diff1 < 0 and diff2 > 0:
                    print(time.time(), " ", self.Rslope[n], " ", self.Lslope[i], " ", diff1, " ", diff2, "action2")
                    self.Rslope.clear()
                    self.Lslope.clear()
                    self.Rslope_b.clear()
                    self.Lslope_b.clear()
                    return True
        self.Lslope.pop(0)
        self.Rslope.pop(0)
        self.Rslope_b.pop(0)
        self.Lslope_b.pop(0)

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
            left_shoulder = self.pose_landmarks.landmark[11]
            right_shoulder = self.pose_landmarks.landmark[12]
            left_elbow = self.pose_landmarks.landmark[13]
            right_elbow = self.pose_landmarks.landmark[14]
            left_wrist = self.pose_landmarks.landmark[15]
            right_wrist = self.pose_landmarks.landmark[16]
        except:
            return False

        # 2. 计算手肘的角度
        left_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)

        if left_angle is None or right_angle is None:
            return False

        # 3. 判断是否前推
        if left_angle > 130 and right_angle > 130:
            hand_push = True
            # logger.debug("Action3-half: straight arm")
        else:
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
            left_hand_Wrist = self.left_hand_landmark.landmark[0]
            left_hand_Thump = [left_hand_Wrist,
                               self.left_hand_landmark.landmark[2],
                               self.left_hand_landmark.landmark[4]]
            left_hand_Middle = [left_hand_Wrist,
                                self.left_hand_landmark.landmark[10],
                                self.left_hand_landmark.landmark[12]]
            left_hand_Ring = [left_hand_Wrist,
                              self.left_hand_landmark.landmark[14],
                              self.left_hand_landmark.landmark[16]]
            # 右手关键点
            right_hand_Wrist = self.right_hand_landmark.landmark[0]
            right_hand_Thump = [right_hand_Wrist,
                                self.right_hand_landmark.landmark[2],
                                self.right_hand_landmark.landmark[4]]
            right_hand_Middle = [right_hand_Wrist,
                                 self.right_hand_landmark.landmark[10],
                                 self.right_hand_landmark.landmark[12]]
            right_hand_Ring = [right_hand_Wrist,
                               self.right_hand_landmark.landmark[14],
                               self.right_hand_landmark.landmark[16]]
        except:
            return False

        # 2. 计算手指方向
        left_hand_Thump_direaction_upward = left_hand_Thump[2].y - left_hand_Thump[1].y
        right_hand_Thump_direaction_upward = right_hand_Thump[2].y - right_hand_Thump[1].y

        left_hand_Ring_direaction = left_hand_Ring[2].y - left_hand_Ring[1].y
        right_hand_Ring_direaction = right_hand_Ring[2].y - right_hand_Ring[1].y

        left_hand_Middle_direction = left_hand_Middle[2].y - left_hand_Middle[1].y
        right_hand_Middle_direction = right_hand_Middle[2].y - right_hand_Middle[1].y

        # 两只大拇指向内
        left_hand_Thump_direction = left_hand_Thump[2].x - left_hand_Thump[0].x
        right_hand_Thump_direction = right_hand_Thump[2].x - right_hand_Thump[0].x

        # 3. 判断是否张开手指
        # a. 手指向上
        hand_open = False

        if left_hand_Middle_direction < 0 and right_hand_Middle_direction < 0:
            if left_hand_Thump_direaction_upward < 0 and right_hand_Thump_direaction_upward < 0:
                if left_hand_Ring_direaction < 0 and right_hand_Ring_direaction < 0:
                    hand_open = True
                    # logger.info("Action3-half: hand upward")
        if hand_open is False:
            return False

        if left_hand_Thump_direction < 0 and right_hand_Thump_direction > 0:
            # logger.info("Action3 done")
            return True


    def sit_detect(self):

        try:
            left_lag_1 = self.pose_landmarks.landmark[24]
            left_lag_middle = self.pose_landmarks.landmark[26]
            left_lag_3 = self.pose_landmarks.landmark[28]
            right_lag_1 = self.pose_landmarks.landmark[23]
            right_lag_middle = self.pose_landmarks.landmark[25]
            right_lag_3 = self.pose_landmarks.landmark[27]
        except:
            if self.sit_down:
                logger.info("Stand up")
            self.sit_down = False
            return False

        left_lag_angle = self.calculate_angle(left_lag_1, left_lag_middle, left_lag_3)
        right_lag_angle = self.calculate_angle(right_lag_1, right_lag_middle, right_lag_3)

        if left_lag_angle is None or right_lag_angle is None:
            return self.sit_down

        if left_lag_angle < 70 and right_lag_angle < 70:
            if not self.sit_down:
                self.sit_down = True
                logger.info("Sit down")
            return True
        else:
            if self.sit_down:
                logger.info("Stand up")
            self.sit_down = False
            return False

    """
    计算三点之间的角度
    Input: x,y,z of landmark1, landmark2, landmark3
    output: 三点之间夹角度数

    logic: 余弦函数
    """

    def calculate_angle(self, landmark1, landmark2, landmark3):
        # 获取坐标
        # 如果关键点不可见，则返回None
        if landmark1.visibility < 0.7 and landmark2.visibility < 0.7 and landmark3.visibility < 0.7:
            return None
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
        self.data = [] * 10
        self.counter = 0
        pass

    def datainput(self, landmark):
        self.pose_landmarks = landmark

        pass

    def jump(self):
        try:
            # left_shoulder = self.pose_landmarks.landmark[11]
            # right_shoulder = self.pose_landmarks.landmark[12]
            # left_hip = self.pose_landmarks.landmark[23]
            # right_hip = self.pose_landmarks.landmark[24]
            left_ankle = self.pose_landmarks.landmark[27]
            right_ankle = self.pose_landmarks.landmark[28]
        except:
            return False

        # print(left_ankle.y, right_ankle.y)
        if left_ankle.visibility < 0.7 and right_ankle.visibility < 0.7:
            return False



        # 计算6个点的重心
        # center_y = (left_shoulder.y + right_shoulder.y + left_hip.y + right_hip.y + left_ankle.y + right_ankle.y) / 6
        center_y = (left_ankle.y + right_ankle.y) / 2

        if self.data == []:
            self.data.append(center_y)
            self.counter += 1
            return False
        for i in self.data:
            if (center_y - i) / center_y < -0.4:
                # print(self.data)
                self.data = [center_y]
                logger.info("Jumping")
                return True
            else:
                self.data.append(center_y)
                # print(self.data)
                if len(self.data) > 10:
                    self.data.pop(0)
                return False
