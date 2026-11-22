# AI AUDIT REPORT — HW05 Performance Testing

**Khai báo bắt buộc theo đề bài (mục 9):** "I use AI tools for the following tasks."

| Mục | Giá trị |
|---|---|
| Sinh viên | Nguyễn Lê Quang Kan — 23120279 |
| AI tool | **GLM (Z.ai)** — trợ lý lập trình/phân tích dùng qua phiên chat có hướng dẫn từng bước |
| Phiên làm việc | 22/11/2026, 07:10 – 09:40 (UTC) |
| Phạm vi AI | Thiết kế test plan (B1–B4), phân tích log (B5), đề xuất tối ưu (B6) — **6 phiên tương tác chuyên biệt** |
| Phạm vi con người | Đọc code SUT, hiệu chỉnh tham số, chạy toàn bộ kịch bản + pilot, soát lỗi AI (10 lỗi thiết kế, 5 misinterpretation, 2 hallucination), viết báo cáo, xử lý anomaly JMeter |
| Tuyên bố | Toàn bộ raw .jtl, monitor log, screenshot trong bài là kết quả chạy thật; mọi số liệu trong báo cáo đều truy vết được về raw log |

---

## Nhật ký tương tác AI (6 phiên chính — prompt đầy đủ, output tóm lược)

### Phiên B1 — 07:12 · Khảo sát SUT, chọn workflow

**Prompt:**
> "SUT là EShop (github.com/ttbhanh/eshop-sut): backend Node.js + Express + SQLite, port 3000.
> API: POST /api/login (JWT, khóa 3 lần sai), GET /api/products?search=, GET /api/products/:id,
> POST /api/cart, POST /api/checkout. Đề bài yêu cầu 1 workflow E2E phủ 3 nhóm endpoint:
> auth-heavy, read-heavy, transactional. Hãy đề xuất workflow và giải thích cách nó phủ từng nhóm."

**Output AI (tóm lược):** đề xuất Login → Search → Detail → Add-to-cart → Checkout; mapping:
login = auth-heavy; search/detail = read-heavy; cart/checkout = transactional. Đề xuất thêm
correlation token → các request sau.

**Review của tôi:** đúng với API spec; chọn nhận (workflow không trùng thành viên nhóm).

### Phiên B2 — 07:14 · Tham số 3 kịch bản

**Prompt:**
> "Đề xuất tham số (số VU, ramp-up, duration, think-time) cho 3 test plan Load/Stress/Spike chạy
> workflow trên. Phần cứng: 2 vCPU, 4GB RAM, SUT và JMeter cùng máy. Nêu căn cứ từng con số."

**Output AI (tóm lược — gồm các lỗi được review ở mục sau):** Load 100 VU / ramp 10s / think 0ms;
Stress 1 TG linear ramp 0→500 VU / 10 phút; Spike 1 TG ramp 0→300 VU trong 5s; assertion Duration
5000ms chung.

**Review của tôi:** 7/10 mục phải sửa (bảng 3.3 trong báo cáo chính: #1, #2, #3, #8, #9, #10 và
thiếu think-time riêng từng kịch bản). AI không biết SUT khóa tài khoản +2/lần → phải bỏ bước
login-sai khỏi vòng lặp.

### Phiên B3 — 07:15 · Sinh .jmx

**Prompt:**
> "Sinh JMeter 5.6.3 test plan XML: workflow 5 request như trên, CSV Data Set (users.csv:
> email,password; products.csv: keyword,product_id,product_name,price), JSON Extractor lấy token
> từ response login, header Authorization cho cart/checkout, assertion HTTP 200 + body + Duration
> theo endpoint, Transaction Controller gom 5 request."

**Output AI:** cấu trúc .jmx hoàn chỉnh (các element đúng loại, thứ tự đúng).

**Review + pilot:** phát hiện 3 lỗi: JSON path `$.user.token` (đúng: `$.token`), thiếu
Content-Type, CSV recycle=false. Sửa trực tiếp trong .jmx; pilot 3 VU/40s xác nhận 111 samples
0 lỗi.

### Phiên B4 — 07:18 · Data-driven

**Prompt:**
> "Thiết kế 2 file CSV parameterize credentials + product + order payload cho workflow. Lưu ý
> keyword tiếng Việt có dấu, response search là mảng JSON."

**Output AI:** cấu trúc cột như đã dùng; gợi ý default value cho JSON Extractor.

**Review:** chấp nhận; sinh dữ liệu thật bằng script seed (100 users + 75 products qua API admin).

### Phiên B5 — 08:05 · Phân tích .jtl (Task 2)

**Prompt (gửi kèm bảng tổng hợp dashboard):**
> "Phân tích kết quả performance test trong file đính kèm (Load/Stress/Spike/Soak). Chỉ ra p95,
> error rate, throughput, bottleneck và đề xuất ngưỡng hiệu năng cho API này."

**Output AI:** 5 nhận định + 2 đề xuất ngưỡng — trong đó 5 nhận định sai/misinterpretation và 2
khuyến nghị hallucination (chi tiết bảng 4.2, 4.3 báo cáo chính: nhầm Max 2,8s thành p95; gọi 613
lỗi Duration Assertion trên HTTP 200 là "lỗi HTTP 500"; lấy trung bình 455,6 req/s gồm cả ramp làm
sức chứa tối đa thay vì đỉnh 496,6 req/s; giải thích "login chậm vì bcrypt" trong khi SUT so sánh
plaintext; bỏ qua xu hướng tăng RSS `node.exe` từ 72,9 → 184,0 MB trong Soak test).

**Prompt lần 2 (gửi 200 dòng .jtl thô):** AI tự sửa 3/4 lỗi — xác nhận nguyên nhân là chất lượng
dữ liệu đầu vào.

### Phiên B6 — 08:08 · Đề xuất tối ưu (Task 2 tiếp)

**Prompt:**
> "Với bottleneck quan sát được, đề xuất các tối ưu hóa cho backend Node.js + SQLite này, xếp theo
> ưu tiên."

**Output AI:** 6 khuyến nghị → tôi phân loại 2 hallucinated (index cho LIKE '%kw%', connection
pool cho SQLite embedded — bác bằng EXPLAIN QUERY PLAN + đọc code), 3 feasible, 1 feasible-with-
constraints (Node cluster vs cart in-memory).

---

## Công cụ khai báo (đề mục 8)

| Công cụ | Dùng để |
|---|---|
| GLM (Z.ai) | 6 phiên thiết kế + phân tích ở trên |
| Apache JMeter 5.6.3 | sinh tải, thu .jtl, HTML dashboard |
| Python 3.12 (script tự viết) | phân tích .jtl, giám sát /proc, vẽ biểu đồ |
| top / /proc | giám sát tài nguyên backend |
| Node.js | script reset lockout, seed dữ liệu |

## Tuyên bố trách nhiệm

Tôi đã đọc, kiểm chứng và chịu trách nhiệm hoàn toàn cho mọi kết quả trong bài nộp. Các lỗi của
AI được liệt kê minh bạch ở mục 3.3 và 4.2 của báo cáo chính — việc nhận diện và sửa chúng chính
là một phần việc của tôi trong chiến lược AI-first của học phần.
