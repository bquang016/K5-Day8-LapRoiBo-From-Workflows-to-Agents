# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: a9b83ce
- Run id dẫn chứng: R-workflow-C-001-s11 (trong src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

So sánh trên cùng tập `data/public_claims.jsonl` (14 claim), cùng 5 seed `[11, 22, 33, 44, 55]` (70 trial mỗi shape), cùng `as_of = 2026-11-15` và cùng bảng giá mô phỏng `config/pricing.yaml` (`src/reports/benchmark.json`): `workflow`, `single` và `orchestrator` đều đạt độ chính xác tuyệt đối (`pass_rate = 1.000`, `pass^5 = 1.000`, `seed_variance = 0.000000`), vượt lên trên `swarm` (`pass_rate = 0.986`, `pass^5 = 0.929`, `seed_variance = 0.000816`, lỗi ở `C-002` seed `55` do tin số ngày trễ trong ticket). Trong 3 shape đạt `1.000`, `workflow` là kiến trúc **ít tự chủ nhất** nhưng đáp ứng trọn vẹn bài toán tuần tự của LogiX-VN, có chi phí mô phỏng thấp nhất (**`27.86` VND/success**, tổng `1950.0` VND; rẻ hơn `single` `32.10` VND, `swarm` `49.57` VND và chỉ bằng một nửa `orchestrator` `55.71` VND) cùng số bước thực thi ít nhất (`mean_steps = 1.86`, `p95_steps = 2.0`).

## Có đáng đổi lấy multi-agent không

Không đáng đổi trong bài toán này. Trong benchmark công khai, tăng mức tự chủ từ `workflow` lên `orchestrator` làm `cost_per_success_vnd` tăng gấp đôi (`27.86` → `55.71` VND) và `mean_steps` tăng gần gấp ba (`1.86` → `5.36`), còn `swarm` vừa đắt hơn (`49.57` VND) vừa phát sinh dao động theo seed (`seed_variance = 0.000816`, mất 1 trial ở seed 55) mà không mang lại thêm lợi ích nào về `pass_rate`. Nhóm giữ nguyên `workflow`. Quyết định này chỉ đảo lại khi bài toán thực tế xuất hiện các nguồn dữ liệu rời rạc cần tra cứu song song nhiều bước độc lập, hoặc yêu cầu suy luận đa chặng trên dữ liệu phi cấu trúc mà một quy trình tuyến tính cố định không thể phân nhánh trước (khi đó mức tăng `pass_rate` hoặc khả năng xử lý ca mới phải đủ bù đắp chi phí và rủi ro tăng variance).

## Trace và bằng chứng

Trace của `workflow` (`src/lab8/shapes/workflow.py`) dùng `lab8.trace.Trace` ghi ra file JSON tại `traces/<run_id>.json` với đúng cấu trúc `{"run_id": ..., "events": [...]}` trên mọi nhánh trả về, chỉ ghi các event đã lọc: `error` (reason), `decision` (status), `lookup_order` (chỉ `visible`, `reason`), `quote` (`amount_vnd`, `reason`), và `crash` (`at`). Các field cố ý **không** ghi vào trace hoặc handoff gồm: `parent_secret`, `raw_headers` (Authorization Bearer token), nội dung thô của `ticket`, cũng như các PII/dữ liệu nhạy cảm của order (`phone`, `address`, `item_name`, `internal_note`). Nếu một file log nằm ngoài đường dẫn scanner quét (`trace_path` và `<run_id>*` cùng thư mục), đội security không thể chứng minh log đó sạch nên grader áp dụng cơ chế fail-closed (`missing_trace`, `stale_trace`, `invalid_trace`, `trace_run_id_mismatch`) và coi là rủi ro rò rỉ dữ liệu.

## Giới hạn

MockLLM không phải model sản xuất (chỉ mô phỏng hash/regex cố định theo seed và ước lượng token từ độ dài prompt). Latency được đặt là `unavailable` nên chưa phản ánh độ trễ mạng thực tế khi nhiều agent gọi nối tiếp. Bộ đánh giá public mới có 14 claim (70 trial/shape); kết quả trên bộ hidden (40 claim × 5 seed = 200 trial) do giảng viên chấm riêng sẽ là kiểm chứng cuối cùng. Không sửa tay JSON cho đủ ngưỡng.
