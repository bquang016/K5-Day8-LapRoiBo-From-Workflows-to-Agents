# Báo cáo cá nhân — Phạm Duy Đức

## 1. Thông tin thành viên

- Họ tên: Phạm Duy Đức
- MSSV: 2A202603611
- Email: 26ai.ducpd@vinuni.edu.vn
- GitHub: [bquang016](https://github.com/bquang016/K5-Day8-LapRoiBo-From-Workflows-to-Agents)

## 2. Phần việc phụ trách

Shape B — Single (ReAct): triển khai `src/lab8/shapes/single.py`, thêm kiểm thử riêng cho shape này và ghi nhận kết quả kiểm thử.

## 3. Đóng góp cụ thể

- Dùng `run_react` để điều phối vòng đọc claim, tra cứu đơn và tính quote; giới hạn vòng lặp tối đa 8 bước.
- Các công cụ trong vòng agent đều là công cụ đọc. `compute_compensation` tính quote bằng code; sau vòng lặp, shape chuyển quote đầy đủ cho `durability.issue_refund`. MockLLM không quyết định số tiền và không được gọi công cụ ghi refund.
- Chuyển tiếp `crash_at` tới host và để `InjectedCrash` truyền ra ngoài để kiểm tra đường khôi phục.
- Ghi trace theo `run_id`, chỉ gồm các trường allowlist; không ghi ticket thô hoặc dữ liệu nhạy cảm.
- Thêm `src/tests/test_single_shape.py`, kiểm tra ticket khai sai số ngày không lấn át dữ liệu đơn và trace không chứa canary.
- Commit chính (hash): `60f94bb` (`Implement single ReAct shape`), branch `Single`.

## 4. Bằng chứng

- Test shape Single: `python -m pytest -q -m student -o addopts= tests/test_public_matrix.py -k 'single and not workflow and not orchestrator and not swarm'`
- Kết quả: **62 passed, 186 deselected**.
- Test riêng: `test_single_uses_order_delay_and_keeps_trace_free_of_ticket_secrets` trong `src/tests/test_single_shape.py`.
- Ca kiểm thử dùng claim `C-002`, seed `55`: ticket nói giao trễ 5 ngày nhưng dữ liệu đơn ghi 2 ngày; kết quả đúng là `denied`, quote `0`.

## 5. Công cụ AI đã dùng

- ChatGPT/Codex: hỗ trợ đọc yêu cầu lab, triển khai `single.py`, viết test và soạn báo cáo.
- Tự kiểm tra bằng cách chạy 62 test dành riêng cho shape Single; rà soát trace không chứa chuỗi `CANARY_SECRET_`.

## 6. Tự đánh giá

Shape Single đáp ứng giới hạn 8 bước, chỉ dùng read tools trong vòng ReAct, và giữ quyết định tài chính cùng thao tác ghi ở code/host. Bộ 62 test công khai dành cho shape đều đạt. Thay đổi được chuẩn bị trên branch cá nhân `Single` để bàn giao cho TV1 tích hợp.
