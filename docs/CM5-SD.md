# Raspberry Pi CM5 Lite microSD image

This image is for an **official Raspberry Pi Compute Module 5 Lite (0 GB
eMMC) in a screenless ANAN G2**, booting from the Saturn carrier's microSD
slot. It includes Raspberry Pi OS Trixie 64 bit, Saturn p2app and XDMA for
`6.18.34+rpt-rpi-2712`.

**Check the module before choosing this download.** “Lite” means no onboard
eMMC, not less RAM. Raspberry Pi's [Compute Module documentation](https://www.raspberrypi.com/documentation/computers/compute-module.html)
explains the storage variants and SD interface. An eMMC-equipped CM5 does
not expose the native SD interface; flashing a card cannot change that.
For that module use the [CM5 eMMC image and guide](CM5.md). This SD image is
not for Radxa CM5, a standalone Pi 5 radio, or a preconfigured internal touch
panel. The original [Pi 4 / CM4 image](../README.md#install-it-pi-4--cm4-microsd)
remains available.

## Download and write the card (macOS, Windows or Linux)

1. Back up files from the old system and keep the original card as your
   rollback. Writing an image erases the selected card and does not migrate
   applications or settings. This image does not install Zeus.
2. Use a **16 GB or larger microSD card**, a card reader and
   [Raspberry Pi Imager](https://www.raspberrypi.com/software/) **2.0.10 or
   newer**. The raw image is 9,452,954,112 bytes; an 8 GB card is too small.
3. From the [CM5 SD release](https://github.com/Zeus-SDR/g2-pi-image/releases/tag/2026.09.07-cm5-sd),
   download [g2-cm5-sd-pi-image.rpi-imager-manifest](https://github.com/Zeus-SDR/g2-pi-image/releases/download/2026.09.07-cm5-sd/g2-cm5-sd-pi-image.rpi-imager-manifest).
   Keep its extension and double-click it to open Imager. Alternatively, in
   Imager use **App Options → Content Repository → Edit → Use custom file**,
   select the manifest, apply and restart Imager.
4. Choose **Raspberry Pi 5**, then **ANAN G2 Raspberry Pi CM5 Lite microSD
   image**. Imager downloads and verifies the correct image automatically.
5. In **OS Customization**, keep the username exactly **`pi`**, choose your
   own password, and enable SSH if you want remote access. Set a hostname
   and Wi-Fi if needed; Ethernet is convenient for first boot. The default
   hostname is `g2pi`. There is **no default password**.
6. Select the **microSD card in your computer's reader**. Confirm its capacity
   and identity; do not select a system disk or backup drive. Allow writing
   and verification to finish, then safely eject it.
7. With the G2 shut down normally and its power supply disconnected, insert
   the card in the Saturn carrier's microSD slot. Follow the
   [G2 manual](https://apache-labs.com/public/storage/download_file/1756364841_1023_1023_G2-manual-v1.4-2_updated.pdf)
   for physical access. Leave the normal boot switch positions in place.
   **No rpiboot, USB programming cable or eMMC programming switch change is
   needed for this SD procedure.** Reassemble the radio, connect Ethernet
   and power it normally.

Do **not** select the `.img.xz` through the OS picker's **Use custom** option.
That path omits the required `cloudinit-rpi` login customization and can leave
`pi` locked. The custom **manifest** procedure above supplies that metadata.

## First boot and receive checks

Allow several minutes for filesystem expansion, any first-boot restart and
fresh SSH host-key creation. Do not interrupt first boot. Find the chosen
hostname or assigned address in your router's DHCP list, then connect:

```bash
ssh pi@g2pi.local
```

Use its IP address if `.local` does not resolve. If SSH reports a changed
host key, verify that the address is the reflashed radio before removing
its old known-host entry. Inside the Pi, run these read-only commands:

```bash
uname -r
/sbin/modinfo -F vermagic xdma
ls /dev/xdma*
systemctl show p2app -p ActiveState -p NRestarts
findmnt -no SOURCE /
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS
df -h /
journalctl -u p2app -b --no-pager
```

Expect kernel `6.18.34+rpt-rpi-2712`, matching XDMA vermagic, XDMA device
nodes, and active p2app without repeated restarts. The root filesystem
should be on the SD card and expanded to its usable size. Refresh discovery
in your SDR client, connect and check receive and audio. Confirm normal
front-button shutdown after testing. No transmit or FPGA update is needed.

## Troubleshooting

| Symptom | Check |
|---|---|
| Card ignored or previous system boots | Verify the module is CM5 **Lite**, the card is in the carrier slot, and normal boot mode is selected. An eMMC module cannot use this native slot. If a Lite bootloader was previously customized, consult Raspberry Pi's bootloader documentation before changing it. |
| Login rejects the password | Reflash using the SD manifest, Imager 2.0.10+ and username `pi`; there is no fallback password. |
| SSH unavailable | Wait for first boot, check the IP and confirm SSH was enabled in Imager. |
| Root remains about 9 GB | Inspect first-boot logs and `lsblk`; record any expansion error. Offline checks verify the expansion setup, not a completed physical first boot. |
| No XDMA nodes or repeated p2app exits | Check kernel/module versions and save the p2app log. After a kernel update follow [the XDMA repair instructions](CM5.md#repair-xdma-after-a-kernel-update). |
| Internal display needs configuration | The release targets a screenless G2; it does not configure a touch panel. |

## Verify the download

The release supplies the `.img.xz`, its `.sha256`, the manifest and these
instructions. The manifest records both compressed and extracted sizes and
SHA-256 hashes. To verify a separately downloaded archive:

```bash
# macOS
shasum -a 256 -c g2-saturn-trixie64-cm5-sd-2026-09-07.img.xz.sha256
# Linux
sha256sum -c g2-saturn-trixie64-cm5-sd-2026-09-07.img.xz.sha256
```

On Windows PowerShell:

```powershell
Get-FileHash .\g2-saturn-trixie64-cm5-sd-2026-09-07.img.xz -Algorithm SHA256
```

Compare the result with the `.sha256` file. Still install through the manifest.

## Build and verification scope

This is a separate SD download built from the same July CM4 base and pinned
CM5 XDMA module as the eMMC edition. The only file difference from the eMMC
edition is the SD first-boot README. Storage is already selected by partition
UUID in `cmdline.txt` and `fstab`; no eMMC device path needs replacing. The
kernel, device tree, Saturn source and radio/boot defaults are retained.

On a Linux image-building host, use the dependencies and pinned inputs in
[the CM5 rebuild guide](CM5.md#rebuild-the-artifact), then run:

```bash
sudo bash scripts/build-cm5-image.sh \
  g2-saturn-trixie64-clean-2026-07-05.img.xz xdma.ko.xz \
  g2-saturn-trixie64-cm5-sd-2026-09-07.img --sd
sudo xz -T2 -6 -k g2-saturn-trixie64-cm5-sd-2026-09-07.img
python3 scripts/cm5-manifest.py --sd \
  g2-saturn-trixie64-cm5-sd-2026-09-07.img.xz \
  rebuilt-cm5-sd.rpi-imager-manifest
```

The build checks input hashes, the CM5 driver/boot assets, clean identity,
SD partition references, rootwait, expansion setup, the SD README and ext4
integrity. The metadata generator reads the full compressed image and its
extracted stream. Filesystem timestamps can change hashes on a rebuild.

**Bench-test prerelease:** fresh CM5 Lite card flashing, Imager login setup,
first boot, expansion, receive/audio and front-button acceptance remain
pending. The working CM5 eMMC driver evidence does not prove an SD boot.
The image carries the original boot voltage/frequency settings; no CM5 tuning
is included. Kernel updates still require rebuilding XDMA.

Licenses, bundled source and credits are in
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md). Packaged by KB2UKA.
