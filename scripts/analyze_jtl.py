#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""analyze_jtl.py — Phan tich raw .jtl cua JMeter cho HW05.
Cho moi kich ban: thong ke theo label (giong Aggregate Report), time-series 10s,
phan tich theo bac thang (Stress), tim breaking point va endurance threshold.
Xuat: analysis/summary_<name>.json + in bang console."""
import csv, json, sys, os
from collections import defaultdict

def pct(sorted_vals, p):
    if not sorted_vals: return 0
    k = (len(sorted_vals) - 1) * p / 100.0
    f = int(k); c = min(f + 1, len(sorted_vals) - 1)
    if f == c: return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)

def analyze(path, name):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("label") == "": continue
            rows.append({
                "ts": int(r["timeStamp"]), "elapsed": int(r["elapsed"]),
                "label": r["label"], "code": r["responseCode"], "ok": r["success"] == "true",
                "threads": int(r["allThreads"]), "latency": int(r.get("Latency") or 0),
                "connect": int(r.get("Connect") or 0),
            })
    if not rows:
        print("EMPTY", path); return None
    t0 = min(r["ts"] for r in rows); t1 = max(r["ts"] for r in rows) + 1
    dur = (t1 - t0) / 1000.0
    api = [r for r in rows if not r["label"].startswith("TC_")]

    # ---- per-label stats (giong cot Aggregate Report)
    labels = defaultdict(list)
    for r in api: labels[r["label"]].append(r)
    per_label = {}
    for lab, rs in labels.items():
        el = sorted(r["elapsed"] for r in rs)
        errs = [r for r in rs if not r["ok"]]
        # error codes phan loai
        codes = defaultdict(int)
        for r in errs: codes[r["code"]] += 1
        per_label[lab] = {
            "count": len(rs), "errors": len(errs), "error_pct": round(100 * len(errs) / len(rs), 3),
            "avg": round(sum(el) / len(el), 1), "min": el[0], "max": el[-1],
            "median": round(pct(el, 50), 1), "p90": round(pct(el, 90), 1),
            "p95": round(pct(el, 95), 1), "p99": round(pct(el, 99), 1),
            "throughput_rps": round(len(rs) / dur, 2),
            "error_codes": dict(codes),
        }
    # overall (chi API samples)
    el_all = sorted(r["elapsed"] for r in api)
    errs_all = [r for r in api if not r["ok"]]
    overall = {
        "samples": len(api), "duration_s": round(dur, 1),
        "error_count": len(errs_all), "error_pct": round(100 * len(errs_all) / len(api), 3),
        "avg": round(sum(el_all) / len(el_all), 1),
        "median": round(pct(el_all, 50), 1), "p90": round(pct(el_all, 90), 1),
        "p95": round(pct(el_all, 95), 1), "p99": round(pct(el_all, 99), 1), "max": el_all[-1],
        "throughput_rps": round(len(api) / dur, 2),
        "iterations_e2e": sum(1 for r in rows if r["label"] == "TC_E2E_Mua_hang"),
    }
    # ---- time series 10s
    BUCKET = 10
    nb = int(dur // BUCKET) + 1
    series = []
    for b in range(nb):
        lo = t0 + b * BUCKET * 1000; hi = lo + BUCKET * 1000
        br = [r for r in api if lo <= r["ts"] < hi]
        if not br: continue
        bel = sorted(r["elapsed"] for r in br)
        series.append({
            "t": b * BUCKET, "rps": round(len(br) / BUCKET, 1),
            "p95": round(pct(bel, 95), 1), "avg": round(sum(bel) / len(bel), 1),
            "err_pct": round(100 * sum(1 for r in br if not r["ok"]) / len(br), 2),
            "vu_max": max(r["threads"] for r in br),
        })
    out = {"scenario": name, "overall": overall, "per_label": per_label, "series": series}
    # ---- stress steps (neu co nhieu ThreadGroup bac thang) — nhan VU tu du lieu that (vu_max)
    if name.lower() == "stress":
        steps = []
        for k in range(8):
            lo = t0 + k * 60 * 1000 + 10000; hi = lo + 45 * 1000  # bo 10s dau bac (ramp), do 45s
            br = [r for r in api if lo <= r["ts"] < hi]
            if not br: continue
            bel = sorted(r["elapsed"] for r in br)
            errs = sum(1 for r in br if not r["ok"])
            steps.append({
                "step": k + 1, "target_vu": max(r["threads"] for r in br),
                "vu_max": max(r["threads"] for r in br),
                "rps": round(len(br) / 45.0, 1), "avg": round(sum(bel) / len(bel), 1),
                "p95": round(pct(bel, 95), 1), "err_pct": round(100 * errs / len(br), 2),
            })
        out["steps"] = steps
    with open(f"/home/z/my-project/hw05/analysis/summary_{name.lower()}.json", "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    # ---- in bang
    print(f"\n===== {name.upper()} — TONG QUAN =====")
    print(json.dumps(overall, indent=1, ensure_ascii=False))
    print(f"\n{'label':28}{'#':>7}{'err%':>7}{'avg':>8}{'med':>7}{'p90':>8}{'p95':>8}{'p99':>8}{'max':>8}{'rps':>8}")
    for lab, s in sorted(per_label.items()):
        print(f"{lab:28}{s['count']:7}{s['error_pct']:7}{s['avg']:8}{s['median']:7}{s['p90']:8}{s['p95']:8}{s['p99']:8}{s['max']:8}{s['throughput_rps']:8}")
    if "steps" in out:
        print(f"\n{'step':>5}{'VU':>6}{'vu_max':>7}{'RPS':>8}{'avg':>8}{'p95':>8}{'err%':>7}")
        for s in out["steps"]:
            print(f"{s['step']:5}{s['target_vu']:6}{s['vu_max']:7}{s['rps']:8}{s['avg']:8}{s['p95']:8}{s['err_pct']:7}")
    return out

if __name__ == "__main__":
    base = "/home/z/my-project/hw05/results"
    for name in sys.argv[1:]:
        p = f"{base}/{name.lower()}/23120279_{name}_20261122.jtl"
        if os.path.exists(p): analyze(p, name)
        else: print("MISSING", p)
