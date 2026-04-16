#!/usr/bin/env python3
"""
drive.py
--------
Manual keyboard control for the robot.
Runs in the terminal on the Raspberry Pi.

Controls:
    W / ↑       Forward
    S / ↓       Backward
    A / ←       Turn left
    D / →       Turn right
    Q           Curve left (forward + left)
    E           Curve right (forward + right)
    SPACE       Stop
    +/=         Increase speed
    -           Decrease speed
    M           Switch to manual/autonomous mode (placeholder)
    CTRL+C      Quit safely

Usage:
    python3 drive.py
"""

import sys
import tty
import termios
import signal
import motor_controller as mc

# ─── Configuration ────────────────────────────────────────────────────────────

DEFAULT_SPEED   = 0.6   # 0.0 - 1.0
SPEED_STEP      = 0.1   # How much +/- changes speed
TURN_SPEED      = 0.55  # Speed used for in-place turns
CURVE_SHARPNESS = 0.45  # 0.0 gentle → 1.0 sharp

# ─── State ────────────────────────────────────────────────────────────────────

speed = DEFAULT_SPEED
current_action = "STOPPED"

# ─── Terminal Helpers ─────────────────────────────────────────────────────────

def get_terminal_settings():
    return termios.tcgetattr(sys.stdin)

def restore_terminal(settings):
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

def get_key():
    """Read a single keypress, including arrow keys (3-byte escape sequences)."""
    ch = sys.stdin.read(1)
    if ch == '\x1b':  # Escape sequence (arrow keys)
        ch2 = sys.stdin.read(1)
        ch3 = sys.stdin.read(1)
        return ch + ch2 + ch3
    return ch

# ─── Display ──────────────────────────────────────────────────────────────────

def print_status():
    """Refresh the status line in place."""
    bar_filled = int(speed * 20)
    bar = '█' * bar_filled + '░' * (20 - bar_filled)
    sys.stdout.write(
        f"\r  Action: {current_action:<20} | Speed: [{bar}] {int(speed * 100):3d}%  "
    )
    sys.stdout.flush()

def print_header():
    print("\n" + "─" * 55)
    print("  🤖  Robot Manual Drive")
    print("─" * 55)
    print("  W / ↑   Forward        A / ←   Turn left")
    print("  S / ↓   Backward       D / →   Turn right")
    print("  Q       Curve left     E       Curve right")
    print("  SPACE   Stop")
    print("  + / -   Speed up / down")
    print("  CTRL+C  Quit")
    print("─" * 55)

# ─── Key → Action Map ─────────────────────────────────────────────────────────

def handle_key(key: str) -> bool:
    """
    Process a keypress and drive the robot accordingly.
    Returns False if the program should exit.
    """
    global speed, current_action

    if key in ('w', 'W', '\x1b[A'):       # W or Up arrow
        mc.forward(speed)
        current_action = "FORWARD"

    elif key in ('s', 'S', '\x1b[B'):     # S or Down arrow
        mc.backward(speed)
        current_action = "BACKWARD"

    elif key in ('a', 'A', '\x1b[D'):     # A or Left arrow
        mc.turn_left(TURN_SPEED)
        current_action = "TURN LEFT"

    elif key in ('d', 'D', '\x1b[C'):     # D or Right arrow
        mc.turn_right(TURN_SPEED)
        current_action = "TURN RIGHT"

    elif key in ('q', 'Q'):
        mc.curve_left(speed, CURVE_SHARPNESS)
        current_action = "CURVE LEFT"

    elif key in ('e', 'E'):
        mc.curve_right(speed, CURVE_SHARPNESS)
        current_action = "CURVE RIGHT"

    elif key == ' ':
        mc.stop()
        current_action = "STOPPED"

    elif key in ('+', '='):
        speed = min(1.0, round(speed + SPEED_STEP, 1))
        current_action = f"SPEED → {int(speed * 100)}%"

    elif key == '-':
        speed = max(0.1, round(speed - SPEED_STEP, 1))
        current_action = f"SPEED → {int(speed * 100)}%"

    elif key == '\x03':  # CTRL+C
        return False

    return True

# ─── Main Loop ────────────────────────────────────────────────────────────────

def main():
    global current_action
    original_settings = get_terminal_settings()

    def safe_exit(sig=None, frame=None):
        restore_terminal(original_settings)
        mc.shutdown()
        print("\n\n  Motors stopped. Goodbye!\n")
        sys.exit(0)

    signal.signal(signal.SIGINT,  safe_exit)
    signal.signal(signal.SIGTERM, safe_exit)

    print_header()
    print_status()

    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            key = get_key()
            should_continue = handle_key(key)
            print_status()
            if not should_continue:
                break
    finally:
        restore_terminal(original_settings)
        mc.shutdown()
        print("\n\n  Motors stopped. Goodbye!\n")

if __name__ == "__main__":
    main()
