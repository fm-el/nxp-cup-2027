import time
from hardware.servo import Servo
from hardware.motors import Motors

servo = None
motors = None

try:
    servo = Servo()
    motors = Motors()

    print("==Test Servo")
    for a in (-120,120,90):
        print(f"  servo : {a}°")
        servo.set_angle(a)
        time.sleep(1.5)

    print("==Test Motors==")
    for a in range(0,101,10):
        print(f"  servo : {a}%")
        motors.set_speed(a,a)
        time.sleep(3)
    motors.set_speed(0,0)

finally :
    if motors: 
        motors.close()
    if servo: 
        servo.close()
    
