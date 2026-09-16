#!/usr/bin/env bash
# Test real p2app code without opening sockets, hardware devices, or a transmitter.
set -euo pipefail
source_root=${1:?usage: test-p2app-status-pacing.sh UNMODIFIED_SATURN_SOURCE}
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
[[ $(uname -s) == Linux ]] || { echo 'FAIL: p2app harness requires a Linux host'; exit 1; }
command -v sha256sum >/dev/null || { echo 'FAIL: sha256sum is required'; exit 1; }
(cd "$source_root" && sha256sum --check "$repo/tests/p2app-status-pacing.sha256") || {
  echo 'FAIL: expected pinned Saturn v46 source and headers'; exit 1;
}
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT
mkdir -p "$work/sw_projects"
cp -R -- "$source_root/sw_projects/P2_app" "$source_root/sw_projects/common" "$work/sw_projects/"
src="$work/sw_projects/P2_app"
compile() {
  "${CC:-cc}" -std=gnu11 -Wall -Wextra -pthread -I "$src" \
    -Dsendmsg=test_sendmsg -Dusleep=test_usleep \
    "$src/OutHighPriority.c" "$repo/tests/p2app-status-pacing.c" -o "$work/pacing-test"
}
compile
for scenario in 0 1 2 3 4 5 6 7; do
  status=0
  "$work/pacing-test" "$scenario" 0 || status=$?
  expected_status=0
  if [[ $scenario == 1 || $scenario == 3 ]]; then expected_status=1; fi
  [[ $status == "$expected_status" ]] || { echo "FAIL: baseline scenario $scenario exit $status"; exit 1; }
  echo "BASELINE scenario=$scenario exit=$status (expected)"
done
(cd "$work" && patch --batch --fuzz=0 -p1 < "$repo/patches/p2app-status-pacing.patch")
compile
for scenario in 0 1 2 3 4 5 6 7; do
  "$work/pacing-test" "$scenario" 1 || {
    status=$?; echo "FAIL: patched scenario $scenario exit $status"; exit 1;
  }
  echo "PASS: patched scenario=$scenario"
done
