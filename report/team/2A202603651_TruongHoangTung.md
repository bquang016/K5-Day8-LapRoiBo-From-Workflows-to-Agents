# Báo cáo cá nhân — MSSV_HoTen

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Trương Hoàng Tùng
- MSSV: 2A202603651
- Email: 26ai.tungth2@vinuni.edu.vn
- GitHub: [Dobit25](https://github.com/Dobit25)

## 2. Phần việc phụ trách

- Shape C: orchestrator và ranh giới handoff tới investigator read-only.
- Bảo đảm handoff theo allowlist, trace không chứa parent secret, raw header hoặc PII.
- Kiểm thử approval gate, cap hoàn tiền theo order và idempotency khi crash/resume.

## 3. Đóng góp cụ thể

- Commit chính: 1aabf9a61d3b36dee7244cafdad54ecd79bf6327
- Hiện thực `src/lab8/shapes/orchestrator.py` bằng `make_handoff` và
  `run_readonly_investigators`.
- Chỉ cấp bốn tool đọc cho investigator: `lookup_order`, `lookup_policy`,
  `lookup_refund_history`, `compute_compensation`.
- Orchestrator giữ quyền gọi duy nhất tới `durability.issue_refund`; investigator
  không nhận write registry.
- Truyền full quote vào host để host áp approval và per-order cap; truyền nguyên
  `crash_at` để kiểm tra durability.
- Thêm `src/tests/test_handoff_orchestrator.py` kiểm tra handoff/trace, approval
  denial, order cap và crash/resume.

## 4. Bằng chứng

- Commit/link: 1aabf9a61d3b36dee7244cafdad54ecd79bf6327
- Test riêng:
  - `test_orchestrator_traces_only_a_sanitized_readonly_handoff`
  - `test_orchestrator_uses_host_for_approval_denial`
  - `test_orchestrator_passes_full_quote_for_order_cap`
  - `test_orchestrator_propagates_crash_and_resume_is_idempotent`
- Public matrix liên quan: T05, T07, T10, T12, T13 và T14.
- Run ID có dạng `R-orchestrator-<claim_id>-s<seed>`.
- Kết quả tự kiểm tại thời điểm hoàn thành:
  - Test riêng: `4 passed`.
  - Public matrix orchestrator: `62 passed`.
  - Host gate: `58 passed, 248 deselected` (58 gồm 4 test mới).

## 5. Công cụ AI đã dùng

- Dùng OpenAI Codex để tóm tắt contract, đề xuất cấu trúc implementation, sửa các lỗi code và test ban đầu.
- Tự kiểm tra bằng cách đọc lại ranh giới code/model, chạy test riêng, public matrix của orchestrator và host gate. Kết quả benchmark/report chỉ lấy từ lệnh chạy thực tế, không tạo hoặc sửa số liệu bằng AI.

## 6. Tự đánh giá

- Hoàn thành phạm vi orchestrator + handoff theo Trace Contract v1.
- Điểm cần tiếp tục: tích hợp vào branch nhóm; đối chiếu benchmark cuối cùng trước khi chọn shape.
