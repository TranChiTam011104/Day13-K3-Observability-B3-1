# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (Final) | 30/100 (Baseline)
- Tổng số traces:
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
  ```json
  {"service": "api", "payload": {"message_preview": "What should not appear in app logs?"}, "event": "request_received", "correlation_id": "req-789deaca", "user_id_hash": "1632c29ecdec", "feature": "qa", "session_id": "s07", "env": "dev", "model": "mock", "level": "info", "ts": "2026-08-11T03:39:14.106862Z"}
  ```
- Evidence PII redaction:
  ```json
  {"service": "api", "payload": {"message_preview": "What is your refund policy? My email is [REDACTED_EMAIL]"}, "event": "request_received", "correlation_id": "req-f6c3426a", "user_id_hash": "2055254ee30a", "feature": "qa", "session_id": "s01", "env": "dev", "model": "mock", "level": "info", "ts": "2026-08-11T03:39:12.384492Z"}
  ```
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`
- Triệu chứng từ metrics: Latency p95 tăng vọt từ ~160ms lên đến 13284ms (hơn 13 giây) dưới tải concurrency = 5.
- Trace ID liên quan: *Chạy offline cục bộ không ghi nhận Trace ID trên Langfuse (Lỗi Auth 401). Đã phân tích chi tiết qua log.*
- Log line/correlation ID liên quan: `req-ee976937` (latency: 13284.6ms), `req-9dd76ee0` (latency: 13283.6ms)
- Root cause:
  1. Incident `rag_slow` kích hoạt một lệnh block đồng bộ `time.sleep(2.5)` trong hàm `retrieve` của `app/mock_rag.py`.
  2. Endpoint `/chat` ở `app/main.py` khai báo là `async def chat` nhưng lại thực thi luồng xử lý đồng bộ blocking `agent.run()`. Điều này khóa chặt FastAPI Event Loop khiến các request đồng thời bị nghẽn và phải xử lý tuần tự (mỗi request mất ~2.6s, request thứ 5 phải đợi cả 4 request trước chạy xong, tổng cộng mất hơn 13s).
- Fix action: Chuyển đổi định nghĩa endpoint thành hàm đồng bộ thông thường `def chat(...)` thay vì `async def` để FastAPI tự động đẩy vào các luồng riêng biệt trong Thread Pool, hoặc chuyển đổi toàn bộ thư viện sang phi tuần tự (async/await) hoàn toàn.
- Preventive measure: Thiết lập static analysis/linting để cấm sử dụng các hàm blocking đồng bộ trong hàm `async def` và cấu hình alert cảnh báo sớm khi latency p95 > 2s.


## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
