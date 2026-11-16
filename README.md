# Autonomy Weekly (AV, automotive AI & SDV)

Each week lives in a `YYYY-MM-DD/` folder named for the week-ending date:
- `report.json`: date, window, title, lead, `src` (id → [label, url]) and `audio` {file, duration_s, label, title}
- `content.json`: headlines, watch, robotaxi_table, adas_table, deep, before, analysis. Items carry company `tags`; the first cell of each table row carries `operator_id`.
- `summary.txt` / `deep-dive.txt`: the narration scripts. Write sentences that end in `. ? !` and avoid
  abbreviations with internal periods ("a.m.", "U.S.", "Dr."), because the tracker splits lines on `.?!` followed by whitespace.
- generated: `summary.mp3`, `deep-dive.mp3`, `cues.json` (per-line cue times), `index.html` (standalone site)

Happy Truck tracker format: /home/box/tesla-tracker/REPORT_FORMAT.md (read-only for us; CDO publishes).

## Weekly steps
1. `cp -r 2026-11-15 2026-11-22`, then rewrite report.json (drop the old `audio` block), content.json,
   summary.txt and deep-dive.txt, and delete the copied mp3/cues/index.html.
2. `scripts/build_audio.sh 2026-11-22`: edge-tts (voice en-US-GuyNeural, rate -4%; override with VOICE= / RATE=).
   Writes both mp3s, `cues.json` from WordBoundary timings aligned to the tracker's line split, and report.json `audio`.
3. `python3 scripts/build_site.py 2026-11-22`: standalone HTML site (optional).
4. `scripts/export_tracker.sh 2026-11-22`: copies the week to `tracker-export/2026-11-22/`, rebuilds
   `tracker-export/weeks.json` (oldest first) and validates the result against REPORT_FORMAT.md. Any mismatch makes it exit non-zero.
5. Message CDO with the export path so they can copy it into `site/report/` and publish.
   (`scripts/publish.sh` publishes the standalone GitHub Pages site. Only run it with Lei's explicit approval.)
