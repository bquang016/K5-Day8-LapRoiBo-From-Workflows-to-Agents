# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R1 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Google Research (2026), *Towards a Science of Scaling Agent Systems*, tham chiếu tài liệu lý thuyết bài giảng Lab 8 (slide 68–69), loại bằng chứng: empirical scaling benchmark trên agent systems. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Với các tác vụ có luồng xử lý phụ thuộc tuần tự rõ ràng, việc tăng số lượng agent/bước điều phối thường làm tăng chi phí giao tiếp và số bước thực thi mà không tự động cải thiện độ chính xác so với luồng tuần tự đơn giản. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Kết luận bị giới hạn trong phạm vi bộ dữ liệu synthetic LogiX-VN (`public_claims.jsonl`: 14 claim, 5 seed `11,22,33,44,55`), backend `MockLLM`, bộ tool cố định theo `tools.manifest.v1.1.yaml` và bảng giá mô phỏng `config/pricing.yaml` (không đo latency thật). |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi đổi từ `workflow` (Shape A — luồng tuần tự cố định) sang `orchestrator` (Shape C — tách orchestrator + investigator qua `handoff.v1`), `pass_rate` và `pass^5` sẽ giữ nguyên ở mức `1.000` (vì dữ liệu và luật tính tiền `compute_compensation` đều do code quyết), nhưng `cost_per_success_vnd` và `mean_steps` sẽ tăng khoảng 2–3 lần do phát sinh thêm bước handoff và các tool điều tra đọc bổ sung. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Biến giữ cố định: backend `MockLLM`, `as_of=2026-11-15`, corpus `data/public_claims.jsonl` (14 claim), `data/public_world_state.json`, seeds `[11, 22, 33, 44, 55]`, `config/pricing.yaml`, evaluator `lab8.metrics`, mỗi trial 1 SQLite mới. Biến duy nhất thay đổi: kiến trúc điều phối (`workflow` so với `orchestrator`). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Chi phí dư thừa / lạm phát số bước (`cost/success` tăng mạnh dù không tăng độ chính xác) và rủi ro rò rỉ dữ liệu qua biên giới handoff; đo bằng `pass_rate`, `pass_5`, `seed_variance`, `cost_per_success_vnd`, `mean_steps`, `p95_steps` và kiểm tra secret/PII leak qua `trial_pass`. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,orchestrator --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out traces/ablation_r1.json` (và đối chiếu với `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`)
- Run id / file report: `src/reports/benchmark.json` (ví dụ cặp trial đối chứng `R-workflow-C-001-s11` vs `R-orchestrator-C-001-s11`, và file ablation `src/traces/ablation_r1.json`)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng với giả thuyết.** Trên cùng 70 trial (14 claim × 5 seed): `workflow` đạt `pass_rate = 1.000`, `pass_5 = 1.000`, `seed_variance = 0.000000`, `cost_per_success_vnd = 27.86` VND (tổng `1950.0` VND), `mean_steps = 1.86`, `p95_steps = 2.0`, `mean_tool_calls = 2.79`. Trong khi đó `orchestrator` đạt cùng `pass_rate = 1.000`, `pass_5 = 1.000`, `seed_variance = 0.000000`, nhưng `cost_per_success_vnd` tăng đúng gấp đôi lên **`55.71` VND** (tổng `3900.0` VND, `+100%`), `mean_steps` tăng lên **`5.36`** (`p95_steps = 6.0`, `+188%`), và `mean_tool_calls` tăng lên `5.57` do thêm các bước handoff (`lookup_policy`, `lookup_refund_history`).
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
