"""
=========================================
 pwm.py - DEBIX Model A PWM Control
=========================================

***PWM driver for the Linux sysfs interface (/sys/class/pwm).***

"""

from pathlib import Path
import time

EXPORT_DELAY_S = 0.1  # time the kernel needs to create the pwmN folder


class PwmChannel:

    def __init__(self, chip: int, freq_hz: int = 1000, channel: int = 0):
        
        self.base = Path(f"/sys/class/pwm/pwmchip{chip}")
        self.channel = channel
        self.period = 1_000_000_000 // freq_hz  # period in nanoseconds

        if not self.exported():
            self.export()
            time.sleep(EXPORT_DELAY_S)

        self.set_duty(0)
        self.set_period(self.period)
        self.enable()

    def _write(self, name: str, value):

        (self.base / f"pwm{self.channel}" / name).write_text(str(value))

    def exported(self) -> bool:

        return (self.base / f"pwm{self.channel}").exists()

    def export(self):

        (self.base / "export").write_text(str(self.channel))

    def unexport(self):
        
        (self.base / "unexport").write_text(str(self.channel))

    def set_duty(self, ratio: float):
       
        ratio = max(0.0, min(1.0, ratio))
        duty_ns = int(ratio * self.period)
        self._write("duty_cycle", duty_ns)

    def set_period(self, period_ns: int):

        self._write("period", period_ns)

    def enable(self):

        self._write("enable", 1)

    def disable(self):

        self._write("enable", 0)

    def close(self):

        self.set_duty(0)
        self.disable()
        self.unexport()
