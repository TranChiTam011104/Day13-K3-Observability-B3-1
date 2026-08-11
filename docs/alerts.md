# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: LatencyP95Exceeded
- Severity: critical
- SLI/SLO liên quan: latency_p95_ms <= 3000ms
- Điều kiện và thời gian duy trì: latency_p95_ms > 3000ms trong 1 phút.
- Ảnh hưởng tới người dùng: Phản hồi từ chatbot bị trễ nặng, người dùng phải chờ lâu hoặc bị timeout.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra endpoint `/health` xem có incident `rag_slow` nào đang bật hay không.
  2. Mở trace trên Langfuse, sắp xếp theo độ trễ giảm dần để xác định span (RAG retrieve hay LLM generate) gây trễ chính.
  3. Tìm kiếm log theo `correlation_id` của request bị trễ để kiểm tra xem có lỗi block Event Loop trong FastAPI hay không.
- Mitigation tạm thời:
  - Tắt incident bằng lệnh: `python scripts/inject_incident.py --disable`.
  - Khởi động lại FastAPI server để làm sạch hàng đợi Event Loop.
- Owner: Thai-V3

## Alert 2

- Tên: ErrorRateHigh
- Severity: warning
- SLI/SLO liên quan: error_rate_pct <= 2%
- Điều kiện và thời gian duy trì: error_rate_pct > 2% trong 2 phút.
- Ảnh hưởng tới người dùng: Người dùng liên tục gặp lỗi hệ thống (HTTP 500) hoặc không nhận được câu trả lời từ chatbot.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra log `data/logs.jsonl` tìm các dòng có `event == "request_failed"` để xác định `error_type` và chi tiết lỗi.
  2. Kiểm tra xem incident `tool_fail` có đang được kích hoạt ở `/health` hay không.
  3. Kiểm tra kết nối mạng tới mô hình LLM hoặc Vector Database.
- Mitigation tạm thời:
  - Nếu do incident `tool_fail`, tắt nó bằng cách disable incident.
  - Sử dụng local model hoặc cơ chế fallback (như cache hoặc câu trả lời mặc định) để tránh trả về HTTP 500 cho người dùng.
- Owner: Thai-V3

## Alert 3

- Tên: CostSpikeAlert
- Severity: warning
- SLI/SLO liên quan: daily_cost_usd <= 2.5 USD
- Điều kiện và thời gian duy trì: total_cost_usd > 2.5 USD trong 5 phút.
- Ảnh hưởng tới người dùng: Không ảnh hưởng trực tiếp đến trải nghiệm người dùng, nhưng gây lãng phí ngân sách lớn và có thể làm cạn kiệt tài khoản API key.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra tổng lượng token tiêu thụ (`tokens_in`, `tokens_out`) trong log xem có tăng đột biến không.
  2. Xem các request có kích thước prompt lớn bất thường và xác định `user_id_hash` hoặc `session_id` đang thực hiện các request này.
  3. Kiểm tra xem incident `cost_spike` có đang bật không.
- Mitigation tạm thời:
  - Disable incident `cost_spike` nếu đang bật.
  - Tạm thời khóa hoặc giới hạn tần suất (rate-limit) đối với `user_id_hash` đang gửi prompt quá lớn hoặc spam liên tục.
- Owner: Thai-V3
