from sklearn.linear_model import LinearRegression
import cv2
class Error_engine_test():

    def __init__(self, mediapipe_hand_engine_instance):
        self.mediapipe_hand_engine_instance = mediapipe_hand_engine_instance

    def calculate_regression_error_sklearn(self):
        if self.mediapipe_hand_engine_instance.left_hand_detected:
            # 获取左手的关键点坐标
            thumb_tip_x = getattr(self.mediapipe_hand_engine_instance, "Hand_0_Thumb_Tip_x")
            thumb_tip_y = getattr(self.mediapipe_hand_engine_instance, "Hand_0_Thumb_Tip_y")

            index_finger_tip_x = getattr(self.mediapipe_hand_engine_instance, "Hand_0_Index_Finger_Tip_x")
            index_finger_tip_y = getattr(self.mediapipe_hand_engine_instance, "Hand_0_Index_Finger_Tip_y")

            # 在这里添加更多的手部关键点...

            # 使用sklearn进行线性回归
            X = [[thumb_tip_x], [index_finger_tip_x]]  # 输入特征，这里以两个关键点为例
            y = [thumb_tip_y, index_finger_tip_y]  # 输出标签

            model = LinearRegression()
            model.fit(X, y)

            # 预测
            predicted_thumb_tip_y = model.predict([[thumb_tip_x]])[0]

            # 计算回归误差
            regression_error = self.calculate_error(thumb_tip_y, predicted_thumb_tip_y)

            return regression_error
        else:
            return None

    def display_FPS(self, img):
        cv2.putText(img, str(int(self.fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 255), 5)