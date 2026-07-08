"""Manual motor smoke test for the real Raspberry Pi car.

Run one action at a time while the wheels are lifted.
Example:
    python -m src.tools.test_motor forward --speed 30 --duration 0.3

调参说明：
- --speed 控制电机速度，范围 0 到 100。电机不动时可以先试 60 或 80。
- --duration 控制动作持续时间，单位是秒。实机第一次测试建议 0.3 到 1 秒。
- 测试前必须架空车轮，确认方向正确后再让小车落地。
"""

import argparse
import time

from src.hardware.motor import MotorController


ACTION_TO_METHOD = {
    # 命令行参数使用短横线，Python 方法名使用下划线，这里做固定映射。
    # 新增动作时，需要同时在 MotorController 中实现方法，并在这里注册命令名。
    "forward": "forward",
    "backward": "backward",
    "left": "left",
    "right": "right",
    "spin-left": "spin_left",
    "spin-right": "spin_right",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Run one short motor action.")
    parser.add_argument("action", choices=ACTION_TO_METHOD.keys())
    parser.add_argument(
        "--speed",
        type=int,
        default=30,
        help="PWM duty cycle from 0 to 100. Try 60 or 80 if 30 cannot start.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=0.3,
        help="Action duration in seconds. Keep it short for first tests.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # 限制测试时长：命令输错或方向反了，也不会让车持续运动太久。
    if args.duration <= 0 or args.duration > 2:
        raise ValueError("duration 必须大于 0 且不超过 2 秒")

    print(f"running {args.action}: speed={args.speed}, duration={args.duration}s")
    motor = MotorController()
    try:
        # 这里只执行一个动作，便于实机确认方向是否符合命令名称。
        action = getattr(motor, ACTION_TO_METHOD[args.action])
        action(args.speed, args.speed)
        time.sleep(args.duration)
    finally:
        # 无论正常结束、报错还是 Ctrl+C，中断前都要停车并释放 GPIO。
        motor.close()
        print("stopped and cleaned GPIO")


if __name__ == "__main__":
    main()
