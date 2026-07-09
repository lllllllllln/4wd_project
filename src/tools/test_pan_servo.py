"""水平云台舵机测试脚本。

用途：
    单独验证摄像头水平云台是否能转动，不涉及摄像头拍照。

常用命令：
    python3 src/tools/test_pan_servo.py
    python3 src/tools/test_pan_servo.py --pin 23 --angles 0,45,90,135,180
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time
from typing import List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from src.hardware.servo import ServoController, ServoError


def parse_angles(value: str) -> List[float]:
    """解析逗号分隔的舵机角度列表。

    参数：
        value: 逗号分隔角度，例如 ``0,45,90,135,180``。

    返回：
        角度列表。
    """

    angles = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        angle = float(item)
        if angle < 0 or angle > 180:
            raise argparse.ArgumentTypeError("角度必须在 0 到 180 之间")
        angles.append(angle)
    if not angles:
        raise argparse.ArgumentTypeError("至少需要一个角度")
    return angles


def parse_args() -> argparse.Namespace:
    """解析水平云台舵机测试参数。"""

    parser = argparse.ArgumentParser(description="水平云台舵机测试。")
    parser.add_argument(
        "--pin",
        type=int,
        default=config.CAMERA_PAN_SERVO_PIN,
        help="水平云台舵机 BCM 引脚，接口表默认是 23。",
    )
    parser.add_argument(
        "--angles",
        type=parse_angles,
        default=parse_angles("0,45,90,135,180,90"),
        help="要依次转到的角度，多个角度用逗号分隔。",
    )
    parser.add_argument(
        "--settle-seconds",
        type=float,
        default=1.0,
        help="每个角度保持的时间。",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="重复角度序列的次数。",
    )
    return parser.parse_args()


def main() -> int:
    """执行水平云台舵机转动测试。

    简单步骤：
        1. 初始化指定 BCM 引脚的 PWM 舵机。
        2. 按角度列表依次转动。
        3. 结束时释放舵机 GPIO。
    """

    args = parse_args()

    print("水平云台舵机测试开始。", flush=True)
    print(f"项目目录: {PROJECT_ROOT}", flush=True)
    print(f"舵机 BCM 引脚: {args.pin}", flush=True)
    print(f"角度序列: {args.angles}", flush=True)

    try:
        with ServoController(args.pin, settle_seconds=args.settle_seconds) as servo:
            for loop_index in range(args.repeat):
                print(f"第 {loop_index + 1} 轮测试。", flush=True)
                for angle in args.angles:
                    print(f"转到 {angle} 度...", flush=True)
                    servo.move_to(angle)
                    time.sleep(0.2)
    except (ServoError, ValueError, RuntimeError) as exc:
        print(f"水平云台舵机测试失败: {exc}", file=sys.stderr)
        print("建议：确认舵机信号线接 BCM 23，电源/GND 接稳，且不要用 wiringPi 编号。", file=sys.stderr)
        return 1

    print("水平云台舵机测试完成。", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
