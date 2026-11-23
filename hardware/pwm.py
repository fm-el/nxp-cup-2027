"""pwm.py - DEBIX Model A Linux sysfs PWM driver

Hardware:
    PWM1 pwmchip0 Pin23: left motor.
    PWM2 pwmchip1 Pin29: right motor.
    PWM3 pwmchip2 Pin34: MG996R steering servo.

Example:
    channel = PwmChannel(chip=0, freq_hz=50)
    channel.set_duty(0.5)
    channel.close()

Sysfs period and duty_cycle values are written in nanoseconds.
"""

from pathlib import Path
import time

SYSFS_PWM_ROOT = Path("/sys/class/pwm")


class PwmChannel:
    """Control one hardware PWM channel through the Linux sysfs interface."""

    EXPORT_DELAY_S = 0.1  # Allow the kernel to create the pwmN directory.

    def __init__(self, chip: int, freq_hz: int = 1000, channel: int = 0):
        """Export and start a PWM channel with a 0% duty cycle.

        Args:
            chip: PWM controller index (pwmchipN).
            freq_hz: PWM frequency in Hz.
            channel: Channel index on this controller.

        Raises:
            ValueError: If the frequency would produce a non-positive period.
            OSError: If a sysfs operation fails (for example, due to permissions
                or a missing PWM controller).
        """
        period = 1_000_000_000 // freq_hz if freq_hz > 0 else 0
        if period <= 0:
            raise ValueError("freq_hz must be positive and produce a period of at least 1 ns")

        print("[PwmChannel] Initializing...")
        self.base = SYSFS_PWM_ROOT / f"pwmchip{chip}"
        self.channel = channel
        self.period = period

        # Export only if the channel directory does not already exist.
        if not self.exported():
            self.export()
            time.sleep(self.EXPORT_DELAY_S)

        # Start at 0% duty, set the period, then enable the output.
        self.set_duty(0)
        self.set_period(self.period)
        self.enable()
        print("[PwmChannel] Ready !")

    def _write(self, name: str, value):
        """Write a value to a file in this channel's sysfs directory."""
        (self.base / f"pwm{self.channel}" / name).write_text(str(value))

    def exported(self) -> bool:
        """Return True if this channel's sysfs directory already exists."""
        return (self.base / f"pwm{self.channel}").exists()

    def export(self):
        """Ask the kernel to create this channel's sysfs directory."""
        (self.base / "export").write_text(str(self.channel))

    def unexport(self):
        """Ask the kernel to release this channel."""
        (self.base / "unexport").write_text(str(self.channel))

    def set_duty(self, ratio: float):
        """Set duty as a fraction of the period, clamped to the range 0.0-1.0."""
        ratio = max(0.0, min(1.0, ratio))
        duty_ns = int(ratio * self.period)
        self._write("duty_cycle", duty_ns)

    def set_period(self, period_ns: int):
        """Set the PWM period in nanoseconds."""
        self._write("period", period_ns)

    def enable(self):
        """Enable the PWM output."""
        self._write("enable", 1)

    def disable(self):
        """Disable the PWM output."""
        self._write("enable", 0)

    def close(self):
        """Set duty to zero, disable the output, and release the channel."""
        self.set_duty(0)
        self.disable()
        self.unexport()
