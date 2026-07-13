#!/usr/bin/env python3
# The publication renderer used for this release is intentionally simple:
# canonical IDs become flat Wiki filenames and [[ID#anchor|label]] becomes
# [label](ID.md#anchor). Re-run the release build for a complete regeneration.
from pathlib import Path
print('See docs/_meta/link-map.csv and wiki/. Canonical files remain authoritative.')
