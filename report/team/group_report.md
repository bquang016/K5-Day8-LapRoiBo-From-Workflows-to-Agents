# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: LapRoiBo (`K5-Day8-LapRoiBo-From-Workflows-to-Agents`)
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 6c47b9e

## 2. Mục tiêu và cách tiếp cận

Bài toán LogiX-VN yêu cầu xây dựng quy trình xử lý khiếu nại hoàn phí vận chuyển (`claim`) dưới **4 kiến trúc khác nhau** (`workflow`, `single`, `orchestrator`, `swarm`), giữ nguyên chữ ký `run_claim` và cùng chịu kiểm soát bởi một lớp **Host** duy nhất (`policy.py`, `durability.py`), nhằm đo đạc và chọn kiến trúc **ít tự chủ nhất nhưng vẫn hoàn thành tốt công việc**.

Nhóm 4 người chia việc song song theo kiến trúc và hạ tầng kiểm thử:
1. **Bùi Đăng Quang (`workflow + integration`):** cài đặt Shape A (`workflow.py`), thiết lập tích hợp và test integration.
2. **Phạm Duy Đức (`single`):** cài đặt Shape B (`single.py`) dùng vòng `run_react` giới hạn 8 bước và test kiểm tra ticket sai sự thật.
3. **Trương Hoàng Tùng (`orchestrator + handoff`):** cài đặt Shape C (`orchestrator.py`) dùng `make_handoff` + `run_readonly_investigators` và bộ test handoff/cap/crash.
4. **Đỗ Hoàng Phúc (`ledger + evaluation`):** kiểm chứng độ bền `refund_ledger`, viết test cho `durability` và `metrics`, chạy `crash_test`, chạy `benchmark` 4 shape, thực hiện ablation và tổng hợp số liệu báo cáo.

Thứ tự triển khai: kiểm tra cổng host (`pytest -q`) → viết song song 3 shape và unit test riêng → tích hợp lên `main` kiểm tra toàn bộ ma trận `student` (`248 passed`) → chạy `crash_test` (`20/20`) và `benchmark` → chọn kiến trúc và hoàn thiện hồ sơ.

## 3. Giải pháp

Cả ba shape do nhóm viết đều tuân thủ chặt chẽ ranh giới **Code vs Model** ([docs/architecture.md](../../docs/architecture.md)):
- **Code quyết định hoàn toàn:** kiểm tra chủ sở hữu đơn hàng (`principal_id`), lọc policy hiệu lực (`is_current` và `effective_date <= 2026-11-15`), tính số tiền đề xuất bằng `compute_compensation`, kiểm tra approval (`approval_id` khớp `claim_id`, còn hạn, status `valid`), tính trần hoàn tiền theo đơn (`per-order cap`) và đảm bảo idempotency (`refund:{claim_id}`) trong transaction SQLite `BEGIN IMMEDIATE` qua `durability.issue_refund`.
- **Chi tiết 3 shape:**
  - **Shape A (`workflow` — `src/lab8/shapes/workflow.py`):** Thực hiện tuần tự bằng Python: `get_claim_view` → kiểm tra `order_id` (`needs_info`) → `lookup_order` (`escalated` nếu không thấy hoặc sai principal) → `compute_compensation` trên order row (bỏ qua số ngày ghi trong ticket) → nếu `quote <= 0` trả `denied`, nếu `quote > 0` truyền **full quote** và `crash_at` vào `durability.issue_refund` (không nuốt `InjectedCrash`).
  - **Shape B (`single` — `src/lab8/shapes/single.py`):** Dùng `lab8.runtime.run_react(..., max_steps=8)` gọi `MockLLM` (`complete`) ở mỗi bước quyết định, chỉ cấp các read tool (`get_claim_view`, `lookup_order`, `compute_compensation`). Vòng lặp tuyệt đối không có tool ghi; sau khi loop kết thúc mới chuyển full quote cho `durability.issue_refund`.
  - **Shape C (`orchestrator` — `src/lab8/shapes/orchestrator.py`):** Đọc `get_claim_view`, đóng gói `make_handoff(..., facts={}, allowed_tools=["lookup_order", "lookup_policy", "lookup_refund_history", "compute_compensation"])` giao cho `run_readonly_investigators`. Investigator chỉ có tool đọc, không nhận write registry. Orchestrator nhận lại quote và là nơi duy nhất gọi `durability.issue_refund`.
- **Sanitize & Trace contract v1:** Cả ba shape không đưa `parent_secret`, `raw_headers`, nội dung `ticket` thô, hay PII của order (`phone`, `address`, `item_name`, `internal_note`) vào handoff hay trace JSON. Mọi nhánh trả về (kể cả `needs_info`, `escalated`, `denied`, `failed` và trước khi `InjectedCrash` thoát ra) đều ghi file `traces/<run_id>.json` đúng schema `{"run_id": ..., "events": [...]}` qua `lab8.trace.Trace` và `finish()`.

## 4. Kết quả

Số liệu tổng hợp từ `src/reports/benchmark.json` (14 claim × 5 seed `11,22,33,44,55` = 70 trial mỗi shape) và `src/reports/crash.json`:

| Shape | Trials | Pass rate | Pass^5 | Seed min–max | Seed variance | Cost/success (VND) | Total cost (VND) | Mean steps | p95 steps |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `workflow` | 70 | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 1950.00 | 1.86 | 2.0 |
| `single` | 70 | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 32.10 | 2247.20 | 3.79 | 4.0 |
| `orchestrator` | 70 | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 55.71 | 3900.00 | 5.36 | 6.0 |
| `swarm` | 70 | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 3420.12 | 2.80 | 3.0 |

- **Kiểm thử chức năng & cổng host:**
  - Cổng host (`python -m pytest -q`): `64 passed` (bao gồm 54 test host gốc và 10 test mới do 4 thành viên bổ sung).
  - Ma trận public T01–T14 (`python -m pytest -q -m student -o addopts=`): `248 passed` (cả `workflow`, `single`, `orchestrator` pass 62/62; `swarm` ghi nhận đúng 1 expected miss ở `C-002` seed `55` với lỗi `status resolved != denied`).
- **Crash safety (`src/reports/crash.json`):** `20/20` (`CR-01` đến `CR-20` đều `passed: true`, gồm 17 điểm crash, retry conflict, thiếu approval và `swarm_after_effect_before_checkpoint`).
- **Tự kiểm `student_drop/`:** Chưa có thư mục `student_drop/` trong repo khi chạy báo cáo.

Quyết định kiến trúc chốt chọn **`workflow`** và lý do chi tiết xem tại `report/team/decision_adr.md`. Phiếu nghiên cứu R1 và kết quả ablation xem tại `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

1. **Khởi tạo môi trường PowerShell trên Windows:** Khi chạy kích hoạt `.venv` trên Windows PowerShell có thể gặp lỗi chính sách thực thi script (`running scripts is disabled`), đã xử lý bằng `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` hoặc gọi trực tiếp `.\.venv\Scripts\python.exe`.
2. **Ranh giới truyền full quote cho `issue_refund` (T13, T14):** Ban đầu dễ nhầm là phải tự trừ phần đã hoàn trước đó (`lookup_refund_history`), nhưng `durability.issue_refund` tự đọc lại tổng tiền đã hoàn bên trong transaction ghi. Nhờ giữ đúng quy ước truyền **full quote** và không nuốt `InjectedCrash`, cả 3 shape đều pass trọn vẹn T11–T14.
3. **Đồng bộ nhiều nhánh Git của 4 thành viên:** Cả 4 thành viên phát triển trên các nhánh riêng (`quang`, `Single`, `tung/orchestrator_handoff`, `feat/ledger-evaluation`) và hợp nhất qua Pull Request lên `main`, giữ `TEAM.md` sạch trước khi tích hợp cuối để tránh conflict.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và 4 báo cáo cá nhân tại `report/team/`:
- `report/team/2A202603640_BuiDangQuang.md`
- `report/team/2A202603611_PhamDuyDuc.md`
- `report/team/2A202603651_TruongHoangTung.md`
- `report/team/2A202603652_DoHoangPhuc.md`

## 7. Hạn chế và hướng cải thiện

- `MockLLM` không phải model sản xuất (sinh text deterministic từ hash và trích xuất regex đơn giản); `latency` là `unavailable` và chi phí VND là chi phí mô phỏng theo `config/pricing.yaml`.
- Bộ public mới gồm 14 claim (70 trial/shape), chưa bao phủ hết các biến thể ngôn ngữ hoặc ca biên phức tạp trên 40 hidden claim.
- Nếu mở rộng sang môi trường thật có ticket đa nghĩa cần phân loại ý định phức tạp hoặc cần đối chiếu dữ liệu từ nhiều hệ thống độc lập, có thể bổ sung tầng tiền xử lý dữ liệu có kiểm chứng hoặc kết hợp human-in-the-loop mà vẫn giữ nguyên cổng `durability.issue_refund` bằng code.

## 8. Tài liệu tham khảo

1. Tài liệu nội bộ Lab 8: `README.md`, `CHECKPOINTS.md`, `RUBRIC.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`.
2. Google Research (2026), *Towards a Science of Scaling Agent Systems* (tham chiếu trong `report/team/research_card.md` và tài liệu bài giảng Lab 8).
