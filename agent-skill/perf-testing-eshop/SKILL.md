# Agent Skill: `perf-testing-eshop`

> Skill tái sử dụng cho quy trình **Performance Testing + JTL Log Analysis** trên SUT EShop
> (và mọi backend REST tương tự). Xây dựng theo yêu cầu mục 7 — HW05 Performance Testing.

## Khi nào dùng skill này

- Cần thiết kế và chạy Load / Stress / Spike / Soak test cho một backend REST API.
- Cần phân tích raw `.jtl` (JMeter) hoặc JSON summary (k6): p50/p90/p95/p99, throughput, error rate, knee/breaking point.
- Cần giám sát tài nguyên backend trong lúc chạy test và đối chiếu với kết quả.
- Cần phát hiện hồi quy hiệu năng giữa hai lần chạy (baseline vs candidate).

## Triết lý (AI-first + Human review)

1. **AI thiết kế, người review**: AI đề xuất workflow, tham số (VU, ramp-up, think-time), khẳng định
   (assertion), cấu trúc CSV; người kiểm chứng từng mục với code/SUT thật (endpoint có tồn tại?
   JSON path đúng? think-time hợp lý với phần cứng?).
2. **Pilot trước khi chạy thật**: luôn chạy 2–5 VU trong 30–60 giây để kiểm chứng correlation
   (token, product ID) trước mọi kịch bản chính.
3. **Một biến, một lần đổi**: khi phải điều chỉnh (vd: tăng biên độ stress), chỉ đổi đúng tham số
   đó, chạy lại, và ghi lại lý do — giữ vết Audit.
4. **Bằng chứng phải đến từ raw log**: mọi kết luận trong báo cáo đều phải trích được từ `.jtl`
   hoặc monitor log, không dùng số "nhớ đại khái".

## Cấu trúc skill

```
perf-testing-eshop/
├── SKILL.md                    # file này — quy trình 6 bước
├── scripts/
│   ├── analyze_jtl.py          # phân tích .jtl: per-label, time-series, stress steps, JSON out
│   ├── monitor.py              # giám sát RSS/CPU (/proc) + SQLite size + orders count → CSV + HTML panel
│   ├── reset_lockout.js        # reset login_attempts/locked_until (account lockout) giữa các lần chạy
│   ├── seed_data.js            # đăng ký users + import products qua API, sinh users.csv/products.csv
│   └── full_reset.sh           # restart SUT (DB re-seed) + seed lại + reset lockout + smoke test
```

## Quy trình 6 bước

### Bước 1 — Khảo sát SUT
- Xác định 3 nhóm endpoint: **auth-heavy** (login), **read-heavy** (search/detail),
  **transactional** (add-to-cart/checkout).
- Đọc code backend để biết: cơ chế lockout (số lần sai, thời gian khóa, cách reset), DB engine
  (SQLite/PostgreSQL), nơi giỏ hàng lưu trữ (memory/DB) — các chi tiết này quyết định thiết kế test.
- Sinh dữ liệu: `node scripts/seed_data.js` (users.csv, products.csv — keyword khớp tên sản phẩm thật).

### Bước 2 — Thiết kế kịch bản (AI-assisted)
- Workflow E2E dùng chung: `Login → Search → Detail → AddToCart → Checkout` (cover đủ 3 nhóm).
- Tham số chuẩn (điểm khởi đầu, hiệu chỉnh theo phần cứng):
  | Kịch bản | VU | Ramp | Duration | Think-time | Listener |
  |---|---|---|---|---|---|
  | Load | 50 | 120s | 420s | Gaussian 1000±500ms | Summary Report |
  | Stress | 60→480 (8 bậc × 60s) | 5s/bậc | 480s | Gaussian 50±50ms | Aggregate Report |
  | Spike | 20 + sóng 300 (×3) | 10s/sóng | 300s | baseline 1000±500 / sóng 50±50 | View Results Tree |
  | Soak | ~75% điểm gối | 30s | 900s | Gaussian 100±100ms | View Results in Table |
- Quy tắc: correlation qua JSON Extractor (`$.token`, `$[0].id`), fallback default từ CSV;
  assertion 3 lớp (HTTP code + body chứa message + Duration theo từng endpoint).

### Bước 3 — Pilot
`jmeter -n -t plan.jmx -l pilot.jtl` với 3 VU / 40s. Checklist: 5 label đều xuất hiện, 0 lỗi,
`TC_E2E` count ≈ số iteration, orderId > 0.

### Bước 4 — Chạy thật + giám sát
- Trước mỗi kịch bản: reset lockout (`node scripts/reset_lockout.js`) — bắt buộc với SUT có
  cơ chế khóa đăng nhập sai.
- Chạy: `bash scripts/run_scenario.sh <Load|Stress|Spike|Soak>` (khởi động monitor.py + top
  snapshot song song, sinh `.jtl` + HTML dashboard).
- Sau mỗi kịch bản: kiểm tra `*_resources.csv` (CPU/RSS có bão hòa không), số orders tăng đều
  (checkout thật), và **không user nào bị khóa**.

### Bước 5 — Phân tích
`python3 scripts/analyze_jtl.py Load Stress Spike Soak` → `summary_*.json`:
- Knee/breaking point: bậc mà throughput chỉ tăng < 10% khi VU +25%, kèm p95 tăng vọt.
- Max stable RPS: bậc cao nhất vẫn p95 < 35ms (hoặc ngưỡng SLA) và error < 1%.
- Phân biệt lỗi **thật** (5xx, timeout) với lỗi **assertion** (200 chậm quá Duration) — đọc cột
  `responseCode` + `failureMessage` trong `.jtl`.

### Bước 6 — Báo cáo & đối chiếu AI
- Cặp đôi: phân tích của AI + bảng "giá trị đúng từ raw log" (mỗi tuyên bố sai phải kèm số đúng).
- Khuyến nghị tối ưu phải đối chiếu **code thật** (vd: index vô dụng với `LIKE '%kw%'` — chạy
  `EXPLAIN QUERY PLAN` để chứng minh; connection pool không tồn tại với SQLite embedded).

## Video demo skill

Quy trình quay (YouTube unlisted, ≥ 6 phút, thuyết minh tiếng Việt):
1. (0:00–0:45) Giới thiệu skill + SUT + 3 nhóm endpoint đã khảo sát.
2. (0:45–2:00) Chạy Bước 1–2: seed dữ liệu, mở test plan, giải thích tham số.
3. (2:00–3:30) Chạy Bước 3–4: pilot → chạy Load thật, chỉ vào monitor.py panel.
4. (3:30–5:00) Chạy Bước 5: analyze_jtl.py, chỉ vào knee trên biểu đồ stress.
5. (5:00–6:30) Bước 6: cho AI phân tích log, chỉ ra 1 misinterpretation và giá trị đúng.

## Ghi chú mở rộng cho endpoint khác

Skill tổng quát hoá được: thay workflow trong Bước 2 bằng chuỗi request của endpoint nhóm mới
(vd: coupon → checkout; admin CRUD), giữ nguyên 6 bước và toàn bộ scripts.
