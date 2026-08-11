# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Nhóm 5 thành viên (TRUNG-V4)
- Repository URL: https://github.com/TranChiTam011104/Day13-K3-Observability-B3-1
- Commit SHA cuối: 5f7e4efebccb6916e4974524fc86b2300e1e33a2 (và commit chứa báo cáo này)
- Thành viên và vai trò:
  - Hùng-V1: Logging & PII
  - Hoàng-V2: Tracing & Prompt Version
  - Thái-V3: Dashboard, SLO & Alert
  - Trung-V4 (tôi): Incident Investigation
  - Tâm-V5: Report & Demo

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100
- Tổng số traces: ~25 traces (tạo cục bộ thông qua client và load tests)
- Số PII leak còn lại: 0 (Đã kiểm tra qua `validate_logs.py` không còn leak)
- Link/đường dẫn dashboard: [config/dashboard.yaml](file:///g:/ALL%20OF%20G/AI%20IN%20ACTION%20VINUNI/LAB/Day13_2A202501687_DinhQuocTrung/Day13-K3-Observability-B3-1/config/dashboard.yaml) (Validator trả về 6/6 panel hợp lệ)

## 3. Logging và tracing

- Evidence correlation ID:
  - Correlation ID được tạo tự động bằng `CorrelationIdMiddleware` dưới định dạng `req-<8-char-hex>` (ví dụ: `req-fa18dd70`).
  - Request log nhận được:
    ```json
    {"service": "api", "payload": {"message_preview": "What is your refund policy? My email is [REDACTED_EMAIL]"}, "event": "request_received", "user_id_hash": "2055254ee30a", "env": "dev", "correlation_id": "req-fa18dd70", "feature": "qa", "session_id": "s01", "model": "mock", "level": "info", "ts": "2026-08-11T03:38:04.255485Z"}
    ```
  - Response log trả về:
    ```json
    {"service": "api", "latency_ms": 150, "tokens_in": 36, "tokens_out": 108, "cost_usd": 0.001728, "quality_score": 0.9, "payload": {"answer_preview": "Starter answer. Teams should improve this output logic and add better quality ch..."}, "event": "response_sent", "user_id_hash": "2055254ee30a", "env": "dev", "correlation_id": "req-fa18dd70", "feature": "qa", "session_id": "s01", "model": "mock", "level": "info", "ts": "2026-08-11T03:38:04.503873Z"}
    ```
- Evidence PII redaction:
  - Khi người dùng cung cấp thông tin nhạy cảm, dữ liệu được che trước khi ghi vào log file `data/logs.jsonl`.
  - Email được che thành `[REDACTED_EMAIL]` (xem dòng log bên trên).
  - Số điện thoại Việt Nam được che thành `[REDACTED_PHONE_VN]`.
  - Số thẻ tín dụng được che thành `[REDACTED_CREDIT_CARD]`.
- Evidence trace waterfall:
  - Hệ thống sử dụng thư viện Langfuse để tracing. Vì không cấu hình API Key đám mây, hệ thống tự động ghi nhận cục bộ thông qua metadata và logs.
- Giải thích một span đáng chú ý:
  - Trong sự cố `rag_slow`, span `retrieve` (truy xuất Vector Store) bị block đồng bộ 2.5s do lệnh `time.sleep(2.5)`. Nó trở thành điểm thắt nút cổ chai (bottleneck) khiến tổng độ trễ xử lý tăng vọt và Event Loop của FastAPI bị block hoàn toàn.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: `local-v1` với label `production`
- Version/label candidate: `local-v1` với label `candidate`
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

- Challenge ID: `day13-k3-observability-v1`
- Triệu chứng từ metrics:
  - Phản hồi từ client bị trễ nặng khi chịu tải đồng thời (concurrency = 5), thời gian phản hồi trung bình đo từ client lên tới **~13.2 giây**, vi phạm nghiêm trọng SLO latency (3 giây).
  - Tuy nhiên, độ trễ đo từ server-side trong log (`response_sent.latency_ms`) của mỗi request chỉ là **~2650ms**.
- Trace ID liên quan:
  - Nhận diện qua Correlation ID của các request challenge: `req-2f15e4ba`, `req-529b93f6`, `req-0df0c311`, `req-d61309ac`, `req-a56422c0`.
- Log line/correlation ID liên quan:
  - Dòng log tiêu biểu:
    ```json
    {"service": "api", "latency_ms": 2650, "tokens_in": 34, "tokens_out": 111, "cost_usd": 0.001767, "quality_score": 0.8, "payload": {"answer_preview": "Starter answer. Teams should improve this output logic and add better quality ch..."}, "event": "response_sent", "user_id_hash": "5da42a0d3d01", "env": "dev", "correlation_id": "req-2f15e4ba", "feature": "refund", "session_id": "k3-challenge-s05", "model": "mock", "level": "info", "ts": "2026-08-11T03:40:22.150673Z"}
    ```
- Root cause:
  - FastAPI handler `/chat` là hàm `async def` chạy trên luồng Event Loop chính.
  - Sự cố `rag_slow` đã kích hoạt lệnh block đồng bộ `time.sleep(2.5)` trong hàm `retrieve()` của [app/mock_rag.py](file:///g:/ALL%20OF%20G/AI%20IN%20ACTION%20VINUNI/LAB/Day13_2A202501687_DinhQuocTrung/Day13-K3-Observability-B3-1/app/mock_rag.py). Lệnh ngủ đồng bộ này chặn cứng toàn bộ Event Loop chính, khiến các request đồng thời khác không thể bắt đầu xử lý và phải đứng đợi trong hàng đợi của Event loop (gây ra Head-of-Line Blocking).
  - Điều này giải thích tại sao độ trễ đo bên trong từng request chỉ là ~2650ms (vì timer chỉ bắt đầu chạy khi request được Event loop xử lý), nhưng từ góc nhìn client, độ trễ bị cộng dồn thành ~13.2 giây.
- Fix action:
  - Đổi định nghĩa hàm `retrieve()` thành bất đồng bộ: `async def retrieve(...)`.
  - Sử dụng `await asyncio.sleep(2.5)` thay thế cho `time.sleep(2.5)` để nhường Event Loop cho các request khác chạy đồng thời.
  - Hoặc nếu thư viện RAG bắt buộc chạy đồng bộ, bọc nó lại bằng thread pool: `await anyio.to_thread.run_sync(retrieve, message)`.
- Preventive measure:
  - Nghiêm cấm dùng bất cứ thư viện block đồng bộ nào (time.sleep, requests đồng bộ) trực tiếp trong route `async def` của FastAPI.
  - Viết concurrency unit tests và load tests chạy tự động trong CI/CD để phát hiện sớm hiện tượng block Event Loop.

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Hùng-V1 | Hoàn thiện Correlation ID, JSON log format, redaction PII | Commit `ea214e6` | Cách cấu hình structlog và middleware để propagate correlation ID |
| Hoàng-V2 | Cấu hình tích hợp tracing Langfuse và Prompt Version | Commit `f1a02e5` | Cách kết nối và quản lý prompt versioning với Langfuse |
| Thái-V3 | Dựng 6 panel cho dashboard.yaml và cấu hình alerts | Commit `5f7e4ef` | Cách xây dựng dashboard contract và thiết kế runbook cho alerts |
| Trung-V4 | Điều tra sự cố Practice & Challenge, viết báo cáo nguyên nhân gốc rễ | Commit chứa báo cáo này | Cơ chế Event Loop của FastAPI và hiện tượng Head-of-Line blocking |
| Tâm-V5 | Hoàn thiện tài liệu evidence, chuẩn bị demo | Commit chứa báo cáo này | Cách thu thập bằng chứng đầy đủ từ logs và metrics phục vụ báo cáo |
