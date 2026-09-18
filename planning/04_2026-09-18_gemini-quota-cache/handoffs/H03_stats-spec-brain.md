# H03 — WP3 `groq=` trong eval stats + số thật vào spec §7 + đồng bộ não + bump v0.2.2 + đóng hồ sơ #04
Vai: worker THI CÔNG (đọc `.agents/skills/vai-thi-cong/SKILL.md`), tầng 🟠 (phần 1) rồi 🟢 (phần 2–4), họ Claude Sonnet. Nối tiếp H01/H02 (cùng worker). Base = Head hiện tại của nhánh.
Bước 0: `node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check` (chỉ đọc; ghi exit code).
Thứ tự đọc: `planning/04_2026-09-18_gemini-quota-cache/plan.md` → `reports/R01_*`, `reports/R02_*` (lấy số đo) → `evidence/wp1/eval-gemini.txt`, `evidence/wp1b/eval-groq.txt`, `evidence/demo/` (liệt kê) → `codebase/backend/eval/run_eval.py` → `codebase/backend/tests/test_golden_set_eval.py` → `spec.md` §7, §9 → `.agents/skills/nao-dong-bo/SKILL.md` → 8 file `brain4agent/`.

## 1. Bối cảnh
Hồ sơ #04: R01 ✅ (xoay Gemini, cache, validator bỏ dấu; 63 test; Gemini thật 18/21), R02 ✅ (Groq chuỗi sau Gemini; 75 test; Groq thật 21/21), WP2 ✅ (video Chrome 23,4s + 8 ảnh tại `evidence/demo/`, quay với Gemini thật qua cache). Còn thiếu: dòng `llm …` của `run_eval.py --llm-stats` chưa in `groq=`; spec §7 chưa có số thật; não chưa đồng bộ; version còn 0.2.1.

## 2. Phạm vi
- ĐƯỢC sửa: `codebase/backend/eval/run_eval.py` (CHỈ hàm format dòng `llm …`) · `codebase/backend/tests/test_golden_set_eval.py` (CHỈ test khớp định dạng dòng đó) · `spec.md` (CHỈ §7 bảng kết quả + dòng ⏳ Gemini, và §9 thêm 1 dòng) · `brain4agent/{index.md,roadmap.md,changelog.md,-known-gotchas.md,memory-distill.txt,project-intro.md,-data-architecture.md}` · `brain4agent/memory/hot/{today.md,state.json}` · `planning/04_*/plan.md` (mục 1 trạng thái, mục 4 checklist) · `reports/R03_stats-spec-brain.md` · `evidence/wp3/*.txt`.
- CẤM chạm: mọi file khác trong `codebase/` · `docs/` · `AGENTS.md` · `CLAUDE.md` · `brain4agent-v1.7.1.md` · `canvas.md` · `README.md` · `.env`. Không tạo file mới trong `brain4agent/`.

## 3. Việc phải làm
1. 🟠 `format_llm_stats_line` in `llm gemini=<n> groq=<n> cache=<n> mock_fallback=<n> model=<…>`; sửa `test_format_llm_stats_line_shape` khớp định dạng mới (chỉ đổi chuỗi kỳ vọng). Xong khi: `LLM_MODE=mock python -m pytest backend -q` ≥75 pass/0 skip; `LLM_MODE=mock python backend/eval/run_eval.py --llm-stats | grep -c 'groq='` = 1.
2. 🟢 `spec.md` §7 bảng kết quả: thay dòng `⏳ Gemini thật (chưa có key)` bằng 2 dòng: `18/9 · Gemini thật (gemini-3.5/3.6-flash, xoay model, 20 req/ngày/model) · 18/21 pass · fallback_ok 7/7 · low_conf_ok 7/7 · citations_invalid 0 · 3 case rớt do validator chặn trích dẫn không khớp (an toàn)` và `18/9 · Groq thật (openai/gpt-oss-120b→20b, qwen3.8-27b) · 21/21 pass · fallback_ok 7/7 · low_conf_ok 7/7 · citations_invalid 0`; thêm dưới bảng 1 dòng ghi thứ tự provider Gemini→Groq→Mock và cache đĩa; §9 thêm dòng `18/9 · hồ sơ #04: số đo AI thật + video CP3 · vì CP3`. Xong khi: `grep -c '⏳' spec.md` = 4 (chỉ còn 4 quote §1).
3. 🟢 Não (Ma Trận 6 Điểm + 2 file ngoài): `changelog.md` thêm `[v0.2.2] - 2026-09-18` lên đầu (Added: GEMINI_MODELS xoay, GroqLLM + ChainLLM, cache đĩa, validator bỏ dấu, `--llm-stats/--sleep`; Notes: số đo thật + video); `roadmap.md`: Done thêm hồ sơ #04, Active cập nhật CP3 "đã có video + số, chờ nộp", Idea Vault thêm "nâng gói trả phí Gemini hoặc chỉ dùng Groq nếu quota"; `-known-gotchas.md` thêm 3 mục (quota 20 req/ngày/model + 2.x 404; `parts[i].thoughtSignature`; `llama-3.3-70b` không có trên Groq, 8000 TPM ⇒ `--sleep 1`); `index.md` codebase map thêm `test_llm_groq.py`, `.runtime/llm-cache*.json`, `planning/04_*`; `memory-distill.txt` cập nhật provider chain + số đo (giữ <100 dòng); `project-intro.md`/`-data-architecture.md` cập nhật LLM chain + cache; `today.md` thêm phiên hồ sơ #04 (số đo, quyết định, gotcha) — KHÔNG kể chuyện; `state.json` `current_version` → `"0.2.2"`, `active_plans_completed` → 4, timestamp mới. Xong khi: `--check` exit 0; `grep -c 'v0.2.2' brain4agent/changelog.md` ≥1; `python -c "import json;print(json.load(open('brain4agent/memory/hot/state.json'))['current_version'])"` = 0.2.2.
4. 🟢 `plan.md` #04: Trạng thái → `✅ ĐÃ HOÀN THÀNH (2026-09-18 HH:MM:SS)`; checklist tick WP3. Xong khi: `grep -c '\[x\]' planning/04_*/plan.md` ≥1 dòng có WP3.
5. Cổng đo: `LLM_MODE=mock python -m pytest backend -q` exit 0/0 skip · `LLM_MODE=mock python backend/eval/run_eval.py --llm-stats` 2 dòng cuối · `--check` exit 0. Lưu vào `evidence/wp3/{pytest,eval,check}.txt`. KHÔNG gọi mạng thật.

## 4. Luật
Commit 1 lần, `git add` từng file, `git commit -m "chore(release): v0.2.2 -- groq stats line, real eval numbers in spec, brain sync" -- <files>`. KHÔNG push. Không in key.

## 5. Tầng
Việc 1 🟠; việc 2–5 🟢.

## 6. Report
`reports/R03_stats-spec-brain.md`: dòng 1 khai vai; dòng 2–4 Handoff/Base/Head; 7 mục; dòng cuối `Chờ phán quyết SO`. Trả lời cuối = nguyên văn report.
