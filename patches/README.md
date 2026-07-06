# Patches applied when building this image

This image ships GPL-licensed software that was **modified** before it was built
into the image. Under the GPL, the modified source (or the changes) must be
made available. The changes are published here.

## `xdma-kernel-6.13-build.patch`

Applies to the Saturn XDMA kernel driver
([`laurencebarker/Saturn`](https://github.com/laurencebarker/Saturn) →
`linuxdriver/xdma/Makefile`). The driver is Xilinx/AMD's `dma_ip_drivers`,
GPL-2.0 with BSD-licensed portions (see `../LICENSES/`).

**Why:** Raspberry Pi OS Trixie runs kernel 6.18. From kernel 6.13, kbuild
changed two things the stock Saturn Makefile relied on:

1. `$(src)` is no longer set the old way for out-of-tree modules, so
   `topdir := $(shell cd $(src)/.. && pwd)` resolved to the wrong directory.
   Fixed by deriving `topdir` from the Makefile's own path via
   `$(dir $(abspath $(lastword $(MAKEFILE_LIST))))/..`.
2. `EXTRA_CFLAGS` is no longer honored; replaced with `ccflags-y`.

Without both, the build fails with `libxdma_api.h: No such file or directory`.

**Modification:** made 2026-07-05 for the ANAN G2 internal CM4 Trixie image.
The driver is **not** built with DKMS, so it must be rebuilt after any kernel
upgrade.

To reproduce: clone Saturn, apply this patch from the repo root
(`git apply patches/xdma-kernel-6.13-build.patch`, or `patch -p1 <` the file),
then build `linuxdriver/xdma` against your running kernel headers.
