#!/usr/bin/env bash
# Usage: scripts/export_tracker.sh YYYY-MM-DD
# Writes a Happy Truck "Weekly Report" week folder (format: /home/box/tesla-tracker/REPORT_FORMAT.md)
# to tracker-export/<date>/ and rebuilds tracker-export/weeks.json (oldest first) from every exported week.
# Only writes inside /home/box/av-weekly-report/tracker-export/. Never touches the tracker repo.
set -euo pipefail
D="${1:?date folder, e.g. 2026-11-15}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/$D"; OUT="$ROOT/tracker-export"; DST="$OUT/$D"
FILES=(report.json content.json summary.txt deep-dive.txt summary.mp3 deep-dive.mp3 cues.json)
for f in "${FILES[@]}"; do [ -f "$SRC/$f" ] || { echo "missing $SRC/$f (run scripts/build_audio.sh $D first)"; exit 1; }; done
rm -rf "$DST"; mkdir -p "$DST"
for f in "${FILES[@]}"; do cp "$SRC/$f" "$DST/$f"; done
python3 "$ROOT/scripts/validate_tracker.py" "$OUT" "$D"
