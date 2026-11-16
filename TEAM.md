# Team

## Thông tin nhóm

- Tên nhóm: LapRoiBo
- Lớp: L3A
- Repo nhóm: `K5-Day8-LapRoiBo-From-Workflows-to-Agents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: `https://github.com/bquang016/K5-Day8-LapRoiBo-From-Workflows-to-Agents.git`, nhánh `main`, commit `PENDING_COMMIT`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Bùi Đăng Quang | 2A202603640 | 26ai.quangbd2@vinuni.edu.vn | bquang016 | workflow + integration |
|   2 | Phạm Duy Đức | 2A202603611 | 26ai.ducpd@vinuni.edu.vn | bquang016 | single |
|   3 | Trương Hoàng Tùng | 2A202603651 | 26ai.tungth2@vinuni.edu.vn | Dobit25 | orchestrator + handoff |
|   4 | Đỗ Hoàng Phúc | 2A202603652 | 26ai.phucdh@vinuni.edu.vn | Codeforlife-MagicWed | ledger + evaluation |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Bùi Đăng Quang | workflow + integration | 9edbf1c | tests/test_workflow_integration.py::test_workflow_unknown_claim, tests/test_workflow_integration.py::test_workflow_injected_crash_propagates |
| Phạm Duy Đức | single | 60f94bb | tests/test_single_shape.py::test_single_uses_order_delay_and_keeps_trace_free_of_ticket_secrets |
| Trương Hoàng Tùng | orchestrator + handoff | 1aabf9a | tests/test_handoff_orchestrator.py (4 tests: handoff trace, approval denial, order cap, crash/resume) |
| Đỗ Hoàng Phúc | ledger + evaluation | 8a43f09 | tests/test_ledger_evaluation.py (3 tests: partial top-up crash/resume, retry conflict, metrics zero-pass/p95) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603640_BuiDangQuang

### Phần việc phụ trách

- `workflow + integration`: Hiện thực Shape A Workflow (deterministic) và bộ test tích hợp.

### Đóng góp cụ thể

- Hiện thực toàn bộ `src/lab8/shapes/workflow.py`: đảm bảo an toàn bảo mật (không leak secret), tính tiền bằng `compute_compensation`, giao tiếp cổng host qua `durability.issue_refund`, tuân thủ idempotency và xử lý crash safety.
- Viết test kỹ thuật `src/tests/test_workflow_integration.py`.

### Bằng chứng

- Commit hash: `9edbf1c`
- Test: `tests/test_workflow_integration.py::test_workflow_injected_crash_propagates`
- Báo cáo chi tiết: `report/team/2A202603640_BuiDangQuang.md`

## 2A202603611_PhamDuyDuc

### Phần việc phụ trách

- `single`: Hiện thực Shape B Single Agent (ReAct tối đa 8 bước) và test kiểm thử riêng.

### Đóng góp cụ thể

- Hiện thực `src/lab8/shapes/single.py` sử dụng `run_react` với `max_steps=8`, chỉ cấp read tools trong vòng lặp, truyền full quote vào `durability.issue_refund` và chuyển tiếp `crash_at`.
- Thêm `src/tests/test_single_shape.py`.

### Bằng chứng

- Commit hash: `60f94bb`
- Test: `tests/test_single_shape.py::test_single_uses_order_delay_and_keeps_trace_free_of_ticket_secrets`
- Báo cáo chi tiết: `report/team/2A202603611_PhamDuyDuc.md`

## 2A202603651_TruongHoangTung

### Phần việc phụ trách

- `orchestrator + handoff`: Hiện thực Shape C Orchestrator và ranh giới handoff tới investigator chỉ đọc.

### Đóng góp cụ thể

- Hiện thực `src/lab8/shapes/orchestrator.py` dùng `make_handoff` và `run_readonly_investigators` theo allowlist, giữ quyền gọi `durability.issue_refund` duy nhất ở orchestrator.
- Thêm `src/tests/test_handoff_orchestrator.py` (4 test cases).

### Bằng chứng

- Commit hash: `1aabf9a`
- Test: `src/tests/test_handoff_orchestrator.py`
- Báo cáo chi tiết: `report/team/2A202603651_TruongHoangTung.md`

## 2A202603652_DoHoangPhuc

### Phần việc phụ trách

- `ledger + evaluation`: Kiểm chứng độ bền sổ cái, chạy crash suite, benchmark 4 kiến trúc, thực hiện ablation R1 và tổng hợp số liệu báo cáo.

### Đóng góp cụ thể

- Thêm `src/tests/test_ledger_evaluation.py` (3 test cases kiểm tra partial top-up crash/resume, retry amount_conflict, metrics zero-pass và p95_steps).
- Chạy `lab8.crash_test` sinh `src/reports/crash.json` (`20/20`) và `lab8.benchmark` sinh `src/reports/benchmark.json` (4 shape × 14 claim × 5 seed); chạy ablation R1 và hoàn thiện `decision_adr.md`, `research_card.md`, `group_report.md`.

### Bằng chứng

- Commit hash: `8a43f09`
- Test: `src/tests/test_ledger_evaluation.py`
- Báo cáo chi tiết: `report/team/2A202603652_DoHoangPhuc.md`

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
