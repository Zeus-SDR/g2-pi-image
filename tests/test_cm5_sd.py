"""Reject incorrect storage references and missing SD first-boot setup."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("verify_sd", Path(__file__).with_name("verify-cm5-sd.py"))
verify_sd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_sd)


class SdBootTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "root"
        self.boot = Path(self.temp.name) / "boot"
        (self.root / "etc").mkdir(parents=True)
        (self.root / "usr/bin").mkdir(parents=True)
        self.boot.mkdir()
        (self.root / "etc/fstab").write_text(
            "PARTUUID=abcd-01 /boot/firmware vfat defaults 0 2\n"
            "PARTUUID=abcd-02 / ext4 defaults 0 1\n")
        (self.boot / "cmdline.txt").write_text("root=PARTUUID=abcd-02 rootwait\n")
        (self.boot / "README-FIRST.txt").write_text(
            "CM5 Lite g2-cm5-sd-pi-image.rpi-imager-manifest\n")
        rc = self.root / "etc/rc.local"
        rc.write_text("#!/bin/sh\nraspi-config --expand-rootfs\n")
        rc.chmod(0o755)
        config = self.root / "usr/bin/raspi-config"
        config.write_text("#!/bin/sh\n")
        config.chmod(0o755)

    def verify(self):
        verify_sd.verify(self.root, self.boot, "abcd-01", "abcd-02")

    def test_uuid_boot_is_valid(self):
        self.verify()

    def test_emmc_device_name_is_rejected(self):
        (self.boot / "cmdline.txt").write_text("root=/dev/mmcblk0p2 rootwait")
        with self.assertRaisesRegex(ValueError, "kernel root"):
            self.verify()

    def test_wrong_partition_is_rejected(self):
        (self.root / "etc/fstab").write_text(
            "PARTUUID=other-01 /boot/firmware vfat defaults 0 2\n"
            "PARTUUID=abcd-02 / ext4 defaults 0 1\n")
        with self.assertRaisesRegex(ValueError, "fstab boot"):
            self.verify()

    def test_conflicting_root_arguments_are_rejected(self):
        (self.boot / "cmdline.txt").write_text(
            "root=PARTUUID=abcd-02 root=/dev/mmcblk0p2 rootwait")
        with self.assertRaisesRegex(ValueError, "kernel root"):
            self.verify()

    def test_missing_rootwait_is_rejected(self):
        (self.boot / "cmdline.txt").write_text("root=PARTUUID=abcd-02")
        with self.assertRaisesRegex(ValueError, "wait"):
            self.verify()

    def test_non_executable_expansion_is_rejected(self):
        (self.root / "etc/rc.local").chmod(0o644)
        with self.assertRaisesRegex(ValueError, "expansion"):
            self.verify()

    def test_emmc_instructions_are_rejected(self):
        (self.boot / "README-FIRST.txt").write_text("Flash CM5 eMMC with usbboot")
        with self.assertRaisesRegex(ValueError, "README"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
