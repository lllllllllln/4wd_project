"""查看 USB 摄像头支持的格式和控制项。

用途：
    用 v4l2-ctl 查询摄像头是否支持焦距、自动对焦、曝光、亮度、对比度等控制。

常用命令：
    python3 src/tools/probe_camera_controls.py --device /dev/video1
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    """解析摄像头探测参数。"""

    parser = argparse.ArgumentParser(description="查看摄像头 V4L2 能力。")
    parser.add_argument(
        "--device",
        default="/dev/video1",
        help="摄像头设备路径，例如 /dev/video1。",
    )
    return parser.parse_args()


def run_v4l2_ctl(device: str, *args: str) -> int:
    """运行一条 v4l2-ctl 命令并直接打印输出。

    参数：
        device: 摄像头设备路径。
        args: v4l2-ctl 的参数。

    返回：
        命令退出码。
    """

    command = ["v4l2-ctl", "--device", device, *args]
    print(f"\n$ {' '.join(command)}", flush=True)
    completed = subprocess.run(command, check=False, text=True)
    return completed.returncode


def main() -> int:
    """执行摄像头能力探测流程。"""

    args = parse_args()

    if shutil.which("v4l2-ctl") is None:
        print("未找到 v4l2-ctl。请先安装 v4l-utils。", file=sys.stderr)
        return 1

    failed = False
    for command_args in (
        ("--info",),
        ("--list-formats-ext",),
        ("--list-ctrls-menus",),
    ):
        if run_v4l2_ctl(args.device, *command_args) != 0:
            failed = True

    if failed:
        print("\n有命令执行失败，请确认设备路径是否正确。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
