import cv2
import mediapipe as mp
import multiprocessing
import threading

def capture_frames(capture_queue):
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))  # set codec
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # set width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # set height
    cap.set(cv2.CAP_PROP_FPS, 60)  # set fps
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        capture_queue.put(frame)
    cap.release()

def process_frames(capture_queue, display_queue, fps_engine):
    mp_face_detection = mp.solutions.face_detection.FaceDetection()
    while True:
        frame = capture_queue.get()
        if frame is None:  # 退出信号
            break
        # 图像处理逻辑
        results = mp_face_detection.process(frame)
        fps = fps_engine.get_fps()
        cv2.putText(frame, f'FPS: {fps}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        display_queue.put(frame)

def display_frames(display_queue):
    while True:
        frame = display_queue.get()
        if frame is None:
            break
        cv2.imshow('Processed Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

def main():
    capture_queue = multiprocessing.Queue()
    display_queue = multiprocessing.Queue()
    fps_engine = FPS_Engine()

    # 捕获线程
    capture_thread = threading.Thread(target=capture_frames, args=(capture_queue,))
    capture_thread.start()

    # 处理进程
    process_process = multiprocessing.Process(target=process_frames, args=(capture_queue, display_queue, fps_engine))
    process_process.start()

    # 显示线程
    display_thread = threading.Thread(target=display_frames, args=(display_queue,))
    display_thread.start()

    capture_thread.join()
    process_process.join()
    display_thread.join()

if __name__ == '__main__':
    from dev.Components.function.FPS_Engine import FPS_Engine
    main()
