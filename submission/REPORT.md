# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

<<<<<<< HEAD
- Tên nhóm: B3-1
- Repository URL: https://github.com/TranChiTam011104/Day13-K3-Observability-B3-1.git
- Commit SHA cuối:
=======
- Tên nhóm: Nhóm 5 thành viên (TRUNG-V4)
- Repository URL: https://github.com/TranChiTam011104/Day13-K3-Observability-B3-1
- Commit SHA cuối: 5f7e4efebccb6916e4974524fc86b2300e1e33a2
>>>>>>> 788528c83fe512f55c0ca3951b30d4cbbf1df6ee
- Thành viên và vai trò:
  - Hùng (V1) — Logging & PII
  - Hoàng (V2) — Tracing & Prompt Version
  - Thái (V3) — Dashboard, SLO & Alert
  - Trung (V4) — Incident Investigation
  - Tâm (V5) — Report & Demo

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100
- Tổng số traces: ~10 traces (được tạo cục bộ thông qua các request baseline)
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: [config/dashboard.yaml](file:///g:/ALL%20OF%20G/AI%20IN%20ACTION%20VINUNI/LAB/Day13_2A202501687_DinhQuocTrung/Day13-K3-Observability-B3-1/config/dashboard.yaml)

## 3. Logging và tracing

- Evidence correlation ID:
  - Correlation ID được tạo bằng `CorrelationIdMiddleware` theo cấu trúc `req-<8-char-hex>` (ví dụ: `req-fa18dd70`).
  - Request log:
    ```json
    {"service": "api", "payload": {"message_preview": "What is your refund policy? My email is [REDACTED_EMAIL]"}, "event": "request_received", "user_id_hash": "2055254ee30a", "env": "dev", "correlation_id": "req-fa18dd70", "feature": "qa", "session_id": "s01", "model": "mock", "level": "info", "ts": "2026-08-11T03:38:04.255485Z"}
    ```
  - Response log:
    ```json
    {"service": "api", "latency_ms": 150, "tokens_in": 36, "tokens_out": 108, "cost_usd": 0.001728, "quality_score": 0.9, "payload": {"answer_preview": "Starter answer. Teams should improve this output logic and add better quality ch..."}, "event": "response_sent", "user_id_hash": "2055254ee30a", "env": "dev", "correlation_id": "req-fa18dd70", "feature": "qa", "session_id": "s01", "model": "mock", "level": "info", "ts": "2026-08-11T03:38:04.503873Z"}
    ```
- Evidence PII redaction:
  - Email, số điện thoại Việt Nam, và số thẻ tín dụng được che thành công trong file logs:
    - Email -> `[REDACTED_EMAIL]` (dòng 2)
    - Phone -> `[REDACTED_PHONE_VN]` (dòng 10)
    - Credit Card -> `[REDACTED_CREDIT_CARD]` (dòng 18)
- Evidence trace waterfall:
  - Bản ghi metadata và logs cục bộ hoạt động tốt làm cơ sở hạ tầng fallback khi không kết nối được tới Langfuse cloud.
- Giải thích một span đáng chú ý:
  - Span `retrieve` (truy xuất Vector Store) trong RAG: Khi bật incident `rag_slow`, span này bị trễ thêm 2.5s do lệnh `time.sleep(2.5)`. Do route handler FastAPI được định nghĩa bằng `async def`, lệnh sleep đồng bộ này đã block toàn bộ Event Loop chính, khiến các request đồng thời khác bị trễ tích lũy (Head-of-Line Blocking).

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: `local-v1` / `production`
- Version/label candidate: `local-v1` / `candidate`
- Trace ID của mỗi version: Traces được map qua metadata trong log `prompt_source=local-fallback` với version `local-v1`.
- Bằng chứng đổi label hoặc rollback: Hoạt động tự động thông qua cơ chế fallback an toàn của ứng dụng khi kết nối Langfuse bị gián đoạn.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
  - Trả về `HỢP LỆ: 6/6 panel có trong dashboard contract`.
  - Bằng chứng được lưu tại [validate_dashboard_result.txt](file:///g:/ALL%20OF%20G/AI%20IN%20ACTION%20VINUNI/LAB/Day13_2A202501687_DinhQuocTrung/Day13-K3-Observability-B3-1/submission/evidence/validate_dashboard_result.txt).
- Evidence dashboard:
  - Bao gồm 6 panel chính: latency percentiles (p50/p95/p99), traffic count, error rates, costs, tokens (in/out), and quality score.
- SLO đã chọn và lý do:
  - Latency P95 <= 3000ms với target 99.5%: Đảm bảo trải nghiệm thời gian thực cho người dùng cuối.
  - Error rate <= 2% với target 99.0%: Hạn chế tối đa lỗi hệ thống.
  - Daily cost <= 2.5 USD với target 100.0%: Quản lý ngân sách gọi API LLM.
- Alert rules và runbook:
  - Đã được cập nhật đầy đủ trong [config/alert_rules.yaml](file:///g:/ALL%20OF%20G/AI%20IN%20ACTION%20VINUNI/LAB/Day13_2A202501687_DinhQuocTrung/Day13-K3-Observability-B3-1/config/alert_rules.yaml) và hướng dẫn xử lý trong [docs/alerts.md](file:///g:/ALL%20OF%20G/AI%20IN%20ACTION%20VINUNI/LAB/Day13_2A202501687_DinhQuocTrung/Day13-K3-Observability-B3-1/docs/alerts.md).

## 6. Điều tra challenge

*Chưa thực hiện - Đang dừng ở giai đoạn CP2 để hoàn thành thực nghiệm practice và xây dựng các chỉ số*

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Hùng-V1 | Hoàn thiện Correlation ID, JSON log format, redaction PII | Commit `ea214e6` | Cách cấu hình structlog và middleware để propagate correlation ID |
| Hoàng-V2 | Cấu hình tích hợp tracing Langfuse và Prompt Version | Commit `f1a02e5` | Cách kết nối và quản lý prompt versioning với Langfuse |
| Thái-V3 | Dựng 6 panel cho dashboard.yaml và cấu hình alerts | Commit `5f7e4ef` | Cách xây dựng dashboard contract và thiết kế runbook cho alerts |
| Trung-V4 | Điều tra sự cố Practice & Challenge, viết báo cáo nguyên nhân gốc rễ | Commit chứa báo cáo này | Cơ chế Event Loop của FastAPI và hiện tượng Head-of-Line blocking |
| Tâm-V5 | Hoàn thiện tài liệu evidence, chuẩn bị demo | Commit chứa báo cáo này | Cách thu thập bằng chứng đầy đủ từ logs và metrics phục vụ báo cáo |
