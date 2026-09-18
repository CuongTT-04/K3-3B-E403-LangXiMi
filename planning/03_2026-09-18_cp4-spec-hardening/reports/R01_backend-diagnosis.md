Vai: worker (vai-thi-cong) · loại: thi công · họ/model: Claude Sonnet · Bước 0: exit 0 · hiểu việc: luồn `chosen` (phương án học viên chọn) từ `service.remediate` → `_remediate_one` → `LLM.generate` để `misconception` giải thích đúng vì sao phương án ĐÃ CHỌN sai (Mock trả field `misconception` mới, Gemini prompt thêm stem/options/đáp án đúng/chosen); validator giữ `misconception` của LLM khi không rỗng (rơi về `misconception_hint` khi thiếu) và so quote sau khi chuẩn hoá khoảng trắng; `GeminiLLM.generate` không bao giờ raise (bọc try/except, retry đúng 1 lần khi timeout/429/5xx, lỗi lần 2 rơi về MockLLM); đáp án câu củng cố của MockLLM đặt theo `chunk_id` thay vì luôn "A"; `confirm_hypothesis` gắn tiền tố explanation khác nhau cho h1/h2; cập nhật `docs/backend.md`. Phạm vi chỉ 4 file app + 4 file test + docs/backend.md (đoạn mô tả) + report/evidence; cấm chạm `schemas.py`, `mock-data/**`, `frontend/**`, `spec.md`, `golden-set.json`, `test_mockdata.py`, `eval/run_eval.py`.
Handoff: planning/03_2026-09-18_cp4-spec-hardening/handoffs/H01_backend-diagnosis.md
Base: 374230daa56ab45db532af3d044c434c4d8d2ccd
Head: e536896ba6a4297e73c4a54e6388535f95d42cfe

## 1. Lệnh + exit code (nguyên văn)
- `node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check` → `🎉 [KẾT QUẢ CHẨN ĐOÁN] BỘ NÃO DỰ ÁN ĐÃ HOÀN HẢO! ... NÃO ĐÃ OK — KHÔNG CẦN NÂNG CẤP THÊM!` → exit 0
- `python -m pytest backend -q` (từ `codebase/`) → `49 passed, 1 warning in 2.65s` → exit 0
- `python backend/eval/run_eval.py` (từ `codebase/`) → `eval pass=21/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0` → exit 0
- 2 lệnh eval/pytest trên đã chạy lại 3 lần trong lúc thi công (mỗi lần SHA của commit tôi bị dịch chuyển do amend/rebase của worker khác — xem mục "Câu hỏi mở") và luôn ra đúng cùng một kết quả: `49 passed, 0 fail, 0 skip` · `eval pass=21/21 ... citations_invalid=0`.
- Output nguyên văn đã lưu: `planning/03_2026-09-18_cp4-spec-hardening/evidence/wp1/pytest.txt`, `.../evidence/wp1/eval.txt` (chụp lần đầu tại commit `36ea84a`; nội dung 7 file thuộc phạm vi tôi không đổi qua các lần amend/rebase sau đó tới `e536896` — đã diff xác nhận rỗng cho 7 file này giữa `36ea84a`/`0c8eaff`/`e536896`).

## 2. Test tổng/pass/fail/skip
- Phạm vi của tôi (`test_service.py` + `test_validator.py` + `test_llm_gemini.py`, các test mới thêm): 10 test mới (`test_misconception_mentions_chosen_option`, `test_reinforcement_answer_position_varies_and_matches_source_chunk`, `test_confirm_hypothesis_branches_explanation_by_hypothesis_id`, `test_validator_keeps_llm_misconception_when_present`, `test_validator_accepts_quote_with_extra_whitespace`, `test_validator_rejects_quote_with_changed_word_even_after_normalizing`, `test_gemini_llm_generate_never_raises_on_connection_error`, `test_gemini_llm_generate_never_raises_on_malformed_json_body`) — tất cả pass; test cũ trong 3 file này (bao gồm `test_validator_accepts_valid_item`, `test_gemini_llm_generate_parses_json_without_network`, `test_confirm_hypothesis_returns_happy_item_with_reinforcement`, …) vẫn pass nguyên vẹn.
- Toàn `backend -q` (bao gồm việc của WP2/WP3 song song trên cùng cây): 49 tổng, 49 pass, 0 fail, 0 skip, 1 warning (DeprecationWarning `anyio.abc.BlockingPortal` trong `starlette/testclient.py`, không liên quan thay đổi của tôi). ≥47 pass theo "xong khi" của WP1 — đạt.
- `eval pass=21/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0` — N=21 vì golden-set.json đã được worker WP2 mở rộng song song (không phải việc của tôi).

## 3. `git diff --stat` + SHA
Diff `374230d..e536896` giới hạn đúng phạm vi của tôi:
```
codebase/backend/app/llm.py               | 124 ++++++++++++++++++++++++------
codebase/backend/app/service.py           |  29 +++++--
codebase/backend/app/validator.py         |  18 ++++-
codebase/backend/tests/test_llm_gemini.py |  30 ++++++++
codebase/backend/tests/test_service.py    |  50 ++++++++++++
codebase/backend/tests/test_validator.py  |  40 ++++++++++
docs/backend.md                           |  20 ++++-
7 files changed, 274 insertions(+), 37 deletions(-)
```
Commit gốc của tôi: `36ea84a933713217a660315770ca2504268c61d1` "fix(remediation): diagnose from chosen option, harden gemini, vary reinforcement answer" (9 files changed, 285 insertions(+), 37 deletions(-) — 7 file trên + 2 file evidence `evidence/wp1/{pytest,eval}.txt`), tạo bằng `git commit -m "..." -- <9 pathspec riêng>` (không `add -A`, không cuốn theo file đang stage sẵn của người khác). Vì 3 worker share 1 cây git không worktree, commit này sau đó bị SHA hoá lại 2 lần bởi hoạt động của worker/SO khác (amend để họ vá dòng "Head" tự tham chiếu trong report của họ, rồi SO rebase khi mở dossier #03): `36ea84a` → `0c8eaff` → `e536896` (SHA hiện tại trong log). Đã diff `36ea84a..e536896` cho đúng 7 file mã nguồn của tôi: rỗng — nội dung không đổi qua các lần đó. Tôi không tự amend/rebase gì.

## 4. Bảng phân công (gói → tầng → họ/model)
| Gói | Tầng | Họ/model |
|---|---|---|
| WP1 (handoff này) | 🟠 | Claude Sonnet |
| WP2 (golden-set ≥20, song song, quan sát qua git log) | 🟠 | Claude Sonnet (worker khác) |
| WP3 (spec fill, song song, quan sát qua git log) | 🟠 | Claude Sonnet (worker khác) |

## 5. Việc KHÔNG làm + lý do
- Không đổi `main.py`: `_score_quiz`/`post_remediate` đã sẵn field `chosen` trong `results` (dòng có sẵn trước handoff), không cần sửa gì để việc 1 chạy được.
- Không thêm test cho nhánh retry "thành công ở lần 2" của `GeminiLLM` (chỉ có 2 test bắt buộc theo "xong khi": ConnectError và JSON hỏng, cả hai đều là lỗi không-retryable nên fallback ngay lần 1) — nằm ngoài "xong khi" của việc 4, không tự thêm để tránh "sửa cho tốt hơn" ngoài phạm vi.
- Không chạm `codebase/mock-data/golden-set.json`, `test_mockdata.py`, `eval/run_eval.py`, `spec.md` — đúng luật CẤM của handoff.

## 6. Câu hỏi mở
- Trong lúc thi công, 3 worker share chung 1 cây git (không worktree, đúng như plan.md đã lường trước) đã xảy ra nhiều sự kiện ngoài kịch bản "index.lock" đơn thuần:
  1. Lần đầu, commit của tôi bị một `git commit` khác của WP2 "nuốt" chung với 15 file của WP2 (không lỗi, không lock — chỉ là 2 tiến trình `git add`/`git commit` xen kẽ trên cùng index); sau đó một tiến trình khác đã `git reset` về base để tách lại — working tree không mất nội dung (mixed reset không đụng working tree), tôi verify lại từng file bằng grep trước khi commit lại.
  2. Sau khi tôi commit bằng `git commit -m ... -- <pathspec đúng 9 file của tôi>` (an toàn hơn add+commit trần vì không cuốn theo file đang stage sẵn của người khác) ra SHA `36ea84a`, ít nhất 2 lần amend/rebase tiếp theo của worker/SO khác (để vá dòng Head tự tham chiếu trong report của họ, rồi SO mở dossier #03 và rebase) đã đổi SHA của đúng commit này thành `0c8eaff` rồi `e536896`, dù nội dung 7 file mã nguồn của tôi không đổi (đã diff xác nhận rỗng). Tôi không có cách nào ngăn từ phía worker WP1 vì SO quyết định không dùng worktree.
  - Đề xuất: từ hồ sơ sau, dùng worktree tách biệt cho mỗi worker, hoặc nếu tiếp tục share 1 cây thì mọi worker dùng `git commit -- <pathspec riêng>` VÀ tránh amend commit không phải của mình.
- Không có câu hỏi mở về spec — 7 việc trong handoff đều có "xong khi" rõ, đã làm đủ và tự kiểm bằng test.

## 7. Tiếp theo
🖐 Cần người: xác nhận SHA cuối của WP1 (hiện là `e536896`, nội dung 7 file không đổi qua các lần rebase) trước khi WP4 thẩm định; SHA có thể còn dịch chuyển tiếp nếu SO tiếp tục rebase — nên chốt bằng nội dung diff, không chỉ bằng số SHA.
🤖 Có thể tự động: WP4 (H04_audit) chạy `pytest backend -q` + `run_eval.py` trên HEAD hiện hành, đối chiếu diff `374230d..HEAD` cho 7 file trên với bảng ở mục 3.
⭐ Đề xuất: dùng worktree riêng cho mỗi worker ở hồ sơ sau để tránh amend/rebase chéo làm SHA trôi giữa chừng.
⏸ Chờ: không có việc nào của WP1 đang treo.

Chờ phán quyết SO.

✅ DUYỆT — SO đo lại 2026-09-18: `git diff --stat 374230d..HEAD` 7 file đúng phạm vi H01, `schemas.py`/mock-data/frontend không đổi · `pytest backend -q` 49 passed/0 skip · eval `pass=21/21 citations_invalid=0` · smoke in-process: misconception nêu phương án đã chọn, đáp án củng cố ∈ {A,B,C,D}, h1/h2 explanation khác nhau, `chosen="Z"` → 200. Ghi nhận đề xuất worktree cho hồ sơ sau.
