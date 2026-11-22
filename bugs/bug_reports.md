# BUG REPORTS — HW05 Performance Testing (EShop SUT)

> Các issue dưới đây đã được kiểm chứng trực tiếp (kèm bằng chứng trong bài nộp và đường dẫn
> code). Đây là nội dung đăng lên **GitHub Issues** của repo bài nộp
> (https://github.com/chubedan4605/HW05_KTPM/issues); sau khi đăng, chụp màn hình từng issue
> và đính kèm vào thư mục `bugs/`.
> Quy ước tiêu đề: `[Bug]` = sai lệch đặc tả, `[Perf]` = vấn đề hiệu năng.

---

## Issue 1 — [Bug] FR-02: Bộ đếm đăng nhập sai tăng +2 mỗi lần (đặc tả yêu cầu +1)

**Mức độ:** High — người dùng bị khóa sau **2** lần sai thay vì 3 lần.

**Các bước tái hiện:**
1. `POST /api/login` với mật khẩu sai lần 1 → 401
2. Kiểm tra DB: `login_attempts` đã thành **2** (bằng chứng: `evidence/lockout_demo.txt`, Bước 4)

**Kết quả thực tế:** `server.js:54` — `const newAttempts = user.login_attempts + 2;`
→ sau 2 lần sai, `newAttempts = 4 ≥ 3` → khóa tài khoản.

**Kết quả mong đợi (đặc tả FR-02):** "Sau mỗi lần đăng nhập sai, hệ thống tăng bộ đếm lên đúng
**1 đơn vị**" → khóa sau đúng 3 lần sai.

**Bằng chứng:** `evidence/lockout_demo.txt` (log đầy đủ 2 lần sai → khóa 403 → reset → mở khóa).

---

## Issue 2 — [Bug] FR-02: Thời gian khóa tài khoản 180 giây thay vì 30 giây

**Mức độ:** Medium.

**Các bước tái hiện:**
1. Thực hiện đủ số lần đăng nhập sai để khóa (xem Issue 1 — chỉ cần 2 lần)
2. Đăng nhập đúng mật khẩu → 403 "Tài khoản đã bị khóa"
3. Đợi và đo thời gian tự mở khóa

**Kết quả thực tế:** `server.js:57` — `new Date(Date.now() + 180000)` = **180 giây**.

**Kết quả mong đợi (đặc tả FR-02):** tạm khóa **30 giây** (môi trường demo).

**Ảnh hưởng với kiểm thử hiệu năng:** phải reset lockout giữa các kịch bản Stress/Spike
(thủ tục trong `evidence/lockout_demo.txt`, script `scripts/reset_lockout.js`).

---

## Issue 3 — [Bug] GET /api/products/:id với ID không tồn tại trả về HTTP 200 + `{}`

**Mức độ:** Medium — client không phân biệt được "không có sản phẩm".

**Các bước tái hiện:**
```bash
curl -i http://localhost:3000/api/products/99999
# HTTP/1.1 200 OK
# {}
```

**Kết quả thực tế:** `server.js:161` — `if (!row) return res.status(200).json({});`

**Kết quả mong đợi:** HTTP **404** + thông báo lỗi (chuẩn REST cho resource không tồn tại).

**Bằng chứng:** `evidence/bug_evidence_products_api.txt`.

---

## Issue 4 — [Bug] GET /api/products/:id với ID chẵn trả về `price` là chuỗi (string)

**Mức độ:** Medium — phá vỡ contract kiểu dữ liệu của API.

**Các bước tái hiện:**
```bash
curl -s http://localhost:3000/api/products/2   # → "price":"28000000"  (STRING)
curl -s http://localhost:3000/api/products/1   # → "price":30000000    (NUMBER)
```

**Kết quả thực tế:** `server.js:162` — `if (row.id % 2 === 0) row.price = row.price.toString();`

**Kết quả mong đợi:** `price` luôn là number trong JSON response.

**Ảnh hưởng kiểm thử hiệu năng:** biến số hóa payload checkout (`total_amount`) nhận kiểu không
nhất quán (string/number) giữa các request — được ghi nhận trong báo cáo HW05 mục 2.3.

**Bằng chứng:** `evidence/bug_evidence_products_api.txt`.

---

## Issue 5 — [Perf] Tìm kiếm sản phẩm quét toàn bảng (full scan), không phân trang

**Mức độ:** Performance (khuyết điểm dài hạn).

**Bằng chứng (EXPLAIN QUERY PLAN):**
```
EXPLAIN QUERY PLAN SELECT * FROM products WHERE name LIKE '%iPhone%';
→ SCAN products          -- quét toàn bộ bảng, không dùng index
```
- `server.js:144`: chuỗi LIKE có `%` **đứng trước** → B-tree index không thể áp dụng.
- `GET /api/products` trả về **toàn bộ** danh sách không có `LIMIT/OFFSET`.

**Đề xuất:** dùng FTS5 (full-text search) hoặc chuẩn hoá tìm kiếm tiền tố `kw%` + index;
thêm phân trang mặc định (20–50 sản phẩm/trang).

**Số liệu từ Stress test HW05:** p95 search 93 ms ở 480 VU (x2.5 lần so với baseline) —
chưa nghiêm trọng ở 80 sản phẩm, sẽ tuyến tính xấu đi theo số dòng.

---

## Issue 6 — [Perf] Journal mode `delete` + ghi DB trên mọi lần login → serialize write ở quá tải

**Mức độ:** Performance.

**Bằng chứng:**
- `PRAGMA journal_mode` → **delete** (chưa bật WAL)
- `server.js:47-50`: mỗi login **thành công** vẫn chạy `UPDATE users SET login_attempts = 0...`
  (write DB); checkout `INSERT` orders — ~40% request trong workflow là ghi DB.
- Kết quả Stress 480 VU: p95 các endpoint chạm SQLite (Login/Search/Detail/Checkout) = **93 ms**,
  trong khi Add-to-cart (chỉ ghi bộ nhớ) = **50 ms** — chênh gần 2 lần.

**Đề xuất:** bật `PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;` khi khởi tạo DB —
giảm chi phí fsync mỗi transaction; cân nhắc bỏ UPDATE login_attempts khi giá trị đã là 0.

---

## Issue 7 — [Perf] Rò rỉ bộ nhớ `userCarts` (+68,2 MB / 15 phút ở tải 1.510 req/s)

**Mức độ:** High (Performance / Stability — gây OOM khi chạy dài hạn).

**Bằng chứng (Soak test 15 phút — 180 VU):**
- `server.js:14`: giỏ hàng được lưu trong biến in-memory `userCarts` và **không được xóa/dọn sau khi checkout**.
- Trong bài test Soak 15 phút (1.359.236 samples, 271.811 vòng E2E, `evidence/mon/Soak_resources.csv`), RSS của tiến trình `node` tăng đơn điệu từ **205,4 MB → 273,6 MB** (+68,2 MB trong 15 phút ≈ **4,5 MB/phút** ở mức 1.510 req/s, tương ứng ~250 byte/vòng E2E).
- Ước tính sẽ cạn 4 GB RAM và gây crash OOM sau khoảng **~10 giờ** vận hành liên tục ở mức tải này.

**Đề xuất:** Xóa mục giỏ hàng (`delete userCarts[userId]` hoặc `userCarts[userId] = []`) ngay sau khi checkout thành công, đồng thời cân nhắc chuyển lưu trữ giỏ hàng sang SQLite/Redis kèm TTL để hỗ trợ scale nhiều process.

---

## Danh sách file bằng chứng kèm theo
| File | Nội dung |
|---|---|
| `evidence/lockout_demo.txt` | Demo đầy đủ Issue 1 & 2 (2 lần sai → khóa → reset SQL → mở khóa) |
| `evidence/bug_evidence_products_api.txt` | curl trực tiếp Issue 3 & 4 |
| `analysis/summary_stress.json` | Số liệu p95 theo endpoint cho Issue 5 & 6 |
| `evidence/mon/Soak_resources.csv` | Số liệu tăng trưởng RSS đơn điệu cho Issue 7 |
| `results/stress/23120279_Stress_20261122.jtl.gz` | Raw log đối chiếu |
