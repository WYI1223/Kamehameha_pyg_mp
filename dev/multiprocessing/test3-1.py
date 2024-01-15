import multiprocessing

# 定义计算 15 次方的函数，并包括输入的序号
def calculate_power_15(number, order):
    try:
        return number ** 15, order
    except Exception as e:
        print(f"计算时发生错误: {e}")
        return None, order

class PowerCalculator:
    def __init__(self):
        self.input_order = multiprocessing.Value('i', 0)
        self.pool = multiprocessing.Pool()

    def print_result(self, result):
        print("回调函数被调用")  # 调试信息
        value, order = result
        if value is not None:
            print(f"用户第 {order} 次输入的数字的 15 次方是: {value}")

    def handle_input(self):
        while True:
            user_input = input("请输入一个数字（输入 'exit' 退出）: ")
            if user_input.lower() == 'exit':
                break
            try:
                number = float(user_input)
                with self.input_order.get_lock():
                    order = self.input_order.value + 1
                    self.input_order.value = order
                self.pool.apply_async(calculate_power_15, args=(number, order), callback=self.print_result)
            except ValueError:
                print("无效输入，请输入一个数字。")

    def close_pool(self):
        self.pool.close()
        self.pool.join()

def main():
    calculator = PowerCalculator()
    calculator.handle_input()
    calculator.close_pool()

if __name__ == "__main__":
    main()
