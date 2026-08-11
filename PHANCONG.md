# Phân công theo Checkpoint — Day 13 Observability

Tài liệu này cụ thể hoá 4 vai trò trong `README.md` thành 5 đầu việc độc lập để cả nhóm chốt được thứ tự "ai đợi ai". Cấu trúc file này là phụ — mọi yêu cầu kỹ thuật và evidence vẫn theo `README.md`, `CHECKPOINTS.md`, `RULES.md` và `RUBRIC.md`.

> Quy định chung (theo `README.md`):
>
> - Một người có thể giữ 2 vai trò khi nhóm ít người; **không tách thêm vai trò chỉ để chia nhỏ đầu việc**.
> - 5 đầu việc dưới đây được cố ý tách sao cho tối đa song song trong CP2 nhưng vẫn khớp 4 vai trò gốc (người giữ 2 vai sẽ rõ đầu việc cần làm).

---

## 5 đầu việc (gán vào 4 vai trò gốc)


| #        | Đầu việc                 | Gán cho vai trò (README.md)       | File chính sở hữu                                                                                |
| -------- | ------------------------ | --------------------------------- | ------------------------------------------------------------------------------------------------ |
| Hùng-V1  | Logging & PII            | Logging & PII                     | `app/logging_config.py`, `app/middleware.py`, `app/pii.py`, `config/logging_schema.json`         |
| Hoàng-V2 | Tracing & Prompt Version | Tracing & Prompt Version          | `app/tracing.py`, `app/prompt_management.py`, `app/agent.py`                                     |
| Thái-V3  | Dashboard, SLO & Alert   | Dashboard, SLO & Alert            | `config/dashboard.yaml`, `config/slo.yaml`, `config/alert_rules.yaml`, `docs/DASHBOARD_SETUP.md` |
| Trung-V4 | Incident Investigation   | Incident, Report & Demo (nửa đầu) | `app/incidents.py`, `scripts/inject_incident.py`, `app/challenge.py`                             |
| Tâm-V5   | Report & Demo            | Incident, Report & Demo (nửa sau) | `submission/REPORT.md`, `submission/evidence/`, `docs/grading-evidence.md`                       |


> Gợi ý gán người (5 người): V1↔P1, V2↔P2, V3↔P3, V4↔P4, V5↔P5.
> Gợi ý 4 người: V1↔P1, V2↔P2, V3↔P3, **P4 giữ cả V4 và V5**.
> Gợi ý 3 người: P1 = V1; P2 = V2; P3 = V3+V4+V5.
> Gợi ý 2 người: P1 = V1; P2 = V2+V3+V4+V5 (P2 chạy V3 và V4 song song sau CP1).

---



## Phụ thuộc giữa các đầu việc (ai đợi ai)

```text
CP0 setup
   │
   ▼
V1 Logging & PII  ──────►  (chặn mọi đầu việc phía sau)
   │  validate_logs.py ≥ 80/100
   │
   ├─► V2 Tracing & Prompt Version  ─┐
   │                                  ├─► V4 Incident Investigation
   └─► V3 Dashboard, SLO & Alert    ─┘            │
                                                   ▼
                                          V5 Report & Demo
```



### Bảng phụ thuộc chi tiết


| Đầu việc | Đợi ai                                                  | Lý do                                                                                                               |
| -------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| V1       | Setup xong (`/health` xanh)                             | Không có API chạy thì không có log để redact                                                                        |
| V2       | V1 (chỉ phần correlation ID + metadata)                 | Trace metadata phải lấy `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model`, `env` từ middleware log |
| V3       | V1 (validate_logs ≥ 80/100)                             | 6 panel validate từ `data/logs.jsonl`; log chưa đủ trường thì không build được đúng contract                        |
| V4       | V2 có ≥10 traces, V3 có dashboard validator `6/6 panel` | Incident chỉ có ý nghĩa khi có trace để mở và dashboard để đọc triệu chứng                                          |
| V5       | V2, V3, V4                                              | Report và evidence lấy từ output của 3 vai trên; demo là tổng hợp                                                   |




### Có thể chạy song song


| Cặp     | Song song được không?                  | Khi nào                                                                                                                                             |
| ------- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| V2 ↔ V3 | **Được** — đây là đoạn song song chính | Sau khi V1 đạt `validate_logs.py ≥ 80/100`                                                                                                          |
| V4 ↔ V5 | **Không**                              | V5 phụ thuộc evidence từ V4                                                                                                                         |
| V2 ↔ V4 | Một phần                               | V4 có thể chạy practice `inject_incident.py --scenario rag_slow` ngay từ CP2 để V5 thu thập ảnh dashboard trước/sau, không đợi challenge chính thức |
| V3 ↔ V4 | **Không**                              | V4 cần dashboard hợp lệ để đọc triệu chứng                                                                                                          |


---



## Phân công theo từng Checkpoint



### CP0 — Setup và baseline (0:00–0:30)


| #   | Đầu việc                                                                                                                         | Đầu ra                                                | Đợi ai                  |
| --- | -------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- | ----------------------- |
| V1  | Setup Python, venv, `pip install -r requirements.txt`, copy `.env.example → .env`, chạy Langfuse cloud (ưu tiên theo `SETUP.md`) | `/health` trả `ok: true`; `data/logs.jsonl` xuất hiện | —                       |
| V2  | Đọc trước `docs/PROMPT_VERSIONING.md`, đăng ký Langfuse key vào `.env`                                                           | Key hợp lệ, list project sẵn                          | V1 cài xong requirement |
| V3  | Đọc trước `config/dashboard.yaml` + `docs/DASHBOARD_SETUP.md` để hiểu 6 panel contract                                           | Note 6 panel + field + threshold                      | —                       |
| V4  | Đọc `app/incidents.py`, `scripts/inject_incident.py` và `docs/mock-debug-qa.md`                                                  | Note các scenario practice                            | V1 chạy API được        |
| V5  | Mở `submission/REPORT.md`, lập khung báo cáo, tạo `submission/evidence/`                                                         | Template rỗng                                         | —                       |


**Song song tối đa ở CP0** — tất cả chạy đồng thời trừ V2 và V4 chờ điều kiện nhỏ.

### CP1 — Logging và PII (0:30–1:30) — **nút thắt**


| #      | Đầu việc                                                                                                                               | Đầu ra                                                                                                                                 | Đợi ai           |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| **V1** | Hoàn thiện correlation ID, JSON log, metadata, redaction trong `app/logging_config.py` + `app/pii.py`; chạy `scripts/validate_logs.py` | `validate_logs.py ≥ 80/100`; log có `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model`, `env`; email/SĐT/số thẻ bị che | —                |
| V2     | **Không vào V2** — chuẩn bị nháp hàm lấy `correlation_id` từ context, đợi V1 xong                                                      | Stub sẵn                                                                                                                               | **V1**           |
| V3     | **Không vào V3** — chuẩn bị notebook/Streamlit skeleton đọc `data/logs.jsonl`, đợi log đúng schema                                     | Notebook rỗng                                                                                                                          | **V1**           |
| V4     | **Không vào V4** — xem `data/incidents.json` và các scenario                                                                           | Note scenario                                                                                                                          | **V1**           |
| V5     | Gom ảnh `/health` và kết quả baseline `validate_logs.py` đầu tiên vào `submission/evidence/`                                           | `evidence/health.png`, `evidence/validate_logs_baseline.txt`                                                                           | V1 xong baseline |


**Lưu ý CP1:** Không ai làm gì ngoài V1. V2/V3/V4/V5 chuẩn bị stub hoặc đọc tài liệu. Nút thắt này cố ý — mọi việc sau phụ thuộc log đúng.

### CP2 — Metrics, traces và dashboard (1:30–2:30) — **đoạn song song chính**


| #      | Đầu việc                                                                                                                                                                                                | Đầu ra                                                                                                                    | Đợi ai                          |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| **V2** | Tạo prompt `day13-chat` v1 (label `baseline` + `production`), v2 (label `candidate`); chạy request với `LANGFUSE_PROMPT_LABEL=baseline` rồi `candidate`; đổi label `production` sang v2; rollback về v1 | ≥10 traces có metadata; ảnh 2 prompt version; ảnh đổi label/rollback; 2 trace ID (v1 baseline, v2 candidate)              | **V1 ≥ 80/100**                 |
| **V3** | Dựng 6 panel theo `config/dashboard.yaml` từ `data/logs.jsonl`; chạy `scripts/validate_dashboard.py`; chạy `inject_incident.py --scenario rag_slow`, chụp dashboard trước/sau                           | `validate_dashboard.py` báo `HỢP LỆ: 6/6 panel`; ảnh dashboard có time range, đơn vị, threshold; ảnh trước/sau `rag_slow` | **V1 ≥ 80/100**                 |
| V4     | Chạy practice: `inject_incident.py --scenario rag_slow` rồi `load_test.py --concurrency 5`; mở trace chậm, copy correlation ID, tìm log cùng ID                                                         | 1 bản note root cause practice; correlation ID minh chứng luồng metrics → traces → logs                                   | V2 có ≥1 trace; V3 có dashboard |
| V5     | Gom evidence CP2: 2 trace ID, 2 ảnh prompt version, ảnh đổi label/rollback, kết quả `validate_dashboard.py`, ảnh dashboard, 1 ảnh trace waterfall                                                       | `submission/evidence/` đầy đủ phần CP2                                                                                    | V2, V3 xong                     |


**Song song tối đa ở CP2:**

- V2 và V3 chạy đồng thời sau khi V1 xong.
- V4 có thể bắt đầu practice ngay từ đầu CP2 song song với V2 (không cần challenge chính thức).
- V5 là consumer, lấy evidence từ V2 và V3; điền song song với V4.



### CP3 — Challenge chính thức (2:30–3:30) — **tuần tự, phối hợp chặt**


| #      | Đầu việc                                                                                                                                                                                                        | Đầu ra                                                                                   | Đợi ai                         |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------ |
| V1     | Không vào; nếu trace thiếu metadata do V1 chưa chuẩn, hỗ trợ V2 vá                                                                                                                                              | —                                                                                        | —                              |
| V2     | Mở trace challenge, lấy trace ID, kiểm tra `prompt_name`/`prompt_label`/`prompt_version`                                                                                                                        | Danh sách trace ID nghi vấn                                                              | Challenge release + V4 inject  |
| **V4** | Chạy `scripts/inject_incident.py` (challenge); chạy `python scripts/load_test.py --challenge --concurrency 5`; đọc metrics trên dashboard V3; khoanh vùng span bất thường từ trace; tìm log cùng correlation ID | Root cause + fix action + preventive measure; trace ID + log line làm bằng chứng         | Challenge release từ Lab Coach |
| V3     | Không sửa panel trong CP3; chỉ trỏ Lab Coach tới dashboard đang chạy nếu cần                                                                                                                                    | Dashboard runtime                                                                        | V3 đã xong CP2                 |
| V5     | Ghi lại root cause vào `submission/REPORT.md` mục 6; lưu evidence challenge vào `submission/evidence/`                                                                                                          | Mục 6 đầy đủ: Challenge ID, triệu chứng, trace ID, log line, root cause, fix, preventive | V4 chốt root cause             |


**Lưu ý CP3:**

- Không tự tạo hoặc sửa `config/challenge.json` (theo `RULES.md`).
- Nếu challenge chưa release → V4 dừng script theo hướng dẫn của `scripts/inject_incident.py`; V5 cập nhật report phần "challenge chưa release" và tận dụng practice `rag_slow` để demo.



### Hoàn tất — Báo cáo và demo (3:30–4:00)


| #      | Đầu việc                                                                                                                                                                     | Đầu ra                                                          | Đợi ai               |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | -------------------- |
| V1     | Kiểm tra `pytest -q`; dọn dẹp test còn TODO                                                                                                                                  | `pytest` xanh                                                   | —                    |
| V2     | Đối chiếu commit cá nhân với evidence tracing/prompt                                                                                                                         | Commit liên quan V2                                             | —                    |
| V3     | Đối chiếu commit cá nhân với evidence dashboard/SLO/alert; hoàn thiện `config/alert_rules.yaml` (đang TODO)                                                                  | Commit liên quan V3                                             | —                    |
| V4     | Đối chiếu commit cá nhân với evidence incident                                                                                                                               | Commit liên quan V4                                             | —                    |
| **V5** | Hoàn thiện `submission/REPORT.md` đủ 7 mục; rà `.env`, secret, PII; `git status --short`; lên commit SHA cuối; chuẩn bị demo theo luồng Metrics → Traces → Logs → Root cause | `REPORT.md` đầy đủ; `evidence/` đầy đủ; commit SHA; demo script | Tất cả đầu việc khác |


---



## Checklist đầu việc (khi nhóm muốn check nhanh)



### V1 — Logging & PII

- [ ] Correlation ID sinh ra ở middleware và xuyên suốt request
- [ ] JSON log có `timestamp`, `level`, `event`, `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model`, `env`
- [ ] Email, SĐT, số thẻ thử nghiệm bị redact trước khi ghi `data/logs.jsonl`
- [ ] `python scripts/validate_logs.py` đạt ≥ 80/100
- [ ] Evidence: ảnh PII trước/sau, log có correlation ID



### V2 — Tracing & Prompt Version

- [ ] Trace có metadata `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model`, `env`
- [ ] ≥10 traces trên Langfuse
- [ ] Prompt `day13-chat` có v1 (label `baseline`, `production`) và v2 (label `candidate`)
- [ ] Trace gắn đúng `prompt_name`, `prompt_label`, `prompt_version`
- [ ] Đã thực hiện đổi label `production` hoặc rollback, có ảnh evidence
- [ ] Nếu Langfuse down: trace metadata ghi đúng `prompt_source=local` hoặc `local-fallback`



### V3 — Dashboard, SLO & Alert

- [ ] 6 panel đúng `config/dashboard.yaml`: latency (p50/p95/p99), traffic, errors, cost, tokens, quality
- [ ] Time range 60 phút, refresh 30 giây (theo contract)
- [ ] Threshold/SLO line hiển thị trên ảnh dashboard
- [ ] `python scripts/validate_dashboard.py` báo `HỢP LỆ: 6/6 panel`
- [ ] Ảnh dashboard trước/sau `rag_slow`
- [ ] `config/slo.yaml` điền target thực tế của nhóm
- [ ] `config/alert_rules.yaml` thay 3 TODO bằng alert thực (severity, condition, owner, runbook)



### V4 — Incident Investigation

- [ ] Practice: `inject_incident.py --scenario rag_slow` → mở trace chậm → log cùng correlation ID
- [ ] Challenge: chạy `load_test.py --challenge --concurrency 5` (chỉ sau khi Lab Coach release)
- [ ] Root cause có bằng chứng: trace ID + log line cụ thể
- [ ] Fix action + preventive measure rõ ràng



### V5 — Report & Demo

- [ ] `submission/REPORT.md` đủ 7 mục (theo template)
- [ ] `submission/evidence/` đủ 11 loại bằng chứng (theo `SUBMISSION.md`)
- [ ] Mục 7 có commit/PR của từng thành viên khớp Git
- [ ] `git status --short` sạch; không có `.env`, secret, PII trong Git
- [ ] `python -m pytest -q` xanh
- [ ] Demo theo luồng: Metrics → Traces → Logs → Root cause

---



## Ma trận "ai đợi ai" một dòng

```text
V1 (CP1 chặt cổng) → {V2 song song V3} → V4 (khi có challenge) → V5 (gom evidence)
V2 và V3 không đợi nhau; chỉ cùng đợi V1.
V4 có thể chạy practice ngay từ CP2, không đợi challenge.
V5 là consumer cuối cùng, đợi tất cả.
```

---



## Khi có ít người hơn 5


| Quy mô  | Gán                                   | Ghi chú                                                              |
| ------- | ------------------------------------- | -------------------------------------------------------------------- |
| 2 người | P1 = V1; P2 = V2+V3+V4+V5             | Sau CP1, P2 chia thời gian: 50% V3, 30% V2, 20% V4; V5 làm cuối ngày |
| 3 người | P1 = V1; P2 = V2; P3 = V3+V4+V5       | V2 và V3 vẫn song song ở CP2                                         |
| 4 người | P1 = V1; P2 = V2; P3 = V3; P4 = V4+V5 | Phổ biến nhất, cân bằng nhất                                         |


Với 2 người, **khuyến nghị**: V2 ưu tiên chạy sau khi V3 có dashboard hợp lệ (vì V2 cần log đúng schema — đã có từ V1 — nhưng V3 cho V2 cái khung để trace có gì để "neo" vào dashboard). Ngược lại vẫn được, nhưng lúc demo sẽ vất hơn vì phải đi tìm trace mà không có dashboard dẫn.