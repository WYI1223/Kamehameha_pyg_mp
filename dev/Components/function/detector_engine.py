import time
from loguru import logger
from sklearn.linear_model import LinearRegression
import math
import cv2
import numpy as np
class TposeDetector:
    def __init__(self,model):
        self.model = model
        self.initilize()

    def initilize(self):
        try:
            self.pose_landmarks = self.model.results.pose_landmarks
        except:
            self.pose_landmarks = None
            pass
        pass
    def calculate_angle(self, point1, point2, point3):
        # Calculate the angle formed by three points
        a = math.sqrt((point2.x - point3.x)**2 + (point2.y - point3.y)**2)
        b = math.sqrt((point1.x - point3.x)**2 + (point1.y - point3.y)**2)
        c = math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
        angle = math.acos((b**2 + c**2 - a**2) / (2 * b * c))
        return math.degrees(angle)

    def is_t_pose(self, landmarks):
        # Using the provided landmarks diagram to identify the correct indices
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_elbow = landmarks[13]
        right_elbow = landmarks[14]
        left_wrist = landmarks[15]
        right_wrist = landmarks[16]
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        left_ankle = landmarks[27]
        right_ankle = landmarks[28]

        # Check if arms are parallel to the ground
        left_arm_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_arm_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
        arms_parallel = abs(left_arm_angle - 180) < 10 and abs(right_arm_angle - 180) < 10

        # Check if feet are together by measuring the distance between the ankles
        feet_distance = math.sqrt((left_ankle.x - right_ankle.x)**2 + (left_ankle.y - right_ankle.y)**2)
        # The threshold for feet_distance can be adjusted based on the model's scale
        feet_together = feet_distance < 0.1

        return arms_parallel and feet_together




    def draw_box(self, image):
        # 获取图像的宽度和高度
        image_height, image_width, _ = image.shape

        # 计算矩形的左上角和右下角坐标，使其位于图像中央并更长而窄
        center_x = image_width // 2
        center_y = image_height // 2
        half_width = 300  # 矩形的一半宽度
        half_height = 520  # 矩形的一半高度

        # 计算矩形的坐标
        top_left = (center_x - half_width, center_y - half_height)
        bottom_right = (center_x + half_width, center_y + half_height)

        # 初始化所有关键点是否在矩形内的标志
        all_landmarks_inside = True
        landmark = None
        try:
            self.pose_landmarks = self.model.results.pose_landmarks
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
        else:
            cv2.rectangle(image, top_left, bottom_right, (0, 0, 255), 2)  # 红色矩形



class attack_detector:
    _logger = None
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
    def set_logger(logger_):
        attack_detector._logger = logger_

    def __init__(self):
        # self.queue = queue.Queue()

        # 目前action状态机，如果为空，则判断action1，成功则+1，并判断下一个动作
        self.state_machine = 0
        self.model = None
        # 需要一个数组来短暂的储存最近几次检测到的动作, 来避免一只手检测另一只手没有检测到后来又检测到的情况
        self.data = {}
        self.sit_down = False

    def intialize_model(self,model):
        self.model = model
        # 当state_machine不为0时，开始计时，超过10s则将state_machine归0
        self.last_time = time.time()

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
                print("Action1 done -- {}".format(time.time()))
            pass

        if self.state_machine == 1:
            if self.action2():
                self.state_machine += 1
                self.last_time = time.time()
                print("Action2 done -- {}".format(time.time()))
            pass

        if self.state_machine == 2:
            if self.action3():
                self.state_machine = 0
                print("Action3 done -- {}".format(time.time()))
                return True
            pass

        # 5s 后状态机归0
        if self.state_machine !=0 and time.time() - self.last_time > 10:
            print("Action reset")
            self.state_machine = 0
        return False

    def action1(self):
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
            return False


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

        # 判断小拇指是否到达指定斜率(动作一左手在上大拇指在后)
        if L_model.coef_ > -0.25 and L_model.coef_ < 0 and diff > 0:
            logger.info("Action1 done")
            return True

        """
        暂定动作一逻辑由拟合直线斜率和z轴坐标来定，斜率需要测试，z轴坐标主要体现在大拇指与小拇指距离差上
            若右手是负值则是小拇指在前，则是动作一
            反之则到了动作二
        """


    def action2(self):
        self.isSuccess2 = False
        try:
            # 详见handlandmark.jpg
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
            return False

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
        R_model.fit(Right_X, Right_y)

        """
        # 左右手小拇指点拟合直线斜率
        print("the slope of L:", L_model.coef_)
        print("the slope of R:", R_model.coef_)
        """

        # z轴小拇指与大拇指的坐标差值
        diff = self.model.results.right_hand_landmarks.landmark[17].z - self.model.results.right_hand_landmarks.landmark[
            3].z

        # 判断小拇指是否到达指定斜率(动作二右手在上大拇指在后)
        if R_model.coef_ > -0.25 and R_model.coef_ < 0 and diff > 0:
            logger.info("Action2 done")
            return True



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
        if left_angle > 125 and right_angle > 125:
            hand_push = True
        # ------------------------------------------------------------------这里需要加入log，这里判断的是手臂伸直，所以应该有个info，手臂伸直的log
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

                logger.info("Action3 done")
                    # ---------------------------这里是判断是否手掌张开并伸直，所以这里要加log，info，手臂伸直并手掌打开，action3动作完成。
                return (True and hand_push)
            return False
        else:
            return False

    def sit_detect(self):

        try:
            left_lag_1 = self.model.results.pose_landmarks.landmark[24]
            left_lag_middle = self.model.results.pose_landmarks.landmark[26]
            left_lag_3 = self.model.results.pose_landmarks.landmark[28]
            right_lag_1 = self.model.results.pose_landmarks.landmark[23]
            right_lag_middle = self.model.results.pose_landmarks.landmark[25]
            right_lag_3 = self.model.results.pose_landmarks.landmark[27]
        except:
            if self.sit_down:
                logger.info("Stand up")
            self.sit_down = False
            return False


        left_lag_angle = self.calculate_angle(left_lag_1, left_lag_middle, left_lag_3)
        right_lag_angle = self.calculate_angle(right_lag_1, right_lag_middle, right_lag_3)

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
        self.data = []*10
        self.counter = 0
        pass

    def intialize_model(self, model):
        self.model = model

        pass
    def jump(self):
        try:
            # left_shoulder = self.model.results.pose_landmarks.landmark[11]
            # right_shoulder = self.model.results.pose_landmarks.landmark[12]
            # left_hip = self.model.results.pose_landmarks.landmark[23]
            # right_hip = self.model.results.pose_landmarks.landmark[24]
            left_ankle = self.model.results.pose_landmarks.landmark[27]
            right_ankle = self.model.results.pose_landmarks.landmark[28]
        except:
            return False

        # 计算6个点的重心
        # center_y = (left_shoulder.y + right_shoulder.y + left_hip.y + right_hip.y + left_ankle.y + right_ankle.y) / 6
        center_y = (left_ankle.y + right_ankle.y) / 2

        if self.data == []:
            self.data.append(center_y)
            self.counter += 1
            return False
        for i in self.data:
            if (center_y - i)/center_y < -0.5:
                print(self.data)
                self.data = [center_y]
                logger.info("Jumping")
                return True
            else:
                self.data.append(center_y)
                if len(self.data) > 10:
                    self.data.pop(0)
                return False




logger.info("")
logger.debug("")
