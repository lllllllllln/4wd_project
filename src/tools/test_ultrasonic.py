"""Manual ultrasonic sensor test for the real Raspberry Pi car.

Run one of the available test modes.

Examples::

    # Default: continuous distance printing (safe, no motor movement).
    python -m src.tools.test_ultrasonic

    # Background monitoring mode (prints only state changes).
    python -m src.tools.test_ultrasonic --monitor

    # Servo scanning mode (rotates the servo).
    python -m src.tools.test_ultrasonic --servo-scan

    # Custom pin / threshold overrides.
    python -m src.tools.test_ultrasonic --trig 17 --echo 18 --threshold 30

Testing notes:
- The ultrasonic module only reads distance; it never drives motors.
- If you see continuous "⚠️ timeout" output, check that the sensor is
  connected and the Trig/Echo pins match your wiring.
- On first test, hold an object ~20 cm in front of the sensor to
  confirm the reading is reasonable.
"""

import argparse
import time
import sys

from src.hardware.ultrasonic import UltrasonicSensor, UltrasonicServo


def parse_args():
    parser = argparse.ArgumentParser(
        description="Test the ultrasonic sensor (read-only, no motors)."
    )
    parser.add_argument(
        "--trig", type=int, default=None,
        help="TrigPin BCM number (default: config.ULTRASONIC_TRIG = 1)",
    )
    parser.add_argument(
        "--echo", type=int, default=None,
        help="EchoPin BCM number (default: config.ULTRASONIC_ECHO = 0)",
    )
    parser.add_argument(
        "--threshold", type=int, default=None,
        help="Obstacle threshold in cm (default: config.ULTRASONIC_THRESHOLD = 20)",
    )
    parser.add_argument(
        "--monitor", action="store_true",
        help="Run in background-monitor mode (prints only state changes).",
    )
    parser.add_argument(
        "--servo-scan", action="store_true",
        help="Run servo scanning test (requires servo connected at SERVO_PIN=23).",
    )
    parser.add_argument(
        "--servo-pin", type=int, default=None,
        help="Servo signal BCM pin (default: config.SERVO_PIN = 23)",
    )
    return parser.parse_args()


# ------------------------------------------------------------------
#   Modes
# ------------------------------------------------------------------

def mode_continuous(sensor):
    """Continuously print distance readings with a simple visual bar."""
    print("  Mode: continuous ranging  (Ctrl+C to stop)")
    print("─" * 50)
    count = 0
    while True:
        d = sensor.read_filtered()
        if d < 0:
            print(f"[{count:04d}]  ⚠️  timeout")
        else:
            bar = "█" * max(1, min(int(d / 5), 20))
            flag = "  ⚠️ OBSTACLE" if sensor.is_obstructed(d) else "  safe"
            print(f"[{count:04d}]  {d:>5.1f} cm  {bar}{flag}")
        count += 1
        time.sleep(0.3)


def mode_monitor(sensor):
    """Run the background monitoring thread; print only state changes."""
    print("  Mode: background monitor  (Ctrl+C to stop)")
    print("─" * 50)
    sensor.start_monitoring()
    last_state = None
    while True:
        cur = sensor.obstacle_detected
        if cur != last_state:
            label = "⚠️ OBSTACLE" if cur else "safe"
            print(f"  state → {label}  (last distance: {sensor.last_distance:.1f} cm)")
            last_state = cur
        time.sleep(0.1)


def mode_servo_scan():
    """Scan left/front/right with the servo and recommend a direction."""
    print("  Mode: servo scan  (Ctrl+C to stop)")
    print("─" * 50)
    us = UltrasonicServo(servo_pin=args.servo_pin)
    try:
        count = 0
        while True:
            print(f"\n--- Scan #{count} ---")
            dm = us.scan_surroundings()
            best = us.choose_best_direction(dm)
            labels = {"front": "⬆ forward", "left": "⬅ left", "right": "➡ right"}
            print(f"  → recommended: {labels.get(best, '❌ all blocked')}")
            count += 1
            time.sleep(1)
    finally:
        us.close()


# ------------------------------------------------------------------
#   Main
# ------------------------------------------------------------------

def main():
    global args
    args = parse_args()

    if args.servo_scan:
        mode_servo_scan()
        return

    # UltrasonicSensor test (continuous or monitor).
    sensor = UltrasonicSensor(
        trig_pin=args.trig,
        echo_pin=args.echo,
        threshold_cm=args.threshold,
    )

    try:
        if args.monitor:
            mode_monitor(sensor)
        else:
            mode_continuous(sensor)
    except KeyboardInterrupt:
        print("\n  User interrupted.")
    finally:
        sensor.close()
        print("  GPIO cleaned up.")


if __name__ == "__main__":
    main()
