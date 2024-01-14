import cv2
import threading
import multiprocessing
import time
from dev.multiprocessing.cameraIO.CV2_Engine import CameraCapture

# CameraCapture 类定义保持不变

def process_image(frame_count,image, result_images):
    # 这里添加图像处理逻辑
    # 示例：将图像转换为灰度
    processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    result_images.put((frame_count,processed_image))

def display_image(result_images):

    # 图片缓冲区
    image_buffer = {}
    expected_frame = 0
    while True:
        if expected_frame not in image_buffer:
            # 如果缓冲区中没有图像，从队列中获取图像
            if not result_images.empty():
                frame_count, image = result_images.get()
                print(f"Received frame {frame_count}")
                if frame_count == expected_frame:
                    cv2.imshow('Processed Frame', image)
                    expected_frame += 1
                else:
                    image_buffer[frame_count] = image
            else:
                # 将缓冲区最小的expected_frame显示出来
                if len(image_buffer) > 0:
                    expected_frame = min(image_buffer.keys())
                else:
                    continue
        else:
            # 如果缓冲区中有图像，显示图像
            image = image_buffer.pop(expected_frame)
            cv2.imshow('Processed Frame', image)
            expected_frame += 1

def main():
    pool = multiprocessing.Pool(4)  # 创建一个进程池，大小为4
    print(1)
    cv2_engine = CameraCapture()
    cv2_engine.start()
    print(2)
    result_images = multiprocessing.Manager().Queue()
    display_image_thread = threading.Thread(target=display_image, args=(result_images,))

    count = 0
    while True:
        image = cv2_engine.get_frame()
        result = pool.apply_async(process_image, [count,image,result_images])  # 将图像添加到进程池
        count += 1

if __name__ == '__main__':
    main()