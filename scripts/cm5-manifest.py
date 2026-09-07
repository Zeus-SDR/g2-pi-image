#!/usr/bin/env python3
"""Generate CM5 Imager metadata from the actual compressed release artifact."""
import argparse
import copy
import hashlib
import json
import lzma
from pathlib import Path


def digest(stream):
    sha = hashlib.sha256()
    size = 0
    while chunk := stream.read(1024 * 1024):
        sha.update(chunk)
        size += len(chunk)
    return size, sha.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    filename = "g2-saturn-trixie64-cm5-2026-09-06.img.xz"
    if args.image.name != filename:
        parser.error(f"this release expects {filename}")
    with args.image.open("rb") as stream:
        compressed_size, compressed_hash = digest(stream)
    with lzma.open(args.image) as stream:
        raw_size, raw_hash = digest(stream)
    if raw_size != 9452954112:
        parser.error("unexpected raw image size; check the build input")
    repo = Path(__file__).resolve().parent.parent
    manifest = json.loads((repo / "g2-pi-image.rpi-imager-manifest").read_text())
    device = copy.deepcopy(manifest["imager"]["devices"][0])
    device.update(name="Raspberry Pi 5", tags=["pi5-64bit"],
                  description="Raspberry Pi 5 and Compute Module 5",
                  icon="https://downloads.raspberrypi.com/imager/icons/RPi_5.png")
    manifest["imager"]["devices"] = [device]
    entry = manifest["os_list"][0]
    entry.update(
        name="ANAN G2 internal Raspberry Pi CM5 image",
        icon=device["icon"],
        description="Screenless G2: Trixie 64-bit, Saturn p2app and CM5 XDMA driver",
        url=f"https://github.com/Zeus-SDR/g2-pi-image/releases/download/2026.09.06-cm5/{filename}",
        release_date="2026-09-06", devices=["pi5-64bit"],
        extract_size=raw_size, extract_sha256=raw_hash,
        image_download_size=compressed_size, image_download_sha256=compressed_hash,
    )
    with args.output.open("x") as stream:
        stream.write(json.dumps(manifest, indent=2) + "\n")
    print(f"{compressed_hash}  {filename}")


if __name__ == "__main__":
    main()
