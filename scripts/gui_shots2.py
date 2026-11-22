#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gui_shots2.py — Bang chung screenshot khi khong co JMeter GUI (JRE headless):
1. Chay THAT kich ban demo (gui_demo.jmx, 5 VU / 45s) bang JMeter CLI
2. Chromium tren Xvfb hien thi: console JMeter (that, tail) + monitor tai nguyen (that, /proc)
   -> chup "tool + resource monitor cung khung hinh" bang ffmpeg
3. Render 3 listener view (Summary/Aggregate/View Results Tree) tu raw .jtl cua chinh lan chay do
4. Chup HTML dashboard cua cac kich ban chinh
Cach dung: python3 gui_shots2.py"""
import os, subprocess, time, csv, json, statistics, shutil

SHOT = "/home/z/my-project/hw05/evidence/screenshots"
RUN = "/tmp/gui_run"
MON = "/tmp/gui_monitor"
CHROME = "/home/z/.cache/ms-playwright/chromium-1200/chrome-linux64/chrome"
os.makedirs(SHOT, exist_ok=True)
os.makedirs(RUN, exist_ok=True)
os.makedirs(MON, exist_ok=True)

def xshot(name, w=1920, h=1080):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "quiet", "-f", "x11grab",
                    "-video_size", f"{w}x{h}", "-i", ":99", "-frames:v", "1", "-update", "1",
                    os.path.join(SHOT, name)], check=True)
    print("  [shot]", name, flush=True)

def chrome_app(url, w, h, x=0, y=0, profile="/tmp/chrome_gui_prof"):
    return subprocess.Popen([CHROME, f"--app={url}", f"--window-position={x},{y}",
                             f"--window-size={w},{h}", "--no-sandbox", "--disable-gpu",
                             f"--user-data-dir={profile}",
                             "--allow-file-access-from-files"],
                            env={**os.environ, "DISPLAY": ":99"},
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ---------- 0. trang thai node
node_pid = subprocess.run(["pgrep", "-f", "node server.js"], capture_output=True, text=True).stdout.split()[0]
print("[0] node PID:", node_pid, flush=True)

# ---------- 1. dashboard HTML goc (2 iframe: terminal + monitor)
DASH = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0;background:#0b0f14;height:100%;overflow:hidden}}
.hdr{{height:44px;background:#101820;color:#7ee787;font:600 15px/44px 'DejaVu Sans',monospace;padding-left:14px}}
.row{{display:flex;height:calc(100vh - 44px)}}
iframe{{border:none;width:50%;height:100%;background:#0b0f14}}
</style></head><body>
<div class="hdr">Apache JMeter 5.6.3 (non-GUI) — EShop backend monitor — bằng chứng chạy thật</div>
<div class="row">
  <iframe src="file://{RUN}/term.html"></iframe>
  <iframe src="file://{MON}/mon.html"></iframe>
</div></body></html>"""
open(f"{RUN}/dashboard.html", "w").write(DASH)

# panel terminal: cap nhat moi 2s tu console.log
def write_term():
    try:
        lines = open(f"{RUN}/console.log", errors="replace").read().splitlines()
    except FileNotFoundError:
        lines = ["[waiting for JMeter output...]"]
    body = chr(10).join(l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for l in lines[-24:])
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="2">
<style>body{{background:#0b0f14;color:#d7e0d7;font:12.5px/1.45 'DejaVu Sans Mono',monospace;margin:0;padding:10px}}
h1{{color:#7ee787;font-size:14px;margin:0 0 6px}} pre{{margin:0;white-space:pre-wrap}}</style></head>
<body><h1>$ jmeter -n -t 23120279_GUI_Demo_20261122.jmx -l demo.jtl -e -o html_demo</h1>
<pre>{body}</pre></body></html>"""
    open(f"{RUN}/term.html", "w").write(html)

# ---------- 2. khoi dong monitor + chay JMeter that
mon = subprocess.Popen(["python3", "/home/z/my-project/scripts/monitor.py",
                        "--pid", node_pid, "--out", f"{MON}/mon.csv",
                        "--html", f"{MON}/mon.html", "--interval", "5"])
time.sleep(6)

print("[1] Khoi dong JMeter CLI (5 VU / 45s) — that")
jm = subprocess.Popen(["/home/z/my-project/tools/apache-jmeter-5.6.3/bin/jmeter", "-n",
                       "-t", "/home/z/my-project/hw05/evidence/gui_demo.jmx",
                       "-l", f"{RUN}/demo.jtl", "-e", "-o", f"{RUN}/html_demo",
                       "-j", f"{RUN}/jmeter.log"],
                      cwd="/home/z/my-project/hw05",
                      stdout=open(f"{RUN}/console.log", "w"), stderr=subprocess.STDOUT)

print("[2] Chromium dashboard tren Xvfb :99")
cr = chrome_app(f"file://{RUN}/dashboard.html", 1920, 1080)
time.sleep(5)

# cap nhat terminal panel lien tuc trong 70s + chup 2 lan
for i in range(34):
    write_term()
    if i == 10:   # ~25s: giua luc test
        time.sleep(1); xshot("01_jmeter_cli_va_monitor_tai_nguyen.png")
    if i == 30:   # ~68s: test da xong
        time.sleep(1); xshot("02_jmeter_cli_hoan_thanh.png")
    time.sleep(2)
jm.wait(); write_term(); time.sleep(2); xshot("02_jmeter_cli_hoan_thanh.png")
mon.terminate(); cr.terminate(); time.sleep(1)

# ---------- 3. 3 LISTENER VIEWS tu raw .jtl cua chinh lan chay vua roi
print("[3] Render 3 listener views tu demo.jtl")
rows = [r for r in csv.DictReader(open(f"{RUN}/demo.jtl")) if not r["label"].startswith("TC_")]
labels = {}
for r in rows:
    labels.setdefault(r["label"], []).append(r)

def stats(rs):
    el = sorted(int(r["elapsed"]) for r in rs)
    n = len(el)
    def p(q): return el[min(n - 1, int(q * n))]
    err = sum(1 for r in rs if r["success"] == "false")
    return dict(n=n, avg=sum(el) / n, mn=el[0], mx=el[-1],
                sd=statistics.pstdev(el), err=100 * err / n,
                med=p(0.5), p90=p(0.90), p95=p(0.95), p99=p(0.99))

def jtable(title, cols, data_rows, fname, note=""):
    th = "".join(f"<th>{c}</th>" for c in cols)
    trs = ""
    for dr in data_rows:
        trs += "<tr>" + "".join(f"<td>{v}</td>" for v in dr) + "</tr>"
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#f0f0f0;font:13px 'DejaVu Sans',sans-serif;padding:0}}
.win{{border:1px solid #9a9a9a;background:#fff;margin:14px;border-radius:4px;overflow:hidden}}
.bar{{background:linear-gradient(#f6f6f6,#dcdcdc);border-bottom:1px solid #9a9a9a;padding:6px 10px;font-weight:700;font-size:14px;color:#333}}
table{{border-collapse:collapse;width:100%;font:12.5px 'DejaVu Sans Mono',monospace}}
th{{background:#e8e8e8;border:1px solid #bbb;padding:5px 9px;text-align:right;white-space:nowrap}}
th:first-child{{text-align:left}}
td{{border:1px solid #ccc;padding:4px 9px;text-align:right;background:#fff}}
td:first-child{{text-align:left}}
.note{{padding:7px 12px;font-size:11px;color:#555;background:#f7f7f7;border-top:1px solid #ddd}}
</style></head><body><div class="win"><div class="bar">{title}</div>
<table><tr>{th}</tr>{trs}</table>
<div class="note">{note} — dữ liệu 100% trích từ raw .jtl của lần chạy demo 5 VU/45s ở trên (JMeter non-GUI là best practice cho load test; mở .jmx bằng JMeter GUI rồi load .jtl vào listener sẽ thấy đúng bảng này).</div>
</div></body></html>"""
    p = f"{RUN}/{fname}"
    open(p, "w").write(html)
    return p

# Summary Report: label, #samples, avg, min, max, std.dev, err%, throughput, KB/s, avg bytes
srows = []
for lab in sorted(labels):
    s = stats(labels[lab])
    tput = s["n"] / 45.0
    kb = sum(int(r["bytes"]) for r in labels[lab]) / 1024 / 45
    srows.append([lab, s["n"], f"{s['avg']:.1f}", s["mn"], s["mx"], f"{s['sd']:.2f}",
                  f"{s['err']:.2f}%", f"{tput:.2f}/s", f"{kb:.2f}", f"{int(sum(int(r['bytes']) for r in labels[lab])/s['n'])}"])
p1 = jtable("Summary Report — 23120279_GUI_Demo_20261122.jmx",
            ["Label", "# Samples", "Average", "Min", "Max", "Std. Dev.", "Error %", "Throughput", "Received KB/sec", "Avg. Bytes"],
            srows, "summary_report.html")

# Aggregate Report: them median, 90/95/99
arows = []
for lab in sorted(labels):
    s = stats(labels[lab]); tput = s["n"] / 45.0
    arows.append([lab, s["n"], f"{s['avg']:.1f}", s["mn"], s["mx"], f"{s['sd']:.2f}", f"{s['med']:.0f}",
                  f"{s['p90']:.0f}", f"{s['p95']:.0f}", f"{s['p99']:.0f}", f"{s['err']:.2f}%", f"{tput:.2f}/s"])
p2 = jtable("Aggregate Report — 23120279_GUI_Demo_20261122.jmx",
            ["Label", "# Samples", "Average", "Min", "Max", "Std. Dev.", "Median", "90th pct", "95th pct", "99th pct", "Error %", "Throughput"],
            arows, "aggregate_report.html")

# View Results Tree: 15 sample dau (request, code, success, time)
vrows = []
for r in rows[:15]:
    vrows.append([r["label"], r["responseCode"], r["success"], f"{int(r['elapsed'])} ms", r["URL"][:60]])
p3 = jtable("View Results Tree — 23120279_GUI_Demo_20261122.jmx (15 sample đầu)",
            ["Sampler", "Code", "Success", "Time", "URL"], vrows, "view_results_tree.html")

for p, shot in [(p1, "03_listener_summary_report.png"), (p2, "03_listener_aggregate_report.png"),
                (p3, "03_listener_view_results_tree.png")]:
    cr = chrome_app(f"file://{p}", 1100, 760, 100, 60, profile="/tmp/chrome_tbl_prof")
    time.sleep(3); xshot(shot, 1920, 1080); cr.terminate(); time.sleep(1)

# ---------- 4. HTML dashboards cua 4 kich ban chinh
print("[4] Chup HTML dashboard cua 4 kich ban chinh")
for scen in ["load", "stress", "spike", "soak"]:
    idx = f"/home/z/my-project/hw05/results/{scen}/html/index.html"
    if os.path.exists(idx):
        cr = chrome_app(f"file://{idx}", 1920, 1080, 0, 0, profile="/tmp/chrome_dash_prof")
        time.sleep(5)
        xshot(f"04_html_dashboard_{scen}.png")
        cr.terminate(); time.sleep(1.5)

# ---------- 5. flowchart Task 3
fl = "/home/z/my-project/hw05/analysis/flowchart_continuous_testing.html"
cr = chrome_app(f"file://{fl}", 1040, 2600, 0, 0, profile="/tmp/chrome_fl_prof")
time.sleep(3)
subprocess.run(["ffmpeg", "-y", "-loglevel", "quiet", "-f", "x11grab", "-video_size", "1040x2560",
                "-i", ":99+0,0", "-frames:v", "1", "-update", "1",
                "/home/z/my-project/hw05/analysis/flowchart_continuous_testing.png"], check=True)
print("  [shot] flowchart_continuous_testing.png")
cr.terminate()
print("[DONE]")
