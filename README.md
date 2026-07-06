# ANAN G2 internal Pi image

A clean, ready to flash Raspberry Pi OS image for the **ANAN G2 internal Compute Module 4**, the small Pi that lives inside the radio and runs the Saturn stack.

It ships with **Raspberry Pi OS Trixie (64 bit)**, the **Saturn `p2app`** running as a systemd service, and the **Trixie power button fix** so the front power button does a clean shutdown. That fix is the reason this image exists: the stock Trixie and Bookworm desktop images leave the power button dead on a screenless G2.

## Download

Grab the latest image from the [Releases page](../../releases/latest). Each release has two files:

* `g2-saturn-trixie64-clean-YYYY-MM-DD.img.xz` (about 1.7 GB compressed)
* `.sha256` so you can verify the download

Verify before flashing:

```bash
sha256sum -c g2-saturn-trixie64-clean-2026-07-05.img.xz.sha256
```

## Flash it

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/).

1. Choose **Use custom** and pick the `.img.xz` file. Imager reads `.xz` directly, so there is no need to unzip it.
2. Click the gear or **Edit Settings** and set **your own** username, password, and (if you use WiFi) your network before writing. See the note below.
3. Write it to your card and boot the G2.

On first boot the root filesystem auto expands to fill your card, and fresh SSH host keys are generated automatically.

## Set your own login

This image ships with **no credentials**. The `pi` account is **locked** until you set a password. Use the Raspberry Pi Imager customization (the gear) to create your username and password, and your WiFi if you need it. Whatever you set there overrides the image, so the login is yours and yours alone.

Default hostname is `g2pi`. Change it in the Imager if you like.

## What is on it

* Raspberry Pi OS Trixie, 64 bit, for the CM4
* Saturn `p2app` as a systemd service (`p2app.service`)
* XDMA driver built for the current kernel
* FPGA and bench tools on the desktop: flashwriter, biascheck, audiotest, AXI reader and writer
* The power button fix and carried over overclock and LED config

## Clean and safe to share

There is nothing personal on this image. No saved WiFi, no SSH keys, no passwords, the machine identity is blanked, host keys are removed so each card generates its own, and logs, shell history, and free space were all wiped. A short `README-FIRST.txt` also lives on the boot partition.

## Hardware

The ANAN G2 contains a Raspberry Pi Compute Module 4 on the Saturn carrier. This image is for that internal CM4. If your G2 has a 1 GB CM4 it is fine for headless operation, the p2app radio job does not need a desktop.

## Licenses and source

This image bundles other people's software under their own licenses, so it comes
with the notices and source pointers those licenses require:

* **Saturn** (`p2app` and the FPGA/bench tools) — GPL-3.0, © Laurence Barker.
  Built unmodified from [`laurencebarker/Saturn`](https://github.com/laurencebarker/Saturn) @ `4b0b76f`.
* **XDMA driver** — GPL-2.0 (with BSD portions), Xilinx/AMD. **Modified** to build
  on kernel ≥ 6.13; the patch is in [`patches/`](patches/).
* **Raspberry Pi OS** — Raspberry Pi Ltd, freely redistributable (Debian).

Full details, license texts, and the exact source/commit for each component are
in **[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)**, license texts in
[`LICENSES/`](LICENSES/), and our modifications in [`patches/`](patches/).

## Credit

Built on Laurence Barker's [Saturn](https://github.com/laurencebarker/Saturn)
project, with the Xilinx/AMD XDMA driver and Raspberry Pi OS. Thanks to the
OpenHPSDR and ANAN community.
