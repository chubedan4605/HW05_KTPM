# Kịch bản video demo HW05 — Performance Testing (EShop)

> Mục tiêu: video YouTube **unlisted**, tổng thời lượng **≥ 6 phút** (khuyến nghị 7–8 phút),
> quay màn hình + giọng thuyết minh **tiếng Việt của chính bạn**, trong cùng khung hình phải thấy
> **cả công cụ (JMeter) và trình giám sát tài nguyên (htop / Task Manager)**.
> Có thể tách thành nhiều clip (1 clip/kịch bản) rồi gộp playlist — ghi rõ thời lượng từng clip.
> Nếu chờ kết quả dài (vd: 5 phút load test), dùng **time-lapse / cắt video**, giữ lại ít nhất 60 giây
> liên tục có tool + monitor cùng khung hình.

## Chuẩn bị trước khi quay (2 phút setup, có thể quay nhanh 10 giây lướt qua)
- [ ] Mở terminal 1: `htop` (hoặc Task Manager → Performance + Processes, hiện process `node`)
- [ ] Mở terminal 2: thư mục `hw05`, sẵn sàng gõ lệnh chạy JMeter
- [ ] Mở JMeter GUI với 3 test plan (Load / Stress / Spike) — chỉ để giới thiệu cấu trúc
- [ ] Đặt tên file video: `23120279_HW05_demo.mp4`
- [ ] Ghi âm micro, kiểm tra âm lượng; môi trường yên tĩnh

---

## CLIP 0 — Giới thiệu (0:00 – 0:45, ~45 giây)

**Hình ảnh:** mặt người (tùy chọn) hoặc màn hình desktop với README bài làm.

**Lời thoại (đọc chậm, rõ):**

> "Xin chào thầy cô và các bạn, em là Nguyễn Lê Quang Kan, mã số sinh viên 23120279. Đây là video demo bài
> tập lớn số 5 — Kiểm thử hiệu năng, trên hệ thống EShop. Em sẽ trình bày ba kịch bản Load, Stress,
> Spike, cùng bài test Soak 15 phút, đều chạy trực tiếp trên máy của em với backend Node.js và
> cơ sở dữ liệu SQLite, công cụ sinh tải là JMeter phiên bản 5.6.3."

## CLIP 1 — Kiến trúc test plan (0:45 – 2:00, ~75 giây)

**Hình ảnh:** mở JMeter GUI lần lượt 3 file `23120279_Load_20261122.jmx`,
`23120279_Stress_20261122.jmx`, `23120279_Spike_20261122.jmx`; mở 2 file CSV bằng editor.

**Lời thoại:**

> "Cả ba test plan dùng chung một workflow end-to-end gồm năm bước: đăng nhập — nhóm auth-heavy;
> tìm kiếm sản phẩm và xem chi tiết — nhóm read-heavy; thêm vào giỏ và thanh toán — nhóm
> transactional. Dữ liệu được tham số hoá bằng hai file CSV: một trăm tài khoản Perf user và
> một trăm dòng từ khoá sản phẩm, nhờ vậy mỗi user ảo mua một sản phẩm khác nhau.
> Ba kịch bản khác nhau ở cấu hình tải: Load là năm mươi user ảo tăng dần trong hai phút;
> Stress là bậc thang từ sáu mươi đến bốn trăm tám mươi user ảo; Spike giữ nền hai mươi user
> rồi bùng lên ba trăm user hai đợt. Ba report view khác nhau được gán cho ba plan: Summary Report,
> Aggregate Report và View Results Tree."

## CLIP 2 — Load test (2:00 – 3:30, ~90 giây)

**Hình ảnh:** terminal chạy `bash scripts/run_scenario.sh Load`; chia đôi màn hình với `htop`.
Giữ ít nhất 45–60 giây khung hình chứa cả console JMeter (dòng `summary + ... Err: 0`) và htop.

**Lời thoại (trong lúc chờ):**

> "Bây giờ em chạy kịch bản Load. Các bạn thấy bên trái là console JMeter, bên phải là htop
> hiển thị tiến trình node của backend. Trong lúc tải tăng dần, CPU của node dao động quanh
> [đọc số liệu thật trên máy bạn] phần trăm, bộ nhớ ở mức [đọc số MB]. Sau bảy phút, kết quả:
> khoảng bốn mươi hai request mỗi giây, tỉ lệ lỗi không phần trăm, và phân vị 95 chỉ khoảng
> một mili giây. Hệ thống vượt qua kịch bản tải mục tiêu một cách dễ dàng."

## CLIP 3 — Stress test + knee (3:30 – 5:00, ~90 giây)

**Hình ảnh:** chạy `bash scripts/run_scenario.sh Stress`; khi chạy xong mở biểu đồ
`analysis/stress_steps.png` và bảng Aggregate Report trong HTML dashboard.

**Lời thoại:**

> "Tiếp theo là Stress test với tám bậc tải. Ở các bậc đầu, thông lượng tăng gần tuyến tính:
> sáu mươi user đạt khoảng một nghìn request mỗi giây. Nhưng từ bậc hai trăm bốn mươi user trở đi,
> thông lượng hầu như không tăng thêm — đây chính là điểm gối, hay knee, của hệ thống, khoảng
> ba nghìn hai trăm đến ba nghìn bốn trăm request mỗi giây. Đồng thời phân vị 95 tăng vọt từ
> ba mươi ba lên một trăm linh bảy mili giây, và xuất hiện những lỗi assertion do phản hồi
> chậm quá hai giây. Điểm thú vị: endpoint thêm vào giỏ luôn nhanh gấp đôi các endpoint chạm
> cơ sở dữ liệu, vì giỏ hàng được lưu trong bộ nhớ."

## CLIP 4 — Spike test + lockout reset (5:00 – 6:15, ~75 giây)

**Hình ảnh:** chạy `bash scripts/run_scenario.sh Spike` (có thể time-lapse); sau đó mở terminal
chạy lại phần demo lockout: 2 lần đăng nhập sai → khóa → `node scripts/reset_lockout.js` → đăng nhập lại thành công.

**Lời thoại:**

> "Spike test giữ nền hai mươi user rồi bùng lên ba trăm user trong hai đợt. Phân vị 95 lúc cao
> nhất khoảng một trăm mười ba mili giây ở đợt một và năm mươi sáu mili giây ở đợt hai, và về lại
> khoảng hai mili giây ngay sau mỗi đợt — hệ thống tự phục hồi, không đổ vỡ. Trước mỗi kịch bản,
> em thực hiện reset cơ chế khoá tài khoản:
> như các bạn thấy, chỉ sau hai lần đăng nhập sai, tài khoản đã bị khoá do SUT đếm sai —
> đây cũng là một bug em đã báo cáo trên GitHub Issues. Sau khi chạy lệnh UPDATE qua script
> reset_lockout, tài khoản đăng nhập lại bình thường."

## CLIP 5 — Soak + phân tích AI (6:15 – 7:45, ~90 giây)

**Hình ảnh:** mở `analysis/soak_resources.png`, `analysis/endpoint_p95_comparison.png`; mở
phần AI Audit trong báo cáo; mở GitHub Issues.

**Lời thoại:**

> "Bài test Soak mười lăm phút ở mức bảy mươi lăm phần trăm điểm gối xác nhận ngưỡng bền bỉ:
> khoảng một nghìn năm trăm mười request mỗi giây duy trì liên tục với p95 hai mili giây, cơ sở
> dữ liệu tăng trưởng tuyến tính theo số đơn hàng, đồng thời phát hiện rò rỉ bộ nhớ ở biến giỏ
> hàng in-memory làm RSS tăng sáu mươi tám megabyte sau mười lăm phút. Cuối cùng, em dùng AI để
> phân tích log và tự mình soát lại: AI nhầm phân vị 95 với thời gian tối đa, nhầm lỗi assertion
> với lỗi máy chủ, và đề xuất thêm index cho câu truy vấn LIKE — mà em đã chứng minh bằng EXPLAIN
> QUERY PLAN là vô dụng vì quét toàn bảng. Toàn bộ tương tác AI được ghi trong AI Audit Report
> đính kèm. Em xin kết thúc video demo tại đây, cảm ơn thầy cô và các bạn đã theo dõi."

---

## Checklist sau khi quay
- [ ] Tổng thời lượng ≥ 6 phút (kiểm tra bằng `ffprobe` hoặc Properties)
- [ ] Tool + resource monitor cùng khung hình ở mọi clip chạy test
- [ ] Giọng đọc tiếng Việt rõ ràng, không nhạc nền lớn át giọng
- [ ] Upload YouTube → chế độ **Unlisted** → dán link vào README.md và báo cáo
- [ ] Đặt tên video: `23120279 HW05 Performance Testing Demo`
