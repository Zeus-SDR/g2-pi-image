#!/usr/bin/env bash
# Create a second image from the public CM4 image and the verified CM5 module.
# Linux host with root, util-linux, kmod, xz, e2fsprogs and Python 3 required.
set -euo pipefail
[[ $# == 3 ]] || { echo "usage: $0 BASE.img.xz XDMA.ko.xz NEW.img" >&2; exit 2; }
[[ $EUID == 0 ]] || { echo 'Run as root on a Linux image-building host.' >&2; exit 2; }
base=$(realpath "$1")
driver=$(realpath "$2")
output=$(realpath -m "$3")
repo=$(cd "$(dirname "$0")/.." && pwd)
kernel=6.18.34+rpt-rpi-2712
[[ -f $base && -f $driver && ! -e $output && ! -L $output ]] || {
    echo 'Inputs must be files; output must not exist (never pass a disk device).' >&2; exit 2;
}
printf '%s  %s\n' 41cecaace018d2680bca788c799da6035ce4b0e1e0fd65fc1a6f64ecab26bd00 "$base" | sha256sum -c -
printf '%s  %s\n' d53b7bff8afbbb2f6e06d6d12b4ebc27cdff15e04ede4022646abd21af8b89b0 "$driver" | sha256sum -c -
[[ $(modinfo -F vermagic "$driver") == "$kernel SMP preempt mod_unload modversions aarch64" ]]
scratch=$(mktemp -d)
loop=
cleanup() {
    # A failed unmount must keep the loop attached for manual recovery.
    local failed=0
    for point in boot root; do
        if mountpoint -q "$scratch/$point"; then
            umount "$scratch/$point" || failed=1
        fi
    done
    if (( failed == 0 )); then
        if [[ -n $loop ]]; then losetup -d "$loop" || return 1; fi
        rmdir "$scratch/boot" "$scratch/root" "$scratch"
    else
        echo "Unmount failed: inspect $scratch and $loop" >&2
        return 1
    fi
}
trap cleanup EXIT
mkdir "$scratch/root" "$scratch/boot"
# noclobber also protects against an output appearing after the check above.
(set -o noclobber; xz -dc "$base" > "$output")
printf '%s  %s\n' ab4a75bd93dfaaa04a204ce44ef1723be03f7d747b20f09d77bb5599dd3a30a4 "$output" | sha256sum -c -
loop=$(losetup --find --show --partscan "$output")
mount "${loop}p2" "$scratch/root"
mount "${loop}p1" "$scratch/boot"
install -D -m 0644 "$driver" "$scratch/root/lib/modules/$kernel/updates/xdma.ko.xz"
depmod -b "$scratch/root" "$kernel"
install -m 0644 "$repo/docs/CM5-FIRST-BOOT.txt" "$scratch/boot/README-FIRST.txt"
bash "$repo/tests/verify-cm5.sh" "$scratch/root" "$scratch/boot"
sync -f "$scratch/root"
sync -f "$scratch/boot"
umount "$scratch/boot"
umount "$scratch/root"
e2fsck -fn "${loop}p2"
echo "Built $output; compress with xz -T2 -6 -k and generate the Imager metadata."
