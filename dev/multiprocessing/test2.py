import cv2
import multiprocessing
import threading
import time
from dev.Components.function.FPS_Engine import FPS_Engine
from dev.Components.mediapipe.mediapipe_engine import *

def capture_frames(capture_queue):
    cap = cv2.VideoCapture(0)
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        timestamp = time.time()  # 获取当前时间戳
        capture_queue.put((frame_count, timestamp, frame))
        frame_count += 1
    cap.release()

def process_frame_wrapper(frame_data):
    print("process_frame_wrapper is running")
    capture_queue, display_queue, frame_count, timestamp, frame = frame_data
    fps_engine = FPS_Engine()
    holistic_detection = mediapipe_holistic_engine()
    if frame is not None:
        results = holistic_detection.process_image(frame)
        holistic_detection.draw_all_landmark_drawing_utils(frame)
        fps = fps_engine.get_fps()
        cv2.putText(frame, f'FPS: {fps}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        display_queue.put((frame_count, timestamp, frame))

def display_frames(display_queue):
    print("display_frames is running")
    buffer = {}
    expected_frame = 0
    while True:
        if not display_queue.empty():
            frame_count, timestamp, frame = display_queue.get()
            print(f"Received frame {frame_count}")
            if frame_count == expected_frame:
                cv2.imshow('Processed Frame', frame)
                expected_frame += 1
            else:
                buffer[frame_count] = frame
        else:
            # 如果队列是空的，检查缓冲区
            if expected_frame in buffer:
                frame = buffer.pop(expected_frame)
                cv2.imshow('Processed Frame', frame)
                expected_frame += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

def main():
    manager = multiprocessing.Manager()
    capture_queue = manager.Queue()
    display_queue = manager.Queue()

    capture_thread = threading.Thread(target=capture_frames, args=(capture_queue,))
    display_thread = threading.Thread(target=display_frames, args=(display_queue,))

    capture_thread.start()
    display_thread.start()

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        while capture_thread.is_alive():
            if not capture_queue.empty():
                frame_data = capture_queue.get()
                pool.apply_async(process_frame_wrapper, args=(frame_data,))

    capture_thread.join()
    display_thread.join()

if __name__ == '__main__':
    main()