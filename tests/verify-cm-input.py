#!/usr/bin/env python3
"""Check the pinned G2 images' USB host setup and built-in input drivers offline."""
import argparse
from pathlib import Path


def verify(root: Path, boot: Path, board: str):
    # The image builder owns this flat config; includes/conditional filters must
    # be reviewed explicitly rather than silently treated as active settings.
    active = []
    section = "all"
    for raw in (boot / "config.txt").read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            if section not in ("all", "cm4", "cm5"):
                raise ValueError(f"unsupported boot filter [{section}]; review USB host configuration")
        elif line.split(maxsplit=1)[0] == "include":
            raise ValueError("included boot configuration requires an explicit USB host review")
        elif section in ("all", board):
            active.append("".join(line.split()))
    host = "dtoverlay=dwc2,dr_mode=host"
    for line in active:
        if line.startswith("dtparam=") and any(
            parameter.startswith("dr_mode=") for parameter in line[8:].split(",")
        ):
            raise ValueError("separate dr_mode override requires an explicit USB host review")
    dwc2 = [line for line in active if line == "dtoverlay=dwc2" or line.startswith("dtoverlay=dwc2,")]
    if board == "cm5" and dwc2 != [host]:
        raise ValueError("CM5 USB host is not enabled: require dtoverlay=dwc2,dr_mode=host in [cm5] or [all]")
    otg = [line for line in active if line.startswith("otg_mode=")]
    if board == "cm4" and otg[-1:] != ["otg_mode=1"] and dwc2 != [host]:
        raise ValueError("CM4 USB host is not enabled")
    kernel = "6.18.34+rpt-rpi-" + ("2712" if board == "cm5" else "v8")
    config = set((root / "boot" / f"config-{kernel}").read_text().splitlines())
    for symbol in ("INPUT", "INPUT_EVDEV", "INPUT_MOUSEDEV", "HID", "HID_GENERIC", "USB_HID", "USB", "USB_DWC2", "USB_XHCI_HCD", "USB_XHCI_PLATFORM"):
        if f"CONFIG_{symbol}=y" not in config:
            raise ValueError(f"{kernel}: missing built-in CONFIG_{symbol}=y")
    if board == "cm5" and not (boot / "overlays/dwc2.dtbo").is_file():
        raise ValueError("missing dwc2.dtbo overlay")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("boot", type=Path)
    parser.add_argument("board", choices=("cm4", "cm5"))
    args = parser.parse_args()
    try:
        verify(args.root, args.boot, args.board)
    except (ValueError, OSError) as error:
        parser.exit(1, f"FAIL: {error}\n")
    print(f"PASS: {args.board} USB host configuration and built-in keyboard/mouse drivers")
