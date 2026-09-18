# R05 — WP5 Đồng bộ não 6 điểm + gotchas + xoay ký ức + bump v0.2.1 + điền số cuối spec §7

Vai: worker (vai-thi-cong) · loại: thi công · họ/model: Claude Sonnet · Bước 0: exit 0 · hiểu việc: đồng bộ Ma Trận 6 Điểm (`index.md`, `roadmap.md`, `changelog.md`, `memory/hot/`, kernel, `-known-gotchas.md`) + 2 file ngoài 6 điểm (`project-intro.md`, `-data-architecture.md`) cho hồ sơ #03, xoay `today.md` (ngày 17) sang `memory/archive/2026-09-17.md`, viết `today.md` mới cho 2026-09-18, bump `state.json.current_version` → `0.2.1`, điền đúng 2 dòng ⏳ ở `spec.md` §7 (cơ cấu golden set + kết quả 18/9) giữ nguyên 5 dòng ⏳ khác, và tick checklist `plan.md` hồ sơ #03. Phạm vi ĐƯỢC chỉ trong `brain4agent/{index.md,roadmap.md,changelog.md,-known-gotchas.md,memory-distill.txt,project-intro.md,-data-architecture.md}`, `brain4agent/memory/hot/{today.md,state.json}`, tạo `brain4agent/memory/archive/2026-09-17.md`, `spec.md` (chỉ 2 dòng ⏳ §7), `plan.md` hồ sơ #03, `reports/R05_brain-sync.md`; CẤM chạm `codebase/`, `docs/`, `AGENTS.md`, `CLAUDE.md`, `brain4agent-v1.7.1.md`, `canvas.md`, `README.md`, `frontend/` root, không đổi hành vi mã.

Handoff: `planning/03_2026-09-18_cp4-spec-hardening/handoffs/H05_brain-sync.md`
Base: `011b8b9`
Head: (commit của việc này, tạo ngay sau report)

## 1. Lệnh + exit code (nguyên văn)
- Trước khi sửa: `node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check` → `🎉 [KẾT QUẢ CHẨN ĐOÁN] BỘ NÃO DỰ ÁN ĐÃ HOÀN HẢO! ... NÃO ĐÃ OK — KHÔNG CẦN NÂNG CẤP THÊM!` → `EXIT_CODE=0`
- Sau khi sửa: cùng lệnh → cùng kết quả `NÃO ĐÃ OK — KHÔNG CẦN NÂNG CẤP THÊM!` → `EXIT_CODE=0`
- `grep -c '^- ' brain4agent/-known-gotchas.md` → `6` (≥6, đạt)
- `grep -c sample-skill brain4agent/index.md` → `0` (đạt)
- `grep -c 'planning/03_' brain4agent/index.md` → `1` (≥1, đạt)
- `grep -n 'v0.2.1' brain4agent/changelog.md` → 1 dòng khớp (≥1, đạt)
- `grep -c 'Ý tưởng mở rộng 1' brain4agent/roadmap.md` → `0` (đạt)
- `wc -l brain4agent/memory-distill.txt` → `41` (< 100, đạt)
- `grep -c 'expect_paths' brain4agent/-data-architecture.md` → `1` (≥1, đạt)
- `python -c "import json;print(json.load(open('brain4agent/memory/hot/state.json'))['current_version'])"` → `0.2.1` (đạt); file kết thúc bằng `\n` (kiểm bằng đọc 5 byte cuối → `b' }\n}\n'`)
- `grep -c '⏳' spec.md` → `5` (đạt, đúng bằng số dòng ⏳ theo yêu cầu)
- `grep -c '\[x\]' planning/03_2026-09-18_cp4-spec-hardening/plan.md` → `2` (≥2, đạt)
- `ls brain4agent/memory/archive/` → `2026-09-17.md` có mặt (đạt)

## 2. Test
Không áp dụng — WP5 chỉ sửa tài liệu não/spec, không đổi hành vi mã. Số đo thay thế: `init_brain.js --check` exit 0 trước và sau khi sửa (xem mục 1).

## 3. `git diff --stat` + SHA
```
git diff --stat -- brain4agent/ spec.md planning/03_2026-09-18_cp4-spec-hardening/plan.md
 brain4agent/-data-architecture.md                 |  15 +++-
 brain4agent/-known-gotchas.md                     |  31 ++++++-
 brain4agent/changelog.md                          |  47 ++++++++++
 brain4agent/index.md                              |  25 ++++--
 brain4agent/memory-distill.txt                    |   2 +-
 brain4agent/memory/hot/state.json                 |   6 +-
 brain4agent/memory/hot/today.md                   | 105 +++++++++++-----------
 brain4agent/project-intro.md                      |  23 +++--
 brain4agent/roadmap.md                            |  11 ++-
 planning/03_2026-09-18_cp4-spec-hardening/plan.md |   6 +-
 spec.md                                           |   4 +-
 11 files changed, 192 insertions(+), 83 deletions(-)
```
Cộng thêm 1 file mới `brain4agent/memory/archive/2026-09-17.md` (chép nguyên văn `today.md` cũ, không nằm trong diff stat của file đã theo dõi vì là file mới). Base hồ sơ #03 (WP1–WP4): `374230d` → `011b8b9`. Head của WP5 là commit ngay sau report này.

## 4. Bảng phân công thực tế
| Gói | Tầng yêu cầu | Họ/model đã dùng |
|---|---|---|
| WP1 (backend chẩn đoán/Gemini) | 🟠 | Claude Sonnet (worker khác, đã DUYỆT ở R01) |
| WP2 (golden set 21 case) | 🟠 | Claude Sonnet (worker khác, đã DUYỆT ở R02) |
| WP3 (spec.md điền §1–§9) | 🟠 | Claude Sonnet (worker khác, đã DUYỆT ở R03) |
| WP4 (thẩm định cô lập WP1+WP2) | 🟠 | Claude Sonnet (worker khác, đã DUYỆT ở R04) |
| WP5 (đồng bộ não — việc này) | 🟢 | Claude Sonnet (tôi) |

## 5. Việc KHÔNG làm + lý do
- Không đụng `codebase/**`, `docs/**`, `AGENTS.md`, `CLAUDE.md`, `brain4agent-v1.7.1.md`, `canvas.md`, `README.md`, `frontend/` root — CẤM tường minh trong handoff.
- Không tạo file mới nào trong `brain4agent/` ngoài `memory/archive/2026-09-17.md` — đúng luật "8 phân vùng chuẩn".
- Không đụng 5 dòng ⏳ còn lại ở `spec.md` (§1 bốn quote nguyên văn ngoài repo, §7 dòng Gemini thật) — thiếu nguồn trong repo (data pack `tutor_turns.csv`/`transcript-04-clean.md` và `GEMINI_API_KEY`), đúng như R03 đã liệt kê.
- Không sửa `evidence/ui-smoke/` (thư mục untracked xuất hiện trong `git status` không do tôi tạo, có thể do SO đang bấm thử UI trên uvicorn port 8000) — ngoài phạm vi WP5, không `git add`.
- Không đổi hành vi mã, không chạy `pytest`/`run_eval.py` lại (không thuộc "xong khi" của WP5; số đo dùng lại nguyên văn từ R01–R04).
- Không tắt uvicorn đang chạy ở port 8000.

## 6. Câu hỏi mở (cần người)
- `GEMINI_API_KEY` và data pack ngoài repo (`tutor_turns.csv`, `transcript-04-clean.md`) — chưa có, nên 5 dòng ⏳ ở `spec.md` chưa điền được (đã nêu ở R03, nhắc lại vì vẫn treo).
- Duyệt xoá `frontend/` ở root (đã ghi "bản cũ mồ côi, chờ duyệt xoá" trong `index.md` — chưa xoá, chờ người).
- Chưa rõ tình trạng video demo CP3 (30 giây) đã quay hay chưa — giữ nguyên mục Active trong `roadmap.md` vì không có bằng chứng đã xong.

## 7. Tiếp theo
🖐 Cần tay người: duyệt WP5, và cấp `GEMINI_API_KEY`/data pack ngoài repo nếu muốn điền nốt 5 dòng ⏳ trước CP4 21:00.
🤖 Agent làm được ngay: không có việc tự động tiếp theo trong phạm vi WP5.
⭐ Nên làm trước: nộp link `spec.md` cho CP4 21:00 — hạn gần nhất, nội dung đã đủ để nộp (5 ⏳ còn lại đều ghi rõ lý do treo).
⏸ Chưa làm: quay video CP3, chuẩn bị slide PDF CP5, xoá `frontend/` root, merge/push nhánh `lenq` — đều cần quyết định/tay người, ngoài phạm vi WP5.

Chờ phán quyết SO.
