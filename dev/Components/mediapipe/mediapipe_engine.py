import mediapipe
import cv2


class mediapipe_holistic_engine():
    def __init__(self):
        self.AI_model = mediapipe.solutions.holistic
        self.AI_model_initialized = self.AI_model.Holistic(
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
            cv2.putText(img, "No pose detected", (10, 110), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        if self.results.left_hand_landmarks:
            self.left_hand_detected = True
            self.Left_Hand_Pixel_Landmark = self.results.left_hand_landmarks.landmark
        else:
            self.left_hand_detected = False
            cv2.putText(img, "No left hand detected", (10, 250), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        if self.results.right_hand_landmarks:
            self.right_hand_detected = True
            self.Right_Hand_Pixel_Landmark = self.results.right_hand_landmarks.landmark
        else:
            self.right_hand_detected = False
            cv2.putText(img, "No right hand detected", (10, 320), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

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


class mediapipe_hand_engine():
    def __init__(self):
        self.AI_model = mediapipe.solutions.hands
        self.AI_model_initialized = self.AI_model.Hands(
            model_complexity=1,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mediapipe.solutions.drawing_utils
        self.mp_drawing_styles = mediapipe.solutions.drawing_styles

    def process_image(self, img):
        results = self.AI_model_initialized.process(img)

        if results.multi_hand_landmarks:
            self.detected = True
            self.Pixel_Landmark = results.multi_hand_landmarks
            self.World_Landmark = results.multi_hand_world_landmarks
        else:
            self.detected = False
            cv2.putText(img, "No hand detected", (10, 110), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    def expand_landmark(self):
        if self.detected:
            # loop the Pixel_Landmark for all detected hands
            for id, hand_landmarks in enumerate(self.Pixel_Landmark):
                setattr(self, "Hand_" + str(id) + "_Wrist_x", hand_landmarks.landmark[0].x)
                """
                output example of first hand:
                self.Hand_0_Wrist_x = (0.5, 0.6, 0.7, 0.8, 0.9, ...)
                output example of second hand:
                self.Hand_1_Wrist_x = (0.5, 0.6, 0.7, 0.8, 0.9, ...)

                get the x value of the first hand's wrist:
                getattr(self, "Hand_" + str(id) + "_Wrist_x")
                """

                setattr(self, "Hand_" + str(id) + "_Wrist_y", hand_landmarks.landmark[0].y)
                setattr(self, "Hand_" + str(id) + "_Thumb_CMC_x", hand_landmarks.landmark[1].x)
                setattr(self, "Hand_" + str(id) + "_Thumb_CMC_y", hand_landmarks.landmark[1].y)
                setattr(self, "Hand_" + str(id) + "_Thumb_MCP_x", hand_landmarks.landmark[2].x)
                setattr(self, "Hand_" + str(id) + "_Thumb_MCP_y", hand_landmarks.landmark[2].y)
                setattr(self, "Hand_" + str(id) + "_Thumb_IP_x", hand_landmarks.landmark[3].x)
                setattr(self, "Hand_" + str(id) + "_Thumb_IP_y", hand_landmarks.landmark[3].y)
                setattr(self, "Hand_" + str(id) + "_Thumb_Tip_x", hand_landmarks.landmark[4].x)
                setattr(self, "Hand_" + str(id) + "_Thumb_Tip_y", hand_landmarks.landmark[4].y)
                setattr(self, "Hand_" + str(id) + "_Index_Finger_MCP_x", hand_landmarks.landmark[5].x)
                setattr(self, "Hand_" + str(id) + "_Index_Finger_MCP_y", hand_landmarks.landmark[5].y)
                setattr(self, "Hand_" + str(id) + "_Index_Finger_PIP_x", hand_landmarks.landmark[6].x)
                setattr(self, "Hand_" + str(id) + "_Index_Finger_PIP_y", hand_landmarks.landmark[6].y)
                setattr(self, "Hand_" + str(id) + "_Index_Finger_DIP_x", hand_landmarks.landmark[7].x)
                setattr(self, "Hand_" + str(id) + "_Index_Finger_DIP_y", hand_landmarks.landmark[7].y)
                setattr(self, "Hand_" + str(id) + "_Index_Finger_Tip_x", hand_landmarks.landmark[8].x)
                setattr(self, "Hand_" + str(id) + "_Index_Finger_Tip_y", hand_landmarks.landmark[8].y)
                setattr(self, "Hand_" + str(id) + "_Middle_Finger_MCP_x", hand_landmarks.landmark[9].x)
                setattr(self, "Hand_" + str(id) + "_Middle_Finger_MCP_y", hand_landmarks.landmark[9].y)
                setattr(self, "Hand_" + str(id) + "_Middle_Finger_PIP_x", hand_landmarks.landmark[10].x)
                setattr(self, "Hand_" + str(id) + "_Middle_Finger_PIP_y", hand_landmarks.landmark[10].y)
                setattr(self, "Hand_" + str(id) + "_Middle_Finger_DIP_x", hand_landmarks.landmark[11].x)
                setattr(self, "Hand_" + str(id) + "_Middle_Finger_DIP_y", hand_landmarks.landmark[11].y)
                setattr(self, "Hand_" + str(id) + "_Middle_Finger_Tip_x", hand_landmarks.landmark[12].x)
                setattr(self, "Hand_" + str(id) + "_Middle_Finger_Tip_y", hand_landmarks.landmark[12].y)
                setattr(self, "Hand_" + str(id) + "_Ring_Finger_MCP_x", hand_landmarks.landmark[13].x)
                setattr(self, "Hand_" + str(id) + "_Ring_Finger_MCP_y", hand_landmarks.landmark[13].y)
                setattr(self, "Hand_" + str(id) + "_Ring_Finger_PIP_x", hand_landmarks.landmark[14].x)
                setattr(self, "Hand_" + str(id) + "_Ring_Finger_PIP_y", hand_landmarks.landmark[14].y)
                setattr(self, "Hand_" + str(id) + "_Ring_Finger_DIP_x", hand_landmarks.landmark[15].x)
                setattr(self, "Hand_" + str(id) + "_Ring_Finger_DIP_y", hand_landmarks.landmark[15].y)
                setattr(self, "Hand_" + str(id) + "_Ring_Finger_Tip_x", hand_landmarks.landmark[16].x)
                setattr(self, "Hand_" + str(id) + "_Ring_Finger_Tip_y", hand_landmarks.landmark[16].y)
                setattr(self, "Hand_" + str(id) + "_Pinky_MCP_x", hand_landmarks.landmark[17].x)
                setattr(self, "Hand_" + str(id) + "_Pinky_MCP_y", hand_landmarks.landmark[17].y)
                setattr(self, "Hand_" + str(id) + "_Pinky_PIP_x", hand_landmarks.landmark[18].x)
                setattr(self, "Hand_" + str(id) + "_Pinky_PIP_y", hand_landmarks.landmark[18].y)
                setattr(self, "Hand_" + str(id) + "_Pinky_DIP_x", hand_landmarks.landmark[19].x)
                setattr(self, "Hand_" + str(id) + "_Pinky_DIP_y", hand_landmarks.landmark[19].y)
                setattr(self, "Hand_" + str(id) + "_Pinky_Tip_x", hand_landmarks.landmark[20].x)
                setattr(self, "Hand_" + str(id) + "_Pinky_Tip_y", hand_landmarks.landmark[20].y)

    def draw_all_landmark_circle(self, img):
        if self.detected:
            for hand_landmarks in self.Pixel_Landmark:
                for id, lm in enumerate(hand_landmarks.landmark):
                    cx, cy = int(lm.x * img.shape[1]), int(lm.y * img.shape[0])
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

    def draw_all_landmark_drawing_utils(self, img):
        if self.detected:
            for hand_landmarks in self.Pixel_Landmark:
                self.mp_drawing.draw_landmarks(
                    img,
                    hand_landmarks,
                    self.AI_model.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style(),
                )


class mediapipe_pose_engine():
    def __init__(self):
        self.AI_model = mediapipe.solutions.pose
        self.AI_model_initialized = self.AI_model.Pose(
            model_complexity=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            enable_segmentation=False,
            smooth_segmentation=False
        )
        self.mp_drawing = mediapipe.solutions.drawing_utils
        self.mp_drawing_styles = mediapipe.solutions.drawing_styles

    def process_image(self, img):
        results = self.AI_model_initialized.process(img)
        if results.pose_landmarks:
            self.Pixel_Landmark_list = results.pose_landmarks
            self.Pixel_Landmark = results.pose_landmarks.landmark
            self.World_Landmark = results.pose_world_landmarks.landmark
        else:
            cv2.putText(img, "No pose detected", (10, 110), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    def expand_landmark(self):
        self.Nose_x, self.Nose_y = self.Pixel_Landmark[0].x, self.Pixel_Landmark[0].y
        self.Left_Eye_Inner_x, self.Left_Eye_Inner_y = self.Pixel_Landmark[1].x, self.Pixel_Landmark[1].y
        self.Left_Eye_x, self.Left_Eye_y = self.Pixel_Landmark[2].x, self.Pixel_Landmark[2].y
        self.Left_Eye_Outer_x, self.Left_Eye_Outer_y = self.Pixel_Landmark[3].x, self.Pixel_Landmark[3].y
        self.Right_Eye_Inner_x, self.Right_Eye_Inner_y = self.Pixel_Landmark[4].x, self.Pixel_Landmark[4].y
        self.Right_Eye_x, self.Right_Eye_y = self.Pixel_Landmark[5].x, self.Pixel_Landmark[5].y
        self.Right_Eye_Outer_x, self.Right_Eye_Outer_y = self.Pixel_Landmark[6].x, self.Pixel_Landmark[6].y
        self.Left_Ear_x, self.Left_Ear_y = self.Pixel_Landmark[7].x, self.Pixel_Landmark[7].y
        self.Right_Ear_x, self.Right_Ear_y = self.Pixel_Landmark[8].x, self.Pixel_Landmark[8].y
        self.Mouth_Left_x, self.Mouth_Left_y = self.Pixel_Landmark[9].x, self.Pixel_Landmark[9].y
        self.Mouth_Right_x, self.Mouth_Right_y = self.Pixel_Landmark[10].x, self.Pixel_Landmark[10].y
        self.Left_Shoulder_x, self.Left_Shoulder_y = self.Pixel_Landmark[11].x, self.Pixel_Landmark[11].y
        self.Right_Shoulder_x, self.Right_Shoulder_y = self.Pixel_Landmark[12].x, self.Pixel_Landmark[12].y
        self.Left_Elbow_x, self.Left_Elbow_y = self.Pixel_Landmark[13].x, self.Pixel_Landmark[13].y
        self.Right_Elbow_x, self.Right_Elbow_y = self.Pixel_Landmark[14].x, self.Pixel_Landmark[14].y
        self.Left_Wrist_x, self.Left_Wrist_y = self.Pixel_Landmark[15].x, self.Pixel_Landmark[15].y
        self.Right_Wrist_x, self.Right_Wrist_y = self.Pixel_Landmark[16].x, self.Pixel_Landmark[16].y
        self.Left_Pinky_x, self.Left_Pinky_y = self.Pixel_Landmark[17].x, self.Pixel_Landmark[17].y
        self.Right_Pinky_x, self.Right_Pinky_y = self.Pixel_Landmark[18].x, self.Pixel_Landmark[18].y
        self.Left_Index_x, self.Left_Index_y = self.Pixel_Landmark[19].x, self.Pixel_Landmark[19].y
        self.Right_Index_x, self.Right_Index_y = self.Pixel_Landmark[20].x, self.Pixel_Landmark[20].y
        self.Left_Thumb_x, self.Left_Thumb_y = self.Pixel_Landmark[21].x, self.Pixel_Landmark[21].y
        self.Right_Thumb_x, self.Right_Thumb_y = self.Pixel_Landmark[22].x, self.Pixel_Landmark[22].y
        self.Left_Hip_x, self.Left_Hip_y = self.Pixel_Landmark[23].x, self.Pixel_Landmark[23].y
        self.Right_Hip_x, self.Right_Hip_y = self.Pixel_Landmark[24].x, self.Pixel_Landmark[24].y
        self.Left_Knee_x, self.Left_Knee_y = self.Pixel_Landmark[25].x, self.Pixel_Landmark[25].y
        self.Right_Knee_x, self.Right_Knee_y = self.Pixel_Landmark[26].x, self.Pixel_Landmark[26].y
        self.Left_Ankle_x, self.Left_Ankle_y = self.Pixel_Landmark[27].x, self.Pixel_Landmark[27].y
        self.Right_Ankle_x, self.Right_Ankle_y = self.Pixel_Landmark[28].x, self.Pixel_Landmark[28].y
        self.Left_Heel_x, self.Left_Heel_y = self.Pixel_Landmark[29].x, self.Pixel_Landmark[29].y
        self.Right_Heel_x, self.Right_Heel_y = self.Pixel_Landmark[30].x, self.Pixel_Landmark[30].y
        self.Left_Foot_Index_x, self.Left_Foot_Index_y = self.Pixel_Landmark[31].x, self.Pixel_Landmark[31].y
        self.Right_Foot_Index_x, self.Right_Foot_Index_y = self.Pixel_Landmark[32].x, self.Pixel_Landmark[32].y

    def draw_all_landmark_circle(self, img):
        for id, lm in enumerate(self.Pixel_Landmark):
            cx, cy = int(lm.x * img.shape[1]), int(lm.y * img.shape[0])
            cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

    def draw_all_landmark_line(self, img):
        # draw line for all relevant landmark
        # draw line for left arm
        cv2.line(img, (int(self.Left_Shoulder_x * img.shape[1]), int(self.Left_Shoulder_y * img.shape[0])),
                 (int(self.Left_Elbow_x * img.shape[1]), int(self.Left_Elbow_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Left_Elbow_x * img.shape[1]), int(self.Left_Elbow_y * img.shape[0])),
                 (int(self.Left_Wrist_x * img.shape[1]), int(self.Left_Wrist_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Left_Wrist_x * img.shape[1]), int(self.Left_Wrist_y * img.shape[0])),
                 (int(self.Left_Pinky_x * img.shape[1]), int(self.Left_Pinky_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Left_Wrist_x * img.shape[1]), int(self.Left_Wrist_y * img.shape[0])),
                 (int(self.Left_Index_x * img.shape[1]), int(self.Left_Index_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Left_Index_x * img.shape[1]), int(self.Left_Index_y * img.shape[0])),
                 (int(self.Left_Thumb_x * img.shape[1]), int(self.Left_Thumb_y * img.shape[0])), (255, 0, 0), 3)
        # draw line for right arm
        cv2.line(img, (int(self.Right_Shoulder_x * img.shape[1]), int(self.Right_Shoulder_y * img.shape[0])),
                 (int(self.Right_Elbow_x * img.shape[1]), int(self.Right_Elbow_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Right_Elbow_x * img.shape[1]), int(self.Right_Elbow_y * img.shape[0])),
                 (int(self.Right_Wrist_x * img.shape[1]), int(self.Right_Wrist_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Right_Wrist_x * img.shape[1]), int(self.Right_Wrist_y * img.shape[0])),
                 (int(self.Right_Pinky_x * img.shape[1]), int(self.Right_Pinky_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Right_Wrist_x * img.shape[1]), int(self.Right_Wrist_y * img.shape[0])),
                 (int(self.Right_Index_x * img.shape[1]), int(self.Right_Index_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Right_Index_x * img.shape[1]), int(self.Right_Index_y * img.shape[0])),
                 (int(self.Right_Thumb_x * img.shape[1]), int(self.Right_Thumb_y * img.shape[0])), (255, 0, 0), 3)
        # draw line for body
        cv2.line(img, (int(self.Left_Shoulder_x * img.shape[1]), int(self.Left_Shoulder_y * img.shape[0])),
                 (int(self.Right_Shoulder_x * img.shape[1]), int(self.Right_Shoulder_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Left_Shoulder_x * img.shape[1]), int(self.Left_Shoulder_y * img.shape[0])),
                 (int(self.Left_Hip_x * img.shape[1]), int(self.Left_Hip_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Right_Shoulder_x * img.shape[1]), int(self.Right_Shoulder_y * img.shape[0])),
                 (int(self.Right_Hip_x * img.shape[1]), int(self.Right_Hip_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Left_Hip_x * img.shape[1]), int(self.Left_Hip_y * img.shape[0])),
                 (int(self.Right_Hip_x * img.shape[1]), int(self.Right_Hip_y * img.shape[0])), (255, 0, 0), 3)
        # draw line for left leg
        cv2.line(img, (int(self.Left_Hip_x * img.shape[1]), int(self.Left_Hip_y * img.shape[0])),
                 (int(self.Left_Knee_x * img.shape[1]), int(self.Left_Knee_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Left_Knee_x * img.shape[1]), int(self.Left_Knee_y * img.shape[0])),
                 (int(self.Left_Ankle_x * img.shape[1]), int(self.Left_Ankle_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Left_Ankle_x * img.shape[1]), int(self.Left_Ankle_y * img.shape[0])),
                 (int(self.Left_Heel_x * img.shape[1]), int(self.Left_Heel_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Left_Ankle_x * img.shape[1]), int(self.Left_Ankle_y * img.shape[0])),
                 (int(self.Left_Foot_Index_x * img.shape[1]), int(self.Left_Foot_Index_y * img.shape[0])), (255, 0, 0),
                 3)
        # draw line for right leg
        cv2.line(img, (int(self.Right_Hip_x * img.shape[1]), int(self.Right_Hip_y * img.shape[0])),
                 (int(self.Right_Knee_x * img.shape[1]), int(self.Right_Knee_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Right_Knee_x * img.shape[1]), int(self.Right_Knee_y * img.shape[0])),
                 (int(self.Right_Ankle_x * img.shape[1]), int(self.Right_Ankle_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Right_Ankle_x * img.shape[1]), int(self.Right_Ankle_y * img.shape[0])),
                 (int(self.Right_Heel_x * img.shape[1]), int(self.Right_Heel_y * img.shape[0])), (255, 0, 0), 3)
        cv2.line(img, (int(self.Right_Ankle_x * img.shape[1]), int(self.Right_Ankle_y * img.shape[0])),
                 (int(self.Right_Foot_Index_x * img.shape[1]), int(self.Right_Foot_Index_y * img.shape[0])),
                 (255, 0, 0), 3)

    def draw_all_landmark_drawing_utils(self, img):
        self.mp_drawing.draw_landmarks(
            img,
            self.Pixel_Landmark_list,
            self.AI_model.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
        )