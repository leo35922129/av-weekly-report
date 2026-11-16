#!/usr/bin/env python3
"""Rebuild <out>/weeks.json from exported week folders and validate one week against REPORT_FORMAT.md."""
import json, os, re, subprocess, sys, glob
out, D = sys.argv[1], sys.argv[2]
w = f"{out}/{D}"; errs = []
def err(m): errs.append(m)
def split_script(text):  # identical to report.js splitScript
    joined = " ".join(s.strip() for s in re.split(r"\n+", text) if s.strip())
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", joined) if s.strip()] if joined else []
def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode())

allowed = {".json", ".txt", ".mp3"}
for f in os.listdir(w):
    if os.path.splitext(f)[1] not in allowed: err(f"unexpected file {f} (only .json/.txt/.mp3 are published)")
rep = json.load(open(f"{w}/report.json")); con = json.load(open(f"{w}/content.json")); cues = json.load(open(f"{w}/cues.json"))
for k in ["date", "window", "title", "lead", "src"]:
    if not rep.get(k): err(f"report.json missing {k}")
if rep.get("date") != D: err("report.json date != folder name")
for k, v in rep["src"].items():
    if not (isinstance(v, list) and len(v) == 2 and str(v[1]).startswith("http")): err(f"src {k} not [label,url]")
for k in ["headlines", "watch", "robotaxi_table", "adas_table", "deep", "before", "analysis"]:
    if k not in con: err(f"content.json missing {k}")
def chk_s(ids, where):
    for i in ids or []:
        if i not in rep["src"]: err(f"{where}: unknown source id {i}")
for k in ["headlines", "watch", "before"]:
    for n, it in enumerate(con.get(k, [])): chk_s(it.get("s"), f"{k}[{n}]")
for th in con.get("deep", []):
    for n, it in enumerate(th["items"]): chk_s(it.get("s"), f"deep {th['h']}[{n}]")
for t in ["robotaxi_table", "adas_table"]:
    for r in con[t]["rows"]:
        if len(r) != len(con[t]["columns"]): err(f"{t}: row width != columns")
        for c in r: chk_s(c.get("s") if isinstance(c, dict) else None, t)
for kind, txt, mp3 in [("summary", "summary.txt", "summary.mp3"), ("deep", "deep-dive.txt", "deep-dive.mp3")]:
    lines = split_script(open(f"{w}/{txt}").read()); cl = cues.get(kind) or []; d = dur(f"{w}/{mp3}")
    if len(cl) != len(lines): err(f"{kind}: {len(cl)} cues vs {len(lines)} player lines")
    for i, c in enumerate(cl):
        if i < len(lines) and c.get("t") != lines[i]: err(f"{kind} cue {i} text differs from player line")
        if not (0 <= c["start"] < c["end"] <= d + 0.05): err(f"{kind} cue {i} times out of range")
        if i and c["start"] < cl[i-1]["start"]: err(f"{kind} cue {i} not increasing")
    a = (rep.get("audio") or {}).get(kind)
    if a:
        if a.get("file") != mp3: err(f"audio.{kind}.file != {mp3}")
        if abs(a.get("duration_s", 0) - d) > 0.05: err(f"audio.{kind}.duration_s {a.get('duration_s')} != {d:.3f}")
    print(f"{kind}: {len(cl)} cues, mp3 {d:.3f}s, last cue ends {cl[-1]['end'] if cl else '-'}")

weeks = []
for p in sorted(glob.glob(f"{out}/20??-??-??")):
    r = json.load(open(f"{p}/report.json"))
    weeks.append({"date": os.path.basename(p), "window": r.get("window"), "title": r.get("title")})
json.dump({"weeks": weeks}, open(f"{out}/weeks.json", "w"), ensure_ascii=False, indent=2)
print("weeks.json:", [x["date"] for x in weeks])
if errs:
    print("INVALID:\n  " + "\n  ".join(errs)); sys.exit(1)
print(f"OK: {w} matches REPORT_FORMAT.md")
