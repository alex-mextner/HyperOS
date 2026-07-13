#!/usr/bin/env bash
# Tier-1 SDK path: build components against prebuilt platform + boot emulator from prebuilts.
# Light: works on a laptop. No platform build involved.
set -euo pipefail
mkdir -p "$HOME/fuchsia-work" && cd "$HOME/fuchsia-work"
if [ ! -d fuchsia-getting-started ]; then
  git clone https://fuchsia.googlesource.com/sdk-samples/getting-started fuchsia-getting-started --recurse-submodules
fi
cd fuchsia-getting-started
scripts/bootstrap.sh
tools/ffx sdk version
tools/ffx product list || true
echo "== pick a bundle from the list, then: tools/ffx product download <URL> <dir>; tools/ffx emu start =="
