# Báo cáo cá nhân — 2A202603640_BuiDangQuang

## 1. Thông tin thành viên

- Họ tên: Bùi Đăng Quang
- MSSV: 2A202603640
- Email: 26ai.quangbd2@vinuni.edu.vn
- GitHub: bquang016

## 2. Phần việc phụ trách

- **Vai trò:** `workflow + integration`
- **Phụ trách kỹ thuật Shape A (Workflow):** Hiện thực hoá toàn bộ logic deterministic cho `src/lab8/shapes/workflow.py`, tuân thủ các quy tắc nghiệp vụ LogiX-VN, xử lý approval binding, per-order refund cap, an toàn khi crash và ghi trace chuẩn Trace contract v1.
- **Phụ trách Integration:** Kiểm soát chất lượng cổng host (`pytest -q`), điều phối tích hợp các shape của nhóm, thiết lập môi trường và cấu hình test suite ban đầu.

## 3. Đóng góp cụ thể

- **Hiện thực Shape A (`src/lab8/shapes/workflow.py`):**
  - Đọc claim thông qua projection an toàn `get_claim_view()` nhằm ngăn chặn rò rỉ `parent_secret`.
  - Kiểm tra `order_id` hợp lệ, trả trạng thái `needs_info` nếu thiếu, không parse dữ liệu từ câu chữ ticket.
  - Kiểm tra quyền sở hữu đơn hàng của principal qua `lookup_order()`, leo thang `escalated` nếu đơn không thuộc về khách hàng (giữ bí mật PII).
  - Định giá bồi thường chính xác qua `compute_compensation()`, tuyệt đối không dùng model LLM để tính tiền hay quyết định số tiền hoàn.
  - Tích hợp cổng host `durability.issue_refund()`: gửi toàn bộ quote đầy đủ, host tự kiểm tra approval và trừ phần đã hoàn trước đó (`order_already_refunded`).
  - Đảm bảo độ bền khi crash: chuyển giao tham số `crash_at` vào host và không bắt ngoại lệ `InjectedCrash` để phục vụ kịch bản kiểm thử T12.
  - Sử dụng hàm chuẩn `finish()` để ghi nhận trace JSON đầy đủ và cập nhật ledger/audit events.
- **Thêm bộ kiểm thử tích hợp (`src/tests/test_workflow_integration.py`):**
  - Viết test `test_workflow_unknown_claim` kiểm tra trường hợp claim không tồn tại.
  - Viết test `test_workflow_injected_crash_propagates` xác minh `InjectedCrash` được ném ra chính xác khi gặp crash point `after_effect_before_checkpoint`.
- **Commit chính:**
  - `9edbf1c`: `feat(workflow): implement deterministic workflow and add integration tests`

## 4. Bằng chứng

- **Commit Hash:** `9edbf1c`
- **Test đã thêm:**
  - `src/tests/test_workflow_integration.py::test_workflow_unknown_claim`
  - `src/tests/test_workflow_integration.py::test_workflow_injected_crash_propagates`
- **Kết quả kiểm thử ma trận student cho workflow:**
  - Lệnh: `python -m pytest -q -m student -o addopts= -k workflow`
  - Kết quả: `62 passed` (đạt 100% trên các ca kiểm thử T01–T14 với 5 seeds).
- **Kết quả cổng Host:**
  - Lệnh: `python -m pytest -q`
  - Kết quả: `56 passed, 248 deselected` (bao gồm 54 test host và 2 test tích hợp mới thêm).

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity AI Assistant.
- **Mục đích sử dụng:**
  - Phân tích yêu cầu đề bài từ `README.md`, `RUBRIC.md`, `CHECKPOINTS.md` và các contracts trong `docs/`.
  - Hỗ trợ rà soát logic boundary cho `workflow.py` (cách truyền full quote cho host, quy tắc xử lý approval mismatch, cách bẫy và chuyển giao `InjectedCrash`).
  - Soạn thảo khung unit test tích hợp trong `test_workflow_integration.py`.
- **Cách tự kiểm tra kết quả:**
  - Tự chạy toàn bộ test suite trên terminal máy cá nhân: `python -m pytest -q` và `python -m pytest -q -m student -o addopts= -k workflow`.
  - Đọc lại code trong `workflow.py` để đảm bảo không ghi đè hoặc sửa đổi các file bị cấm (`metrics.py`, `durability.py`, `policy.py`).

## 6. Tự đánh giá

- **Mức độ hoàn thành:** 100% phần việc `workflow` và giai đoạn đầu của `integration`.
- **Kỹ năng đạt được:** Hiểu sâu về ranh giới an toàn giữa code và model (Code enforces security, money & idempotency; model chỉ soạn văn bản), nắm vững cơ chế Idempotency qua SQLite transaction và cách phòng chống leak PII/secret trong trace.
