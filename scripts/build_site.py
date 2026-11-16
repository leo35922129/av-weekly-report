#!/usr/bin/env python3
"""Render <date>/index.html from <date>/report.json + content.json, and the root index.html.
Usage: python3 scripts/build_site.py 2026-11-15"""
import json, sys, os, html, subprocess, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = sys.argv[1]
rep = json.load(open(f"{ROOT}/{D}/report.json")); c = json.load(open(f"{ROOT}/{D}/content.json"))
SRC = rep["src"]; e = html.escape

def cites(keys):
    return "".join(f' <a class="src" href="{e(SRC[k][1])}" target="_blank" rel="noopener">{e(SRC[k][0])}</a>' for k in keys or [])
def dur(n):
    p = f"{ROOT}/{D}/{n}.mp3"
    try:
        s = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]).decode())
        return f"{int(s//60)}:{int(s%60):02d}"
    except Exception: return ""
def player(n, label):
    return f'''<div class="player"><button class="play" data-a="{n}" aria-label="Play {label}">▶ Play</button>
<div class="pmeta"><b>{label}</b><span id="t-{n}">{dur(n)}</span></div>
<audio id="a-{n}" src="{n}.mp3" preload="none"></audio></div>'''
def table(t):
    h = "".join(f"<th>{e(x)}</th>" for x in t["columns"])
    rows = "".join("<tr>" + "".join(f"<td>{e(cell['t'])}{cites(cell.get('s'))}</td>" for cell in r) + "</tr>" for r in t["rows"])
    return f'<div class="tw"><table><thead><tr>{h}</tr></thead><tbody>{rows}</tbody></table></div>'

heads = "".join(f'''<article class="card"><div class="num">{i+1}</div><h3>{e(x["h"])}</h3><p>{e(x["t"])}{cites(x["s"])}</p><p class="why"><b>Why it matters:</b> {e(x["why"])}</p></article>''' for i,x in enumerate(c["headlines"]))
watch = "".join(f"<li>{e(x['t'])}{cites(x['s'])}</li>" for x in c["watch"])
deep = ""
for sec in c["deep"]:
    deep += f'<section><h2>{e(sec["h"])}</h2><ul>' + "".join(f"<li>{e(i['t'])}{cites(i['s'])}</li>" for i in sec["items"]) + "</ul></section>"
    if sec["h"].startswith("Tesla"):
        deep += f'<section><h2>Tesla vs robotaxi competitors</h2>{table(c["robotaxi_table"])}</section>'
        deep += f'<section><h2>Tesla FSD vs consumer driver-assist rivals</h2>{table(c["adas_table"])}</section>'
before = "".join(f"<li>{e(x['t'])}{cites(x['s'])}</li>" for x in c["before"])
analysis = "".join(f"<li>{e(x)}</li>" for x in c["analysis"])

page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark">
<title>{e(rep["title"])} · {e(rep["window"])}</title><link rel="stylesheet" href="../style.css"></head><body>
<header><p class="kicker">Week of {e(rep["window"])}</p><h1>{e(rep["title"])}</h1><p class="lead">{e(rep["lead"])}</p>
<nav class="tabs" role="tablist"><button class="tab on" data-v="sum">3-min summary</button><button class="tab" data-v="deep">Deep dive</button></nav></header>
<main>
<div id="v-sum" class="view">{player("summary","Listen: 3-minute summary")}
<h2>Top headlines</h2>{heads}
<h2>What to watch next week</h2><ul>{watch}</ul></div>
<div id="v-deep" class="view" hidden>{player("deep-dive","Listen: deep dive")}
{deep}
<section><h2>Just before the window</h2><ul>{before}</ul></section>
<section><h2>Analysis</h2><p class="note">Our interpretation, based on the sourced items above.</p><ul>{analysis}</ul></section></div>
</main><footer><p>Every claim links to its source. <a href="../">All weeks</a></p></footer>
<script src="../app.js"></script></body></html>'''
open(f"{ROOT}/{D}/index.html","w").write(page)

weeks = sorted([os.path.basename(p) for p in glob.glob(f"{ROOT}/20??-??-??") if os.path.exists(f"{p}/index.html")], reverse=True)
items = "".join(f'<li><a href="{w}/">Week ending {w}</a></li>' for w in weeks)
open(f"{ROOT}/index.html","w").write(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><title>Autonomy Weekly</title><link rel="stylesheet" href="style.css"></head><body>
<header><h1>Autonomy Weekly</h1><p class="lead">AV, automotive AI and software-defined vehicles, every week.</p>
<p><a class="cta" href="{weeks[0]}/">Read the latest ({weeks[0]}) →</a></p></header><main><h2>Archive</h2><ul>{items}</ul></main></body></html>''')
print("built", D, "weeks:", weeks)
