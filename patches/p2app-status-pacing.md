# Bound repeated ADC-overload status traffic

Review candidate for Saturn p2app v46 at upstream commit
`4b0b76f345961cfeeb447abc6d8b0373f5743245`. This patch is not included in
any published image or update manifest yet. It changes the Raspberry Pi
application, not FPGA gateware, Zeus, or PureSignal settings.

`OutHighPriority.c` normally waits 1 ms in TX or 200 ms in RX, polling every
500 microseconds for changes. An ADC-overload report exits that wait before
any sleep. Continuous overload therefore creates an unpaced status-send loop.
A G2 capture measured approximately 24,000–28,000 status datagrams per second.

The patch moves the existing 500-microsecond sleep before the overload check.
Normal TX/RX pacing is unchanged. Repeated overload incurs one polling delay
per report (about 2,000 reports/second maximum absent interrupted sleeps).
This remains twice the nominal TX status rate (1,000/s) and 400 times the
nominal RX status rate (5/s). PTT/key changes retain their immediate exit before that delay. Overload flags
and ADC peaks remain accumulated until the next packet; no report fields,
attenuation values, transmit controls, or calibration settings change.

A newly detected overload may be reported up to one polling interval later.
This is a traffic bound, not a cure for ADC clipping or an assurance against
all network loss. It does not eliminate IP fragmentation or alter host
fragment-reassembly limits. The same G2 sender behavior affects any client OS;
the incident's total reassembly starvation was reproduced on Linux only.

## Reproduce the regression

Use a separate unmodified Saturn checkout of the pinned revision. The test
verifies hashes of the status source and all its local headers and copies sources into a temporary directory;
it does not edit that checkout. A C compiler, pthread headers, `patch`, and
`sha256sum` are required on a Linux development/test host.

```bash
git clone https://github.com/laurencebarker/Saturn.git /tmp/saturn-pacing-source
git -C /tmp/saturn-pacing-source checkout --detach 4b0b76f345961cfeeb447abc6d8b0373f5743245
bash tests/test-p2app-status-pacing.sh /tmp/saturn-pacing-source
```

The harness compiles the actual outgoing status loop with simulated hardware
reads, sends, and sleeps. Baseline continuous-overload cases must fail; all
patched cases must pass. Cases cover TX/RX without overload, sustained overload
in both states, urgent PTT transitions with/without overload, and retaining a
transient overload plus its peak value in both TX and RX, return to normal
pacing after that transient, and sustained-overload peaks after the first packet. No RF or socket I/O occurs.

## Build a candidate

From a separate Saturn source checkout at the revision above:

```bash
git apply /path/to/g2-pi-image/patches/p2app-status-pacing.patch
make -C sw_projects/P2_app -j2
```

Use the G2's matching Debian/architecture and libgpiod ABI. Building does not
install or start the binary. Record the clean source revision, the applied
source diff and its SHA256, and the candidate binary's SHA256 together. Check
that the diff is exactly the reviewed pacing change. After an approved
installation and service restart, hash `/proc/<pid>/exe` for the active p2app
process and compare it with that binary record; the installed pathname alone
does not establish which binary is running.

## Incident-matched live trial

This trial addresses the recorded Linux disconnect, not all client platforms.
Use the original Linux laptop, kernel, office Wi-Fi/VPN path, Zeus comparison
build and preferences from the failing 768 kHz baseline. Record the kernel,
Zeus revision, interface MTUs and `net.ipv4.ipfrag_high_thresh`, `ipfrag_time`
and `ipfrag_max_dist` before/after; keep them unchanged. Preserve the failing
baseline capture/logs and record any changed conditions. A different host or
changed baseline makes an incident-cure comparison inconclusive, even if the
radio-side pacing check passes. The recorded host used a 4 MiB fragment limit,
30-second timeout and distance 64; the comparison executable was Zeus 2.0.25.

The operator engages PS and manually transmits FT8 at 768 kHz with unchanged
drive and feedback settings. Automation never keys the transmitter. Any
radio disconnect, RX-silence recovery, or IQ starvation **anywhere in the
entire run** fails the connection check, including cycles/windows excluded
from rate analysis. Never discard a failed cycle and then select three clean
ones. Missing evidence is inconclusive, not a pass.

Before the operator keys, confirm the radio interface, actual client reply
address (including any NAT/VPN translation), negotiated ports, and an available
tcpdump or equivalent PCAP collector. Verify a non-empty RX-only capture of
status and idle host-MOX control packets. Do not proceed with an empty or
unverified capture. The incident used eth0 and default ports 1025/1027.

Capture status and host-MOX control on the radio with the **same capture clock**,
kernel filtering and a 192-byte snapshot length. This retains the full status
payload and the MOX field in the initial fragment of a host control packet.
Substitute the verified interface, ports and client address in this example:

```bash
sudo tcpdump -i eth0 -s 192 -B 8192 -w status.pcap \
  '(udp src port 1025 and dst host CLIENT_IP) or (udp dst port 1027 and src host CLIENT_IP)'
```

Save capture-drop statistics. Record host MOX start/end from the client-to-radio
high-priority control stream (destination port 1027, payload offset 4 bit 1,
mask `0x02`) in that same capture. Do not use unaligned laptop log timestamps
for these boundaries. Status offset 4 is hardware PTT/key input, not host MOX.
Only radio-to-client status packets count toward status-rate/sequence checks. Keep a separate IQ/host-counter record; do not transfer
the packet capture over the tested VPN during TX.

All status offsets are zero-based UDP payload offsets: sequence at 0–3
(big-endian unsigned 32-bit, wrapping modulo 2^32), PTT/key inputs at 4,
ADC-overload flags at 5. Apply these rules:

- Evaluate the upper rate bound over sliding half-open one-second intervals
  wholly inside host MOX TX, anchored at every captured status packet. Exclude
  intervals with hardware PTT/key transitions, which retain immediate reporting.
  At most 2,100 packets may occur in any such interval (2,000/s plus 5%
  measurement tolerance). Any observed excess fails the pacing check, even
  when capture loss also occurred. Do not excuse excess as possible EINTR.
- In sequence-ordered samples, a modulo sequence span plus one is a lower bound
  on sends between the first and last samples. A send-count lower bound above 2,100
  (span >= 2,100) within less than one second fails even with gaps. Ambiguous resets, duplicates,
  reordering or capture drops prevent a positive rate pass; they never erase
  an already observed failure.
- For positive overload evidence, each of three cycles must also contain two
  adjacent complete UTC-aligned one-second windows wholly inside TX, with no
  hardware PTT/key transitions, no capture discontinuities, and overload flags
  set in every status packet. Require more than 1,100 packets in each window
  as well as the upper bound: this exceeds the pinned loop's nominal TX
  ceiling (two 500-us sleeps per report) and avoids counting build-read-only
  or second-poll overload as proof of the fast overload path. Save the normal
  no-overload TX reference rate for comparison (about 866/s in this incident).
- No-overload or otherwise inconclusive cycles do not count toward those three
  evidence cycles, but **their connection failures still fail the whole run**.
  Repeat only at the operator's unchanged settings; do not increase drive or
  reduce attenuation to force overload. If suitable overload does not recur,
  leave the pacing comparison inconclusive.
- Record radio IQ packet counts, client IQ-receive counters, and host
  `ReasmReqds`, `ReasmOKs`, `ReasmFails` plus fragment memory every second.
  For every DDC the radio is actively emitting, require that stream's client
  receive counter to advance in each full second. A stall in **any** such DDC
  fails independently of other streams. Also require `ReasmOKs` to advance
  every full second while fragmented IQ is emitted; a stall in that counter
  independently fails. Aggregate or cached positive rates alone are insufficient. Over each complete TX/RX
  cycle require `delta(ReasmFails) / delta(ReasmReqds) <= 0.001`, with a positive
  denominator. This is a trial limit on failure events per fragment request,
  **not a packet-loss estimate or a universal Wi-Fi standard**. The earlier
  PS-off reference was approximately 0.00021. Unexpected unrelated fragmented
  traffic or missing counter samples makes attribution inconclusive.

A live pass requires all three overload-evidence cycles, the rate checks, and
connection/continuity checks for **every** cycle in the run. Report actual
counts, rates, counter deltas, fragment-memory peaks and all excluded intervals;
reduced status traffic alone does not establish an incident cure. The separate
hardware-free regression remains the direct proof that the sender loop is paced.

Preserve the installed binary and source before any trial; restore both if the
trial is rejected. Do not infer a successful live trial from the unit test.

Upstream Saturn source is GPL-3.0; see `LICENSES/GPL-3.0.txt`. Patch prepared
by KB2UKA, 2026-09-16.
