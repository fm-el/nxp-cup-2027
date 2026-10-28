"""
=======================================================
 servo.py - DEBIX Model A steering servo motor control
=======================================================

Hardware:
    - PWM1 (pwmchip0) Pin23 → Left motor
    - PWM2 (pwmchip1) Pin29 → Right motor
    - PWM3 (pwmchip2) Pin34 → MG996R steering servo
    
Example : 
        from servo import Servo
        s = Servo()
        s.set_angle(90) #Set the servo motor at 90°
        s.stop()
        s.close()

"""

import time
from hardware.pwm import PwmChannel

#=========================================
# Steering servo motor constants
#=========================================

SERVO_FREQ_HZ = 50        # standard RC servo frequency (20 ms period)

MIN_ANGLE = 0
MAX_ANGLE = 180

MIN_PULSE_MS = 0.6
MAX_PULSE_MS = 2.0


INIT_POS = 90             # straight ahead
CLOSE_DELAY_S = 0.3       # time for the servo to reach INIT_POS before shutdown


class Servo:

    def __init__(self):

        self.servo = PwmChannel(chip=2, freq_hz=SERVO_FREQ_HZ)
        self.set_angle(INIT_POS)

    def set_angle(self, angle: float):
        
        angle = max(MIN_ANGLE, min(MAX_ANGLE, angle))

        ratio = (angle - MIN_ANGLE) / (MAX_ANGLE - MIN_ANGLE)
        pulse_ms = MIN_PULSE_MS + ratio * (MAX_PULSE_MS - MIN_PULSE_MS)

        period_ms = 1000 / SERVO_FREQ_HZ
        self.servo.set_duty(pulse_ms / period_ms)

    def close(self):

        self.set_angle(INIT_POS)
        time.sleep(CLOSE_DELAY_S)  # let the servo finish its move
        self.servo.close()
