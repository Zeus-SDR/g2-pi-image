#!/usr/bin/env python3
"""Check SD boot references and expansion setup in an offline mounted image."""
import argparse
from pathlib import Path


def verify(root, boot, boot_partuuid, root_partuuid):
    entries = {}
    for line in (root / "etc/fstab").read_text().splitlines():
        fields = line.split()
        if fields and not fields[0].startswith("#"):
            entries[fields[1]] = fields[0]
    if entries.get("/") != f"PARTUUID={root_partuuid}":
        raise ValueError("fstab root must identify the image root partition by PARTUUID")
    if entries.get("/boot/firmware") != f"PARTUUID={boot_partuuid}":
        raise ValueError("fstab boot must identify the image boot partition by PARTUUID")
    cmdline = (boot / "cmdline.txt").read_text().split()
    roots = [field for field in cmdline if field.startswith("root=")]
    if roots != [f"root=PARTUUID={root_partuuid}"]:
        raise ValueError("kernel root must match the image PARTUUID, not an eMMC device name")
    if "rootwait" not in cmdline:
        raise ValueError("kernel must wait for the SD root device")
    rc = root / "etc/rc.local"
    if not rc.stat().st_mode & 0o111 or "raspi-config --expand-rootfs" not in rc.read_text():
        raise ValueError("first-boot root expansion is missing")
    if not (root / "usr/bin/raspi-config").stat().st_mode & 0o111:
        raise ValueError("raspi-config must be executable")
    readme = (boot / "README-FIRST.txt").read_text()
    if "CM5 Lite" not in readme or "g2-cm5-sd-pi-image.rpi-imager-manifest" not in readme:
        raise ValueError("boot README must describe the CM5 Lite SD installation")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("boot", type=Path)
    parser.add_argument("boot_partuuid")
    parser.add_argument("root_partuuid")
    args = parser.parse_args()
    try:
        verify(args.root, args.boot, args.boot_partuuid, args.root_partuuid)
    except (ValueError, OSError) as error:
        parser.exit(1, f"FAIL: {error}\n")
    print("PASS: SD PARTUUID references, rootwait, expansion setup and SD first-boot guide")


if __name__ == "__main__":
    main()
