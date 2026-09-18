# H02 — WP1b Groq làm tầng dự phòng thứ hai (sau Gemini, trước Mock)
Vai: worker THI CÔNG (đọc `.agents/skills/vai-thi-cong/SKILL.md`), tầng 🟠, họ Claude Sonnet. Nối tiếp H01 (cùng worker, cùng cây, base = Head của R01).
Bước 0: `node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check` (chỉ đọc; ghi exit code).
Thứ tự đọc: `planning/04_2026-09-18_gemini-quota-cache/plan.md` §2 → `codebase/backend/app/llm.py` (bản sau H01) → `codebase/backend/tests/test_llm_gemini.py` → `codebase/.env.example` → `docs/backend.md`.

## 1. Bối cảnh
`codebase/.env` (gitignored) đã có `GROQ_API_KEY` thật và `GROQ_MODEL=openai/gpt-oss-120b`. Groq = API kiểu OpenAI: `POST https://api.groq.com/openai/v1/chat/completions`, header `Authorization: Bearer <key>`, body `{"model", "messages":[{"role":"user","content":prompt}], "response_format":{"type":"json_object"}, "temperature":0.2}`, kết quả ở `choices[0].message.content` (chuỗi JSON, có thể có fence). Đã đo: 1000 request/ngày, 8000 token/phút; model văn bản dùng được: `openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, `openai/gpt-oss-20b` (`llama-3.3-70b-versatile` KHÔNG có). Lỗi 429/5xx/404 ⇒ đổi model kế. Spec §4 chốt Gemini là AI lõi ⇒ thứ tự: Gemini (xoay model) → Groq (xoay model) → Mock.

## 2. Phạm vi
- ĐƯỢC sửa: `codebase/backend/app/llm.py` · `codebase/backend/tests/test_llm_gemini.py` (hoặc tạo `test_llm_groq.py`) · `codebase/.env.example` · `docs/backend.md` · `planning/04_*/reports/R02_groq-provider.md` · `planning/04_*/evidence/wp1b/*.txt`.
- CẤM chạm: `schemas.py` · `service.py` · `validator.py` · `run_eval.py` · `mock-data/**` · `frontend/**` · `.env` (không in key; che `gsk_***`). Không hồi quy H01 (xoay Gemini, cache, STATS).

## 3. Việc phải làm
1. `GroqLLM(api_key, models: list[str])` cùng interface `generate(question, chunks, distractor_pool=None, chosen=None)`, dùng lại `_build_prompt` và `_parse_json_text`; xoay model trong `GROQ_MODELS` (mặc định `openai/gpt-oss-120b,qwen/qwen3.8-27b,openai/gpt-oss-20b`; `GROQ_MODEL` nếu có đưa lên đầu); 429/404/5xx/timeout/JSON hỏng ⇒ model kế; hết ⇒ raise `ProviderExhausted` (exception nội bộ trong `llm.py`) để tầng chain xử lý. Đặt `last_model`. Xong khi: test monkeypatch `httpx.Client.post` (429 model 1, 200 model 2) ⇒ parse từ model 2, `last_model == "qwen/qwen3.8-27b"`; test tất cả 5xx ⇒ raise `ProviderExhausted`.
2. Chuỗi provider: khi `LLM_MODE=gemini` (giữ tên cũ cho tương thích) hoặc `LLM_MODE=chain`, `get_llm()` trả `ChainLLM([GeminiLLM nếu có GEMINI_API_KEY, GroqLLM nếu có GROQ_API_KEY])` → hết chuỗi ⇒ `MockLLM` (đúng hành vi cũ). `LLM_MODE=groq` ⇒ chỉ Groq → Mock. Cache đĩa của H01 áp cho MỌI kết quả thật (Gemini hay Groq) — key cache KHÔNG chứa tên provider. `STATS` thêm khoá `"groq"`. Xong khi: test `LLM_MODE=gemini` + cả hai key + Gemini toàn 429 + Groq 200 ⇒ kết quả từ Groq, `STATS["groq"]==1`, `STATS["mock_fallback"]==0`; test không key nào ⇒ `MockLLM`.
3. `run_eval.py --llm-stats` in thêm `groq=<n>` vào dòng `llm …` (chỉ chỗ format, không đổi logic khác). Xong khi: dòng có `groq=`.
4. `.env.example` + `docs/backend.md`: `GROQ_API_KEY`, `GROQ_MODELS`, thứ tự Gemini→Groq→Mock, giới hạn 1000/ngày & 8000 token/phút, `--sleep 1` khi eval. Xong khi: `grep -c GROQ_MODELS codebase/.env.example docs/backend.md` ≥1 mỗi file.
5. Cổng đo (từ `codebase/`): `LLM_MODE=mock python -m pytest backend -q` ⇒ exit 0, pass ≥ (số pass của R01 + 4), 0 skip, không gọi mạng. Rồi ĐÚNG MỘT lần eval thật: `LLM_MODE=groq LLM_CACHE_PATH=backend/.runtime/llm-cache-groq.json python backend/eval/run_eval.py --llm-stats --verbose --sleep 1` ⇒ ghi nguyên văn vào `evidence/wp1b/eval-groq.txt`; mục tiêu `pass≥18/21`, `citations_invalid=0`, `groq ≥ 40`. Lưu `evidence/wp1b/pytest.txt`. (Dùng cache path riêng để KHÔNG ghi đè cache Gemini của H01.)

## 4. Luật
Không đổi shape contract. Không in key. `git add` từng file, commit 1 lần tiếng Anh vd `feat(llm): add groq provider chained after gemini with model rotation`. KHÔNG push. Test cũ không giảm, 0 skip.

## 5. Tầng
🟠 toàn gói.

## 6. Report
`planning/04_2026-09-18_gemini-quota-cache/reports/R02_groq-provider.md`: dòng 1 khai vai; dòng 2–4 `Handoff:`/`Base: <Head R01>`/`Head:`; 7 mục + bảng 21 case eval Groq (case → expect → got → model). Dòng cuối `Chờ phán quyết SO`. Trả lời cuối = nội dung report.
