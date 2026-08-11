# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: B3-1
- Repository URL: https://github.com/TranChiTam011104/Day13-K3-Observability-B3-1.git
- Commit SHA cuối: `168c2fc`
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

### Challenge ID
`day13-k3-observability-v1` (Cohort: K3)

### Triệu chứng từ metrics
- **Latency tăng vọt**: Từ ~150ms (normal) lên ~12,000-15,000ms (incident)
- **Vượt ngưỡng**: 2000ms threshold bị vượt xa ~6-7 lần
- **5/5 requests** trong challenge đều có latency > 2000ms
- Latency breakdown:
  - `req-530fa146`: 12369.7ms (HTTP), 4309ms (server-side)
  - `req-b6280f50`: 15027.0ms (HTTP), 2651ms (server-side)
  - `req-bc3fcd0b`: 15025.9ms (HTTP), 2650ms (server-side)
  - `req-9d7ab041`: 15027.3ms (HTTP), 2651ms (server-side)
  - `req-8f242549`: 15025.0ms (HTTP), 2651ms (server-side)

### Trace ID liên quan
- Primary: `req-530fa146` (challenge k3-challenge-s05)
- Secondary: `req-b6280f50`, `req-bc3fcd0b`, `req-9d7ab041`, `req-8f242549`

### Log line/correlation ID liên quan
```json
{"service": "api", "event": "request_received", "correlation_id": "req-530fa146", "session_id": "k3-challenge-s05", "feature": "refund", "user_id_hash": "5da42a0d3d01", "level": "info", "ts": "2026-08-11T05:48:06.113585Z"}
{"service": "api", "event": "response_sent", "latency_ms": 4309, "correlation_id": "req-530fa146", "session_id": "k3-challenge-s05", "feature": "refund", "level": "info", "ts": "2026-08-11T05:48:10.508179Z"}
```
Incident enable log:
```json
{"service": "control", "event": "incident_enabled", "payload": {"name": "rag_slow"}, "correlation_id": "req-ab7bb3ee", "level": "warning", "ts": "2026-08-11T05:47:48.106982Z"}
```

### Root cause
**Head-of-Line Blocking do Synchronous Sleep trong Async Handler**

Khi incident `rag_slow` được kích hoạt, hàm `retrieve()` trong `app/mock_rag.py` thực hiện:
```python
if STATE["rag_slow"]:
    time.sleep(2.5)  # Blocking synchronous sleep!
```

**Vấn đề**: Route handler FastAPI được định nghĩa bằng `async def`, nhưng `time.sleep()` là blocking operation. Lệnh sleep đồng bộ này **block toàn bộ Event Loop**, khiến:
1. Request đầu tiên bị trễ thêm ~2.5s
2. Các request đồng thời khác phải đợi (Head-of-Line Blocking)
3. Mỗi request tiếp theo tích lũy thêm ~2.5s chờ đợi Event Loop

**Mã nguồn gây lỗi** (`app/mock_rag.py:17-18`):
```python
if STATE["rag_slow"]:
    time.sleep(2.5)  # ← Blocking!
```

### Fix action
**Thay `time.sleep()` bằng `asyncio.sleep()` trong async context**:

```python
import asyncio

async def retrieve_async(message: str) -> list[str]:
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        await asyncio.sleep(2.5)  # ← Non-blocking!
    # ... rest of logic
```

Hoặc sử dụng thread pool cho blocking operations:
```python
await asyncio.to_thread(time.sleep, 2.5)
```

### Preventive measure
1. **Code Review Checklist**: Tất cả `async def` handlers phải tránh blocking operations (`time.sleep`, synchronous I/O)
2. **Static Analysis**: Cấu hình linter (ruff, pylint) để cảnh báo `time.sleep()` trong async functions
3. **Alert Rule**: Alert khi `latency_p95 > 2000ms` với thời gian khôi phục tự động
4. **Load Testing**: Thêm load test với `--concurrency 5` vào CI pipeline để phát hiện race conditions
5. **Documentation**: Ghi chú rõ ràng trong `docs/ARCHITECTURE.md` về việc sử dụng async/await đúng cách

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Hùng-V1 | Hoàn thiện Correlation ID, JSON log format, redaction PII | Commit `ea214e6` | Cách cấu hình structlog và middleware để propagate correlation ID |
| Hoàng-V2 | Cấu hình tích hợp tracing Langfuse và Prompt Version | Commit `f1a02e5` | Cách kết nối và quản lý prompt versioning với Langfuse |
| Thái-V3 | Dựng 6 panel cho dashboard.yaml và cấu hình alerts | Commit `5f7e4ef` | Cách xây dựng dashboard contract và thiết kế runbook cho alerts |
| Trung-V4 | Điều tra sự cố Practice & Challenge, viết báo cáo nguyên nhân gốc rễ | Commit chứa báo cáo này | Cơ chế Event Loop của FastAPI và hiện tượng Head-of-Line blocking |
| Tâm-V5 | Hoàn thiện tài liệu evidence, chuẩn bị demo | Commit chứa báo cáo này | Cách thu thập bằng chứng đầy đủ từ logs và metrics phục vụ báo cáo |
