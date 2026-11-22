# AI CRITIQUE — HW05 Performance Testing (23120279 — Nguyễn Lê Quang Kan)

**Yêu cầu đề bài (mục 10):** đoạn văn 200–300 từ phê phán AI — AI sai/bias/thiếu gì ở đâu, vì sao
AI không tự bắt được lỗi, và nguyên tắc làm việc với AI rút ra.

---

Làm việc với AI trong HW05, tôi thấy AI mạnh nhất ở khâu *sinh cấu trúc* — test plan JMeter với
correlation và assertion được tạo trong vài phút — nhưng yếu nhất ở khâu *gắn với thực tế*. AI
đề xuất 100 VU với ramp 10 giây và think-time 0 ms mà không xét phần cứng chạy cùng máy, sinh JSON
path sai (`$.user.token` thay vì `$.token`) và không hề biết SUT khóa tài khoản sau hai lần sai vì
bộ đếm tăng +2 — lỗi chỉ lộ ra khi tôi chạy pilot và đọc code. Ở khâu phân tích, AI nhầm giá trị
Max 2,8 giây thành "p95", gán nhãn HTTP 500 cho 613 lỗi vốn là HTTP 200 vượt ngưỡng Duration
Assertion, và kiên định giải thích login chậm bằng bcrypt trong khi SUT thực chất so sánh mật khẩu
thô. Cả ba lỗi đều cùng một gốc: AI làm việc trên số liệu tổng hợp và kiến thức phổ biến, không có
raw log và không có source code. Nguyên nhân sâu xa là ban đầu tôi chỉ đưa cho nó bảng dashboard —
chất lượng prompt quyết định chất lượng câu trả lời. Nguyên tắc tôi rút ra: **AI là trợ lý soạn
thảo, không phải nguồn chân lý** — mọi con số phải được truy vết về raw `.jtl`, mọi khuyến nghị
phải được kiểm chứng bằng `EXPLAIN QUERY PLAN` hoặc đọc code, và pilot run không bao giờ được bỏ
qua. Kinh nghiệm đối chiếu "AI nói — log nói" trong Task 2 cho tôi quy trình làm việc cụ thể: cung
cấp dữ liệu thô cho AI, yêu cầu trích dẫn dòng, rồi tự kiểm chứng từng trích dẫn đó.

*(285 từ)*
