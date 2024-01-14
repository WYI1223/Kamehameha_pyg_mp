import multiprocessing
import time


# 定义计算 15 次方的函数
def calculate_power_15(number):
    time.sleep(number)
    return number ** 1 + number ** 2 + number ** 3 + number ** 4 + number ** 5 + number ** 6 + number ** 7 + number ** 8 + number ** 9 + number ** 10 + number ** 11 + number ** 12 + number ** 13 + number ** 14 + number ** 15

# 处理计算结果的回调函数
def print_result(result):
    print(f"结果是: {result}")

# 主函数
def main():
    pool = multiprocessing.Pool()

    while True:
        user_input = input("请输入一个数字（输入 'exit' 退出）: ")
        if user_input.lower() == 'exit':
            break
        try:
            number = float(user_input)
            pool.apply_async(calculate_power_15, args=(number,), callback=print_result)
        except ValueError:
            print("无效输入，请输入一个数字。")

    pool.close()
    pool.join()

if __name__ == "__main__":
    main()
