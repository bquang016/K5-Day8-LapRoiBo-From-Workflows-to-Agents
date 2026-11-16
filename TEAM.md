# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Bùi Đăng Quang | 2A202603640 | 26ai.quangbd2@vinuni.edu.vn | bquang016 | workflow + integration |
|   2 |        |      |       |        | single |
|   3 |        |      |       |        | orchestrator + handoff |
|   4 |        |      |       |        | ledger + evaluation |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Bùi Đăng Quang | workflow + integration | 9edbf1c | tests/test_workflow_integration.py::test_workflow_injected_crash_propagates |

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

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
