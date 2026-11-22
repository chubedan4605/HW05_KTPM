#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""monitor.py — Giam sat tai nguyên tien trinh backend EShop + he thong.
Cach dung: python3 monitor.py --pid <PID> --out <csv> --html <html> [--db <sqlite>] [--interval 5]
Ghi CSV moi <interval> giay: ts, elapsed_s, cpu_pct_1core, rss_mb, load1, db_mb, orders
Dong thoi sinh trang HTML tu cap nhat (tu refresh 2s) lam panel giam sat cho screenshot."""
import argparse, os, time, sqlite3, html

CLK_TCK = os.sysconf("SC_CLK_TCK")

def read_proc(pid):
    with open(f"/proc/{pid}/stat") as f:
        parts = f.read().rsplit(")", 1)[1].split()
    utime, stime = int(parts[11]), int(parts[12])  # cot 14,15 (sau comm)
    rss_pages = int(parts[21])
    return utime + stime, rss_pages * os.sysconf("SC_PAGE_SIZE")

def read_rss_mb(pid):
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024
    except FileNotFoundError:
        return None
    return None

def orders_count(db_path):
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=1)
        n = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        con.close()
        return n
    except Exception:
        return -1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pid", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--html", default=None)
    ap.add_argument("--db", default="/home/z/my-project/eshop-sut/backend/database.sqlite")
    ap.add_argument("--interval", type=float, default=5)
    ap.add_argument("--duration", type=float, default=1e9)
    args = ap.parse_args()

    rows = []
    t0 = time.time()
    cpu_prev, _ = read_proc(args.pid)
    t_prev = t0
    header = "ts,elapsed_s,cpu_pct_1core,rss_mb,load1,db_mb,orders"
    with open(args.out, "w") as f:
        f.write(header + "\n")
    while time.time() - t0 < args.duration:
        time.sleep(args.interval)
        now = time.time()
        try:
            cpu_now, _ = read_proc(args.pid)
        except FileNotFoundError:
            break
        dt = now - t_prev
        cpu_pct = (cpu_now - cpu_prev) / (dt * CLK_TCK) * 100
        cpu_prev, t_prev = cpu_now, now
        rss = read_rss_mb(args.pid)
        load1 = open("/proc/loadavg").read().split()[0]
        try:
            db_mb = os.path.getsize(args.db) / 1048576
        except FileNotFoundError:
            db_mb = -1
        orders = orders_count(args.db)
        row = [time.strftime("%H:%M:%S"), round(now - t0, 1), round(cpu_pct, 1),
               round(rss, 1), load1, round(db_mb, 3), orders]
        rows.append(row)
        with open(args.out, "a") as f:
            f.write(",".join(map(str, row)) + "\n")
        if args.html and len(rows) % 1 == 0:
            write_html(args.html, rows)

def write_html(path, rows):
    last = rows[-1] if rows else ["-", 0, 0, 0, 0, 0, 0]
    tbl = "\n".join(
        "<tr><td>%s</td><td>%.0fs</td><td>%.1f%%</td><td>%.1f</td><td>%s</td><td>%.3f</td><td>%s</td></tr>" % tuple(r)
        for r in rows[-16:])
    doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="2">
<style>
body {{ background:#0b0f14; color:#d7e0d7; font-family:'DejaVu Sans Mono',monospace; margin:0; padding:12px; }}
h1 {{ color:#7ee787; font-size:16px; margin:0 0 6px; }}
.big {{ font-size:26px; color:#7ee787; margin:2px 0 8px; }}
table {{ border-collapse:collapse; font-size:13px; width:100%; }}
th,td {{ border:1px solid #22303a; padding:3px 7px; text-align:right; }}
th {{ background:#101820; color:#9db1c9; }}
td:first-child,th:first-child {{ text-align:left; }}
.note {{ color:#8b949e; font-size:11px; margin-top:6px; }}
</style></head><body>
<h1>htop-style monitor — node server (EShop backend, PID monitored)</h1>
<div class="big">CPU {last[2]}% &nbsp;|&nbsp; RSS {last[3]} MB &nbsp;|&nbsp; load {last[4]} &nbsp;|&nbsp; DB {last[5]} MB &nbsp;|&nbsp; orders {last[6]}</div>
<table><tr><th>time</th><th>elapsed</th><th>CPU % (1 core)</th><th>RSS MB</th><th>load1</th><th>SQLite MB</th><th>orders</th></tr>
{tbl}
</table><div class="note">Sampled from /proc every 5s — live evidence panel</div>
</body></html>"""
    with open(path, "w") as f:
        f.write(doc)

if __name__ == "__main__":
    main()
