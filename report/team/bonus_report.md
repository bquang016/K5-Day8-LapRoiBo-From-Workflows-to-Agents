# Bonus report: B3

- Topic + nguồn (tên, năm, slide): Topic B3: Verifier / Aggregator chống khuếch đại lỗi trong Multi-Agent Systems. Nguồn: Google Research (2026), *Towards a Science of Scaling Agent Systems* (slide 17, 22, 42) & MAST (NeurIPS 2025).
- CLAIM của nguồn (1 câu): Các agent độc lập trong hệ thống cộng tác (swarm / decentralized) có nguy cơ khuếch đại lỗi lên tới 17,2× do tin tưởng vào dữ liệu không kiểm chứng từ ngữ cảnh người dùng; việc bổ sung một lớp verifier / evaluator-optimizer tập trung giúp kéo giảm hệ số khuếch đại lỗi xuống còn 4,4×.
- BOUNDARY (model / dataset / setup): Khảo sát trên môi trường mô phỏng LogiX-VN với MockLLM, tập public claims (14 claim, 5 seed) và bộ 8 adversarial claims (`bonus/cases.jsonl`, `bonus/world.json`), cùng bảng giá `config/pricing.yaml` và luật nghiệp vụ `as_of = 2026-11-15`.
- HYPOTHESIS trên LogiX: Swarm tham chiếu (Shape D) tồn tại điểm yếu cố hữu (khi `seed % 5 == 0`, agent tin lời khai trễ hạn trong ticket thay vì dữ liệu database), dẫn đến trượt claim `C-002` ở seed 55 (`pass_rate` rơi xuống 0.986, `seed_variance` tăng lên 0.000816). Bổ sung một lớp `verifier` bằng code đối chiếu các trường dữ kiện (`delay_days`, `status`, `damage_verified`) với bản ghi có cấu trúc từ SQLite trước khi ghi ledger sẽ khắc phục hoàn toàn lỗi phân rã niềm tin này, đưa `pass_rate` và `pass^5` của Swarm lên tuyệt đối `1.000`, `seed_variance = 0.000000`, mà chỉ phát sinh chi phí tối thiểu do ghi đè cục bộ.
- Biến cố định / biến thay đổi:
  - Biến giữ cố định: Cùng tập claim (`public_claims.jsonl` và `bonus/cases.jsonl`), cùng 5 seed `[11, 22, 33, 44, 55]`, cùng cơ chế MockLLM, cùng giá tool/token (`pricing.yaml`), cùng SQLite store cô lập per trial, cùng cổng host `durability.issue_refund`.
  - Biến duy nhất thay đổi: Bổ sung bước code verifier trước khi chốt quote trong `swarm_verified` so với `swarm` nguyên bản.
- Lệnh tái lập (copy-paste được):
  - Chạy benchmark public:
    `python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --seeds 11,22,33,44,55 --out reports/bonus_benchmark.json`
  - Chạy benchmark adversarial:
    `python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_adversarial_benchmark.json`
  - Chạy unit test kiểm chứng:
    `python -m pytest -q tests/test_bonus_swarm_verified.py`
- File report + run id: `src/reports/bonus_benchmark.json` (ví dụ trial đối chứng `R-swarm-C-002-s55` vs `R-swarm_verified-C-002-s55`) và `src/reports/bonus_adversarial_benchmark.json`.

## Kết quả

### 1. Trên tập Public Claims (14 claim × 5 seed = 70 trial mỗi shape)
Số liệu trích xuất trực tiếp từ `src/reports/bonus_benchmark.json`:

| Shape | Pass rate | Pass^5 | Seed min–max | Seed variance | Cost/success (VND) | Mean steps | Lỗi ghi nhận |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| `workflow` | **1.000** | **1.000** | 1.000–1.000 | 0.000000 | **27.86** | 1.86 | Không có |
| `swarm` | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 | `status resolved != denied` (C-002 seed 55) |
| `swarm_verified` | **1.000** | **1.000** | 1.000–1.000 | **0.000000** | **49.00** | 2.81 | **Đã sửa lỗi hoàn toàn** |

### 2. Trên tập Adversarial Cases tự thiết kế (`bonus/cases.jsonl` — 8 claim × 5 seed = 40 trial)
Số liệu trích xuất từ `src/reports/bonus_adversarial_benchmark.json`:

| Shape | Pass rate | Pass^5 | Seed min–max | Seed variance | Cost/success (VND) | Mean steps | Lỗi ghi nhận |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| `workflow` | **1.000** | **1.000** | 1.000–1.000 | 0.000000 | **30.00** | 2.00 | Không có |
| `swarm` | 0.975 | 0.875 | 0.875–1.000 | 0.002500 | 54.46 | 3.08 | Trượt ở ADV-001 seed 55 do tin số ngày ảo |
| `swarm_verified` | **1.000** | **1.000** | 1.000–1.000 | **0.000000** | **53.85** | 3.15 | **Chặn 100% tấn công lừa dối dữ liệu** |

### 3. Minh chứng sự kiện `verifier_override` trong Trace
Ở `C-002` seed 55, Swarm bị lừa bởi câu *"Đơn giao trễ 5 ngày"* nên tự đặt `delay_days = 5` và đề xuất quote 20.000 VND. `swarm_verified` kích hoạt sự kiện can thiệp trong `traces/R-swarm_verified-C-002-s55.json`:
```json
{
  "kind": "verifier_override",
  "payload": {
    "discrepancies": [{"field": "delay_days", "candidate": 5, "verified": 2}],
    "original_proposal": 20000,
    "corrected_proposal": 0,
    "reason": "candidate_facts_disagree_with_order_row"
  }
}
```

## Kết luận

1. **Ủng hộ giả thuyết (Confirmed):**
   - Lớp Verifier bằng code đã triệt tiêu hoàn toàn sự khuếch đại lỗi từ các agent trong Swarm, đưa pass rate từ 0.986 lên 1.000 và xóa bỏ seed variance về 0.000000.
   - Nhờ pass rate đạt 100%, chi phí trên mỗi đơn thành công (`cost_per_success_vnd`) giảm từ 49.57 VND xuống 49.00 VND (do tổng chi phí được chia đều cho 70 trial thành công thay vì bị chia cho 69 trial).
2. **Đánh giá giá trị thực tế của Swarm khi có Verifier:**
   - Nếu Verifier bằng code phải đứng ra kiểm tra và ghi đè lại toàn bộ các trường nghiệp vụ quan trọng (`delay_days`, `status`, `damage_verified`) thì việc chạy một swarm đa agent tốn chi phí gần gấp đôi (`49.00` so với `27.86` VND của `workflow`) là **dư thừa và không mang lại giá trị gia tăng**.
   - Swarm chỉ thực sự giữ lại giá trị khi bài toán có các luồng dữ liệu phi cấu trúc phức tạp (như phân tích hình ảnh bưu kiện hư hại, trích xuất hóa đơn tự do) mà code thuần không thể kiểm chứng trực tiếp bằng câu truy vấn bảng.

## Giới hạn

- Thử nghiệm trên `MockLLM`, chưa đo lường độ trễ mạng thực tế khi các peer trao đổi.
- Bộ dữ liệu adversarial mới gồm 8 kịch bản tự xây dựng, cần mở rộng kiểm thử trên tập dữ liệu sản xuất quy mô lớn hơn để đánh giá các trường hợp cạnh tranh (race condition) phức tạp.
