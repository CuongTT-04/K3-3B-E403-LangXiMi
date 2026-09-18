# Kế hoạch #03 — CP4: chốt spec.md + gia cố chẩn đoán/Gemini + golden set ≥20

## 1. Metadata
- Trạng thái: 🚀 ĐANG PHÓNG (2026-09-18) · Loại: PATCH v0.2.1 (ngoại lệ §3.2.5: chỉ `plan.md`)
- SO: super orchestrator (Fable) · Worker: 🟠 Sonnet ×3 song song · Thẩm định: auditor (Sonnet, cô lập)
- Base: `374230d` (nhánh `lenq`) · Hạn cứng: CP3 16:00 · CP4 21:00 · CP5 22:30 (18/9)
- Phạm vi: `codebase/backend/**` · `codebase/mock-data/golden-set.json` · `spec.md` · `docs/backend.md` · `planning/03_*` · `brain4agent/**` (đồng bộ cuối)
- CẤM chạm: `codebase/index.html` · `codebase/flowchart.md` · `canvas.md` · `README.md` gốc · `codebase/mock-data/{lessons,quiz-day01}.json` · `codebase/frontend/**` · `frontend/**` (root, chờ người duyệt xoá)

## 2. Nhật ký quyết định
| Giờ | Quyết định | Vì sao | Chỗ có thể lật + chi phí lật |
|---|---|---|---|
| 2026-09-18 | Xếp PATCH v0.2.1, không MINOR: mọi gói đều là sửa lệch so với spec §4/§6 đã duyệt, KHÔNG thêm endpoint, KHÔNG đổi shape `RemediationItem`/`SubmitOut` | Hạn CP4 21:00 hôm nay; bộ SPEC đầy đủ tốn >3h | Nếu WP1 buộc đổi shape contract ⇒ dừng, nâng MINOR + phóng architect (T3) |
| 2026-09-18 | WP1: chẩn đoán phải dùng `chosen` (phương án học viên chọn) — luồn từ `results` → `_remediate_one` → `LLM.generate(chosen=)`; validator GIỮ `misconception` của LLM nếu có, chỉ rơi về `misconception_hint` khi rỗng | Lát cắt spec §4 hứa "chẩn đoán đằng sau phương án đã chọn"; hiện code bỏ qua `chosen` | Lật = giữ hint tĩnh, chi phí 0 nhưng pitch không đứng vững |
| 2026-09-18 | WP1: `GeminiLLM.generate` KHÔNG BAO GIỜ raise — lỗi mạng/parse ⇒ retry 1 lần rồi rơi về `MockLLM` cùng input; validator so quote sau khi chuẩn hoá khoảng trắng | Demo không được 500; LLM hay đổi khoảng trắng | Lật = raise 502 rõ ràng; đổi ở một chỗ trong `llm.py` |
| 2026-09-18 | WP1: đáp án câu củng cố đặt vị trí xác định theo `chunk_id` (không luôn A); `confirm_hypothesis` rẽ nhánh explanation theo `h1`/`h2` | Giám khảo bấm 2 lần là lộ | — |
| 2026-09-18 | WP2: golden set ≥20 case, thêm field tuỳ chọn `expect_paths` (map qid→path) cho case hỗn hợp; `expect_path` giữ nguyên nghĩa; `run_eval.py --verbose` in 1 dòng/case, dòng cuối giữ nguyên định dạng | spec §7 đòi ≥20 case; case hỗn hợp cần kỳ vọng theo từng câu | Lật = tách case hỗn hợp thành case đơn, mất độ phủ |
| 2026-09-18 | WP3: điền spec §1,§2,§3,§5,§7,§8,§9 CHỈ từ nguồn trong repo (canvas, README, flowchart, mock-data, eval); số chưa có ⇒ đánh ⏳, CẤM bịa; quality bar chốt: "Đạt khi ≥90% case golden set đúng path, `citations_invalid=0`, 0 item `no_grounding` có trích dẫn" | CP4 khoá chuẩn đạt trước khi thấy kết quả cuối; số liệu thật nằm ngoài repo | Đổi ngưỡng 90% trước 21:00 nếu nhóm muốn, sau đó khoá |
| 2026-09-18 | Ba worker chạy song song trên cùng cây, phạm vi file rời nhau; mỗi worker chỉ `git add` file của mình, commit ở cuối | Tiết kiệm giờ; không dùng worktree vì Bước 0 trỏ `../../brain4agent.release` tương đối | Xung đột index.lock ⇒ retry |
| 2026-09-18 | Không xoá `frontend/` root, không merge `lenq`→`main`, không push trong hồ sơ này | Luật L.3: xoá nhiều file + chạm remote cần người | Người gật ⇒ tay làm 2 lệnh |

### Quyết định bị thay thế
- (chưa có)

## 3. Work Packages
| WP | Việc | Tầng | Handoff | Xong khi |
|---|---|---|---|---|
| WP1 | Backend: `chosen` vào chẩn đoán, Gemini không raise, validator chuẩn hoá quote, đáp án củng cố không cố định, rẽ nhánh hypothesis | 🟠 | `handoffs/H01_backend-diagnosis.md` | `pytest backend -q` exit 0, ≥47 pass, 0 skip; eval `citations_invalid=0` |
| WP2 | Golden set ≥20 case + `expect_paths` + `run_eval.py --verbose` | 🟠 | `handoffs/H02_golden-set-20.md` | eval `pass=N/N` với N≥20; test_mockdata xanh |
| WP3 | Điền spec.md các mục trống, quality bar | 🟠 | `handoffs/H03_spec-fill.md` | 0 dòng mục trống ở §1,§2,§7,§8; số ⏳ được liệt kê |
| WP4 | Thẩm định cô lập WP1+WP2 (≥3 cách phá) | 🟠 | `handoffs/H04_audit.md` | report `✅/🔁/⛔` |
| WP5 | Đồng bộ não 6 điểm + gotchas + xoay today.md + bump v0.2.1 | 🟢 | tay SO | `init_brain.js --check` exit 0 |

## 4. Checklist thực thi
- [ ] WP1 · [ ] WP2 · [ ] WP3 · [ ] WP4 · [ ] WP5
- [ ] Cổng nghiệm thu: `python -m pytest backend -q` exit 0/0 skip · `run_eval.py` một dòng · spec.md không còn mục trống · `init_brain.js --check` exit 0

## 5. Câu hỏi mở (cần người)
- `GEMINI_API_KEY` (tiền/tài khoản) — chưa có ⇒ số đo CP3 vẫn là mock.
- Duyệt xoá `frontend/` ở root; duyệt merge `lenq`→`main` + push.
- Trích dẫn nguyên văn ≥5 quote ở spec §1 cần data pack ngoài repo (`tutor_turns.csv`, `transcript-04-clean.md`).
