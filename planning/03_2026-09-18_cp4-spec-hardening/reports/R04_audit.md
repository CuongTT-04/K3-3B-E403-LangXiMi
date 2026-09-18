# R04 — WP4 Thẩm định cô lập WP1 + WP2

Vai: worker (vai-thi-cong) · loại: thẩm định · họ/model: Claude Sonnet · Bước 0: exit 0 · hiểu việc: đo lại mọi "xong khi" của H01 (8 việc, `codebase/backend/app/{service,llm,validator}.py` + tests + `docs/backend.md`) và H02 (5 việc, `golden-set.json` ≥20 case + `run_eval.py --verbose` + `expect_paths`), so `git diff --stat 374230d..HEAD` với phạm vi ĐƯỢC của H01+H02+H03, tự nghĩ ≥3 cách phá khác test hiện có (đã làm 5), và chứng minh `run_eval.py` ĐỎ trên dữ liệu cố tình hỏng đặt ở thư mục tạm qua `DATA_DIR` mà không đụng file trong repo. Chỉ đọc + chạy lệnh, chỉ ghi `reports/R04_audit.md` và `evidence/wp4/*.txt`.

Handoff: `planning/03_2026-09-18_cp4-spec-hardening/handoffs/H04_audit.md`
Base: 374230d
Head: 36b838f4bb499c7de0d048429bde93bb6840ed8c

## 1. Lệnh + exit code (nguyên văn, xem thêm `evidence/wp4/*.txt`)

`git status --short` TRƯỚC khi bắt đầu đo: rỗng (sạch). (Sau khi tôi tạo `evidence/wp4/` để ghi report thì mới xuất hiện `?? .../evidence/wp4/` — đúng phạm vi cho phép của chính tôi.)

- `node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check` → `EXIT:0` (não OK, không cần nâng cấp). → `evidence/wp4/00_init_brain_check.txt`
- `git diff --stat 374230d..HEAD` → 24 file, +971/-74 → `evidence/wp4/01_git_status_diffstat.txt`
- `python -m pytest backend -q` (từ `codebase/`) → `49 passed, 1 warning in 2.23s`, `EXIT:0` → `evidence/wp4/02_pytest_full.txt`
- `grep -n chosen backend/app/service.py backend/app/llm.py | wc -l` → `19` (≥4, đạt) → `evidence/wp4/03_grep_chosen.txt`
- `python -c "...len(golden-set.json)..."` → `21` (≥20, đạt) → `evidence/wp4/04_golden_set_count.txt`
- `python backend/eval/run_eval.py` → `eval pass=21/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0`, `EXIT:0` → `evidence/wp4/05_eval_summary.txt`
- `python backend/eval/run_eval.py --verbose | wc -l` → `22` = N+1 với N=21 (đạt) → `evidence/wp4/06_eval_verbose.txt`
- `python -m pytest backend/tests/test_mockdata.py backend/tests/test_golden_set_eval.py -q` → `8 passed`, `EXIT:0` → `evidence/wp4/07_pytest_wp2_scope.txt`
- `python -m pytest backend -q -k "test_misconception_mentions_chosen_option or test_validator_keeps_llm_misconception_when_present or test_validator_accepts_valid_item" -v` → `3 passed, 46 deselected`, `EXIT:0` → `evidence/wp4/08_pytest_wp1_named_tests.txt`

## 2. Test tổng/pass/fail/skip

`python -m pytest backend -q` → **49 tổng / 49 pass / 0 fail / 0 skip**, exit 0. So với base ghi trong handoff (39 pass/0 skip): **tăng +10, không giảm** — đạt. So với ngưỡng H01 (≥47 pass, 0 skip): đạt.

## 3. `git diff --stat` 374230d..HEAD + SHA + file ngoài phạm vi

SHA: 374230d → 36b838f. 24 file thay đổi (+971/-74):

- Trong phạm vi H01: `codebase/backend/app/{llm,service,validator}.py`, `codebase/backend/tests/{test_llm_gemini,test_service,test_validator}.py`, `docs/backend.md`, `reports/R01_backend-diagnosis.md`, `evidence/wp1/{eval,pytest}.txt`.
- Trong phạm vi H02: `codebase/mock-data/golden-set.json`, `codebase/backend/eval/run_eval.py`, `codebase/backend/tests/{test_mockdata,test_golden_set_eval}.py`, `reports/R02_golden-set-20.md`, `evidence/wp2/{eval,pytest}.txt`.
- Trong phạm vi H03 (không thuộc việc thẩm định của tôi nhưng nằm trong diff): `spec.md`, `reports/R03_spec-fill.md`.
- Hạ tầng của SO (không phải worker H01/H02/H03 ghi): `plan.md`, `handoffs/H01–H04_*.md` — do commit `3824f03 docs(planning): open dossier #03 ...` cùng tác giả `lenq`, đây là commit mở hồ sơ của SO chứ không phải worker tự ý ghi ngoài phạm vi của mình.

**File ngoài phạm vi ĐƯỢC của H01+H02+H03: KHÔNG có.** Mọi file trong diff đều khớp danh sách "ĐƯỢC sửa" của một trong ba handoff, hoặc là artefact mở hồ sơ do SO tạo.

## 4. Bảng phân công

| Gói | Tầng | Họ/model |
|---|---|---|
| WP1 (backend chẩn đoán/Gemini) | 🟠 | Claude Sonnet (worker khác) |
| WP2 (golden set ≥20) | 🟠 | Claude Sonnet (worker khác) |
| WP3 (spec fill) | 🟠 | Claude Sonnet (worker khác) |
| WP4 (thẩm định — việc này) | 🟠 | Claude Sonnet (tôi) |

## 5. Các cách phá đã thử + kết quả

| # | Cách phá | Lệnh/script | Kết quả |
|---|---|---|---|
| a | Submit `day01` với `chosen="Z"` (không có trong bất kỳ option nào) cho cả 11 câu qua `TestClient` | `evidence/wp4/10_break_a_chosen_not_in_options.txt` | **XANH** — status 200, `score=0/11`, không item nào `misconception` rỗng (rơi về `misconception_hint` tĩnh vì `chosen not in options`, đúng logic ở `llm.py:62`) |
| b | `LLM_MODE=gemini` + `GEMINI_API_KEY=fake-key-123` + `HTTPS_PROXY`/`HTTP_PROXY=http://127.0.0.1:9` (cổng chết) → submit toàn bộ 11 câu sai | `evidence/wp4/11_break_b_gemini_dead_network.txt` | **XANH** — log `GeminiLLM.generate failed (no retry): [WinError 10061] ...`, `POST /submit` vẫn 200, 11 item đủ đúng 11 field bắt buộc của `RemediationItem`. Ghi chú: không retry vì `ConnectError` không nằm trong tập retryable (`TimeoutException`/429/5xx) — đúng theo spec H01 việc 4, không phải lỗi |
| c | Gọi thẳng `validator.validate` với quote bịa: đổi 1 từ ("suy luan" → "suy nghi") + chèn khoảng trắng/newline lạ, xem chuẩn hoá khoảng trắng có vô tình cho lọt không | `evidence/wp4/12_break_c_validator_fabricated_quote.txt` | **XANH** — `fallback=True`, `citations=[]`, quote đổi từ vẫn bị từ chối dù có whitespace lạ |
| d (bắt buộc) | Copy `lessons.json`/`quiz-day01.json`/`golden-set.json` ra thư mục tạm NGOÀI repo (`mktemp -d`), cố ý sửa `expect_path`/`expect_paths` của case-01,02,03 (happy→no_grounding) và case-18:q01, case-19:q09 (đảo path) CHỈ trong bản copy, chạy `DATA_DIR=<tmp>/mock-data python backend/eval/run_eval.py --verbose` | `evidence/wp4/13_break_d_eval_red_on_corrupted_data_DATA_DIR.txt` | **ĐỎ đúng như kỳ vọng** — `pass` giảm từ `21/21` (dữ liệu thật) xuống **`pass=16/21`**, `fallback_ok` giảm `7/7`→`6/12`... cụ thể `fallback_ok=7/12`; 5 case sai (case-01,02,03,18,19) đều in `passed=False`. Xác nhận repo KHÔNG bị đụng: `git status --short` và `git diff --stat -- codebase/mock-data/golden-set.json` sau khi chạy đều rỗng |
| f (tự nghĩ) | Submit với 1 `qid` lạ không tồn tại trong quiz lẫn trong `answers`, rồi gọi `POST /api/remediate/confirm` với `hypothesis_id="h-garbage-999"` cho MỌI câu sai | `evidence/wp4/14_break_f_unknown_qid_garbage_hypothesis.txt` | **XANH** — submit vẫn 200 (qid lạ bị bỏ qua khi chấm), `confirm_hypothesis` với id rác không crash ở câu nào, tất cả 200 |

Tổng: 5 cách phá (≥3 theo yêu cầu), gồm đúng 1 cách bắt buộc (d) chứng minh bộ đo mới đỏ trên dữ liệu hỏng qua `DATA_DIR`, không sửa file nào trong repo. 4/5 cách còn lại không lật được pipeline (hệ đang XANH thật, không phải do tôi thiếu cố gắng phá — đã thử cả input rác, mạng chết, quote bịa, qid lạ).

## 6. Câu hỏi mở

- Không có mâu thuẫn với SPEC hay quyết định thiếu cần người trong phạm vi WP4. Một quan sát nhỏ (không phải lỗi): ở break-test (b), `GeminiLLM._is_retryable_error` không coi `httpx.ConnectError` là retryable nên không retry trước khi fallback — đúng với "xong khi" của H01 việc 4 (chỉ retry khi Timeout hoặc 429/5xx), nêu ra để SO biết đây là hành vi cố ý chứ không phải sót.

## 7. Tiếp theo
🖐 SO xem `evidence/wp4/13_...DATA_DIR.txt` để tự kiểm chứng bộ đo mới nhạy với dữ liệu hỏng.
🤖 Không có việc tự động tiếp theo trong phạm vi WP4.
⭐ Không đề xuất thêm.
⏸ Chờ phán quyết SO cho WP1+WP2 dựa trên số đo ở trên.

Chờ phán quyết SO.

✅ DUYỆT
