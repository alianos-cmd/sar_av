#!/usr/bin/env python3
"""
motor_controller.py
-------------------
Low-level motor control for a 4-wheel differential drive robot.
Uses a PCA9685 PWM board over I2C to drive two L298N-style controllers.

Wiring assumption:
  Controller 1 (channels 0-3) → LEFT side motors
  Controller 2 (channels 4-7) → RIGHT side motors

If the robot turns the wrong way, flip SWAP_CONTROLLERS to True.
If a single motor spins the wrong direction, adjust the INVERT_* flags.
"""

try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
except ImportError as e:
    raise RuntimeError(
        "Missing PWM board libraries. Install with:\n"
        "pip install adafruit-circuitpython-pca9685"
    ) from e

# ─── Configuration ────────────────────────────────────────────────────────────

PWM_FREQUENCY = 1000  # Hz

# Swap left/right controllers if the robot turns the wrong way
SWAP_CONTROLLERS = False

# Invert individual sides if a motor spins backwards
INVERT_LEFT  = False
INVERT_RIGHT = False

# ─── PCA9685 Channel Map ───────────────────────────────────────────────────────

# Controller 1: channels 0-3
CTRL1_IN1, CTRL1_IN2 = 0, 1  # Motor A (e.g. front-left)
CTRL1_IN3, CTRL1_IN4 = 2, 3  # Motor B (e.g. rear-left)

# Controller 2: channels 4-7
CTRL2_IN1, CTRL2_IN2 = 4, 5  # Motor C (e.g. front-right)
CTRL2_IN3, CTRL2_IN4 = 6, 7  # Motor D (e.g. rear-right)

MAX_DUTY = 65535
MIN_DUTY = 0

# ─── Setup ────────────────────────────────────────────────────────────────────

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = PWM_FREQUENCY

# ─── Internal Helpers ─────────────────────────────────────────────────────────

def _set_channel(channel: int, value: int) -> None:
    """Set a PCA9685 channel to a duty cycle value (0 - 65535)."""
    pca.channels[channel].duty_cycle = max(MIN_DUTY, min(MAX_DUTY, value))


def _speed_to_duty(speed: float) -> int:
    """Convert a speed percentage (0.0 - 1.0) to a duty cycle value."""
    return int(MAX_DUTY * max(0.0, min(1.0, speed)))


def _drive_side(in1: int, in2: int, in3: int, in4: int, speed: float, invert: bool) -> None:
    """
    Drive one side (2 motors) at a given speed and direction.
    speed:  0.0 (stop) to 1.0 (full speed)
    invert: flip direction for this side
    If speed > 0 → forward (or backward if inverted)
    If speed < 0 → backward (or forward if inverted)
    """
    duty = _speed_to_duty(abs(speed))
    forward = (speed >= 0) ^ invert  # XOR flips direction if inverted

    if duty == 0:
        # Coast to stop
        _set_channel(in1, MIN_DUTY)
        _set_channel(in2, MIN_DUTY)
        _set_channel(in3, MIN_DUTY)
        _set_channel(in4, MIN_DUTY)
    elif forward:
        _set_channel(in1, duty)
        _set_channel(in2, MIN_DUTY)
        _set_channel(in3, duty)
        _set_channel(in4, MIN_DUTY)
    else:
        _set_channel(in1, MIN_DUTY)
        _set_channel(in2, duty)
        _set_channel(in3, MIN_DUTY)
        _set_channel(in4, duty)


# ─── Public API ───────────────────────────────────────────────────────────────

def drive(left_speed: float, right_speed: float) -> None:
    """
    Core drive function. Control each side independently.

    Args:
        left_speed:  -1.0 (full reverse) to 1.0 (full forward) for left wheels
        right_speed: -1.0 (full reverse) to 1.0 (full forward) for right wheels

    Examples:
        drive(1.0, 1.0)    → full speed forward
        drive(-1.0, -1.0)  → full speed backward
        drive(1.0, -1.0)   → spin clockwise
        drive(0.5, 0.5)    → half speed forward
        drive(1.0, 0.3)    → curve left
    """
    if SWAP_CONTROLLERS:
        left_speed, right_speed = right_speed, left_speed

    _drive_side(CTRL1_IN1, CTRL1_IN2, CTRL1_IN3, CTRL1_IN4, left_speed,  INVERT_LEFT)
    _drive_side(CTRL2_IN1, CTRL2_IN2, CTRL2_IN3, CTRL2_IN4, right_speed, INVERT_RIGHT)


def forward(speed: float = 0.7) -> None:
    """Drive forward at given speed (0.0 - 1.0)."""
    drive(speed, speed)


def backward(speed: float = 0.7) -> None:
    """Drive backward at given speed (0.0 - 1.0)."""
    drive(-speed, -speed)


def turn_left(speed: float = 0.6) -> None:
    """Turn left in place at given speed."""
    drive(-speed, speed)


def turn_right(speed: float = 0.6) -> None:
    """Turn right in place at given speed."""
    drive(speed, -speed)


def curve_left(speed: float = 0.7, sharpness: float = 0.4) -> None:
    """
    Curve left while moving forward.
    sharpness: 0.0 (gentle) to 1.0 (nearly spinning in place)
    """
    drive(speed * (1.0 - sharpness), speed)


def curve_right(speed: float = 0.7, sharpness: float = 0.4) -> None:
    """
    Curve right while moving forward.
    sharpness: 0.0 (gentle) to 1.0 (nearly spinning in place)
    """
    drive(speed, speed * (1.0 - sharpness))


def stop() -> None:
    """Stop all motors immediately."""
    drive(0.0, 0.0)


def shutdown() -> None:
    """Stop motors and release the PCA9685."""
    stop()
    pca.deinit()
