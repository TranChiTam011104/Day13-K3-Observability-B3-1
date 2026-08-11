# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: high_latency_p95
- Severity: warning
- SLI/SLO liên quan: latency_p95_ms (SLO < 3000ms)
- Điều kiện và thời gian duy trì: latency_p95_ms > 2000 cho 5m
- Ảnh hưởng tới người dùng: Ứng dụng phản hồi chậm, trải nghiệm người dùng giảm sút.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra dashboard xem có sự gia tăng đột biến về thời gian xử lý (latency percentiles).
  2. Tra cứu logs để kiểm tra xem có incident nào đang được kích hoạt (như `rag_slow`).
  3. Mở Langfuse trace để tìm span nào đang tốn nhiều thời gian nhất trong luồng xử lý.
- Mitigation tạm thời: Tắt incident đang kích hoạt hoặc chuyển sang chế độ fallback cục bộ (local fallback) để tránh gọi vector store bị chậm.
- Owner: Thái-V3

## Alert 2

- Tên: high_error_rate
- Severity: critical
- SLI/SLO liên quan: error_rate_pct (SLO < 2%)
- Điều kiện và thời gian duy trì: error_rate_pct > 2% trong 5m
- Ảnh hưởng tới người dùng: Người dùng nhận phản hồi lỗi 500 từ hệ thống, chat bị gián đoạn.
- Ba bước kiểm tra đầu tiên:
  1. Xem dashboard để xác định tỷ lệ lỗi hiện tại.
  2. Tra cứu logs tìm các bản ghi lỗi (`request_failed`) để lấy `error_type` và chi tiết thông báo lỗi.
  3. Tìm kiếm correlation ID liên quan để tái hiện lỗi cục bộ.
- Mitigation tạm thời: Rollback phiên bản deploy gần nhất nếu lỗi do code mới, hoặc kích hoạt mạch ngắt (circuit breaker) cho dịch vụ bên thứ ba bị lỗi.
- Owner: Thái-V3

## Alert 3

- Tên: total_cost_spike
- Severity: warning
- SLI/SLO liên quan: daily_cost_usd (SLO < 2.5 USD)
- Điều kiện và thời gian duy trì: total_cost_usd > 2.5 USD
- Ảnh hưởng tới người dùng: Nguy cơ cạn kiệt ngân sách API dẫn đến dừng dịch vụ toàn hệ thống.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra panel chi phí (Cost over time) để xác định xem chi phí tăng từ thời điểm nào.
  2. Truy vấn logs lọc theo lượng token lớn nhất hoặc user tiêu tốn nhiều chi phí nhất.
  3. Kiểm tra xem ứng dụng có bị lặp truy vấn vô hạn hoặc tải lên tài liệu quá lớn không.
- Mitigation tạm thời: Áp dụng rate limiting chặt hơn cho user spam, hoặc tạm thời chuyển đổi sang model có chi phí rẻ hơn (như Claude Haiku/GPT-4o-mini).
- Owner: Thái-V3

