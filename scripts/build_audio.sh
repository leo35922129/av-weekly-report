#!/usr/bin/env bash
# Usage: scripts/build_audio.sh YYYY-MM-DD
# Narrates <date>/summary.txt and <date>/deep-dive.txt with edge-tts (WordBoundary events captured),
# writes summary.mp3 / deep-dive.mp3, per-line cues in <date>/cues.json (Happy Truck format:
# {"summary":[{t,start,end}], "deep":[...]}), and fills report.json "audio" {file,duration_s,label,title}.
set -euo pipefail
D="${1:?date folder, e.g. 2026-11-15}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VOICE="${VOICE:-en-US-GuyNeural}"; RATE="${RATE:--4%}"
PY=/home/box/tts-venv/bin/python
[ -x "$PY" ] || python3 -m venv /home/box/tts-venv
"$PY" -c "import edge_tts" 2>/dev/null || /home/box/tts-venv/bin/pip install -q edge-tts
W="$ROOT/$D"
"$PY" "$ROOT/scripts/tts_cues.py" "$W/summary.txt" "$W/summary.mp3" "$W/.summary.cues.json" "$VOICE" "$RATE"
"$PY" "$ROOT/scripts/tts_cues.py" "$W/deep-dive.txt" "$W/deep-dive.mp3" "$W/.deep.cues.json" "$VOICE" "$RATE"
python3 - "$W" <<'PY'
import json, subprocess, sys, os
w = sys.argv[1]
def dur(f): return round(float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode()), 3)
cues = {"summary": json.load(open(f"{w}/.summary.cues.json")), "deep": json.load(open(f"{w}/.deep.cues.json"))}
rep = json.load(open(f"{w}/report.json")); rep.setdefault("audio", {})
for kind, f, title in [("summary","summary.mp3","3-min summary"), ("deep","deep-dive.mp3","10-min deep dive")]:
    d = dur(f"{w}/{f}"); c = cues[kind]
    c[-1]["end"] = d  # last cue runs to the end of the file
    assert all(0 <= x["start"] < x["end"] <= d + 0.01 for x in c), kind
    rep["audio"][kind] = {"file": f, "duration_s": d, "label": f"{int(d//60)}:{int(d%60):02d}", "title": title}
    print(f"{f}: {d}s, {len(c)} cues")
json.dump(cues, open(f"{w}/cues.json","w"), ensure_ascii=False, indent=1)
json.dump(rep, open(f"{w}/report.json","w"), ensure_ascii=False, indent=1)
for x in (".summary.cues.json", ".deep.cues.json"): os.remove(f"{w}/{x}")
PY
