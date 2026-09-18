# H01 — WP1 Backend: chẩn đoán theo `chosen`, Gemini không raise, củng cố không cố định
Vai: worker THI CÔNG (đọc `.agents/skills/vai-thi-cong/SKILL.md`), tầng 🟠, họ Claude Sonnet.
Bước 0: từ root repo chạy `node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check` (chỉ đọc; ghi exit code vào report).
Thứ tự đọc: `planning/03_2026-09-18_cp4-spec-hardening/plan.md` §2 → `docs/backend.md` → `codebase/backend/app/{service,llm,validator,main}.py` → `codebase/backend/tests/`.

## 1. Bối cảnh
Quiz Remediation MVP (FastAPI + mock LLM). Pipeline hiện bỏ qua phương án học viên chọn (`chosen`), validator ghi đè misconception bằng hint tĩnh, `GeminiLLM.generate` raise khi lỗi mạng/parse, câu củng cố mock luôn đáp án A, hai hypothesis trả cùng kết quả. Spec §4/§6 (`spec.md`) đã chốt: chẩn đoán phải nói rõ vì sao phương án ĐÃ CHỌN sai.

## 2. Phạm vi
- ĐƯỢC sửa: `codebase/backend/app/{service.py,llm.py,validator.py,main.py}` · `codebase/backend/tests/{test_service.py,test_validator.py,test_llm_gemini.py,test_api.py}` · `docs/backend.md` (chỉ đoạn mô tả chẩn đoán/Gemini) · `planning/03_*/reports/R01_backend-diagnosis.md` · `planning/03_*/evidence/wp1/*.txt`.
- CẤM chạm: `codebase/mock-data/**` · `codebase/frontend/**` · `codebase/index.html` · `spec.md` · `brain4agent/**` · `schemas.py` (KHÔNG đổi/xoá/thêm field bắt buộc nào của `RemediationItem`, `SubmitOut`).
- Một worker khác đang sửa `golden-set.json`, `test_mockdata.py`, `eval/run_eval.py` song song trên cùng cây — KHÔNG đụng 3 file đó; `git add` TƯỜNG MINH từng file của mình; commit ở CUỐI; gặp `index.lock` thì đợi 5s rồi thử lại. Nếu pytest đỏ ở test KHÔNG thuộc phạm vi bạn ⇒ ghi vào report, KHÔNG sửa.

## 3. Việc phải làm (mỗi việc kèm "xong khi")
1. Luồn `chosen`: `service.remediate` truyền `result.get("chosen")` vào `_remediate_one(question, lessons_by_id, lessons, chosen=None)`; `LLM.generate(self, question, chunks, distractor_pool=None, chosen=None)` (tham số mới có mặc định, tương thích ngược). `MockLLM` trả thêm key `"misconception"`: nếu `chosen` hợp lệ và `chosen != question["answer"]` ⇒ `f"Bạn chọn {chosen} ('{options[chosen]}') nhưng đáp án đúng là {answer} ('{options[answer]}'). {hint}"`, ngược lại dùng `misconception_hint`. `_build_prompt` (Gemini) thêm stem, options, đáp án đúng, phương án đã chọn, và yêu cầu field `"misconception"` trong JSON.
   Xong khi: test mới `test_misconception_mentions_chosen_option` (submit q01 với chosen sai) pass; `grep -n chosen codebase/backend/app/service.py codebase/backend/app/llm.py` có ≥4 dòng.
2. Validator giữ `raw_item["misconception"]` nếu là chuỗi không rỗng, ngược lại rơi về `misconception_hint` như cũ. Xong khi: test `test_validator_keeps_llm_misconception_when_present` pass và test cũ `test_validator_accepts_valid_item` vẫn pass.
3. Validator chuẩn hoá khoảng trắng: hàm `_norm(s) = " ".join(s.split())`, so `_norm(quote) in _norm(chunk_text)`. Xong khi: test quote có xuống dòng/2 khoảng trắng ⇒ chấp nhận; quote đổi một từ ⇒ vẫn bị từ chối (2 test).
4. `GeminiLLM.generate` KHÔNG raise: bọc HTTP + parse trong try/except (`httpx.HTTPError`, `ValueError`, `KeyError`, `IndexError`, `TypeError`); retry đúng 1 lần khi `httpx.TimeoutException` hoặc status 429/5xx; lỗi lần 2 ⇒ `logger.warning` rồi `return MockLLM().generate(question, chunks, distractor_pool, chosen=chosen)`. Xong khi: 2 test mới (post raise `httpx.ConnectError`; body JSON hỏng) đều trả dict có 4 key `explanation/citations/reinforcement/confidence` và không raise; test cũ trong `test_llm_gemini.py` giữ nguyên pass.
5. Đáp án củng cố không cố định: vị trí đáp án đúng = `"ABCD"[sum(ord(c) for c in chunk["id"]) % 4]`, các distractor xếp vào chữ còn lại theo thứ tự; `answer` khớp chữ đó; `source_id` giữ nguyên. Xong khi: test duyệt cả 11 câu sai của `day01` ⇒ tập `answer` có ≥2 chữ khác nhau, và với mọi item `options[answer]` == câu đầu của chunk `source_id`.
6. `confirm_hypothesis(hypothesis_id)` rẽ nhánh: `h1` ⇒ `explanation` mở đầu bằng `"Nguyên nhân bạn xác nhận: nhầm lẫn khái niệm. "`, `h2` ⇒ `"Nguyên nhân bạn xác nhận: đọc lướt bỏ sót từ khoá. "` rồi nối explanation gốc; id khác ⇒ giữ nguyên. Xong khi: test gọi h1 và h2 cho `q09` ⇒ `explanation` khác nhau, `citations` bằng nhau, `path == "happy"`.
7. Cập nhật `docs/backend.md`: đoạn "Bật Gemini thật" ghi rõ hành vi không raise + retry; đoạn Schema ghi `misconception` nay lấy từ LLM có `chosen`. Xong khi: `grep -n "retry" docs/backend.md` ≥1 dòng.
8. Cổng đo cuối (chạy từ `codebase/`): `python -m pytest backend -q` ⇒ exit 0, ≥47 pass, 0 skip · `python backend/eval/run_eval.py` ⇒ dòng cuối có `citations_invalid=0` và `pass=N/N` (N = tổng case hiện có trong `golden-set.json`, có thể đã tăng do worker kia). Lưu nguyên văn 2 output vào `evidence/wp1/pytest.txt`, `evidence/wp1/eval.txt`.

## 4. Luật
- Không sửa số kỳ vọng của test cũ, trừ khi handoff nêu; test không được giảm; 0 skip. Không `git add -A`. Commit 1 lần, tiếng Anh, Conventional Commits, ví dụ `fix(remediation): diagnose from chosen option, harden gemini, vary reinforcement answer`. KHÔNG push.
- Không "sửa cho tốt hơn" ngoài 7 việc trên. Thiếu quyết định ⇒ ghi "Câu hỏi mở" vào report, làm phần độc lập.

## 5. Tầng
Cả gói 🟠 (có spec + test tự biết đúng/sai). Không ghi tên model vào code.

## 6. Report
Viết `planning/03_2026-09-18_cp4-spec-hardening/reports/R01_backend-diagnosis.md` theo mẫu: dòng 1 khai vai (`Vai: worker (vai-thi-cong) · loại: thi công · họ/model: … · Bước 0: exit … · hiểu việc: …`); dòng 2–4 `Handoff:`/`Base: 374230d`/`Head: <sha>`; rồi 7 mục: lệnh + exit code nguyên văn · test tổng/pass/fail/skip · `git diff --stat` + SHA · bảng phân công (gói → tầng → họ/model) · việc KHÔNG làm + lý do · câu hỏi mở · Tiếp theo 4 dòng (🖐/🤖/⭐/⏸). Dòng cuối: `Chờ phán quyết SO`. Trả lời cuối cho SO = nội dung report đó, không kể chuyện.
