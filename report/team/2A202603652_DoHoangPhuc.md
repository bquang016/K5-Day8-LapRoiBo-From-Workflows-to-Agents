# Báo cáo cá nhân — 2A202603652_DoHoangPhuc


## 1. Thông tin thành viên

- Họ tên: Đỗ Hoàng Phúc
- MSSV: 2A202603652
- Email: 26ai.phucdh@vinuni.edu.vn
- GitHub: Codeforlife-MagicWed

## 2. Phần việc phụ trách

- Vai trò trong nhóm: **`ledger + evaluation`** (nhánh `feat/ledger-evaluation`).
- Phụ trách chính:
  - Kiểm chứng độ bền sổ cái (`refund_ledger`), cơ chế chống ghi trùng (`idempotency`), giới hạn hoàn tiền theo đơn (`per-order cap`) và xử lý lỗi sập nguồn (`crash_at` / `InjectedCrash`).
  - Viết test bổ sung cho phần `durability` và `metrics`.
  - Chạy bộ kiểm thử sập nguồn (`lab8.crash_test`) và chạy benchmark tổng hợp 4 kiến trúc (`lab8.benchmark`), trích xuất số liệu cho `decision_adr.md`, `research_card.md` và `group_report.md`.
  - Kiểm tra hợp lệ bài nộp bằng `lab8.check_submission`.

## 3. Đóng góp cụ thể

- **Test đã thêm:** Tạo mới `src/tests/test_ledger_evaluation.py` với 3 test case kiểm tra các trường hợp biên của ledger và evaluation metrics:
  1. `test_partial_refund_topup_crash_resume_preserves_order_cap`: kiểm tra tình huống đơn đã hoàn một phần trước đó (`O-515` đã hoàn `30.000` VND; claim `C-014` có quote `150.000` VND, phần chênh `120.000` VND), xảy ra crash tại `after_effect_before_checkpoint`, sau đó resume không ghi đúp tiền, không vượt trần đơn (`150.000` VND) và giữ đúng 1 audit `refund_committed`.
  2. `test_retry_conflict_after_partial_topup_keeps_original_amount`: kiểm tra khi gọi lại claim `C-014` đã commit với số tiền khác (`50.000` VND) thì hệ thống báo `amount_conflict` (`conflict=True`) và giữ nguyên số tiền đã commit (`120.000` VND).
  3. `test_summarize_zero_passes_and_p95_steps`: kiểm tra hàm `lab8.metrics.summarize` khi có 0 trial pass trả về `cost_per_success_vnd = None` (không lỗi chia cho 0) và tính đúng `p95_steps`.
- **Bằng chứng crash suite:** Chạy `python -m lab8.crash_test --count 20 --out reports/crash.json` tạo `src/reports/crash.json` đạt `20/20`.
- **Commit chính:** `8a43f09` (`test(ledger,eval): add durability/metrics tests and 20/20 crash report`).
- **Benchmark & báo cáo cuối buổi:** Chạy `lab8.benchmark` tạo `src/reports/benchmark.json` (4 shape × 14 claim × 5 seed = 70 trial/shape; `workflow` đạt `pass_rate = 1.000`, `pass^5 = 1.000`, `variance = 0.000000`, `cost/success = 27.86` VND), chạy ablation R1 (`workflow` vs `orchestrator`), và hoàn thiện `decision_adr.md`, `research_card.md`, `group_report.md`, `TEAM.md`. Run ID dẫn chứng: `R-workflow-C-001-s11`.

## 4. Bằng chứng

- File test mới: `src/tests/test_ledger_evaluation.py`
  - Chạy riêng file test: `python -m pytest -q tests/test_ledger_evaluation.py` → `3 passed in 0.31s`.
  - Chạy cổng host toàn bộ: `python -m pytest -q` → `57 passed, 248 deselected in 7.58s` (tăng từ 54 lên 57 passed, không làm hỏng test host).
- File crash report: `src/reports/crash.json` → `"crash_safety": "20/20"` (20/20 scenarios `passed: true`).
- Commit hash: `8a43f09` (https://github.com/bquang016/K5-Day8-LapRoiBo-From-Workflows-to-Agents/commit/8a43f09)

## 5. Công cụ AI đã dùng

- **Công cụ:** Trợ lý AI (Antigravity / Gemini) trong quá trình làm lab.
- **Mục đích sử dụng:**
  - Giải thích đề bài, kiến trúc 4 shape, luật nghiệp vụ (`docs/business_rules.md`), cơ chế `refund_ledger`, `idempotency_key`, `InjectedCrash` và các chỉ số đánh giá (`pass_rate`, `pass^5`, `seed_variance`, `cost_per_success_vnd`, `p95_steps`).
  - Hỗ trợ thiết lập môi trường ảo `.venv` và viết 3 test case trong `src/tests/test_ledger_evaluation.py`.
  - Hỗ trợ soạn khung báo cáo cá nhân.
- **Cách tự kiểm tra kết quả:**
  - Đọc lại trực tiếp code nguồn hệ thống (`src/lab8/durability.py`, `src/lab8/policy.py`, `src/lab8/metrics.py`, `src/lab8/crash_test.py`) để đối chiếu logic mà AI giải thích.
  - Tự chạy lại các lệnh `python -m pytest -q`, `python -m lab8.smoke`, `python -m lab8.crash_test --count 20 --out reports/crash.json` trên terminal máy cá nhân và đối chiếu trực tiếp kết quả đầu ra trong `src/reports/crash.json`.

## 6. Tự đánh giá

- Đã nắm được ranh giới giữa code và model trong hệ thống (tiền hoàn, approval, trần theo đơn và idempotency do code host quyết định trong transaction SQLite; model/shape không tự sửa ledger).
- Hoàn thành phần test bổ sung và kiểm thử crash suite `20/20` đúng tiến độ trên nhánh riêng `feat/ledger-evaluation`.
- Phần việc còn chờ phối hợp cùng nhóm: sau khi 3 thành viên còn lại hoàn thiện `workflow`, `single`, `orchestrator` và merge vào `main`, sẽ chạy `lab8.benchmark` (tạo `src/reports/benchmark.json`), hoàn thiện số liệu vào `decision_adr.md`, `research_card.md`, `group_report.md` và kiểm tra `python -m lab8.check_submission` đạt `0 FAIL`.
