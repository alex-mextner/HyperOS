#!/usr/bin/env bash
# Tier-2 full-tree first build + emulator boot. Run on x86-64 Debian-based Linux
# (native box or VM). Needs ~250GB free disk, 16+ cores recommended, hours for the first build.
set -euo pipefail
echo "== prereqs: git curl unzip python3; ~250GB free; this WILL take hours on first run =="
df -h . && nproc
mkdir -p "$HOME/fuchsia-work" && cd "$HOME/fuchsia-work"
if [ ! -d fuchsia ]; then
  curl -s "https://fuchsia.googlesource.com/fuchsia/+/HEAD/scripts/bootstrap?format=TEXT" | base64 --decode | bash
fi
cd fuchsia
export CCACHE_DIR="${CCACHE_DIR:-$HOME/.ccache}"; mkdir -p "$CCACHE_DIR"
time scripts/fx set minimal.x64 --release
time scripts/fx build            # record this number as evidence (first build)
echo "== incremental probe: touch one file and rebuild, record the time =="
time scripts/fx build            # no-op build time (graph health)
echo "== boot the emulator =="
scripts/fx ffx emu start --headless
