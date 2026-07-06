# Third-party software and licenses

The G2 internal Pi image is an **aggregate**: a Raspberry Pi OS image with
additional software installed on it. That software is the work of others and is
distributed under its own licenses. This file lists each component, its author,
its license, and where to get the source — as those licenses require.

Full license texts are in [`LICENSES/`](LICENSES/). Modifications we made to any
of this software are published in [`patches/`](patches/).

## Components on the image

### Raspberry Pi OS (Trixie, 64-bit)
- **From:** Raspberry Pi Ltd — <https://www.raspberrypi.com/software/operating-systems/>
- **License:** an aggregate of many free-software licenses (Debian). The base OS
  is freely redistributable; per-package source is available from the Debian and
  Raspberry Pi archives (`apt source <pkg>`). The Raspberry Pi firmware/bootloader
  carries its own license — see <https://github.com/raspberrypi/firmware>.
- **Modified?** No. Stock Raspberry Pi OS Trixie with configuration added (see below).

### Saturn — `p2app` and the FPGA/bench tools
- **What:** the `p2app` radio service and the `flashwriter`, `biascheck`,
  `audiotest`, and AXI read/write tools.
- **From:** Laurence Barker — <https://github.com/laurencebarker/Saturn>
- **Built from:** `p2app v46`, upstream commit
  [`4b0b76f`](https://github.com/laurencebarker/Saturn/commit/4b0b76f).
- **License:** **GPL-3.0-or-later** — [`LICENSES/GPL-3.0.txt`](LICENSES/GPL-3.0.txt).
- **Modified?** No. Built unmodified from the upstream commit above; that repo is
  the Corresponding Source (GPLv3 §6).

### XDMA kernel driver
- **What:** the `xdma` kernel module that `p2app` uses to talk to the Saturn FPGA.
- **From:** Xilinx/AMD `dma_ip_drivers`, carried in Saturn's `linuxdriver/xdma`.
- **License:** **GPL-2.0** ([`LICENSES/GPL-2.0.txt`](LICENSES/GPL-2.0.txt)) with
  BSD-licensed portions ([`LICENSES/XDMA-BSD.txt`](LICENSES/XDMA-BSD.txt)).
- **Modified?** **Yes.** The Makefile was patched to build against Linux kernel
  ≥ 6.13 (Trixie ships 6.18). The change and its rationale are in
  [`patches/xdma-kernel-6.13-build.patch`](patches/xdma-kernel-6.13-build.patch)
  and [`patches/README.md`](patches/README.md). Modification date: 2026-07-05.

## Configuration and fixes added by this image

These are this image's own additions/config (not modifications to the software
above), documented for transparency:

- **Power-button fix:** a per-user `Hidden=true` override of
  `/etc/xdg/autostart/pwrkey.desktop` plus a `systemd-logind` drop-in, so the
  front power button does a clean shutdown on the screenless G2 (the stock GUI
  handler waits for an on-screen dialog that never appears).
- **`p2app.service`:** a systemd unit that runs `p2app -s -p` at boot.
- **`config.txt`:** Trixie base plus the carried-over `gpio-shutdown` (pin 26),
  `gpio=15=op,dh` LED, and 2 GHz overclock. The stock file is kept as
  `config.txt.stock` on the image.

## Attribution

Built on **Laurence Barker's [Saturn](https://github.com/laurencebarker/Saturn)**
project, with the **Xilinx/AMD XDMA driver** and **Raspberry Pi OS** by Raspberry
Pi Ltd. Packaged for the OpenHPSDR Zeus project. Thanks to the OpenHPSDR and ANAN
community.
