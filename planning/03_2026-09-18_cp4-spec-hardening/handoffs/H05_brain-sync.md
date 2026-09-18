# H05 — WP5 Đồng bộ não 6 điểm + gotchas + xoay ký ức + bump v0.2.1 + điền số cuối spec §7
Vai: worker THI CÔNG (đọc `.agents/skills/vai-thi-cong/SKILL.md`), tầng 🟢 (có mẫu chép theo), họ Claude Sonnet.
Bước 0: từ root repo chạy `node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check` (chỉ đọc; ghi exit code).
Thứ tự đọc: `.agents/skills/nao-dong-bo/SKILL.md` → `.agents/skills/nao-dong-phien/SKILL.md` → `AGENTS.md` §2, §5.A–B → `planning/03_2026-09-18_cp4-spec-hardening/plan.md` → `reports/R01..R04` (chỉ lấy số đo) → `git diff --stat 374230d..HEAD` → 8 file trong `brain4agent/`.

## 1. Bối cảnh
Hồ sơ #03 đã qua thẩm định: WP1 (chẩn đoán theo `chosen`, Gemini không raise + retry 1 lần, validator chuẩn hoá khoảng trắng, đáp án củng cố theo chunk id, rẽ nhánh h1/h2), WP2 (golden set 21 case, `expect_paths`, `--verbose`), WP3 (spec.md điền §1–§3,§5,§7–§9), WP4 audit ✅. Số đo cuối: `pytest backend -q` 49 passed/0 skip · `run_eval.py` → `eval pass=21/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0`. Base `374230d`. Hôm nay 2026-09-18; `today.md` hiện ghi ngày 17.

## 2. Phạm vi
- ĐƯỢC sửa: `brain4agent/{index.md,roadmap.md,changelog.md,-known-gotchas.md,memory-distill.txt,project-intro.md,-data-architecture.md}` · `brain4agent/memory/hot/{today.md,state.json}` · TẠO `brain4agent/memory/archive/2026-09-17.md` · `spec.md` (CHỈ 2 dòng ⏳ ở §7 về số N và kết quả 18/9) · `planning/03_*/plan.md` (mục 1 trạng thái + mục 4 checklist) · `reports/R05_brain-sync.md`.
- CẤM chạm: mọi file trong `codebase/`, `docs/`, `AGENTS.md`, `CLAUDE.md`, `brain4agent-v1.7.1.md`, `canvas.md`, `README.md`, `frontend/` root. KHÔNG tạo file mới trong `brain4agent/` ngoài file archive nêu trên.

## 3. Việc phải làm
1. Xoay ký ức: chép toàn bộ nội dung `memory/hot/today.md` hiện tại (ngày 17) sang `memory/archive/2026-09-17.md` (append, giữ nguyên văn); viết lại `today.md` cho ngày 2026-09-18: phiên hồ sơ #03 — 3 worker song song + audit, số đo cuối, phán quyết, sự cố git chung index. Xong khi: `ls brain4agent/memory/archive/` có `2026-09-17.md`; `head -3 today.md` ghi ngày 2026-09-18.
2. `-known-gotchas.md`: chuyển 3 gotcha từ today.md cũ (autofill hardcode đáp án; grep `fetch(` literal; token `scaling` cho overlap) + thêm 2 gotcha mới: (a) 3 worker chung một `.git/index` không worktree ⇒ commit của nhau bị gom/amend chéo, cách phòng: `git commit -- <pathspec>` hoặc worktree riêng; (b) `GeminiLLM` chỉ retry Timeout/429/5xx, `ConnectError` fallback ngay (cố ý); (c) fallback text trong `validator._fallback_item` chưa có dấu tiếng Việt (UI hiện lẫn dấu/không dấu). Xong khi: `grep -c '^- ' brain4agent/-known-gotchas.md` ≥ 6.
3. `index.md`: bảng 1.2 skill thay `sample-skill` bằng 6 skill thật (`nao-commit, nao-dong-bo, nao-dong-phien, nao-ten-phien, vai-dieu-phoi, vai-thi-cong`, mô tả 1 dòng lấy từ frontmatter `description`); codebase map thêm `spec.md`, `canvas.md`, `codebase/index.html` (prototype CP2), `codebase/flowchart.md`, `frontend/` root (ghi "bản cũ mồ côi, chờ duyệt xoá"), `planning/03_*` (Done), `handoffs/ reports/ evidence/`; router thêm dòng `spec.md`. Xong khi: `grep -c sample-skill brain4agent/index.md` = 0; `grep -c 'planning/03_' brain4agent/index.md` ≥ 1.
4. `changelog.md`: thêm mục `[v0.2.1] - 2026-09-18` (Added/Changed/Notes theo mẫu v0.2.0, ghi số đo cuối) LÊN ĐẦU; sắp lại thứ tự để mục `[v1.0.0] Initial Project Scaffolding` nằm cuối và ghi chú đó là mốc khung não, không phải version sản phẩm. Xong khi: `grep -n 'v0.2.1' brain4agent/changelog.md` ≥1.
5. `roadmap.md`: Active bỏ mục CP3 nếu vẫn đúng thì giữ, thêm "CP4 21:00 nộp link spec.md", "CP5 22:30 slide PDF + video dự phòng"; Done thêm Hồ sơ #03 kèm số đo; Idea Vault xoá placeholder "Ý tưởng mở rộng 1", thêm: thêm dấu tiếng Việt cho lessons.json/fallback text; worktree riêng cho worker; retrieval BM25 từ stem+options thay vì `source_ids`. Xong khi: `grep -c 'Ý tưởng mở rộng 1' roadmap.md` = 0.
6. `memory-distill.txt`: cập nhật `<project_foundation>` (hồ sơ #03 Done, 49 test, golden 21 case, contract không đổi, `chosen` vào chẩn đoán, Gemini không raise); giữ < 100 dòng. Xong khi: `wc -l` < 100.
7. `project-intro.md` + `-data-architecture.md`: rà và sửa tối thiểu (golden-set 21 case có `expect_paths`; pipeline nhận `chosen`; validator chuẩn hoá khoảng trắng). Xong khi: `grep -c 'expect_paths' brain4agent/-data-architecture.md` ≥1.
8. `state.json`: `current_version` → `"0.2.1"`, `active_plans_completed` → 3, `last_verification.timestamp` = giờ hiện tại ISO, `grade` giữ. Xong khi: `python -c "import json;print(json.load(open('brain4agent/memory/hot/state.json'))['current_version'])"` = 0.2.1.
9. `spec.md` §7: thay dòng ⏳ về cơ cấu golden set bằng "21 case (10 happy · 3 low_confidence · 4 no_grounding · 4 mixed) — `codebase/mock-data/golden-set.json`"; thay dòng ⏳ "18/9 sau hồ sơ #03" trong bảng kết quả bằng `18/9 · mock · 21/21 pass · fallback_ok 7/7 · low_conf_ok 7/7 · citations_invalid 0`. KHÔNG đụng dòng ⏳ khác (quote §1, Gemini thật). Xong khi: `grep -c '⏳' spec.md` = 5.
10. `plan.md` hồ sơ #03: mục 1 Trạng thái → `✅ ĐÃ HOÀN THÀNH (2026-09-18 HH:MM:SS)`; mục 4 checklist tick WP1–WP5 và cổng nghiệm thu, kèm số đo. Xong khi: `grep -c '\[x\]' plan.md` ≥ 2.
11. Cổng đo: `node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check` exit 0 sau khi sửa. Commit 1 lần: `git add` tường minh từng file, `git commit -m "docs(brain): sync brain for dossier #03, rotate memory, bump to v0.2.1" -- <các file>`. KHÔNG push.

## 4. Luật
Không đổi hành vi mã. Không tạo file ngoài phân vùng. Tiếng Việt có dấu. Không kể chuyện trong today.md, chỉ số đo + quyết định + gotcha.

## 5. Tầng
🟢 toàn gói.

## 6. Report
`reports/R05_brain-sync.md`: dòng 1 khai vai; dòng 2–4 Handoff/Base `011b8b9`/Head; 7 mục (lệnh + exit code · test "không áp dụng, --check exit code" · `git diff --stat` + SHA · bảng phân công · việc KHÔNG làm · câu hỏi mở · Tiếp theo). Dòng cuối `Chờ phán quyết SO`. Trả lời cuối = nội dung report.
