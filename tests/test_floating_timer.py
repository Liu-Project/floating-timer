import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from floating_timer import format_mode_label, format_time


class TestFormatTime(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_time(0), "00:00")

    def test_seconds_only(self):
        self.assertEqual(format_time(59), "00:59")

    def test_one_minute(self):
        self.assertEqual(format_time(60), "01:00")

    def test_under_an_hour(self):
        self.assertEqual(format_time(3599), "59:59")

    def test_over_an_hour(self):
        self.assertEqual(format_time(3600), "01:00:00")

    def test_hours_minutes_seconds(self):
        self.assertEqual(format_time(3661), "01:01:01")

    def test_float_input_is_truncated(self):
        self.assertEqual(format_time(59.9), "00:59")


class TestFormatModeLabel(unittest.TestCase):
    def test_countup_label(self):
        self.assertEqual(format_mode_label("countup", 900), "正计时")

    def test_countdown_label(self):
        self.assertEqual(format_mode_label("countdown", 900), "倒计时 15:00")

    def test_countdown_label_over_hour(self):
        self.assertEqual(format_mode_label("countdown", 3600), "倒计时 60:00")


if __name__ == "__main__":
    unittest.main()
