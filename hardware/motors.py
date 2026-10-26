"""DC motor driver: two motors driven through an H-bridge (HW-354)."""

from hardware.pwm import PwmChannel


class Motors:
    """Control the left and right propulsion motors.

    Each motor uses one PWM input of the H-bridge (IN1 / IN3). The matching
    direction input (IN2 / IN4) is wired to 0, so the motors only turn forward.
    Speeds are ratios from 0.0 (stopped) to 1.0 (full speed).
    """

    MOTOR_FREQ_HZ = 20_000  # above audible range, avoids motor whine
    MAX_STEP = 0.05         # max speed change per set_speed() call (soft start)

    def __init__(self):
        """Start both PWM channels with motors stopped."""
        self.motor1 = PwmChannel(chip=0, freq_hz=self.MOTOR_FREQ_HZ)  # pin 23 -> IN1 (left)
        self.motor2 = PwmChannel(chip=1, freq_hz=self.MOTOR_FREQ_HZ)  # pin 29 -> IN3 (right)

        # Current applied speeds, needed by the ramp to know where we are
        self.left_speed = 0.0
        self.right_speed = 0.0

    def _ramp(self, current: float, target: float) -> float:
        """Move `current` toward `target` by at most MAX_STEP.

        Limits acceleration and deceleration: it protects the H-bridge and
        the battery from current spikes, and avoids wheel slip.
        """
        delta = target - current
        delta = max(-self.MAX_STEP, min(self.MAX_STEP, delta))
        return current + delta

    def set_speed(self, left: float, right: float):
        """Set the target speed of each motor.

        The real speed reaches the target progressively (see _ramp), so this
        method must be called repeatedly, e.g. once per control loop cycle.

        Args:
            left: target speed of the left motor, clamped to 0.0 - 1.0.
            right: target speed of the right motor, clamped to 0.0 - 1.0.
        """
        left = max(0.0, min(1.0, left))
        right = max(0.0, min(1.0, right))

        self.left_speed = self._ramp(self.left_speed, left)
        self.right_speed = self._ramp(self.right_speed, right)

        self.motor1.set_duty(self.left_speed)
        self.motor2.set_duty(self.right_speed)

    def stop(self):
        """Stop both motors immediately (no ramp, used for emergency stop)."""
        self.left_speed = 0.0
        self.right_speed = 0.0
        self.motor1.set_duty(0)
        self.motor2.set_duty(0)

    def close(self):
        """Stop the motors and release both PWM channels."""
        self.stop()
        self.motor1.close()
        self.motor2.close()