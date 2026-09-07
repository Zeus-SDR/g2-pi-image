"""Exercise release selection without allocating a full disk image."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "cm5_manifest", Path(__file__).resolve().parents[1] / "scripts/cm5-manifest.py")
manifest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manifest)


class GeneratorTests(unittest.TestCase):
    def test_both_editions_keep_customization_and_artifact_hashes(self):
        for sd, filename, tag in (
            (False, "g2-saturn-trixie64-cm5-2026-09-06.img.xz", "2026.09.06-cm5"),
            (True, "g2-saturn-trixie64-cm5-sd-2026-09-07.img.xz", "2026.09.07-cm5-sd"),
        ):
            with self.subTest(sd=sd), tempfile.TemporaryDirectory() as temp:
                source = Path(temp) / filename
                source.touch()
                output = Path(temp) / "manifest.json"
                argv = ["cm5-manifest.py", str(source), str(output)] + (["--sd"] if sd else [])
                with patch("sys.argv", argv), patch.object(manifest, "digest", side_effect=[
                    (1234, "a" * 64), (9452954112, "b" * 64)
                ]), patch.object(manifest.lzma, "open", return_value=io.BytesIO()), contextlib.redirect_stdout(io.StringIO()):
                    manifest.main()
                entry = json.loads(output.read_text())["os_list"][0]
                self.assertTrue(entry["url"].endswith(f"/{tag}/{filename}"))
                self.assertEqual(entry["init_format"], "cloudinit-rpi")
                self.assertEqual(entry["image_download_sha256"], "a" * 64)
                self.assertEqual(entry["extract_sha256"], "b" * 64)
                self.assertEqual(entry["image_download_size"], 1234)
                self.assertEqual(entry["extract_size"], 9452954112)
                self.assertEqual("Lite" in entry["name"], sd)

    def test_sd_rejects_emmc_filename(self):
        with patch("sys.argv", ["cm5-manifest.py", "g2-saturn-trixie64-cm5-2026-09-06.img.xz", "out", "--sd"]), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                manifest.main()
            self.assertEqual(result.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
