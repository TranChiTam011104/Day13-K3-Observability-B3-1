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

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
