#!/usr/bin/env bash
# Validate an offline, mounted CM5 image; never load a driver or access a radio.
set -euo pipefail
root=${1:?usage: verify-cm5.sh ROOT_MOUNT BOOT_MOUNT}
boot=${2:?usage: verify-cm5.sh ROOT_MOUNT BOOT_MOUNT}
kernel=6.18.34+rpt-rpi-2712
module="$root/lib/modules/$kernel/updates/xdma.ko.xz"
test -f "$module" || { echo "FAIL: missing CM5 XDMA module for $kernel"; exit 1; }
test "$(modinfo -F vermagic "$module")" = "$kernel SMP preempt mod_unload modversions aarch64"
test "$(modinfo -F name "$module")" = xdma
modinfo -F alias "$module" | grep -q 'pci:v000010EEd00007024'
grep -q 'updates/xdma.ko.xz:' "$root/lib/modules/$kernel/modules.dep"
grep -q 'pci:v000010EEd00007024.* xdma$' "$root/lib/modules/$kernel/modules.alias"
test "$(stat -c '%u:%g:%a' "$module")" = 0:0:644
test -f "$boot/kernel_2712.img"
test -f "$boot/bcm2712-rpi-cm5-cm5io.dtb"
test -f "$boot/initramfs_2712"
test "$(readlink "$root/etc/systemd/system/multi-user.target.wants/p2app.service")" = /etc/systemd/system/p2app.service
test -f "$root/etc/systemd/system/p2app.service"
test -x "$root/home/pi/github/Saturn/sw_projects/P2_app/p2app"
test -x "$root/etc/rc.local"
test ! -s "$root/etc/machine-id"
test -z "$(find "$root/etc/ssh" -name 'ssh_host_*' -print -quit)"
test -z "$(find "$root/home" "$root/root" \( -name authorized_keys -o -name id_ed25519 -o -name id_rsa \) -type f -size +0c -print -quit)"
awk -F: '$1 == "pi" { found=1; if ($2 !~ /^[!*]/) exit 1 } END { if (!found) exit 1 }' "$root/etc/shadow"
echo 'PASS: CM5 driver, PCIe alias, boot assets, service, expansion and clean identity'
