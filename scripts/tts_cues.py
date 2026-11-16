#!/usr/bin/env python3
r"""Narrate one script with edge-tts and emit per-line cue times that match the
Happy Truck player's line split (site/report.js splitScript):
  join non-empty lines with spaces, then split on /(?<=[.!?])\s+/.
Usage: tts_cues.py <script.txt> <out.mp3> <out.cues.json> [voice] [rate]
Cue times come from edge-tts WordBoundary events (offsets in 100-ns ticks)."""
import asyncio, json, re, sys
import edge_tts

def split_script(text):
    joined = " ".join(s.strip() for s in re.split(r"\n+", text) if s.strip())
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", joined) if s.strip()] if joined else []

def norm(s):
    return re.sub(r"[^0-9a-z]", "", s.lower())

async def main(txt, mp3, out, voice, rate):
    text = open(txt, encoding="utf-8").read()
    lines = split_script(text)
    words = []
    comm = edge_tts.Communicate(" ".join(lines), voice, rate=rate, boundary="WordBoundary")
    with open(mp3, "wb") as f:
        async for ch in comm.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append((ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]))
    # Character stream of the script (alnum only) with line start positions.
    stream, starts = "", []
    for ln in lines:
        starts.append(len(stream)); stream += norm(ln)
    # Place each spoken word in the stream, scanning forward.
    pos, placed = 0, []
    for st, en, w in words:
        n = norm(w)
        if not n:
            continue
        i = stream.find(n, pos)
        if i < 0 or i - pos > 200:   # not found nearby (e.g. TTS normalised text): skip
            continue
        placed.append((i, st, en)); pos = i + len(n)
    cues = []
    for k, ln in enumerate(lines):
        s0 = starts[k]; s1 = starts[k + 1] if k + 1 < len(lines) else len(stream)
        inl = [p for p in placed if s0 <= p[0] < s1]
        if not inl:
            raise SystemExit(f"no word timing for line {k}: {ln!r}")
        cues.append({"t": ln, "start": round(inl[0][1], 3), "end": round(inl[-1][2], 3)})
    # Make cues contiguous: each cue ends where the next starts (pauses belong to the earlier line).
    for k in range(len(cues) - 1):
        cues[k]["end"] = cues[k + 1]["start"]
    cues[0]["start"] = 0.0
    json.dump(cues, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{mp3}: {len(lines)} lines, {len(placed)}/{len(words)} words placed, last word ends {words[-1][1]:.2f}s")

if __name__ == "__main__":
    a = sys.argv
    asyncio.run(main(a[1], a[2], a[3], a[4] if len(a) > 4 else "en-US-GuyNeural", a[5] if len(a) > 5 else "-4%"))
