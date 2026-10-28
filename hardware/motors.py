"""
=========================================
 motors.py - DEBIX Model A motor control
=========================================

***Control the left and right propulsion motors.***

Hardware:
    - PWM1 (pwmchip0) Pin23 → Left motor
    - PWM2 (pwmchip1) Pin29 → Right motor
    - PWM3 (pwmchip2) Pin34 → MG996R steering servo
    
    Example : 
        from motors import Motors
        m = Motors()
        m.set_speed(80,30)  #Set left motor at 80% of its speed and right motor at 30% of its speed
        m.stop()
        m.close()
   
    """

from hardware.pwm import PwmChannel

MOTOR_FREQ_HZ = 1_000


class Motors:

    def __init__(self):
    
        print("[Motors] Initialisation...")
        self.motor1 = PwmChannel(chip=0, freq_hz=MOTOR_FREQ_HZ) 
        self.motor2 = PwmChannel(chip=1, freq_hz=MOTOR_FREQ_HZ)
        self.left_speed = 0.0
        self.right_speed = 0.0
        print("[Motors] Ready !")


    def set_speed(self, left: float, right: float):

        left = max(0.0, min(100.0, left))/100
        right = max(0.0, min(100.0, right))/100

        self.motor1.set_duty(left)
        self.motor2.set_duty(right)

    def stop(self):

        self.left_speed = 0.0
        self.right_speed = 0.0
        self.motor1.set_duty(0)
        self.motor2.set_duty(0)

    def close(self):

        self.stop()
        self.motor1.close()
        self.motor2.close()
