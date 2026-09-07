# Raspberry Pi CM5 image

This second image targets the **official Raspberry Pi Compute Module 5 with
eMMC in a screenless ANAN G2**. It does not configure an internal touch panel
and is not for the Radxa CM5.

## What changed from the CM4 image

The July 5 image already contains the CM5 kernel, initramfs and device tree.
Its boot configuration, `kernel_2712.img` and `bcm2712-rpi-cm5-cm5io.dtb`
match the running CM5 verified on September 6. Its Saturn revision is
`4b0b76f345961cfeeb447abc6d8b0373f5743245` (p2app v46).

However, it only installs XDMA under `6.18.34+rpt-rpi-v8`, the CM4 kernel.
The CM5 boots `6.18.34+rpt-rpi-2712`. Without an XDMA module for that kernel,
there are no `/dev/xdma*` devices and p2app repeatedly exits.

The CM5 image adds the module verified on the working CM5, regenerates the
CM5 module dependency/PCIe alias indexes, and updates the boot-partition
README. It preserves the original boot settings, Saturn software, first-boot
expansion and credential cleanup. It contains no Zeus installation or
operator settings copied from the running radio.

The module is built from the existing Saturn source and its existing kernel
6.13 compatibility changes. No additional driver source modification is
needed. The source remains in `/home/pi/github/Saturn` in the image.

## Install or replace an existing CM5 image

**Already have a Raspberry Pi CM5 in your G2? Start here.** Leave the module
installed. A CM5 with onboard eMMC uses the same USB programming procedure
whether its storage is blank or already contains a working image. You do not
need to reinstall the module or buy a separate I/O board for this procedure.

Writing this image **erases the selected eMMC**, including installed programs,
accounts and locally saved settings. While the old system still works, copy
any files and settings you need to another computer. Keep that backup private.
This is a full system replacement; it does not migrate settings or install
Zeus. Ordinary package/application updates are separate from reimaging.

This guide targets the eMMC model. A **CM5 Lite without eMMC** uses a different
storage procedure; do not follow the eMMC disk-selection steps for it. A Radxa
CM5 is also different hardware and cannot use this image.

### 1. Gather the downloads and equipment

- A Mac, Windows PC or Linux computer with internet access.
- A **micro-USB data cable**, plus an adapter if your computer needs one.
  A charge-only cable will not work.
- Ethernet from the G2 to your normal network for first-boot access.
- [Raspberry Pi Imager](https://www.raspberrypi.com/software/), **2.0.10 or newer**.
- From the [CM5 release](https://github.com/Zeus-SDR/g2-pi-image/releases/tag/2026.09.06-cm5),
  download **g2-cm5-pi-image.rpi-imager-manifest**. Keep that extension.
  Imager will download and verify the image named in the manifest; you do not
  need to decompress the `.img.xz` yourself.

The raw image is 9,452,954,112 bytes. The destination must be larger than that;
32 GB eMMC is the configuration used for the existing CM5 verification.

### 2. Prepare the USB flashing tool on your computer

Use the current official [Raspberry Pi usbboot](https://github.com/raspberrypi/usbboot)
with the **mass-storage-gadget64** payload that supports CM5. Older CM4-only
USB boot tools are not the correct choice.

**macOS** — with Homebrew and Apple's command-line build tools installed:

```bash
brew install libusb pkg-config
git clone --recurse-submodules --shallow-submodules --depth=1 \
  https://github.com/raspberrypi/usbboot ~/Downloads/g2-usbboot
cd ~/Downloads/g2-usbboot
make INSTALL_PREFIX=/usr/local
```

If `g2-usbboot` already exists, use your existing up-to-date checkout or pick
another empty directory; do not overwrite unrelated files. If macOS requests
command-line tools, finish their installation and rerun `make`.

**Windows** — install `rpiboot_setup.exe` from the official
[usbboot Windows release](https://github.com/raspberrypi/usbboot/releases/tag/windows-v1.1).
That release supports CM5. Accept the driver's installation prompt. The
installed `rpi-mass-storage-gadget64.bat` runs the CM5 mass-storage command.
If needed, open a Command Prompt in the installation directory and use
`rpiboot.exe -d mass-storage-gadget64`.

**Debian/Ubuntu Linux** — install the build tools, then build usbboot:

```bash
sudo apt install git libusb-1.0-0-dev pkg-config build-essential
git clone --recurse-submodules --shallow-submodules --depth=1 \
  https://github.com/raspberrypi/usbboot ~/g2-usbboot
cd ~/g2-usbboot
make
```

Other Linux distributions should use the equivalent dependencies listed in
usbboot's README. These commands prepare the host; they do not write the G2.

### 3. Put the installed CM5 into USB programming mode

Use the board diagram in the
[G2 manual, pages 40–41](https://apache-labs.com/public/storage/download_file/1756364841_1023_1023_G2-manual-v1.4-2_updated.pdf#page=40)
while identifying the connector and switch.

1. Shut down the existing G2 normally, then disconnect its power supply.
   Remove the top cover and observe static precautions.
2. Locate the **internal micro-USB programming connector** on the Saturn
   board beside Ethernet and the four-position switch. This is the internal
   programming connection, not a front/rear USB host port.
3. Photograph the switch positions. In the manual's diagram, the switch bank
   is marked **SW1**. Move **only the second switch inward from the board
   edge toward the micro-USB connector**, matching that diagram. The manual's
   closing text calls it SW2; use the physical diagram rather than guessing
   from that inconsistent label. If your board differs, establish its correct
   programming setting before proceeding.
4. Connect the internal micro-USB socket to the computer with the data cable.
   Do not force the plug against nearby hardware.
5. Start the mass-storage tool. On macOS or Linux, from the usbboot directory:

   ```bash
   sudo ./rpiboot -d mass-storage-gadget64
   ```

   On Windows, run `rpi-mass-storage-gadget64.bat`, or the equivalent command
   in step 2. Leave its window open while it waits for the device.
6. Apply power to the G2. Wait for usbboot to transfer its payload and for
   the CM5 eMMC to appear as a USB storage device. If the computer offers to
   initialize or format an unreadable disk, **cancel** that prompt.

The old operating system does not need to boot or accept a login for this
procedure. A working or damaged prior image is overwritten in the same way.

### 4. Open the CM5 manifest and set your login

1. Double-click **g2-cm5-pi-image.rpi-imager-manifest** to open it in Imager.
   If file association does not open it, use **App Options → Content
   Repository → Edit → Use custom file**, select the manifest, apply and
   restart Imager.
2. Select **Raspberry Pi 5**, then
   **ANAN G2 internal Raspberry Pi CM5 image**.
3. In OS Customization, keep the username **exactly `pi`**. The installed
   Saturn paths depend on `/home/pi`. Choose your own password; the image
   has **no default password**.
4. Set a hostname (default `g2pi`), locale and network settings as needed.
   Enable SSH and choose your authentication method if you want remote
   access. Ethernet is the straightforward first-boot connection.

**Do not select the `.img.xz` through the OS picker's “Use custom.”** This
image requires the manifest's `cloudinit-rpi` metadata to apply your login.
The Content Repository's **Use custom file** above selects the manifest and
is the correct workflow.

### 5. Select the eMMC, write and verify

1. Identify the newly appeared USB disk by its connection and capacity.
   On macOS, `diskutil list` helps; on Linux, use `lsblk`; on Windows, check
   Disk Management. Do not initialize it there. A nominal 32 GB eMMC may be
   shown as approximately 29 GiB.
2. Select **that CM5 eMMC** in Imager. Check the destination again: writing
   erases it. Never select your computer's system disk or your backup card.
3. Start the write and apply the customization. Allow both writing and
   verification to finish; do not disconnect the cable or radio power.
4. After Imager reports success, eject the USB disk. Disconnect G2 power,
   remove the programming USB cable, and restore the photographed normal
   switch positions. The manual shows all four toward the board mounting
   hole for normal operation.
5. With power still disconnected, restore any hardware moved for cable
   access and refit the cover. Connect Ethernet and power the G2 normally.

### 6. Let first boot finish, then check the radio

Allow several minutes for filesystem expansion and fresh SSH host-key
creation. The existing first-boot expansion process can restart the system.
Do not interrupt it. Find the G2 using its chosen hostname or your router's
DHCP client list.

```bash
ssh pi@g2pi.local
```

If `.local` names do not resolve, substitute the G2's assigned IP. If SSH says
that the host key changed, verify that the address belongs to the radio you
just reflashed before removing its old entry with `ssh-keygen -R g2pi.local`
(or the IP you used). A fresh image generates a new identity.

Inside the Pi, run these read-only checks:

```bash
uname -r
/sbin/modinfo -F vermagic xdma
ls /dev/xdma*
systemctl show p2app -p ActiveState -p NRestarts
df -h /
```

Expected: kernel `6.18.34+rpt-rpi-2712`; XDMA vermagic begins with that exact
version; XDMA device nodes exist; p2app is active without repeated restarts;
the root filesystem has expanded to use the eMMC.

Refresh discovery in your SDR client, connect to the G2 and verify **receive
and audio**. For logs, use `journalctl -u p2app -b --no-pager` or watch with
`journalctl -fu p2app`. Verify the front button performs a normal shutdown
when you finish testing. This procedure does not require transmitting or
updating the Saturn FPGA.

### Troubleshooting

| Symptom | Check |
|---|---|
| usbboot keeps waiting; no USB disk | Data-capable cable, internal programming port, manual's switch position, radio power, current CM5 mass-storage payload. |
| Login rejects the password | Reflash through the CM5 manifest with Imager 2.0.10+ and username `pi`; there is no fallback password. |
| SSH refused | Wait for first boot; confirm the IP and that SSH was enabled in customization. With local keyboard/display access, `sudo systemctl enable --now ssh` enables it. |
| No `/dev/xdma*` or p2app repeatedly exits | Check the kernel and module versions above. A later kernel update needs a newly built matching XDMA module. Save the p2app log. |
| Internal touch panel does not work | This is the screenless configuration; panel-specific setup is outside this image. |

### Verify a separately downloaded image

The release includes the `.img.xz` and its `.sha256` for archival verification.
In the directory containing both files:

```bash
# macOS
shasum -a 256 -c g2-saturn-trixie64-cm5-2026-09-06.img.xz.sha256
# Linux
sha256sum -c g2-saturn-trixie64-cm5-2026-09-06.img.xz.sha256
```

On Windows PowerShell, run
`Get-FileHash .\g2-saturn-trixie64-cm5-2026-09-06.img.xz -Algorithm SHA256`
and compare the result with the `.sha256` file. Still use the manifest to
install so Imager applies the credentials correctly.

## If you are also upgrading from a CM4

Back up your files first. With the radio power disconnected, preserve the
original CM4 and its SD card unchanged as your rollback. Fit the official
Raspberry Pi CM5 and appropriate cooling according to the hardware supplier's
instructions, then follow the eMMC flashing steps above. The eMMC-equipped
CM5 does not boot from the G2's native SD slot. Module replacement is only
needed for this hardware upgrade; existing CM5 owners leave theirs installed.

## Verification scope

The matching driver runs on KB2UKA's CM5 with p2app active and zero restarts.
The new image is checked offline for the matching driver, lookup indexes,
boot assets, service, filesystem integrity and cleared identity. **A fresh
flash and first-boot acceptance test of this assembled image remains a human
bench step.** Existing-radio evidence is not a fresh-flash test.

The boot configuration retains the July image's 2 GHz and voltage settings;
this release does not tune CM5 performance. Display variants and other CM5
memory/storage variants have not been bench-tested.

## Rebuild the artifact

Use a Linux build host with root access, util-linux, kmod, xz, e2fsprogs and
Python 3. The build only writes a new regular image file, never a disk.

Inputs:

- Published July 5 `.img.xz`, SHA-256
  `41cecaace018d2680bca788c799da6035ce4b0e1e0fd65fc1a6f64ecab26bd00`.
- Verified `xdma.ko.xz` release asset, SHA-256
  `d53b7bff8afbbb2f6e06d6d12b4ebc27cdff15e04ede4022646abd21af8b89b0`.

```bash
sudo bash scripts/build-cm5-image.sh \
  g2-saturn-trixie64-clean-2026-07-05.img.xz xdma.ko.xz \
  g2-saturn-trixie64-cm5-2026-09-06.img
sudo xz -T2 -6 -k g2-saturn-trixie64-cm5-2026-09-06.img
python3 scripts/cm5-manifest.py g2-saturn-trixie64-cm5-2026-09-06.img.xz \
  rebuilt-cm5.rpi-imager-manifest
```

The script checks both input hashes and the raw image hash, installs the
module, regenerates indexes, runs the offline assertions, and checks ext4.
The metadata generator reads the actual artifact to calculate both sizes
and hashes; filesystem timestamps can cause rebuild hashes to differ.

To build XDMA from source on an ARM64 Linux build system with the matching
kernel headers and the source provided in the image:

```bash
cd /home/pi/github/Saturn/linuxdriver/xdma
make BUILDSYSTEM_DIR=/lib/modules/6.18.34+rpt-rpi-2712/build clean
make BUILDSYSTEM_DIR=/lib/modules/6.18.34+rpt-rpi-2712/build
```

The resulting `xdma.ko` may differ byte-for-byte from the pinned release
binary; validate it before selecting it for a new release. A later kernel
update also requires rebuilding this out-of-tree driver. The image does not
add DKMS or promise compatibility with future kernels.

### Repair XDMA after a kernel update

The fixed-version commands above build a module for image packaging; they do
not install it into a running radio. If an OS update has booted a new kernel
and XDMA is missing, stop any connected SDR client first. On the G2, install
headers for the **running** kernel and build and install the driver:

```bash
sudo apt install "linux-headers-$(uname -r)"
cd /home/pi/github/Saturn/linuxdriver/xdma
make clean && make && sudo make install
```

Proceed only if all commands succeed. The existing `make install` installs
the module and runs `depmod`. Then load the missing module and restart p2app:

```bash
sudo modprobe xdma
sudo systemctl restart p2app
```

Repeat the read-only checks in step 6 and test receive. If headers are
unavailable or the build fails, save the error; a new kernel may require
source changes. Do not force an old module into a different kernel. This
repair is for a missing module after a kernel change, not replacing a driver
that is already loaded and in use.
