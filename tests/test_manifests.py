"""Protect Imager customization and board selection for all three downloads."""
import json
from pathlib import Path
import unittest

REPO = Path(__file__).resolve().parent.parent


class ManifestTests(unittest.TestCase):
    def test_each_board_has_its_own_customizable_download(self):
        urls = set()
        for filename, tag in (
            ("g2-pi-image.rpi-imager-manifest", "pi4-64bit"),
            ("g2-cm5-pi-image.rpi-imager-manifest", "pi5-64bit"),
            ("g2-cm5-sd-pi-image.rpi-imager-manifest", "pi5-64bit"),
        ):
            with self.subTest(filename=filename):
                manifest = json.loads((REPO / filename).read_text())
                self.assertEqual(len(manifest["os_list"]), 1)
                entry = manifest["os_list"][0]
                # A custom file without this metadata can leave pi locked.
                self.assertEqual(entry["init_format"], "cloudinit-rpi")
                self.assertEqual(entry["architecture"], "armv8")
                self.assertEqual(entry["devices"], [tag])
                self.assertIn(tag, manifest["imager"]["devices"][0]["tags"])
                self.assertRegex(entry["extract_sha256"], r"^[a-f0-9]{64}$")
                self.assertRegex(entry["image_download_sha256"], r"^[a-f0-9]{64}$")
                self.assertGreater(entry["extract_size"], entry["image_download_size"])
                self.assertLess(entry["image_download_size"], 2 * 1024**3)
                self.assertTrue(entry["url"].startswith(
                    "https://github.com/Zeus-SDR/g2-pi-image/releases/download/"))
                if "cm5-sd" in filename:
                    self.assertIn("CM5 Lite", entry["name"])
                    self.assertIn("microSD", entry["name"])
                    self.assertIn("/2026.09.07-cm5-sd/", entry["url"])
                urls.add(entry["url"])
        self.assertEqual(len(urls), 3)


if __name__ == "__main__":
    unittest.main()
