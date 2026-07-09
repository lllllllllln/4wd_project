"""扫描摄像头参数并给照片清晰度打分。

用途：
    测试 brightness/contrast/exposure/focus 等参数是否能改善模糊。
    每次拍照后用 Laplacian 方差计算清晰度分数，分数越高通常越清晰。

常用命令：
    python3 src/tools/sweep_camera_settings.py --device 1
    python3 src/tools/sweep_camera_settings.py --device 1 --focus-values 0,20,40,60,80,100
    python3 src/tools/sweep_camera_settings.py --device 1 --exposure-values 80,120,160,220
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
import sys
import time
from typing import Iterable, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def parse_csv_numbers(value: Optional[str]) -> List[float]:
    """解析逗号分隔数字列表。

    参数：
        value: 逗号分隔数字，或 None。

    返回：
        数字列表；未传入时返回空列表。
    """

    if not value:
        return []
    numbers = []
    for item in value.split(","):
        item = item.strip()
        if item:
            numbers.append(float(item))
    return numbers


def parse_args() -> argparse.Namespace:
    """解析摄像头参数扫描选项。"""

    parser = argparse.ArgumentParser(description="扫描摄像头参数并计算清晰度分数。")
    parser.add_argument("--device", type=int, default=1, help="OpenCV 摄像头编号。")
    parser.add_argument("--width", type=int, default=640, help="图像宽度。")
    parser.add_argument("--height", type=int, default=480, help="图像高度。")
    parser.add_argument("--fps", type=float, default=30, help="请求帧率。")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("captures") / "camera_setting_sweeps",
        help="输出目录。",
    )
    parser.add_argument(
        "--brightness-values",
        default="",
        help="亮度扫描值，例如 20,40,60。不传则不扫描。",
    )
    parser.add_argument(
        "--contrast-values",
        default="",
        help="对比度扫描值，例如 20,40,60。不传则不扫描。",
    )
    parser.add_argument(
        "--exposure-values",
        default="",
        help="曝光扫描值，例如 80,120,160。不传则不扫描。",
    )
    parser.add_argument(
        "--focus-values",
        default="",
        help="焦距扫描值，例如 0,20,40,60。不传则不扫描。",
    )
    parser.add_argument(
        "--disable-autofocus",
        action="store_true",
        help="如果摄像头支持，关闭自动对焦后再设置 focus。",
    )
    parser.add_argument(
        "--disable-auto-exposure",
        action="store_true",
        help="如果摄像头支持，关闭自动曝光后再设置 exposure。",
    )
    parser.add_argument("--warmup-frames", type=int, default=12, help="每组参数预热帧数。")
    parser.add_argument("--settle-seconds", type=float, default=0.5, help="设置参数后等待时间。")
    return parser.parse_args()


def main() -> int:
    """执行摄像头参数扫描。"""

    args = parse_args()

    try:
        import cv2
    except ImportError:
        print("未安装 OpenCV，无法扫描摄像头参数。", file=sys.stderr)
        return 1

    session_dir = args.output_dir / datetime.now().strftime("sweep_%Y%m%d_%H%M%S")
    session_dir.mkdir(parents=True, exist_ok=True)

    settings = list(_build_settings(args))
    if not settings:
        settings = [{}]

    csv_path = session_dir / "results.csv"
    print("摄像头参数扫描开始。", flush=True)
    print(f"输出目录: {session_dir}", flush=True)
    print(f"测试组数: {len(settings)}", flush=True)

    rows = []
    for index, setting in enumerate(settings):
        image_path = session_dir / f"setting_{index:02d}.jpg"
        print(f"测试 {index + 1}/{len(settings)}: {setting}", flush=True)
        try:
            score = _capture_one_with_setting(cv2, args, setting, image_path)
        except RuntimeError as exc:
            print(f"  失败: {exc}", file=sys.stderr)
            score = -1.0

        row = {"index": index, "sharpness": score, "path": str(image_path)}
        row.update(setting)
        rows.append(row)
        print(f"  sharpness={score:.2f}, path={image_path}", flush=True)

    fieldnames = sorted({key for row in rows for key in row.keys()})
    with csv_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    best = max(rows, key=lambda row: row["sharpness"])
    print(f"结果表: {csv_path}", flush=True)
    print(f"最佳分数: {best['sharpness']:.2f}", flush=True)
    print(f"最佳照片: {best['path']}", flush=True)
    print(f"最佳参数: {best}", flush=True)
    return 0


def _build_settings(args: argparse.Namespace) -> Iterable[dict]:
    """生成要测试的参数组合。"""

    brightness_values = parse_csv_numbers(args.brightness_values)
    contrast_values = parse_csv_numbers(args.contrast_values)
    exposure_values = parse_csv_numbers(args.exposure_values)
    focus_values = parse_csv_numbers(args.focus_values)

    for name, values in (
        ("brightness", brightness_values),
        ("contrast", contrast_values),
        ("exposure", exposure_values),
        ("focus", focus_values),
    ):
        for value in values:
            yield {name: value}


def _capture_one_with_setting(cv2, args: argparse.Namespace, setting: dict, image_path: Path) -> float:
    """按指定参数拍一张照片并返回清晰度分数。"""

    camera = cv2.VideoCapture(args.device)
    try:
        if not camera.isOpened():
            raise RuntimeError(f"无法打开摄像头 {args.device}")

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
        camera.set(cv2.CAP_PROP_FPS, args.fps)
        camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))

        if args.disable_autofocus and hasattr(cv2, "CAP_PROP_AUTOFOCUS"):
            camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        if args.disable_auto_exposure and hasattr(cv2, "CAP_PROP_AUTO_EXPOSURE"):
            camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)

        _apply_setting(cv2, camera, setting)
        if args.settle_seconds > 0:
            time.sleep(args.settle_seconds)

        frame = None
        for _ in range(max(1, args.warmup_frames)):
            ok, current = camera.read()
            if ok and current is not None:
                frame = current
            else:
                time.sleep(0.05)

        if frame is None:
            raise RuntimeError("摄像头打开了，但没有读到画面")

        if not cv2.imwrite(str(image_path), frame):
            raise RuntimeError(f"无法保存照片: {image_path}")
        return _sharpness_score(cv2, frame)
    finally:
        camera.release()


def _apply_setting(cv2, camera, setting: dict) -> None:
    """把一个参数字典应用到 OpenCV 摄像头。"""

    mapping = {
        "brightness": cv2.CAP_PROP_BRIGHTNESS,
        "contrast": cv2.CAP_PROP_CONTRAST,
        "exposure": cv2.CAP_PROP_EXPOSURE,
    }
    if hasattr(cv2, "CAP_PROP_FOCUS"):
        mapping["focus"] = cv2.CAP_PROP_FOCUS

    for name, value in setting.items():
        prop = mapping.get(name)
        if prop is not None:
            camera.set(prop, value)


def _sharpness_score(cv2, frame) -> float:
    """使用拉普拉斯方差估计图像清晰度。"""

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


if __name__ == "__main__":
    raise SystemExit(main())
