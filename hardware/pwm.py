"""PWM driver for the Linux sysfs interface (/sys/class/pwm)."""

from pathlib import Path
import time


class PwmChannel:
    """Control one hardware PWM channel through sysfs.

    All values written to sysfs are integers in nanoseconds
    (period, duty_cycle) or 0/1 (enable).
    """

    EXPORT_DELAY_S = 0.1  # time the kernel needs to create the pwmN folder

    def __init__(self, chip: int, freq_hz: int = 1000, channel: int = 0):
        """Export and start a PWM channel with a 0% duty cycle.

        Args:
            chip: index of the PWM controller (pwmchipN).
            freq_hz: PWM frequency in Hz.
            channel: channel index on this controller.
        """
        self.base = Path(f"/sys/class/pwm/pwmchip{chip}")
        self.channel = channel
        self.period = 1_000_000_000 // freq_hz  # period in nanoseconds

        # Create the pwmN folder only if it does not exist yet
        if not self.exported():
            self.export()
            time.sleep(self.EXPORT_DELAY_S)

        # 0% duty first, then period, then enable the output
        self.set_duty(0)
        self.set_period(self.period)
        self.enable()

    def _write(self, name: str, value):
        """Write a value into a file of the pwmN folder (e.g. 'duty_cycle')."""
        (self.base / f"pwm{self.channel}" / name).write_text(str(value))

    def exported(self) -> bool:
        """Return True if the channel folder already exists."""
        return (self.base / f"pwm{self.channel}").exists()

    def export(self):
        """Ask the kernel to create the pwmN folder for this channel."""
        (self.base / "export").write_text(str(self.channel))

    def unexport(self):
        """Ask the kernel to remove the pwmN folder (release the channel)."""
        (self.base / "unexport").write_text(str(self.channel))

    def set_duty(self, ratio: float):
        """Set the duty cycle as a ratio of the period.

        Args:
            ratio: 0.0 (always low) to 1.0 (always high). Clamped to this range.
        """
        ratio = max(0.0, min(1.0, ratio))
        duty_ns = int(ratio * self.period)
        self._write("duty_cycle", duty_ns)

    def set_period(self, period_ns: int):
        """Set the PWM period in nanoseconds."""
        self._write("period", period_ns)

    def enable(self):
        """Start the PWM output."""
        self._write("enable", 1)

    def disable(self):
        """Stop the PWM output."""
        self._write("enable", 0)

    def close(self):
        """Stop the signal safely and release the channel."""
        self.set_duty(0)
        self.disable()
        self.unexport()