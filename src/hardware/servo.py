"""Servo control helpers for Yahboom car modules.

This module is the hardware boundary for PWM servos. Tasks should call this
class instead of writing GPIO pins directly.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Optional

from src import config


class ServoError(RuntimeError):
    """Raised when a servo cannot be initialized or moved safely."""


@dataclass(frozen=True)
class ServoPosition:
    """Metadata for one completed servo movement."""

    pin: int
    angle: float
    duty_cycle: float


class ServoController:
    """Control one BCM GPIO servo pin with a 50 Hz PWM signal.

    Args:
        pin: Servo GPIO pin in BCM numbering.
        frequency: PWM frequency. Standard steering servos use 50 Hz.
        min_duty: Duty cycle for 0 degrees.
        max_duty: Duty cycle for 180 degrees.
        settle_seconds: Time to wait after setting the target angle.
        gpio: Optional injected GPIO module, mainly for tests.
    """

    def __init__(
        self,
        pin: int,
        *,
        frequency: int = config.SERVO_PWM_FREQUENCY,
        min_duty: float = 2.5,
        max_duty: float = 12.5,
        settle_seconds: float = 0.5,
        gpio=None,
    ):
        if pin is None:
            raise ServoError("Servo pin must be configured before use")
        if frequency <= 0:
            raise ValueError("frequency must be greater than 0")
        if min_duty >= max_duty:
            raise ValueError("min_duty must be less than max_duty")
        if settle_seconds < 0:
            raise ValueError("settle_seconds must be greater than or equal to 0")

        if gpio is None:
            try:
                import RPi.GPIO as gpio
            except ModuleNotFoundError as exc:
                raise ServoError("RPi.GPIO can only be used on Raspberry Pi") from exc

        self.pin = int(pin)
        self.frequency = frequency
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.settle_seconds = settle_seconds
        self.gpio = gpio
        self._pwm = None
        self._setup_gpio()

    def move_to(self, angle: float) -> ServoPosition:
        """Move the servo to the target angle.

        Args:
            angle: Target angle from 0 to 180 degrees.

        Returns:
            ServoPosition with the target pin, angle, and duty cycle.
        """

        angle = float(angle)
        if angle < 0 or angle > 180:
            raise ValueError("angle must be between 0 and 180 degrees")

        # Step 1: convert the requested angle to the servo PWM duty cycle.
        duty_cycle = self._angle_to_duty(angle)

        # Step 2: output PWM long enough for the servo to reach the angle.
        self._pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(self.settle_seconds)

        # Step 3: stop the holding pulse to reduce jitter and heating.
        self._pwm.ChangeDutyCycle(0)
        return ServoPosition(pin=self.pin, angle=angle, duty_cycle=duty_cycle)

    def close(self) -> None:
        """Stop PWM and release only this servo pin."""

        if self._pwm is not None:
            self._pwm.stop()
            self._pwm = None
        self.gpio.cleanup(self.pin)

    def _setup_gpio(self) -> None:
        """Initialize GPIO mode, output pin, and PWM object."""

        self.gpio.setmode(self.gpio.BCM)
        self.gpio.setwarnings(False)
        self.gpio.setup(self.pin, self.gpio.OUT)
        self._pwm = self.gpio.PWM(self.pin, self.frequency)
        self._pwm.start(0)

    def _angle_to_duty(self, angle: float) -> float:
        """Convert a 0-180 degree servo angle into duty cycle."""

        span = self.max_duty - self.min_duty
        return self.min_duty + span * angle / 180.0

    def __enter__(self) -> "ServoController":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()
