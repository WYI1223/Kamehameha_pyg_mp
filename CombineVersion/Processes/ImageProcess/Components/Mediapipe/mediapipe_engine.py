import mediapipe
import cv2


class mediapipe_holistic_engine:
    def __init__(self):
        self.AI_model = mediapipe.solutions.holistic
        self.AI_model_initialized = self.AI_model.Holistic(
            # face = False,
            model_complexity=1,
            refine_face_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mediapipe.solutions.drawing_utils
        self.mp_drawing_styles = mediapipe.solutions.drawing_styles

    def process_image(self, img):
        self.results = self.AI_model_initialized.process(img)

        if self.results.pose_landmarks:
            self.pose_detected = True
            self.Pose_Pixel_Landmark_list = self.results.pose_landmarks
            self.Pose_Pixel_Landmark = self.results.pose_landmarks.landmark
            self.Pose_World_Landmark = self.results.pose_world_landmarks.landmark
        else:
            self.pose_detected = False
            cv2.putText(img, "No pose detected", (10, 110), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)

        if self.results.left_hand_landmarks:
            self.left_hand_detected = True
            self.Left_Hand_Pixel_Landmark = self.results.left_hand_landmarks.landmark
        else:
            self.left_hand_detected = False
            cv2.putText(img, "No left hand detected", (10, 250), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)

        if self.results.right_hand_landmarks:
            self.right_hand_detected = True
            self.Right_Hand_Pixel_Landmark = self.results.right_hand_landmarks.landmark
        else:
            self.right_hand_detected = False
            cv2.putText(img, "No right hand detected", (10, 320), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)

    def draw_all_landmark_drawing_utils(self, img):

        if self.pose_detected:
            self.mp_drawing.draw_landmarks(
                img,
                self.results.pose_landmarks,
                self.AI_model.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles
                .get_default_pose_landmarks_style())
        if self.left_hand_detected:
            self.mp_drawing.draw_landmarks(
                img,
                self.results.left_hand_landmarks,
                self.AI_model.HAND_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles
                .get_default_hand_landmarks_style())
        if self.right_hand_detected:
            self.mp_drawing.draw_landmarks(
                img,
                self.results.right_hand_landmarks,
                self.AI_model.HAND_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles
                .get_default_hand_landmarks_style())

            # 在图片上绘制特定手部标记的坐标
        def draw_hand_point(img, hand_landmarks, point_idx):
            if hand_landmarks:
                hand_point = hand_landmarks.landmark[point_idx]
                x, y, z = int(hand_point.x * img.shape[1]), int(hand_point.y * img.shape[0]), hand_point.z
                cv2.putText(img, f"Point {point_idx}: ({x}, {y}, {z:.2f})", (10, y), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)

            # 绘制左手的17号和3号点的坐标
        if self.left_hand_detected:
            draw_hand_point(img, self.results.left_hand_landmarks, 17)
            draw_hand_point(img, self.results.left_hand_landmarks, 3)

            # 绘制右手的17号和3号点的坐标
        if self.right_hand_detected:
            draw_hand_point(img, self.results.right_hand_landmarks, 17)
            draw_hand_point(img, self.results.right_hand_landmarks, 3)

