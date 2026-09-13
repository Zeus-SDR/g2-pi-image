"""Protect CM-specific USB host configuration in offline images."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

spec = importlib.util.spec_from_file_location("verify_input", Path(__file__).with_name("verify-cm-input.py"))
verify_input = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_input)


class InputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "root"
        self.boot = Path(self.temp.name) / "boot"
        (self.root / "boot").mkdir(parents=True)
        (self.boot / "overlays").mkdir(parents=True)
        (self.boot / "overlays/dwc2.dtbo").touch()
        self.config = "[cm4]\notg_mode=1\n[all]\n"
        for suffix in ("v8", "2712"):
            (self.root / f"boot/config-6.18.34+rpt-rpi-{suffix}").write_text("\n".join(
                f"CONFIG_{symbol}=y" for symbol in (
                    "INPUT", "INPUT_EVDEV", "INPUT_MOUSEDEV", "HID", "HID_GENERIC",
                    "USB_HID", "USB", "USB_DWC2", "USB_XHCI_HCD", "USB_XHCI_PLATFORM")))

    def verify(self, board="cm5"):
        (self.boot / "config.txt").write_text(self.config)
        verify_input.verify(self.root, self.boot, board)

    def test_released_config_enables_cm4(self):
        self.verify("cm4")

    def test_released_config_leaves_cm5_without_usb_host(self):
        with self.assertRaisesRegex(ValueError, "CM5 USB host"):
            self.verify()

    def test_cm5_host_overlay(self):
        self.config += "[cm5]\ndtoverlay=dwc2,dr_mode=host\n[all]\n"
        self.verify()
        self.verify("cm4")

    def test_wrong_filter_comment_and_peripheral_do_not_enable_host(self):
        for extra in ("# dtoverlay=dwc2,dr_mode=host\n", "[cm4]\ndtoverlay=dwc2,dr_mode=host\n", "[cm5]\ndtoverlay=dwc2,dr_mode=peripheral\n"):
            with self.subTest(extra=extra), self.assertRaisesRegex(ValueError, "CM5 USB host"):
                self.config = "[all]\n" + extra
                self.verify()

    def test_missing_driver_and_overlay_are_rejected(self):
        self.config += "[cm5]\ndtoverlay=dwc2,dr_mode=host\n"
        path = self.root / "boot/config-6.18.34+rpt-rpi-2712"
        original = path.read_text()
        path.write_text(original.replace("CONFIG_USB_HID=y", "# CONFIG_USB_HID is not set"))
        with self.assertRaisesRegex(ValueError, "CONFIG_USB_HID"):
            self.verify()
        path.write_text(original)
        (self.boot / "overlays/dwc2.dtbo").unlink()
        with self.assertRaisesRegex(ValueError, "dwc2.dtbo"):
            self.verify()

    def test_conflicting_overlay_is_rejected(self):
        self.config += "[cm5]\ndtoverlay=dwc2,dr_mode=host\ndtoverlay=dwc2,dr_mode=peripheral\n"
        with self.assertRaisesRegex(ValueError, "CM5 USB host"):
            self.verify()

    def test_unevaluated_includes_and_filters_are_rejected(self):
        for extra in ("include custom.txt\n", "include\tcustom.txt\n", "[gpio4=1]\n"):
            with self.subTest(extra=extra), self.assertRaisesRegex(ValueError, "review"):
                self.config = "[cm5]\ndtoverlay=dwc2,dr_mode=host\n" + extra
                self.verify()

    def test_separate_mode_override_requires_review(self):
        for extra in ("dtparam=dr_mode=peripheral\n", "dtparam=g-rx-fifo-size=558,dr_mode=peripheral\n"):
            with self.subTest(extra=extra), self.assertRaisesRegex(ValueError, "mode override"):
                self.config = "[cm5]\ndtoverlay=dwc2,dr_mode=host\n" + extra
                self.verify()

    def test_cli_reports_a_clean_failure(self):
        (self.boot / "config.txt").write_text(self.config)
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("verify-cm-input.py")),
             str(self.root), str(self.boot), "cm5"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stderr.startswith("FAIL: CM5 USB host"), result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
