"""test_pwm.py - DEBIX Model A PWM channel hardware test

Verify duty-cycle writes and release of all three PWM channels.
Run on the target hardware only when pwm0 is not already exported on chips
0, 1, and 2. This test controls real hardware outputs.
"""

from pathlib import Path

from hardware.pwm import PwmChannel


def is_exported(chip):
    """Return whether pwm0 is currently exported for the specified chip."""
    return Path(f"/sys/class/pwm/pwmchip{chip}/pwm0").exists()


# Refuse to interfere with channels that are already exported.
for chip in (0, 1, 2):
    assert not is_exported(chip), (
        f"pwmchip{chip}/pwm0 is already exported; clean it up first"
    )

for chip in (0, 1, 2):
    channel = PwmChannel(chip=chip, freq_hz=50)
    try:
        assert is_exported(chip)
        for ratio in (0.05, 0.075, 0.10):
            channel.set_duty(ratio)
            duty_ns = int(
                Path(f"/sys/class/pwm/pwmchip{chip}/pwm0/duty_cycle").read_text()
            )
            assert duty_ns == int(ratio * channel.period), (duty_ns, ratio)
        print(f"[test_pwm] pwmchip{chip} OK")
    finally:
        channel.close()
    assert not is_exported(chip), f"pwmchip{chip}: channel still exported after close()"

print("[test_pwm] All channels passed; no exported channels remain.")
