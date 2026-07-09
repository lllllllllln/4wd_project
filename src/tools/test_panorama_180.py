"""180 度摄像头舵机全景拍照测试脚本。

用途：
    仅当摄像头本身有独立水平舵机时使用。
    控制摄像头水平云台从 0 度转到 180 度，按角度拍摄多张照片。
    默认只保存原始照片；确认云台和摄像头都正常后，可加 --stitch 尝试拼接。

常用命令：
    python3 src/tools/test_panorama_180.py --pan-pin 摄像头舵机BCM编号
    python3 src/tools/test_panorama_180.py --pan-pin 摄像头舵机BCM编号 --frames 13 --stitch

如果摄像头没有独立云台，请使用：
    python3 src/tools/test_panorama_180_car_turn.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from src.hardware.camera import CameraCaptureError
from src.hardware.servo import ServoError
from src.tasks.panorama import PanoramaError, capture_panorama


def parse_args() -> argparse.Namespace:
    """解析 180 度全景拍照测试参数。"""

    parser = argparse.ArgumentParser(description="180 度全景拍照测试。")
    parser.add_argument(
        "--backend",
        choices=("auto", "opencv", "libcamera", "raspistill"),
        default="opencv",
        help="拍照后端。USB 摄像头建议用 opencv。",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=1,
        help="OpenCV 摄像头编号。你当前普通拍照测试成功的是 1。",
    )
    parser.add_argument(
        "--pan-pin",
        type=int,
        default=config.CAMERA_PAN_SERVO_PIN,
        help="摄像头水平云台舵机 BCM 引脚；没有独立摄像头云台时不要使用此脚本。",
    )
    parser.add_argument(
        "--start-angle",
        type=float,
        default=0,
        help="起始角度。",
    )
    parser.add_argument(
        "--end-angle",
        type=float,
        default=180,
        help="结束角度。",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=7,
        help="拍照张数。第一次建议 7，稳定后可改 13 或 31。",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("captures") / "panorama_180_tests",
        help="测试照片输出目录。",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=640,
        help="请求图像宽度。测试阶段用 640 更快。",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=480,
        help="请求图像高度。测试阶段用 480 更快。",
    )
    parser.add_argument(
        "--warmup-frames",
        type=int,
        default=8,
        help="打开摄像头后丢弃的预热帧数。",
    )
    parser.add_argument(
        "--warmup-seconds",
        type=float,
        default=0.8,
        help="打开摄像头后的预热时间。",
    )
    parser.add_argument(
        "--servo-settle-seconds",
        type=float,
        default=0.8,
        help="每次舵机转到目标角度后的等待时间。",
    )
    parser.add_argument(
        "--capture-delay-seconds",
        type=float,
        default=0.3,
        help="每张照片读取前额外等待时间。",
    )
    parser.add_argument(
        "--stitch",
        action="store_true",
        help="拍完后尝试生成 panorama.jpg。",
    )
    parser.add_argument(
        "--no-servo",
        action="store_true",
        help="不转动云台，只连续拍照。用于单独排查摄像头。",
    )
    return parser.parse_args()


def main() -> int:
    """执行 180 度全景拍照测试。

    简单步骤：
        1. 生成 0 到 180 度之间的拍照角度。
        2. 水平云台转到每个角度并拍照。
        3. 保存所有原始照片；如果指定 --stitch，再尝试拼接。
    """

    args = parse_args()

    print("180 度全景拍照测试开始。", flush=True)
    print(f"项目目录: {PROJECT_ROOT}", flush=True)
    print(f"摄像头编号: {args.device}", flush=True)
    print(f"拍照后端: {args.backend}", flush=True)
    print(f"云台 BCM 引脚: {args.pan_pin}", flush=True)
    print(
        f"拍摄角度: {args.start_angle} -> {args.end_angle}, 张数: {args.frames}",
        flush=True,
    )
    print(f"是否拼接: {'是' if args.stitch else '否，只保存原图'}", flush=True)

    try:
        if args.pan_pin is None and not args.no_servo:
            raise ValueError(
                "没有配置摄像头水平云台舵机。若摄像头固定在车身上，"
                "请改用 src/tools/test_panorama_180_car_turn.py。"
            )
        result = capture_panorama(
            output_dir=args.output_dir,
            backend=args.backend,
            device_index=args.device,
            width=args.width,
            height=args.height,
            warmup_frames=args.warmup_frames,
            warmup_seconds=args.warmup_seconds,
            start_angle=args.start_angle,
            end_angle=args.end_angle,
            frame_count=args.frames,
            pan_servo_pin=args.pan_pin,
            use_servo=not args.no_servo,
            servo_settle_seconds=args.servo_settle_seconds,
            capture_delay_seconds=args.capture_delay_seconds,
            stitch=args.stitch,
        )
    except (CameraCaptureError, PanoramaError, ServoError, ValueError) as exc:
        print(f"180 度全景拍照测试失败: {exc}", file=sys.stderr)
        print(
            "建议：先确认普通拍照 device=1 可用，再确认云台舵机接在 BCM 23。",
            file=sys.stderr,
        )
        return 1

    print("180 度全景拍照测试成功。", flush=True)
    print(f"测试目录: {result.session_dir}", flush=True)
    print(f"原始照片数量: {len(result.frame_paths)}", flush=True)
    print(f"实际角度序列: {result.angles}", flush=True)
    print("原始照片列表:", flush=True)
    for angle, path in zip(result.angles, result.frame_paths):
        print(f"  {angle} 度 -> {path}", flush=True)
    if result.panorama_path is not None:
        print(f"拼接结果: {result.panorama_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
