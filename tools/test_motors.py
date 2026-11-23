"""===== test_motors.py - DEBIX Model A motor ramp test =====
***Exercise each drive motor separately, then verify the emergency stop.***

Hardware:
    PWM1 pwmchip0 Pin23: left motor.
    PWM2 pwmchip1 Pin29: right motor.

Example :
    python test_motors.py
    Keep the vehicle secured before running this hardware test.
"""

import time
from hardware.motors import Motors

# Keep a handle for guaranteed motor cleanup in the finally block.
m = None
try:
    # Initialize the motor controller before running the test profiles.
    m = Motors()
    # Ramp the left motor up and back down while holding the right motor still.
    print("Left motor only, 0 -> 30% and back")
    for target in (30, 0):
        for _ in range(12):          # Repeated calls are needed to advance the speed ramp.
            m.set_speed(target, 0.0)
            time.sleep(0.1)
        time.sleep(1)

    # Repeat the ramp test with only the right motor active.
    print("Right motor only, same profile")
    for target in (30, 0):
        for _ in range(12):
            m.set_speed(0.0, target)
            time.sleep(0.1)
        time.sleep(1)

    # Test the emergency stop after briefly driving both motors.
    print("Emergency stop: ramp to 30% then stop()")
    for _ in range(8):
        m.set_speed(30, 30)
        time.sleep(0.1)
    m.stop()
    time.sleep(1)
except KeyboardInterrupt:
    print("Ctrl+C: shutting down cleanly")
finally:
    if m:
        m.close()