"""===== test_servo.py - DEBIX Model A steering-servo test =====
***Check servo latency, repeatability, and PWM-channel cleanup.***

Hardware:
    PWM3 pwmchip2 Pin34: MG996R steering servo.

Example :
    python test_servo.py
    Observe the servo during the prompted angle and repeatability tests.
"""

import time
from pathlib import Path
from servo import Servo, MIN_ANGLE, MAX_ANGLE

# Conservative initial angle bounds; expand only after checking mechanics.
SAFE_MIN, SAFE_MAX = 80, 100   # Expand in 5-degree steps only after checking the mechanism.
assert MIN_ANGLE <= SAFE_MIN <= SAFE_MAX <= MAX_ANGLE
# Read back the sysfs duty-cycle value for the steering PWM channel.
DUTY = Path("/sys/class/pwm/pwmchip2/pwm0/duty_cycle")

s = None
try:
    # Initialize the servo, then check latency and repeated travel.
    s = Servo()
    print("T1 neutral, wait 2 s")
    time.sleep(2)

    # Measure each set_angle call and wait for movement confirmation.
    print("T2 latency: measuring set_angle time")
    for a in (SAFE_MAX, 90, SAFE_MIN, 90):
        t = time.perf_counter()
        s.set_angle(a)
        dt = (time.perf_counter() - t) * 1000
        print(f"  {a}° : {dt:.2f} ms, duty={DUTY.read_text().strip()}")
        input("  Press Enter when the servo has finished moving... ")

    # Repeat a fixed sequence to visually assess return-to-center consistency.
    print("T3 repeatability: 20 round trips")
    for _ in range(20):
        for a in (SAFE_MIN, 90, SAFE_MAX, 90):
            s.set_angle(a)
            time.sleep(0.5)
    print("Has the neutral position drifted? Check visually.")
except KeyboardInterrupt:
    print("Ctrl+C: shutting down cleanly")
finally:
    if s:
        s.close()
print("Channel released:", not Path("/sys/class/pwm/pwmchip2/pwm0").exists())