# HƯỚNG DẪN TÁI LẬP KẾT QUẢ TRÊN MÁY CỦA BẠN (RUN_LOCAL)

> Bài làm được chạy đầy đủ và thu bằng chứng thật trên môi trường Linux (spec ở mục Hardware
> của báo cáo). Nếu bạn muốn **tái lập trên máy mình** để có bằng chứng mang hostname của bạn
> (TA đối chiếu với các bài trước), làm theo các bước dưới đây — toàn bộ script đã kèm trong bài nộp.

## 0. Yêu cầu môi trường
- Node.js ≥ 18, Python ≥ 3.10, Java ≥ 11 (cho JMeter 5.6.3), `git`
- Khoảng 30–40 phút rảnh cho 4 kịch bản (7 + 8 + 5 + 15 phút) + thời gian chuẩn bị
- **Đóng các ứng dụng nặng** trong lúc chạy để số liệu sạch

## 1. Khởi động SUT
```bash
git clone https://github.com/ttbhanh/eshop-sut.git   # hoặc fork của bạn
cd eshop-sut/backend && npm install
node server.js        # giữ nguyên terminal này, hoặc nohup node server.js &
```
> Lưu ý: mỗi lần khởi động lại, `database.js` tự DROP và re-seed toàn bộ bảng.

## 2. Đặt SUT này cạnh thư mục `hw05/`, rồi seed dữ liệu
```bash
# sửa 3 đường dẫn trong scripts/reset_lockout.js + seed_data.js + full_reset.sh
# trỏ tới backend của bạn (mặc định: /home/z/my-project/eshop-sut/backend)
node scripts/seed_data.js     # tạo 100 users + 75 products + users.csv/products.csv
```

## 3. Cài JMeter
```bash
wget https://dlcdn.apache.org/jmeter/binaries/apache-jmeter-5.6.3.tgz
tar xzf apache-jmeter-5.6.3.tgz -C ~/tools/
```

## 4. Chạy từng kịch bản (từ thư mục `hw05/`)
```bash
bash scripts/full_reset.sh                                  # trạng thái sạch + reset lockout
~/tools/apache-jmeter-5.6.3/bin/jmeter -n -t testplans/23120279_Load_20261122.jmx \
    -l results/load/23120279_Load_20261122.jtl -e -o results/load/html
# giữa các kịch bản: node scripts/reset_lockout.js  (reset khóa tài khoản)
# ...tương tự cho Stress / Spike / Soak
```
> Cách nhanh hơn: dùng `scripts/run_scenario.sh Load|Stress|Spike|Soak` (tự kèm monitor tài nguyên).
> **Quan trọng**: lệnh JMeter phải chạy từ thư mục `hw05/` (file CSV dùng đường dẫn tương đối `data/`).

## 5. Trong lúc chạy — chụp bằng chứng
- Mở `htop` (Linux/macOS) hoặc Task Manager (Windows) cạnh console JMeter → **chụp ảnh màn hình**
  cùng khung hình ở: giữa kịch bản Load, ở bậc cao nhất của Stress (phút 6–8), ở đỉnh sóng Spike.
- Chạy `screenfetch` (Linux) / `systeminfo` (Windows) → chụp lại làm hardware report
  (hostname phải trùng các bài trước của bạn).

## 6. Phân tích lại
```bash
python3 scripts/analyze_jtl.py Load Stress Spike Soak   # sinh analysis/summary_*.json
python3 scripts/make_charts.py                          # vẽ lại toàn bộ biểu đồ
```

## 7. Sau khi có kết quả riêng — cập nhật báo cáo
- Thay các bảng số liệu + ảnh chụp trong `report/23120279_HW05_Report.md` bằng số liệu máy bạn
  (giữ nguyên cấu trúc, chỉ đổi số) rồi xuất lại PDF.
- Ghi rõ thông số phần cứng thật của bạn vào bảng Hardware (mục 2.5).

## Sự khác biệt có thể gặp
- Điểm gối (knee) và max RPS sẽ **khác** — phụ thuộc CPU/đĩa của bạn; đây là điều bình thường,
  đề bài yêu cầu "threshold on your own hardware".
- Nếu Stress chưa thấy gãy ở 480 VU (máy mạnh), tăng số bậc hoặc giảm think-time còn 0ms.
