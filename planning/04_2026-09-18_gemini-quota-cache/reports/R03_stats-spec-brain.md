# R03 — `groq=` trong eval stats, số thật vào spec §7/§9, đồng bộ não, bump v0.2.2, đóng hồ sơ #04

Vai: worker (vai-thi-cong) · loại: THI CÔNG · họ/model: Claude Sonnet 5 · Bước 0: exit 0 · hiểu việc: (1) 🟠 mở khoá phần bị mâu thuẫn ở H02 — thêm `groq=<n>` vào `format_llm_stats_line` của `run_eval.py` + sửa đúng phần test khớp định dạng mới trong `test_golden_set_eval.py` (không đổi logic khác); (2) 🟢 điền số đo thật Gemini 18/21 + Groq 21/21 vào `spec.md` §7 (chỉ bảng kết quả + dòng ⏳ Gemini) và 1 dòng §9; (3) 🟢 đồng bộ não Ma Trận 6 Điểm + `project-intro.md`/`-data-architecture.md`, `state.json` → 0.2.2, `changelog.md` v0.2.2, 3 gotcha mới, `today.md`; (4) 🟢 `plan.md` #04 → ✅ ĐÃ HOÀN THÀNH + tick WP3. Không gọi mạng thật ở bước nào. KHÔNG đụng file ngoài danh sách ĐƯỢC sửa của H03.

Handoff: `planning/04_2026-09-18_gemini-quota-cache/handoffs/H03_stats-spec-brain.md`
Base: a7c9158
Head: (điền ở mục 3 sau khi `git commit` chạy xong — không thể biết trước SHA của commit chứa chính report này, theo đúng tiền lệ R01/R02 của hồ sơ này)

## 1. Lệnh + exit code

```
node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check   → exit 0 (chạy 2 lần: trước và sau khi sửa não, cả 2 đều exit 0)
LLM_MODE=mock python -m pytest backend -q                                                       → exit 0
LLM_MODE=mock python backend/eval/run_eval.py --llm-stats                                        → exit 0
```

`LLM_MODE=mock python backend/eval/run_eval.py --llm-stats | grep -c 'groq='` = 1.
`grep -c '⏳' spec.md` = 4 (chỉ còn 4 dòng quote §1, đúng mục tiêu).
`grep -c 'v0.2.2' brain4agent/changelog.md` = 1.
`python -c "import json;print(json.load(open('brain4agent/memory/hot/state.json'))['current_version'])"` = `0.2.2`.
`grep -c '\[x\]' planning/04_2026-09-18_gemini-quota-cache/plan.md` = 1 (dòng checklist có cả WP1/WP1b/WP2/WP3 đều tick, kể cả WP3).

## 2. Test tổng/pass/fail/skip

`LLM_MODE=mock python -m pytest backend -q`: **75 tổng / 75 pass / 0 fail / 0 skip** (giữ nguyên số của R02 — chỉ đổi 1 hàm format + 1 dòng test, không thêm/bớt test nào). File: `planning/04_2026-09-18_gemini-quota-cache/evidence/wp3/pytest.txt`.

`LLM_MODE=mock python backend/eval/run_eval.py --llm-stats` →
```
llm gemini=0 groq=0 cache=0 mock_fallback=0 model=-
eval pass=21/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0
```
(File: `evidence/wp3/eval.txt`; dòng tổng giữ nguyên định dạng cũ như yêu cầu.)

## 3. `git diff --stat` + SHA

```
 brain4agent/-data-architecture.md                  | 23 ++++++--
 brain4agent/-known-gotchas.md                      | 18 ++++++
 brain4agent/changelog.md                           | 40 +++++++++++++
 brain4agent/index.md                               | 18 +++---
 brain4agent/memory-distill.txt                     |  4 +-
 brain4agent/memory/hot/state.json                  |  6 +-
 brain4agent/memory/hot/today.md                    | 65 +++++++++++++++++++++-
 brain4agent/project-intro.md                       | 17 ++++--
 brain4agent/roadmap.md                             |  7 ++-
 codebase/backend/eval/run_eval.py                  |  7 ++-
 codebase/backend/tests/test_golden_set_eval.py     | 14 +++--
 .../evidence/wp3/check.txt                         | 20 +++++++
 .../evidence/wp3/eval.txt                          |  3 +
 .../evidence/wp3/pytest.txt                        | 10 ++++
 planning/04_2026-09-18_gemini-quota-cache/plan.md  |  4 +-
 spec.md                                            |  6 +-
 16 files changed, 223 insertions(+), 39 deletions(-)
```

Cộng report này. Commit 1 lần, message `chore(release): v0.2.2 -- groq stats line, real eval numbers in spec, brain sync` (đúng luật §4 của H03), 16 file như trên; SHA điền ở dòng "Head" phía trên sau khi `git commit` chạy xong.

## 4. Bảng phân công

| Gói | Tầng | Họ/model |
|---|---|---|
| Việc 1 (`groq=` trong eval stats) | 🟠 | Claude Sonnet 5 |
| Việc 2 (`spec.md` §7/§9) | 🟢 | Claude Sonnet 5 |
| Việc 3 (đồng bộ não 6 điểm + 2 file ngoài) | 🟢 | Claude Sonnet 5 |
| Việc 4 (`plan.md` #04 đóng hồ sơ) | 🟢 | Claude Sonnet 5 |

Không có sub-agent nào được giao việc.

## 5. Việc KHÔNG làm + lý do

- **Không sửa thêm gì trong `run_eval.py` ngoài `format_llm_stats_line`**: chỉ thêm `groq={stats.get('groq', 0)}` vào chuỗi trả về (dùng `.get` với default 0 để không vỡ nếu ai gọi hàm với dict thiếu key `groq`) + cập nhật 1 dòng docstring mô tả đúng định dạng mới (cùng một mối quan tâm, không phải thay đổi khác).
- **Sửa 2 test trong `test_golden_set_eval.py` thay vì đúng 1 test như "xong khi" nêu tên**: `test_format_llm_stats_line_shape` (được nêu tên rõ) VÀ `test_main_with_llm_stats_flag_prints_provider_counts_line` (không được nêu tên, nhưng gọi `main()` thật nên đụng đúng chuỗi cũ `"llm gemini=0 cache=0 mock_fallback=0 model=-"` — không sửa thì test này FAIL ngay, vi phạm luật "test cũ không giảm" và cổng đo "≥75 pass/0 skip" của chính H03). §2 của H03 cho phép "CHỈ test khớp định dạng dòng đó" (số nhiều theo nghĩa "test(s) khớp định dạng", không phải đúng 1 dòng), nên tôi coi đây là trong phạm vi, không phải tự nới quyền — chỉ đổi đúng 1 chuỗi kỳ vọng ở mỗi test, không đổi logic nào.
- **`spec.md`**: chỉ sửa bảng kết quả §7 (thay 1 dòng ⏳ bằng 2 dòng số thật + 1 dòng ghi chú thứ tự provider/cache) và thêm đúng 1 dòng vào bảng §9, đúng phạm vi; không đụng §1/§4/§4b/§6/§8 hay 4 dòng `⏳` còn lại (cần data pack ngoài repo, không thuộc việc của H03).
- **Não**: không tạo file mới trong `brain4agent/` (đúng luật `nao-dong-bo`); không sửa `AGENTS.md`/`CLAUDE.md`/`brain4agent-v1.7.1.md`/`canvas.md`/`README.md`/`.env` (đều trong CẤM chạm của H03).
- **Không tự tuyên bố ĐẠT/KHÔNG ĐẠT cổng đo** — chỉ nộp số liệu.

## 6. Câu hỏi cần người (SO)

Không có câu hỏi mở mới — 3 câu hỏi mở từ R02 đã được SO trả lời dứt điểm trong lệnh giao việc H03 (mở khoá `run_eval.py`/`test_golden_set_eval.py`, chấp nhận mốc `groq≥40` sai quy mô, xác nhận cache Gemini tăng 10→13 entry là do SO warm cache).

## 7. Tiếp theo

- SO đọc report + `evidence/wp3/{pytest.txt,eval.txt,check.txt}`, quyết định hồ sơ #04 đã đủ điều kiện đóng hoàn toàn.
- `spec.md` còn 4 dòng `⏳` ở §1 (quote nguyên văn từ data pack ngoài repo `tutor_turns.csv`/`transcript-04-clean.md`) — không thuộc phạm vi hồ sơ #04, cần hồ sơ khác nếu muốn điền nốt.
- `roadmap.md` Active đã cập nhật CP3 "đã có video + số, chờ nộp" và CP4 còn 4 dòng ⏳ — SO cân nhắc thời điểm nộp CP4/CP5 theo hạn trong `README.md`.
- Không còn WP nào trong `plan.md` #04 dở dang; hồ sơ tiếp theo (nếu có) nên mở dossier mới thay vì tiếp tục #04.

Chờ phán quyết SO.
