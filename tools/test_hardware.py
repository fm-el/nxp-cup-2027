import time
from hardware.servo import Servo
from hardware.motors import Motors

servo = None
motors = None

try:

    servo = Servo()
    motors = Motors()

    print("==Test Servo")
    for a in (-20,20,0):
        print(f"  servo : {a}°")
        servo.steer(a)
        time.sleep(1.5)

    print("==Test Motors==")
    for i in range(0,5):
        speed = i/10
        print(f"  speed : {speed:.0%}")
        motors.set_speed(speed,speed)
        time.sleep(0.5)
        
    time.sleep(2)
    motors.set_speed(0,0)

finally :
    if motors: 
        motors.close()
    if servo: 
        servo.close()
    