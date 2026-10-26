"""Steering servo driver (standard RC servo, 50 Hz PWM, 1-2 ms pulse)."""

import time
from hardware.pwm import PwmChannel


class Servo:
    """Control the steering servo with an angle in degrees.

    Two ranges are distinguished on purpose:
      - the ELECTRICAL range (FULL_MIN/MAX_ANGLE, 0-180 deg) maps angles to
        pulse widths (1-2 ms), as defined by the servo standard;
      - the MECHANICAL range (MIN/MAX_ANGLE, 60-120 deg) is what the steering
        linkage can physically reach without forcing.
    Going beyond the mechanical range could stall the servo and damage it.
    """

    SERVO_FREQ_HZ = 50        # standard RC servo frequency (20 ms period)

    # Electrical range: angle <-> pulse width mapping
    FULL_MIN_ANGLE = 0        # angle matching MIN_PULSE_MS
    FULL_MAX_ANGLE = 180      # angle matching MAX_PULSE_MS
    MIN_PULSE_MS = 1.0        # pulse width at FULL_MIN_ANGLE
    MAX_PULSE_MS = 2.0        # pulse width at FULL_MAX_ANGLE

    # Mechanical range: safe limits of the steering linkage
    MIN_ANGLE = 60            # full steering on one side
    MAX_ANGLE = 120           # full steering on the other side

    INIT_POS = 90             # straight ahead
    STEER_LIMIT = 20          # max offset around INIT_POS used by steer()
    CLOSE_DELAY_S = 0.3       # time for the servo to reach INIT_POS before shutdown

    def __init__(self):
        """Start the PWM channel and center the steering."""
        self.servo = PwmChannel(chip=2, freq_hz=self.SERVO_FREQ_HZ)
        self.set_angle(self.INIT_POS)

    def steer(self, offset: float):
        """Steer relative to the straight-ahead position.

        Args:
            offset: degrees around INIT_POS, clamped to +/- STEER_LIMIT.
                    The sign convention (left/right) depends on how the
                    servo is mounted and must be checked on the car.
        """
        offset = max(-self.STEER_LIMIT, min(self.STEER_LIMIT, offset))
        self.set_angle(self.INIT_POS + offset)

    def set_angle(self, angle: float):
        """Move the servo to an absolute angle.

        The angle is first clamped to the mechanical range, then converted
        to a pulse width, then to a duty cycle ratio for the PWM.

        Args:
            angle: target angle in degrees (clamped to MIN_ANGLE - MAX_ANGLE).
        """
        angle = max(self.MIN_ANGLE, min(self.MAX_ANGLE, angle))

        # Angle -> position in the electrical range (0.0 to 1.0)
        ratio = (angle - self.FULL_MIN_ANGLE) / (self.FULL_MAX_ANGLE - self.FULL_MIN_ANGLE)
        # Position -> pulse width in ms (linear interpolation 1-2 ms)
        pulse_ms = self.MIN_PULSE_MS + ratio * (self.MAX_PULSE_MS - self.MIN_PULSE_MS)

        # Pulse width -> duty cycle: pulse / period (e.g. 1.5 ms / 20 ms = 7.5 %)
        period_ms = 1000 / self.SERVO_FREQ_HZ
        self.servo.set_duty(pulse_ms / period_ms)

    def close(self):
        """Center the steering, then release the PWM channel."""
        self.set_angle(self.INIT_POS)
        time.sleep(self.CLOSE_DELAY_S)  # let the servo finish its move
        self.servo.close()