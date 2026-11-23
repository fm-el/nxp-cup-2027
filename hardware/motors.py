"""motors.py - DEBIX Model A motor control

Hardware:
    PWM1 pwmchip0 Pin23: left motor.
    PWM2 pwmchip1 Pin29: right motor.
    PWM3 pwmchip2 Pin34: MG996R steering servo.

Example:
    motors = Motors()
    motors.set_speed(80, 30)
    motors.stop()
    motors.close()
"""

from hardware.pwm import PwmChannel

MOTOR_FREQ_HZ = 1_000


class Motors:
    """Control the left and right drive motors with PWM."""

    def __init__(self):
        """Initialize both motor PWM channels at zero speed."""
        print("[Motors] Initializing...")
        self.motor1 = PwmChannel(chip=0, freq_hz=MOTOR_FREQ_HZ)
        self.motor2 = PwmChannel(chip=1, freq_hz=MOTOR_FREQ_HZ)
        self.left_speed = 0.0
        self.right_speed = 0.0
        print("[Motors] Ready !")

    def set_speed(self, left, right):
        """Set left and right motor speeds as percentages from 0 to 100."""
        self.left_speed = max(0.0, min(100.0, left)) / 100
        self.right_speed = max(0.0, min(100.0, right)) / 100
        self.motor1.set_duty(self.left_speed)
        self.motor2.set_duty(self.right_speed)

    def stop(self):
        """Stop both motors and reset their stored speeds."""
        self.left_speed = 0.0
        self.right_speed = 0.0
        self.motor1.set_duty(0)
        self.motor2.set_duty(0)

    def close(self):
        """Stop and release both PWM channels."""
        self.stop()
        self.motor1.close()
        self.motor2.close()
