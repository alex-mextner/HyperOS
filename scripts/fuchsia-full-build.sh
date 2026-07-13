#!/usr/bin/env bash
# Tier-2 full-tree first build + emulator boot. Run on x86-64 Debian-based Linux
# (native box or VM). Needs ~250GB free disk, 16+ cores recommended, hours for the first build.
set -euo pipefail
# Full forked-tree build. SUPPORTED ONLY on x86-64 Debian-based Linux (e.g. Ubuntu).
# Ideal home target: the i7 + RTX 3060 Ubuntu laptop. Not for macOS.
if [ "$(uname -s)" != "Linux" ] || [ "$(uname -m)" != "x86_64" ]; then
  echo "ERROR: full-tree build needs x86-64 Linux (Debian/Ubuntu). Host is $(uname -s)/$(uname -m)."
  echo "Use the Ubuntu laptop for this; use scripts/fuchsia-sdk-quickstart.sh on the Mac."
  exit 1
fi
. /etc/os-release 2>/dev/null || true
case "${ID:-}${ID_LIKE:-}" in *debian*|*ubuntu*) : ;; *) echo "WARN: non-Debian distro ($PRETTY_NAME); Fuchsia officially supports Debian-based only.";; esac
echo "== prereqs: git curl unzip python3; ~200-250GB free; first build takes hours; ccache makes reruns fast =="
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
