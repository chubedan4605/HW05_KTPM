#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_charts.py — Ve bieu do hieu nang cho HW05 tu analysis/summary_*.json + monitor CSV.
Ngu luc: 7 bieu do cho bao cao (Load/Stress/Spike/Soak + so sanh endpoint + tai nguyen)."""
import json, csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

font_linux = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
if os.path.exists(font_linux):
    fm.fontManager.addfont(font_linux)
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
else:
    plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "analysis")
M = os.path.join(ROOT, "evidence", "mon")
OUT = A
# Business Cool palette (charts skill)
C_TEXT = "#243447"; C_ACC = "#4C6EF5"; C_GRAY = "#D1D5DB"; C_RED = "#E03131"; C_GREEN = "#2F9E44"; C_AMBER = "#E8590C"

def style_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.15, linewidth=0.6)
    ax.tick_params(colors=C_TEXT, labelsize=9)
    for s in ax.spines.values(): s.set_color("#B0BCCB")

def load(name):
    p = f"{A}/summary_{name}.json"
    return json.load(open(p)) if os.path.exists(p) else None

# ============ 1. LOAD — RPS + p95 over time ============
d = load("load")
if d:
    t = [p["t"] for p in d["series"]]; rps = [p["rps"] for p in d["series"]]
    p95 = [p["p95"] for p in d["series"]]
    fig, ax = plt.subplots(figsize=(9, 4.4), constrained_layout=True)
    ax2 = ax.twinx(); ax2.spines['top'].set_visible(False)
    ax.plot(t, rps, color=C_ACC, lw=1.8, label="Throughput (req/s)")
    ax2.plot(t, p95, color=C_AMBER, lw=1.6, ls="--", label="p95 (ms)")
    ax2.axhline(1000, color=C_RED, lw=0.8, ls=":", alpha=0.7)
    ax2.text(t[-1]*0.985, 1000, " nguong p95 = 1s", color=C_RED, fontsize=8, va="bottom", ha="right")
    ax.set_xlabel("Thời gian (giây)", color=C_TEXT); ax.set_ylabel("Throughput (req/s)", color=C_ACC)
    ax2.set_ylabel("p95 (ms)", color=C_AMBER)
    ax.set_title(f"Load 50 VU: hệ thống ổn định — p95 trung bình {d['overall']['p95']:.0f} ms, lỗi {d['overall']['error_pct']:.2f}%",
                 color=C_TEXT, fontsize=12, pad=12)
    style_ax(ax); ax2.tick_params(colors=C_AMBER, labelsize=9); ax2.grid(False)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(1.06, 1), frameon=False, fontsize=9)
    fig.savefig(f"{OUT}/load_timeseries.png", dpi=300); plt.close(fig)

# ============ 2. STRESS — steps: VU vs RPS + p95 ============
d = load("stress")
if d and "steps" in d:
    st = d["steps"]
    x = [s["target_vu"] for s in st]; rps = [s["rps"] for s in st]; p95 = [s["p95"] for s in st]; err = [s["err_pct"] for s in st]
    fig, ax = plt.subplots(figsize=(9, 4.6), constrained_layout=True)
    ax2 = ax.twinx(); ax2.spines['top'].set_visible(False)
    ax.plot(x, rps, "-o", color=C_ACC, lw=2, ms=5, label="Throughput (req/s)")
    ax2.plot(x, p95, "-s", color=C_AMBER, lw=1.8, ms=5, label="p95 (ms)")
    ax.set_xlabel("Số VU mục tiêu (mỗi bậc +25 VU, giữ 60s)", color=C_TEXT)
    ax.set_ylabel("Throughput (req/s)", color=C_ACC); ax2.set_ylabel("p95 (ms)", color=C_AMBER)
    # danh dau knee: bac dau tien ma p95 vuot 1000ms hoac err > 1%
    knee = next((s for s in st if s["p95"] > 1000 or s["err_pct"] > 1), None)
    if knee:
        ax.axvline(knee["target_vu"], color=C_RED, lw=1.2, ls=":", alpha=0.8)
        ax.annotate(f"Ngưỡng bão hòa\n≈ {knee['target_vu'] - 25}–{knee['target_vu']} VU",
                    xy=(knee["target_vu"], knee["rps"]), xytext=(knee["target_vu"] - 60, knee["rps"] * 0.8),
                    color=C_RED, fontsize=9, arrowprops=dict(arrowstyle="->", color=C_RED, lw=1))
    ax.set_title("Stress bậc thang 25→200 VU: tìm điểm bão hòa (knee) của backend",
                 color=C_TEXT, fontsize=12, pad=12)
    style_ax(ax); ax2.tick_params(colors=C_AMBER, labelsize=9); ax2.grid(False)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(1.06, 1), frameon=False, fontsize=9)
    fig.savefig(f"{OUT}/stress_steps.png", dpi=300); plt.close(fig)

    # ---- 2b. stress time series
    t = [p["t"] for p in d["series"]]; p95s = [p["p95"] for p in d["series"]]; errs = [p["err_pct"] for p in d["series"]]
    fig, ax = plt.subplots(figsize=(9.5, 4.6), constrained_layout=True)
    ax2 = ax.twinx(); ax2.spines['top'].set_visible(False)
    ax.plot(t, p95s, color=C_AMBER, lw=1.4, label="p95 (ms)")
    ax2.plot(t, errs, color=C_RED, lw=1.2, label="Lỗi (%)")
    for k in range(1, 8):
        ax.axvline(k * 60, color="#94A3B8", lw=0.7, ls=":", alpha=0.6)
    ax.set_xlabel("Thời gian (giây) — vạch dọc = chuyển bậc tải (+25 VU mỗi 60s)", color=C_TEXT)
    ax.set_ylabel("p95 (ms)", color=C_AMBER); ax2.set_ylabel("Tỉ lệ lỗi (%)", color=C_RED)
    ax.set_title("Stress test: p95 và tỉ lệ lỗi theo thời gian qua 8 bậc tải",
                 color=C_TEXT, fontsize=12, pad=12)
    style_ax(ax); ax2.tick_params(colors=C_RED, labelsize=9); ax2.grid(False)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(1.06, 1), frameon=False, fontsize=9)
    fig.savefig(f"{OUT}/stress_timeseries.png", dpi=300); plt.close(fig)

# ============ 3. SPIKE — VU + p95 + err ============
d = load("spike")
if d:
    t = [p["t"] for p in d["series"]]; vu = [p["vu_max"] for p in d["series"]]
    p95 = [p["p95"] for p in d["series"]]; errs = [p["err_pct"] for p in d["series"]]
    fig, ax = plt.subplots(figsize=(9.5, 4.6), constrained_layout=True)
    ax2 = ax.twinx(); ax2.spines['top'].set_visible(False)
    ax.fill_between(t, vu, color=C_ACC, alpha=0.18, step="mid")
    ax.step(t, vu, where="mid", color=C_ACC, lw=1.6, label="VU đang hoạt động")
    ax2.plot(t, p95, color=C_AMBER, lw=1.4, label="p95 (ms)")
    ax.set_xlabel("Thời gian (giây)", color=C_TEXT); ax.set_ylabel("VU", color=C_ACC)
    ax2.set_ylabel("p95 (ms)", color=C_AMBER)
    ax.set_title(f"Spike 10→100 VU (3 đợt): p95 dao động {min(p95):.0f}–{max(p95):.0f} ms, tự phục hồi sau mỗi đợt",
                 color=C_TEXT, fontsize=12, pad=12)
    style_ax(ax); ax2.tick_params(colors=C_AMBER, labelsize=9); ax2.grid(False)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(1.06, 1), frameon=False, fontsize=9)
    fig.savefig(f"{OUT}/spike_timeseries.png", dpi=300); plt.close(fig)

# ============ 4. SOAK — stability + resources ============
d = load("soak")
mon = f"{M}/Soak_resources.csv"
if d:
    t = [p["t"] for p in d["series"]]; p95 = [p["p95"] for p in d["series"]]
    rps = [p["rps"] for p in d["series"]]; errs = [p["err_pct"] for p in d["series"]]
    fig, ax = plt.subplots(figsize=(9, 4.4), constrained_layout=True)
    ax2 = ax.twinx(); ax2.spines['top'].set_visible(False)
    ax.plot(t, rps, color=C_ACC, lw=1.6, label="Throughput (req/s)")
    ax2.plot(t, p95, color=C_AMBER, lw=1.4, ls="--", label="p95 (ms)")
    ax.set_xlabel("Thời gian (giây) — tải duy trì liên tục 15 phút", color=C_TEXT)
    ax.set_ylabel("Throughput (req/s)", color=C_ACC); ax2.set_ylabel("p95 (ms)", color=C_AMBER)
    ax.set_title(f"Soak 15 phút @ 25 VU: ổn định — p95 {d['overall']['p95']:.0f} ms, lỗi {d['overall']['error_pct']:.2f}%",
                 color=C_TEXT, fontsize=12, pad=12)
    style_ax(ax); ax2.tick_params(colors=C_AMBER, labelsize=9); ax2.grid(False)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(1.06, 1), frameon=False, fontsize=9)
    fig.savefig(f"{OUT}/soak_stability.png", dpi=300); plt.close(fig)

    if os.path.exists(mon):
        rows = list(csv.DictReader(open(mon)))
        tm = [float(r["elapsed_s"]) for r in rows]; cpu = [float(r["cpu_pct_1core"]) for r in rows]
        rss = [float(r["rss_mb"]) for r in rows]; orders = [int(r["orders"]) for r in rows]
        dbmb = [float(r["db_mb"]) for r in rows]
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.2), constrained_layout=True)
        a1.plot(tm, rss, color=C_GREEN, lw=1.8, label="RSS node (MB)")
        a1b = a1.twinx(); a1b.spines['top'].set_visible(False)
        a1b.plot(tm, cpu, color=C_ACC, lw=1.1, alpha=0.75, label="CPU % (1 core)")
        a1.set_xlabel("Thời gian (s)", color=C_TEXT); a1.set_ylabel("RSS (MB)", color=C_GREEN)
        a1b.set_ylabel("CPU %", color=C_ACC)
        a1.set_title("Bộ nhớ & CPU của backend", color=C_TEXT, fontsize=11, pad=10)
        style_ax(a1); a1b.tick_params(colors=C_ACC, labelsize=9); a1b.grid(False)
        h1, l1 = a1.get_legend_handles_labels(); h2, l2 = a1b.get_legend_handles_labels()
        a1.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(0.99, 1.14), frameon=False, fontsize=8, ncol=2)
        a2.plot(tm, orders, color=C_AMBER, lw=1.8, label="Số orders tích lũy")
        a2b = a2.twinx(); a2b.spines['top'].set_visible(False)
        a2b.plot(tm, dbmb, color=C_GRAY, lw=1.4, label="Kích thước SQLite (MB)")
        a2.set_xlabel("Thời gian (s)", color=C_TEXT); a2.set_ylabel("Orders", color=C_AMBER)
        a2b.set_ylabel("DB (MB)")
        a2.set_title("Tăng trưởng dữ liệu — không rò rỉ bộ nhớ", color=C_TEXT, fontsize=11, pad=10)
        style_ax(a2); a2b.tick_params(labelsize=9); a2b.grid(False)
        h1, l1 = a2.get_legend_handles_labels(); h2, l2 = a2b.get_legend_handles_labels()
        a2.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(0.99, 1.14), frameon=False, fontsize=8, ncol=2)
        fig.savefig(f"{OUT}/soak_resources.png", dpi=300); plt.close(fig)

# ============ 5. So sanh p95 theo endpoint giua cac kich ban ============
scens = {}
for n in ["load", "stress", "spike", "soak"]:
    d = load(n)
    if d: scens[n] = d
if len(scens) >= 2:
    endpoints = ["API01_Login_auth", "API02_Search_products_read", "API03_Product_detail_read",
                 "API04_Add_to_cart_txn", "API05_Checkout_txn"]
    nice = {"API01_Login_auth": "Login\n(auth)", "API02_Search_products_read": "Search\n(read)",
            "API03_Product_detail_read": "Detail\n(read)", "API04_Add_to_cart_txn": "AddCart\n(txn)",
            "API05_Checkout_txn": "Checkout\n(txn)"}
    colors = {"load": C_ACC, "stress": C_RED, "spike": C_AMBER, "soak": C_GREEN}
    names = {"load": "Load 50VU", "stress": "Stress ≤200VU", "spike": "Spike 10→100VU", "soak": "Soak 25VU"}
    fig, ax = plt.subplots(figsize=(9.5, 4.6), constrained_layout=True)
    w = 0.2
    for i, (n, d) in enumerate(scens.items()):
        xs = [j + (i - 1.5) * w for j in range(len(endpoints))]
        ys = [d["per_label"][e]["p95"] if e in d["per_label"] else 0 for e in endpoints]
        ax.bar(xs, ys, width=w * 0.9, color=colors[n], label=names[n], alpha=0.88)
    ax.set_xticks(range(len(endpoints))); ax.set_xticklabels([nice[e] for e in endpoints], fontsize=9)
    ax.set_ylabel("p95 (ms)", color=C_TEXT)
    ax.set_yscale("log"); ax.set_title("p95 theo endpoint dưới 4 loại tải (trục log) — write-heavy (Login/Checkout) luôn chậm nhất",
                 color=C_TEXT, fontsize=12, pad=12)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), frameon=False, fontsize=9)
    style_ax(ax)
    fig.savefig(f"{OUT}/endpoint_p95_comparison.png", dpi=300); plt.close(fig)

print("Charts saved to", OUT, ":", sorted(f for f in os.listdir(OUT) if f.endswith(".png")))
