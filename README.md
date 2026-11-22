# HW05 — Performance Testing · EShop SUT

| | |
|---|---|
| **Sinh viên** | Nguyễn Lê Quang Kan — MSSV `23120279` |
| **Học phần** | Kiểm thử Phần mềm — FIT, HCMUS |
| **SUT** | [ttbhanh/eshop-sut](https://github.com/ttbhanh/eshop-sut) — backend Node.js + Express + SQLite |
| **Môi trường** | `DESKTOP-O38ONUM` — Dell Precision 3520, Intel Core i7-7820HQ (4C/8T), 16 GB RAM, Windows 10 Pro 64-bit |
| **Công cụ** | Apache JMeter 5.6.3 (CLI non-GUI + GUI), OpenJDK 17, Node.js, Windows Task Manager, GLM (Z.ai) — khai báo trong `ai-audit/` |
| **Ngày** | 23/11/2026 |

## Self-assessment (đề mục 15)

| # | Tiêu chí | Điểm tối đa | Tự đánh giá |
|---|---|---:|---:|
| 1 | Task 1 — Load testing | 30 | 29 |
| 2 | Task 1 — Stress testing | 20 | 19 |
| 3 | Task 1 — Spike testing | 20 | 19 |
| 4 | Task 2 — AI analysis + misinterpretation hunt (correct values từ raw logs) | 10 | 10 |
| 5 | Task 3 — Continuous Performance Testing proposal (G9.6) | 10 | 10 |
| 6 | Agent Skills | 10 | 9 |
| | **Tổng** | **100** | **96** |

## Test summary report (đề mục 14)

**Scenarios run** — 4 kịch bản thực thi trực tiếp trên máy `DESKTOP-O38ONUM` (toàn bộ raw `.jtl` + HTML dashboard đính kèm):

| Kịch bản | Tham số | Samples | Throughput | p95 | Lỗi |
|---|---|---:|---|---:|---|
| Load | 50 VU · ramp 120s · 420s · think ~1s | 17.825 | 42,45 req/s | 11 ms | 0% |
| Stress | 60→480 VU (8 bậc × 60s) · think ~50ms | 218.771 | đỉnh 496,6 req/s (@180 VU) | 1.672 ms | 0,28% (613 lỗi Duration Assertion, 0 lỗi 5xx) |
| Spike | nền 20 VU + 2 sóng 300 VU / 40s | 39.075 | đỉnh sóng 505,0 req/s | 976 ms (đỉnh 1.080 ms) | 0% |
| Soak | 180 VU · 900s (15 phút) | 418.392 | 464,84 req/s duy trì | 502 ms | 0% |

**Endpoint groups covered** (workflow E2E `Login → Search → Detail → AddCart → Checkout` dùng chung, không trùng thành viên khác trong nhóm):

- **Auth-heavy:** `POST /api/login` (FR-02, kèm xử lý + reset account-lockout giữa các lần chạy bằng `scripts/reset_lockout.js`)
- **Read-heavy:** `GET /api/products?search=` (FR-05) + `GET /api/products/:id` (FR-06)
- **Transactional:** `POST /api/cart` (FR-07) + `POST /api/checkout` (FR-08)

**Endurance threshold (số cụ thể trên phần cứng `DESKTOP-O38ONUM`):**

- **Max stable RPS (knee):** ≈ **496,6 req/s** tại bậc **180 VU** (`p95 = 545 ms`, `0%` lỗi); từ 240 VU trở lên thông lượng bão hòa quanh 480–492 req/s trong khi p95 tăng vọt 998 → 2.300 ms.
- **Bền bỉ kiểm chứng (Soak 15 phút):** **464,84 req/s** duy trì liên tục ở 180 VU, `p95 = 502 ms`, `0%` lỗi trong suốt 900 giây (83.626 vòng E2E).
- **Memory & DB ceiling:** RSS tiến trình `node.exe` tăng từ **72,9 → 184,0 MB** (+111,1 MB trong 15 phút chạy tải cao do biến in-memory `userCarts` không dọn sau checkout — Bug #7); SQLite tăng tuyến tính **3,72 → 9,00 MB** (~63 B/order).

**Bugs / performance issues: 7** — 4 bug đặc tả (lockout +2, khóa 180s, `products/:id` trả `200 + {}`, `price` kiểu string với id chẵn) + 3 vấn đề hiệu năng (full-scan search, SQLite `journal_mode=delete` + write mỗi login, rò rỉ bộ nhớ `userCarts`) — đã đăng công khai tại [GitHub Issues (#1–#7)](https://github.com/chubedan4605/HW05_KTPM/issues) kèm ảnh chụp trong `bugs/screenshots/` và chi tiết trong `bugs/bug_reports.md`.

**Demo video:** `【ĐIỀN LINK YOUTUBE (unlisted) SAU KHI UPLOAD】`

## Repo công khai (đề mục 14)

> **GitHub repo (test plans + data files + scripts + issues):** https://github.com/chubedan4605/HW05_KTPM

## Cấu trúc thư mục

```
├── README.md                              # file này (self-assessment + test summary)
├── report/                                # báo cáo chính MD + PDF
├── testplans/                             # 4 .jmx: 23120279_{Load,Stress,Spike,Soak}_20261122.jmx
├── data/                                  # users.csv, products.csv
├── results/{load,stress,spike,soak}/      # raw .jtl + html/ dashboard
├── evidence/                              # hardware/ (dxdiag + systeminfo) · mon/ · screenshots/ · lockout_demo.txt · bug_evidence
├── analysis/                              # summary_*.json · 7 biểu đồ PNG · flowchart CI
├── agent-skill/perf-testing-eshop/        # Agent Skill tái sử dụng (SKILL.md + 5 scripts)
├── ai-audit/                              # AI Audit Report + AI Critique (MD + PDF)
├── video/23120279_demo_video_script.md    # kịch bản thuyết minh video demo
├── bugs/                                  # bug_reports.md + screenshots/ (GitHub Issues #1-#7)
├── git/git_commit_log.txt                 # lịch sử commit từng bước
└── scripts/                               # script tự động hóa (run_win.ps1, seed, reset_lockout, analyze, charts)
```

## Tái lập nhanh trên Windows

```powershell
# 1) Khởi động SUT: cd ..\eshop-sut\backend && npm install && node server.js
# 2) Seed dữ liệu: node scripts\seed_data.js
# 3) Chạy từng kịch bản (tự reset lockout + monitor node.exe + xuất HTML dashboard):
.\scripts\run_win.ps1 Load     # hoặc Stress / Spike / Soak
# 4) Phân tích & vẽ biểu đồ:
python scripts\analyze_jtl.py Load Stress Spike Soak
python scripts\make_charts.py
```
