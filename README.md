# HW05 — Performance Testing · EShop SUT

| | |
|---|---|
| **Sinh viên** | Nguyễn Lê Quang Kan — 23120279 |
| **Học phần** | Kiểm thử Phần mềm — FIT, HCMUS |
| **SUT** | [ttbhanh/eshop-sut](https://github.com/ttbhanh/eshop-sut) — backend Node.js + Express + SQLite |
| **Công cụ** | Apache JMeter 5.6.3 (non-GUI), GLM (Z.ai) — khai báo trong `ai-audit/` |
| **Ngày** | 22/11/2026 |

## Self-assessment (đề mục 15)

| # | Tiêu chí | Điểm tối đa | Tự đánh giá |
|---|---|---|---|
| 1 | Task 1 — Load testing | 30 | 29 |
| 2 | Task 1 — Stress testing | 20 | 19 |
| 3 | Task 1 — Spike testing | 20 | 19 |
| 4 | Task 2 — AI analysis + misinterpretation hunt (correct values từ raw logs) | 10 | 10 |
| 5 | Task 3 — Continuous Performance Testing proposal (G9.6) | 10 | 10 |
| 6 | Agent Skills | 10 | 9 |
| | **Tổng** | **100** | **96** |

## Test summary report (đề mục 14)

**Scenarios run** — 4 kịch bản chính + pilot + 4 lần lặp để debug (toàn bộ .jtl đính kèm):

| Kịch bản | Tham số | Samples | Throughput | p95 | Lỗi |
|---|---|---|---|---|---|
| Load | 50 VU · ramp 120s · 420s · think 1s | 17.853 | 42,5 req/s | 1 ms | 0% |
| Stress | 60→480 VU (8 bậc × 60s) · think 50ms | 1.374.611 | đỉnh 3.678 req/s | 90 ms (DB: 93 ms) | 0,006% (Duration Assertion) |
| Spike | nền 20 VU + 2 sóng 300 VU/40s | 224.033 | đỉnh sóng 3.411 req/s | 79 ms (sóng ≤ 113 ms) | 0% |
| Soak | 180 VU · 900s (15 phút) | 1.359.236 | 1.510 req/s duy trì | 2 ms | 0% |

**Endpoint groups covered** (workflow E2E `Login→Search→Detail→AddCart→Checkout` dùng chung,
không trùng thành viên khác trong nhóm):

- Auth-heavy: `POST /api/login` (FR-02, kèm xử lý + reset account-lockout giữa các lần chạy)
- Read-heavy: `GET /api/products?search=` (FR-05) + `GET /api/products/:id` (FR-06)
- Transactional: `POST /api/cart` (FR-07) + `POST /api/checkout` (FR-08)

**Endurance threshold (số cụ thể):**

- Max stable RPS ≈ **3.260 req/s** (bậc 240 VU: p95 33 ms, 0% lỗi); knee 240–300 VU
- Bền bỉ kiểm chứng: **1.510 req/s × 15 phút**, p95 = 2 ms không trồi sụt
- Memory ceiling: không chạm trong 15 phút; RSS 205→273 MB (**rò rỉ `userCarts` +68 MB/15 phút ≈
  4,5 MB/phút @1.510 req/s** — Bug #7; ước cạn 4 GB sau ~10 giờ); DB tăng 63 B/order

**Bugs / performance issues: 7** — 4 bug đặc tả (lockout +2, khóa 180s, products/:id trả 200+{},
price string với id chẵn) + 3 perf (full-scan search, journal delete + write mỗi login, rò rỉ
`userCarts`) — đã đăng công khai tại [GitHub Issues (#1–#7)](https://github.com/chubedan4605/HW05_KTPM/issues) kèm ảnh chụp trong `bugs/screenshots/` và chi tiết trong `bugs/bug_reports.md`.

**Demo video:** `【ĐIỀN LINK YOUTUBE (unlisted) SAU KHI QUAY — kịch bản sẵn trong video/】`

## Repo công khai (đề mục 14)

> **GitHub repo (test plans + data files + scripts):** https://github.com/chubedan4605/HW05_KTPM

## Cấu trúc thư mục

```
├── README.md                    # file này
├── report/                      # báo cáo chính MD + PDF
├── testplans/                   # 4 .jmx: 23120279_{Load,Stress,Spike,Soak}_20261122.jmx
├── data/                        # users.csv, products.csv
├── results/{load,stress,spike,soak}/   # .jtl raw + html/ + *_supplementary.jtl
├── evidence/                    # mon/ · screenshots/ · hardware/ · lockout_demo.txt · bug_evidence
├── analysis/                    # summary_*.json · 7 biểu đồ PNG · flowchart
├── agent-skill/perf-testing-eshop/
├── ai-audit/                    # AI Audit Report + AI Critique (MD + PDF)
├── video/23120279_demo_video_script.md
├── bugs/bug_reports.md
├── git/git_commit_log.txt
├── scripts/                     # script chạy thật (seed/monitor/analyze/reset…)
└── RUN_LOCAL.md                 # tái lập trên máy bạn (hostname của bạn)
```

## Chạy lại trên máy bạn

```bash
# 1) start SUT: cd eshop-sut/backend && npm install && node server.js
# 2) node scripts/seed_data.js          # sinh users/products + CSV
# 3) cd hw05 && bash ../scripts/run_scenario.sh Load   # (hoặc Stress/Spike/Soak)
#    — nhớ node scripts/reset_lockout.js giữa các kịch bản
# 4) python3 scripts/analyze_jtl.py Load Stress Spike Soak
```

Chi tiết đầy đủ + cách thay bằng chứng bằng máy cá nhân: `RUN_LOCAL.md`.
