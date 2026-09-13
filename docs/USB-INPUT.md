# CM5 USB keyboard and mouse recovery

The **September 7 CM5 Lite SD** and **September 6 CM5 eMMC** downloads have
an image configuration defect: `config.txt` enables the USB host controller
only inside `[cm4]`. That section does not apply on CM5. Both images already
contain USB HID, generic HID, evdev, mouse input and DWC2 drivers, plus the
Libinput desktop packages and Logitech receiver modules. Installing more
keyboard packages does not enable the missing USB host controller.

The July 5 CM4 image has its own `otg_mode=1` setting and is not affected by
this CM5 configuration omission. This audit does not prove every keyboard
model works, or diagnose Bluetooth pairing or a particular operator's hardware.

The builder now adds a CM5-specific host overlay and verifies input support.
The **September 13 CM5 SD and eMMC downloads include the correction**.
Cards flashed from the older downloads above still require the repair below
or a reflash with the new image. The CM4 download is unchanged.

## Repair an existing CM5 Lite SD card

1. Shut the G2 down normally yourself, disconnect its supply, and remove the
   microSD card. Keep a backup of the card and its `config.txt` before editing.
2. Insert the card in a computer. Open `config.txt` on its FAT boot partition
   (`bootfs`) with a plain-text editor. Windows and macOS can edit this
   partition without reading the Linux root partition. **Cancel any Windows
   prompt to format a drive**. Windows cannot read the Linux root partition;
   do not format it. This also applies when exposing eMMC below. Make sure the editor
   saves `config.txt`, not `config.txt.txt`.
3. Append this block at the **end** of the file, once:

   ```ini
   [cm5]
   # Enable the USB 2 host on the Saturn carrier.
   dtoverlay=dwc2,dr_mode=host
   [all]
   ```

4. Save, safely eject, reinstall the card and power up the G2 yourself.
   Try a known-working wired USB keyboard and mouse on the normal peripheral
   ports. The internal USB programming connection is not a keyboard port.

This edit preserves the password and installed applications. No reflash,
new driver package, FPGA update or radio transmit test is needed.

For a reachable CM5 over SSH, the same file is `/boot/firmware/config.txt`:
back it up, edit it with `sudo nano /boot/firmware/config.txt`, and append the
same block once. The human operator then performs a normal restart when safe.
This also repairs the CM5 eMMC edition. If eMMC has no SSH access, use the
[eMMC access guide](CM5.md) to expose its boot partition and edit that file;
you do not need to erase or reimage it.

## Verify and separate input from login problems

Over SSH, collect these read-only checks after the operator has restarted:

```bash
tr -d '\0' < /proc/device-tree/model
uname -r
lsusb -t
cat /proc/bus/input/devices
sudo journalctl -k -b --no-pager | grep -Ei 'usb|dwc2|hid|input|under.voltage'
systemctl show p2app -p ActiveState -p NRestarts
grep -i dwc /proc/interrupts
```

Look for a USB host bus, the keyboard/mouse or receiver binding to `usbhid`,
and keyboard/mouse entries in `/proc/bus/input/devices`. For desktop-only
failures, `sudo libinput list-devices` checks whether Libinput sees them.
Save the output together with the keyboard model, connection type and image
release if input still fails. Do not type or capture passwords in diagnostics.
A built-in driver does not appear in `lsmod`; its absence there is not proof
that the driver is missing.

At a text console, passwords normally produce **no visible characters or
asterisks**. Check typing at the username prompt first. If typing works but
login rejects the password, follow the [Imager customization instructions](../README.md#set-your-own-login);
the image has no default password. A wireless USB receiver uses the USB path;
a Bluetooth keyboard additionally requires pairing and is a separate check.

For acceptance on **both CM5 Lite SD and CM5 eMMC**, leave the USB keyboard
and mouse attached while checking receive/audio. Confirm p2app stays active
without an increasing restart count. Capture the p2app status and DWC2
interrupt counts twice, about 30 seconds apart, with the other diagnostics.
This checks radio operation alongside the newly enabled USB host. No transmit
test is needed.

## Evidence and scope

All three published compressed images and extracted images were downloaded
and matched against their manifests' SHA-256 values on September 13, 2026.
The two CM5 images failed `tests/verify-cm-input.py` for missing USB host
configuration; CM4 passed. Their kernel configs enable `CONFIG_USB_HID`,
`CONFIG_HID_GENERIC`, `CONFIG_INPUT_EVDEV`, `CONFIG_INPUT_MOUSEDEV` and
`CONFIG_USB_DWC2` as built-ins. Offline module lookup also resolves the
Logitech DJ and HID++ receiver drivers for both kernels.

The required CM5 USB 2 setting is documented in the
[Raspberry Pi CM5 datasheet, section 2.4.2](https://datasheets.raspberrypi.com/cm5/cm5-datasheet.pdf).
The CM4-specific setting is described in Raspberry Pi's
[`otg_mode` documentation](https://www.raspberrypi.com/documentation/computers/config_txt.html#otg_mode-raspberry-pi-4-only).

Physical keyboard/mouse enumeration, typing and receive checks on freshly
flashed CM5 Lite SD and CM5 eMMC remain human bench checks. Offline checks establish the configuration
and driver contents; they cannot prove a physical USB connection works.
