import time
from collections import deque

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
        self.Lslope = deque(maxlen=10)
        self.Lslope_b = deque(maxlen=10)
        self.Rslope = deque(maxlen=10)
        self.Rslope_b = deque(maxlen=10)

        self.arm_last_time = 0

        self.LAslope = None
        self.RAslope = None

        self.diff_from_left2right = deque(maxlen=10)



        self.pose_landmarks = None
        self.left_hand_landmark = None
        self.right_hand_landmark = None
        self.last_time = time.time()

        self.sit_down = False
        self.previous_sit_down = False

        self.jump_data = deque(maxlen=10)
        self.jump = False
        self.jump_last_time = time.time()

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

    def perform_action(self, action, next_state, action_number):
        if action():
            self.state_machine = next_state
            self.last_time = time.time()
            logger.debug(f"Action{action_number} done -- {time.time()}")
            return action_number +1
        return self.state_machine + 1

    def detect(self):

        # 检查状态机超时并重置
        if self.state_machine != 0 and time.time() - self.last_time > 10:
            logger.debug("Action reset")
            self.state_machine = 0
            return False

        actions = {
            0: (self.action1, 1, 1),
            1: (self.action2, 2, 2),
            2: (self.action3, 0, 3)
        }

        if self.state_machine in actions:
            action, next_state, action_number = actions[self.state_machine]
            return self.perform_action(action, next_state, action_number)

        return False

    def draw_box(self,image):
        # 获取图像的宽度和高度
        image_height, image_width, _ = image.shape
        # image_height = 1080
        # image_width = 680

        # 计算矩形的左上角和右下角坐标，使其位于图像中央并更长而窄
        center_x = image_width // 2
        center_y = image_height // 2
        half_width = 340  # 矩形的一半宽度
        half_height = 540  # 矩形的一半高度

        # 计算矩形的坐标
        top_left = (center_x - half_width, center_y - half_height)
        bottom_right = (center_x + half_width, center_y + half_height)

        # 初始化所有关键点是否在矩形内的标志
        all_landmarks_inside = True
        landmark = None
        try:
            landmark = self.pose_landmarks.landmark
        except:
            return False

        # 检查所有关键点是否在矩形内
        for landmark in landmark:
            x, y = int(landmark.x * image_width), int(landmark.y * image_height)
            # 如果关键点在矩形外
            if not (top_left[0] <= x <= bottom_right[0] and top_left[1] <= y <= bottom_right[1]):
                all_landmarks_inside = False
                break  # 一旦找到不在矩形内的关键点，退出循环

        # 根据所有关键点是否在矩形内来决定矩形的颜色
        if all_landmarks_inside:
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)  # 绿色矩形
            return True
        else:
            cv2.rectangle(image, top_left, bottom_right, (0, 0, 255), 2)  # 红色矩形



    """
        动作1：龟派气功动作1检测
        
        Input: 左右手的小拇指关键点, left_hand_landmark 和 right_hand_landmark
               关键点包括：17-MCP, 18-PIP, 19-DIP, 20-Tip
        Output: 返回True表示检测到特定动作，False表示未检测到或数据不足

        logic: 对左右手的小拇指关键点进行线性回归，计算拟合直线的斜率。
               如果左右手任一手的斜率超过0.25，或者左右手的Z轴深度差异满足特定条件（左手深度小于右手深度），
               则认为检测到了特定动作。在数据不足（如未捕捉到手的关键点）时返回False。
    """
    def action1(self):

        L_exception = False
        R_exception = False
        LA_exception = False
        RA_exception = False
        left_pinky_mcp, left_pinky_pip, left_pinky_dip, left_pinky_tip = None, None, None, None
        right_pinky_mcp, right_pinky_pip, right_pinky_dip, right_pinky_tip = None, None, None, None
        left_arm_elbow, right_arm_elbow, left_arm_wrist, right_arm_wrist = None, None, None, None

        try:
            left_arm_elbow = [self.right_hand_landmark.landmark[13].x,
                               self.right_hand_landmark.landmark[13].y]
            right_arm_elbow = [self.right_hand_landmark.landmark[14].x,
                               self.right_hand_landmark.landmark[14].y]
            left_arm_wrist = [self.right_hand_landmark.landmark[15].x,
                               self.right_hand_landmark.landmark[15].y]
            right_arm_wrist = [self.right_hand_landmark.landmark[16].x,
                               self.right_hand_landmark.landmark[16].y]
        except:
            if len(self.LAslope) == 0:
                return False
            LA_exception = True

            if len(self.RAslope) == 0:
                return False
            RA_exception = True

        if not LA_exception and not RA_exception:
            diff_between_left2right = left_arm_wrist[1] - right_arm_wrist[1]
            self.diff_from_left2right.append(diff_between_left2right)

        if not LA_exception:
            LA_X = [left_arm_elbow[0], left_arm_wrist[0]]
            LA_y = [left_arm_elbow[1], left_arm_wrist[1]]

            LA_X = np.array(LA_X).reshape(-1, 1)
            LA_y = np.array(LA_y).reshape(-1, 1)

            LA_model = LinearRegression()
            LA_model.fit(LA_X, LA_y)

            self.LAslope = np.abs(LA_model.coef_)

        if not RA_exception:
            RA_X = [right_arm_elbow[0], right_arm_wrist[0]]
            RA_y = [right_arm_elbow[1], right_arm_wrist[1]]

            RA_X = np.array(RA_X).reshape(-1, 1)
            RA_y = np.array(RA_y).reshape(-1, 1)

            RA_model = LinearRegression()
            RA_model.fit(RA_X, RA_y)

            self.RAslope = np.abs(RA_model.coef_)

        if self.LAslope < 0.25 and self.RAslope < 0.25:
            # 如果计时尚未开始，开始计时
            if self.arm_last_time is None:
                self.arm_last_time = time.time()
            # 如果已经计时，并且计时超过4秒，将success_action设置为True并退出循环
            elif time.time() - self.arm_last_time >= 4:
                self.arm_last_time = None
                return True
        else:
            # 如果条件不满足，重置计时器
            self.arm_last_time = None


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
        except:
            if len(self.Lslope) == 0:
                return False
            L_exception = True

        if not L_exception:
            left_X = [left_pinky_mcp[0], left_pinky_pip[0], left_pinky_dip[0], left_pinky_tip[0]]
            left_y = [left_pinky_mcp[1], left_pinky_pip[1], left_pinky_dip[1], left_pinky_tip[1]]

            Left_X = np.array(left_X).reshape(-1, 1)
            Left_y = np.array(left_y).reshape(-1, 1)
            L_model = LinearRegression()
            L_model.fit(Left_X, Left_y)

            diff = (self.left_hand_landmark.landmark[17].z -
                    self.left_hand_landmark.landmark[3].z)

            self.Lslope_b.append(diff)
            self.Lslope.append(np.abs(L_model.coef_))

        try:
            right_pinky_mcp = [self.right_hand_landmark.landmark[17].x,
                               self.right_hand_landmark.landmark[17].y]
            right_pinky_pip = [self.right_hand_landmark.landmark[18].x,
                               self.right_hand_landmark.landmark[18].y]
            right_pinky_dip = [self.right_hand_landmark.landmark[19].x,
                               self.right_hand_landmark.landmark[19].y]
            right_pinky_tip = [self.right_hand_landmark.landmark[20].x,
                               self.right_hand_landmark.landmark[20].y]
        except:
            if len(self.Rslope) == 0:
                return False
            R_exception = True

        if not R_exception:
            right_X = [right_pinky_mcp[0], right_pinky_pip[0], right_pinky_dip[0], right_pinky_tip[0]]
            right_y = [right_pinky_mcp[1], right_pinky_pip[1], right_pinky_dip[1], right_pinky_tip[1]]

            Right_X = np.array(right_X).reshape(-1, 1)
            Right_y = np.array(right_y).reshape(-1, 1)

            R_model = LinearRegression()
            R_model.fit(Right_X, Right_y)

            diff = (self.right_hand_landmark.landmark[17].z -
                    self.right_hand_landmark.landmark[3].z)

            self.Rslope_b.append(diff)
            self.Rslope.append(np.abs(R_model.coef_))



        """
        # 左右手小拇指点拟合直线斜率
        print("the slope of L:", L_model.coef_)
        print("the slope of R:", R_model.coef_) 
        """


        for i in range(len(self.Lslope)):
            for n in range(len(self.Rslope)):
                if self.Rslope[n] > 0.25 and self.Lslope[i] > 0.25:
                    continue
                diff1 = self.Rslope_b[n]
                diff2 = self.Lslope_b[i]
                if diff1 > 0 and diff2 < 0 and diff_between_left2right > 0:
                    self.Rslope.clear()
                    self.Lslope.clear()
                    self.Rslope_b.clear()
                    self.Lslope_b.clear()
                    return True
        self.Rslope.popleft()
        self.Lslope.popleft()

        self.Rslope_b.popleft()
        self.Lslope_b.popleft()
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
        
        L_exception = False
        R_exception = False
        left_pinky_mcp, left_pinky_pip, left_pinky_dip, left_pinky_tip = None, None, None, None
        right_pinky_mcp, right_pinky_pip, right_pinky_dip, right_pinky_tip = None, None, None, None

        try:
            left_arm_elbow = [self.right_hand_landmark.landmark[13].x,
                               self.right_hand_landmark.landmark[13].y]
            right_arm_elbow = [self.right_hand_landmark.landmark[14].x,
                               self.right_hand_landmark.landmark[14].y]
            left_arm_wrist = [self.right_hand_landmark.landmark[15].x,
                               self.right_hand_landmark.landmark[15].y]
            right_arm_wrist = [self.right_hand_landmark.landmark[16].x,
                               self.right_hand_landmark.landmark[16].y]
        except:
            if len(self.LAslope) == 0:
                return False
            LA_exception = True

            if len(self.RAslope) == 0:
                return False
            RA_exception = True

        if not LA_exception and not RA_exception:
            diff_between_left2right = left_arm_wrist[1] - right_arm_wrist[1]
            self.diff_from_left2right.append(diff_between_left2right)

        if not LA_exception:
            LA_X = [left_arm_elbow[0], left_arm_wrist[0]]
            LA_y = [left_arm_elbow[1], left_arm_wrist[1]]

            LA_X = np.array(LA_X).reshape(-1, 1)
            LA_y = np.array(LA_y).reshape(-1, 1)

            LA_model = LinearRegression()
            LA_model.fit(LA_X, LA_y)

            self.LAslope = np.abs(LA_model.coef_)

        if not RA_exception:
            RA_X = [right_arm_elbow[0], right_arm_wrist[0]]
            RA_y = [right_arm_elbow[1], right_arm_wrist[1]]

            RA_X = np.array(RA_X).reshape(-1, 1)
            RA_y = np.array(RA_y).reshape(-1, 1)

            RA_model = LinearRegression()
            RA_model.fit(RA_X, RA_y)

            self.RAslope = np.abs(RA_model.coef_)

        if self.LAslope < 0.5 and self.RAslope > -0.5:
            # 如果计时尚未开始，开始计时
            if self.arm_last_time is None:
                self.arm_last_time = time.time()
            # 如果已经计时，并且计时超过4秒，将success_action设置为True并退出循环
            elif time.time() - self.arm_last_time >= 4:
                self.arm_last_time = None
                return True
        else:
            # 如果条件不满足，重置计时器
            self.arm_last_time = None

        
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
        except:
            if len(self.Lslope) == 0:
                return False
            L_exception = True
        
        if not L_exception:    
            left_X = [left_pinky_mcp[0], left_pinky_pip[0], left_pinky_dip[0], left_pinky_tip[0]]
            left_y = [left_pinky_mcp[1], left_pinky_pip[1], left_pinky_dip[1], left_pinky_tip[1]]
            Left_X = np.array(left_X).reshape(-1, 1)
            Left_y = np.array(left_y).reshape(-1, 1)
            L_model = LinearRegression()
            L_model.fit(Left_X, Left_y)
    
            diff = (self.left_hand_landmark.landmark[17].z -
                    self.left_hand_landmark.landmark[3].z)
    
            self.Lslope_b.append(diff)
            self.Lslope.append(np.abs(L_model.coef_))


        try:
            right_pinky_mcp = [self.right_hand_landmark.landmark[17].x,
                               self.right_hand_landmark.landmark[17].y]
            right_pinky_pip = [self.right_hand_landmark.landmark[18].x,
                               self.right_hand_landmark.landmark[18].y]
            right_pinky_dip = [self.right_hand_landmark.landmark[19].x,
                               self.right_hand_landmark.landmark[19].y]
            right_pinky_tip = [self.right_hand_landmark.landmark[20].x,
                               self.right_hand_landmark.landmark[20].y]

        except:
            if len(self.Rslope) == 0:
                return False
            R_exception = True
            
        if not R_exception:
            right_X = [right_pinky_mcp[0], right_pinky_pip[0], right_pinky_dip[0], right_pinky_tip[0]]
            right_y = [right_pinky_mcp[1], right_pinky_pip[1], right_pinky_dip[1], right_pinky_tip[1]]
    
            Right_X = np.array(right_X).reshape(-1, 1)
            Right_y = np.array(right_y).reshape(-1, 1)
    
            R_model = LinearRegression()
            R_model.fit(Right_X, Right_y)
    
            diff = self.right_hand_landmark.landmark[17].z - \
                   self.right_hand_landmark.landmark[3].z
    
            self.Rslope_b.append(diff)
            self.Rslope.append(np.abs(R_model.coef_))

        """
        # 左右手小拇指点拟合直线斜率
        print("the slope of L:", L_model.coef_)
        print("the slope of R:", R_model.coef_)
        """



        for i in range(len(self.Lslope)):
            for n in range(len(self.Rslope)):
                if self.Rslope[n] > 0.25 and self.Lslope[i] > 0.25:
                    return False
                diff1 = self.Rslope_b[n]
                diff2 = self.Lslope_b[i]
                if diff1 < 0 and diff2 > 0 and diff_between_left2right < 0:
                    self.Rslope.clear()
                    self.Lslope.clear()
                    self.Rslope_b.clear()
                    self.Lslope_b.clear()
                    return True

        self.Lslope.popleft()
        self.Rslope.popleft()
        self.Rslope_b.popleft()
        self.Lslope_b.popleft()

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
            return True

    def jump_detect(self):
        if self.jump:
            if time.time() - self.jump_last_time > 0.5:
                logger.info("Drop down")
                self.jump = False
        try:
            left_ankle = self.pose_landmarks.landmark[27]
            right_ankle = self.pose_landmarks.landmark[28]
        except:
            return False

        # print(left_ankle.y, right_ankle.y)
        if left_ankle.visibility < 0.7 and right_ankle.visibility < 0.7:
            return self.jump

        # 计算6个点的重心
        # center_y = (left_shoulder.y + right_shoulder.y + left_hip.y + right_hip.y + left_ankle.y + right_ankle.y) / 6
        center_y = (left_ankle.y + right_ankle.y) / 2

        if len(self.jump_data) == 0:
            self.jump_data.append(center_y)
            # self.counter += 1
            self.jump = False
            return False
        # print(self.data)
        for i in self.jump_data:
            if (center_y - i) / center_y < -0.20:
                self.jump_data.clear()
                self.jump_data.append(center_y)
                if not self.jump:
                    logger.info("Jumping")
                    self.jump = True
                    self.jump_last_time = time.time()
                return True
            elif (center_y - i) / center_y > 0.20:
                self.jump_data.clear()
                self.jump_data.append(center_y)
                if self.jump:
                    logger.info("Drop down")
                    self.jump = False
                return False
            else:
                self.jump_data.append(center_y)
                return self.jump
        self.jump_data.popleft()




    def sit_detect(self):

        if self.jump:
            return False
        try:
            left_lag_1 = self.pose_landmarks.landmark[24]
            left_lag_middle = self.pose_landmarks.landmark[26]
            left_lag_3 = self.pose_landmarks.landmark[28]
            right_lag_1 = self.pose_landmarks.landmark[23]
            right_lag_middle = self.pose_landmarks.landmark[25]
            right_lag_3 = self.pose_landmarks.landmark[27]
        except:
            # logger.debug("No pose_landmarks---------------------------")
            return self.previous_sit_down

        left_lag_angle = self.calculate_angle(left_lag_1, left_lag_middle, left_lag_3)
        right_lag_angle = self.calculate_angle(right_lag_1, right_lag_middle, right_lag_3)

        if left_lag_angle is None or right_lag_angle is None:
            # logger.debug("--------------------------------point not exist")
            return self.previous_sit_down

        if left_lag_angle < 50 and right_lag_angle < 50:
            self.sit_down = True
        elif left_lag_angle > 70 and right_lag_angle > 70:
            # logger.debug("---------------sit down detect false------------------")
            self.sit_down = False
        else:
            return self.previous_sit_down

        if self.sit_down:
            if self.previous_sit_down:
                return True
            else:
                self.previous_sit_down = True
                logger.info("Sit down")
                return True
        else:
            if self.previous_sit_down:
                logger.info("Stand up")
            self.previous_sit_down = False
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
