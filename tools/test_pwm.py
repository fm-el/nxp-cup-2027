"""===== test_pwm.py - DEBIX Model A PWM channel test =====
***Verify duty-cycle writes and release of the three PWM channels.***

Hardware:
    PWM1 pwmchip0 Pin23: left motor.
    PWM2 pwmchip1 Pin29: right motor.
    PWM3 pwmchip2 Pin34: MG996R steering servo.

Example :
    python test_pwm.py
    Run only when pwm0 is not already exported on chips 0, 1, and 2.
"""

import time
from pathlib import Path
from hardware.pwm import PwmChannel

def state(chip):
    """Return whether pwm0 is currently exported for the specified PWM chip."""
    return Path(f"/sys/class/pwm/pwmchip{chip}/pwm0").exists()

# Refuse to interfere with PWM channels that are already exported.
for chip in (0, 1, 2):
    assert not state(chip), f"pwmchip{chip}/pwm0 is already exported: clean it up first"

for chip in (0, 1, 2):
    # Test each channel at servo-style frequency and verify duty-cycle writes.
    ch = PwmChannel(chip=chip, freq_hz=50)
    try:
        assert state(chip)
        for r in (0.05, 0.075, 0.10):
            ch.set_duty(r)
            d = int(Path(f"/sys/class/pwm/pwmchip{chip}/pwm0/duty_cycle").read_text())
            assert d == int(r * ch.period), (d, r)
        print(f"chip {chip} OK")
    # Always disable and release the PWM channel, including after assertion failures.
    finally:
        ch.close()
    assert not state(chip), f"chip {chip}: leak after close()"
print("PWM: all channels OK, no leaks")