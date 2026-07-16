# ANAN G2 internal Pi image

A clean, ready to flash Raspberry Pi OS image for the **ANAN G2 internal Compute Module 4**, the small Pi that lives inside the radio and runs the Saturn stack.

It ships with **Raspberry Pi OS Trixie (64 bit)**, the **Saturn `p2app`** running as a systemd service, and the **Trixie power button fix** so the front power button does a clean shutdown. That fix is the reason this image exists: the stock Trixie and Bookworm desktop images leave the power button dead on a screenless G2.

## Install it

Use the latest official [Raspberry Pi Imager](https://www.raspberrypi.com/software/),
version **2.0.10 or newer**.

> [!IMPORTANT]
> Do **not** download the image and select **Use custom**. A local image does
> not tell Imager that Trixie's `cloudinit-rpi` customization is required, so
> the username and password will not be applied. The result is a login prompt
> with no usable password.

1. Download and save
   [`g2-pi-image.rpi-imager-manifest`](g2-pi-image.rpi-imager-manifest?raw=1).
   Keep the `.rpi-imager-manifest` filename extension.
2. Double-click the manifest to open it in Raspberry Pi Imager. If Imager is
   already open, use **App Options → Content Repository → Edit → Use custom
   file**, select the manifest, then apply and restart Imager.
3. Select **Raspberry Pi 4** as the device and **ANAN G2 internal CM4 image**
   as the operating system.
4. In **OS Customization**, set the username to exactly **`pi`** and choose
   your own password. Configure WiFi and SSH there if needed. Do not choose a
   different username: the Saturn tools and desktop are installed under
   `/home/pi`.
5. Select the microSD card, write it, and boot the G2.

On first boot the root filesystem auto expands to fill your card, and fresh SSH host keys are generated automatically.

## Set your own login

This image ships with **no credentials**. The `pi` account is **locked** until
the manifest-guided Imager customization sets your password. There is no
default password. Keep the username `pi`; only the password is yours to choose.

Default hostname is `g2pi`. Change it in the Imager if you like.

## Troubleshooting first boot

### The login prompt rejects my password

The card was most likely written through **Use custom**, or with an older
Imager. Reflash it by opening the manifest and following the steps above. The
image has no fallback or factory password.

### `/home/pi` appears to belong to the wrong user

Linux stores file ownership as numeric IDs. This image owns `/home/pi` as
UID/GID `1000:1000`, which is `pi:pi` inside the image. If you mount the card
on another Linux computer, that computer may display its own UID-1000 username
instead. That does not mean ownership was lost; do not recursively `chown` the
card based on the displayed name.

The released image also contains the LightDM login manager, Labwc/Wayland, and
WayVNC. Booting the card in a different CM4 does not remove those components;
a passwordless login prompt is the locked-account problem described above.

## Direct image download and verification

The [Releases page](../../releases/latest) contains the compressed `.img.xz`
and its `.sha256` file for verification and archival use. For installation,
open the manifest as described above instead of flashing the downloaded image
through **Use custom**.

```bash
sha256sum -c g2-saturn-trixie64-clean-2026-07-05.img.xz.sha256
```

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
