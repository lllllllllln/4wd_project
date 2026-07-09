"""OpenCV camera probe script based on the classroom camera tutorial.

This script is intentionally independent from the project camera module. It is
for Raspberry Pi troubleshooting: try camera indexes, save a frame, and
optionally show a preview window when a desktop display is available.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import time
from typing import Iterable, List, Optional, Sequence, Tuple


DEFAULT_DEVICE_INDEXES = (-1, 0, 1, 2, 3)
DEFAULT_OUTPUT_DIR = Path("captures")


def parse_device_indexes(raw_indexes: Optional[str]) -> List[int]:
    """Parse camera indexes entered as comma-separated numbers.

    Args:
        raw_indexes: Text such as ``"-1,0,1,2,3"``. If omitted, the tutorial
            default indexes are returned.

    Returns:
        A list of OpenCV camera indexes to test in order.
    """

    if not raw_indexes:
        return list(DEFAULT_DEVICE_INDEXES)

    indexes = []
    for item in raw_indexes.split(","):
        item = item.strip()
        if item:
            indexes.append(int(item))
    return indexes


def build_output_path(output_dir: Path, device_index: int) -> Path:
    """Build a timestamped test image path for one device index.

    Args:
        output_dir: Directory where test images are saved.
        device_index: OpenCV camera index that produced the frame.

    Returns:
        A path such as ``captures/opencv_device_0_20260709_120000.jpg``.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return output_dir / "opencv_device_{0}_{1}.jpg".format(device_index, timestamp)


def read_warmup_frame(camera, warmup_frames: int) -> Tuple[bool, Optional[object]]:
    """Read several frames and return the newest valid frame.

    Args:
        camera: OpenCV ``VideoCapture`` object.
        warmup_frames: Number of frames to try before deciding the camera works.

    Returns:
        ``(True, frame)`` when a frame is available, otherwise ``(False, None)``.
    """

    frame = None
    ok = False
    for _ in range(max(1, warmup_frames)):
        ok, current_frame = camera.read()
        if ok and current_frame is not None:
            frame = current_frame
        else:
            time.sleep(0.1)
    return frame is not None, frame


def test_one_device(
    device_index: int,
    *,
    output_dir: Path,
    width: Optional[int],
    height: Optional[int],
    warmup_frames: int,
) -> Optional[Path]:
    """Open one OpenCV camera index and save one frame if possible.

    Args:
        device_index: Camera index passed to ``cv2.VideoCapture``.
        output_dir: Directory where the captured test image is saved.
        width: Optional requested frame width.
        height: Optional requested frame height.
        warmup_frames: Number of frames to read before saving.

    Returns:
        The saved image path if this device works, otherwise ``None``.
    """

    import cv2

    print("Testing VideoCapture({0})...".format(device_index), flush=True)
    camera = cv2.VideoCapture(device_index)
    try:
        if not camera.isOpened():
            print("  Failed: camera index cannot be opened.", flush=True)
            return None

        if width is not None:
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        if height is not None:
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        ok, frame = read_warmup_frame(camera, warmup_frames)
        if not ok:
            print("  Failed: camera opened but no frame was read.", flush=True)
            return None

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = build_output_path(output_dir, device_index)
        saved = cv2.imwrite(str(output_path), frame)
        if not saved:
            print("  Failed: frame was read but could not be saved.", flush=True)
            return None

        frame_height, frame_width = frame.shape[:2]
        print(
            "  Success: saved {0} ({1}x{2}).".format(
                output_path, frame_width, frame_height
            ),
            flush=True,
        )
        return output_path
    finally:
        camera.release()


def preview_device(device_index: int, *, width: Optional[int], height: Optional[int]) -> int:
    """Show a live preview window until the user presses ``q``.

    Args:
        device_index: Camera index passed to ``cv2.VideoCapture``.
        width: Optional requested frame width.
        height: Optional requested frame height.

    Returns:
        ``0`` when preview exits normally, ``1`` when the camera cannot open.
    """

    import cv2

    print("Opening preview for VideoCapture({0}). Press q to quit.".format(device_index))
    camera = cv2.VideoCapture(device_index)
    try:
        if not camera.isOpened():
            print("Preview failed: camera index cannot be opened.", flush=True)
            return 1

        if width is not None:
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        if height is not None:
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        while True:
            ok, frame = camera.read()
            if not ok or frame is None:
                print("Preview failed: no frame was read.", flush=True)
                return 1

            cv2.imshow("Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

    return 0


def probe_devices(
    device_indexes: Iterable[int],
    *,
    output_dir: Path,
    width: Optional[int],
    height: Optional[int],
    warmup_frames: int,
) -> List[Tuple[int, Path]]:
    """Try multiple camera indexes and collect successful captures.

    Args:
        device_indexes: Ordered OpenCV camera indexes to test.
        output_dir: Directory where test images are saved.
        width: Optional requested frame width.
        height: Optional requested frame height.
        warmup_frames: Number of frames to read before saving.

    Returns:
        A list of ``(device_index, image_path)`` for working camera indexes.
    """

    working_devices = []
    for device_index in device_indexes:
        output_path = test_one_device(
            device_index,
            output_dir=output_dir,
            width=width,
            height=height,
            warmup_frames=warmup_frames,
        )
        if output_path is not None:
            working_devices.append((device_index, output_path))
    return working_devices


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command-line options for the tutorial camera test.

    Args:
        argv: Optional argument list for tests. The default reads ``sys.argv``.

    Returns:
        Parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Probe Raspberry Pi OpenCV camera indexes and save test frames."
    )
    parser.add_argument(
        "--devices",
        default=None,
        help="Comma-separated camera indexes to test, for example -1,0,1,2,3.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for saved test photos.",
    )
    parser.add_argument("--width", type=int, default=None, help="Requested width.")
    parser.add_argument("--height", type=int, default=None, help="Requested height.")
    parser.add_argument(
        "--warmup-frames",
        type=int,
        default=10,
        help="Frames to read before saving each test image.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Open a GUI preview window after a working device is found.",
    )
    parser.add_argument(
        "--preview-device",
        type=int,
        default=None,
        help="Camera index used for preview. Defaults to the first working device.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the camera probe workflow.

    Args:
        argv: Optional argument list for tests. The default reads ``sys.argv``.

    Returns:
        Process exit code. ``0`` means at least one camera index worked.
    """

    args = parse_args(argv)
    device_indexes = parse_device_indexes(args.devices)

    print("OpenCV camera tutorial test started.", flush=True)
    print("Devices to test: {0}".format(device_indexes), flush=True)
    print("Output directory: {0}".format(args.output_dir), flush=True)

    try:
        working_devices = probe_devices(
            device_indexes,
            output_dir=args.output_dir,
            width=args.width,
            height=args.height,
            warmup_frames=args.warmup_frames,
        )
    except ImportError:
        print("OpenCV import failed. Install it with: sudo apt install python3-opencv")
        return 1

    if not working_devices:
        print("No working OpenCV camera index was found.", flush=True)
        print("Next checks: cable, camera enable setting, /dev/video*, and services.")
        return 1

    print("Working camera indexes:", flush=True)
    for device_index, output_path in working_devices:
        print("  {0}: {1}".format(device_index, output_path), flush=True)

    if args.preview:
        preview_index = args.preview_device
        if preview_index is None:
            preview_index = working_devices[0][0]
        return preview_device(preview_index, width=args.width, height=args.height)

    print("Camera probe finished. Copy the saved jpg back to Windows to view it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
