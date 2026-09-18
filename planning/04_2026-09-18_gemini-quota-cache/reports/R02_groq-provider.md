# R02 — Groq làm tầng dự phòng thứ hai (Gemini → Groq → Mock)

Vai: worker (vai-thi-cong) · loại: THI CÔNG · họ/model: Claude Sonnet 5 · Bước 0: exit 0 · hiểu việc: WP1b = thêm `GroqLLM` (API kiểu OpenAI, xoay `GROQ_MODELS`, KHÔNG retry cùng model kể cả timeout, hết danh sách raise `ProviderExhausted` nội bộ thay vì tự rơi Mock) + `ChainLLM` (Gemini→Groq→Mock, mỗi provider rotate riêng qua `_rotate_or_raise`, chỉ rơi Mock khi CẢ chuỗi cạn) + `STATS["groq"]`; cache đĩa H01 dùng chung cho cả 2 provider (khoá không chứa tên provider); `.env.example`/`docs/backend.md` mô tả `GROQ_API_KEY/GROQ_MODEL/GROQ_MODELS`; 1 lần eval thật `LLM_MODE=groq` với cache path riêng (`llm-cache-groq.json`, không đụng cache Gemini của H01); KHÔNG đụng `schemas.py`/`service.py`/`validator.py`/`mock-data`/`frontend`/`.env` (không in key, che `gsk_***`); không hồi quy H01.

Handoff: `planning/04_2026-09-18_gemini-quota-cache/handoffs/H02_groq-provider.md`
Base: c0c5b20
Head: (SHA của commit chính — điền ở mục 3 sau khi `git commit` chạy xong, theo đúng tiền lệ R01/R02_golden-set-20)

## 1. Lệnh + exit code

```
node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check   → exit 0
LLM_MODE=mock python -m pytest backend -q                                                       → exit 0
LLM_MODE=mock python backend/eval/run_eval.py                                                    → exit 0 (pass=21/21, không đổi so R01 -- không chạm service/validator/run_eval)
LLM_MODE=groq LLM_CACHE_PATH=backend/.runtime/llm-cache-groq.json python backend/eval/run_eval.py --llm-stats --verbose --sleep 1   → exit 0
```

`grep -c GROQ_MODELS codebase/.env.example docs/backend.md` → 2 và 2 (≥1 mỗi file).

## 2. Test tổng/pass/fail/skip

`LLM_MODE=mock python -m pytest backend -q`: **75 tổng / 75 pass / 0 fail / 0 skip** (yêu cầu ≥ 63+4=67; R01 có 63). Không test nào gọi mạng thật: `test_llm_gemini.py` và `test_llm_groq.py` đều monkeypatch `httpx.Client.post` và đặt `LLM_CACHE_PATH` vào `tmp_path` qua fixture `autouse`; fixture của cả 2 file còn tự `delenv` `GEMINI_MODEL`/`GROQ_MODEL`/`GROQ_API_KEY` để tránh giá trị thật trong `.env` (được `python-dotenv` nạp vào `os.environ` một lần khi import `app.data`, vì shell chỉ set `LLM_MODE=mock` chứ không xoá các key) rò vào một test không chủ đích test chuỗi 2 provider. File: `planning/04_2026-09-18_gemini-quota-cache/evidence/wp1b/pytest.txt`.

`LLM_MODE=mock python backend/eval/run_eval.py` → `eval pass=21/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0` (không đổi vì không chạm `run_eval.py`/`service.py`/`validator.py`).

## 3. `git diff --stat` + SHA

```
 codebase/.env.example                              |  63 +++--
 codebase/backend/app/llm.py                        | 278 +++++++++++++++++---
 codebase/backend/tests/test_llm_gemini.py          |  27 +-
 codebase/backend/tests/test_llm_groq.py            | 285 +++++++++++++++++++++
 docs/backend.md                                    |  69 ++++-
 .../evidence/wp1b/eval-groq.txt                    |  33 +++
 .../evidence/wp1b/pytest.txt                       |  10 +
 7 files changed, 696 insertions(+), 69 deletions(-)
```

Cộng report này. Commit chính 1 lần (`feat(llm): add groq provider chained after gemini with model rotation`), SHA điền ở dòng "Head" phía trên sau khi chạy `git commit` (không thể biết trước SHA của một commit đang chứa chính file này — theo đúng tiền lệ `R02_golden-set-20.md`/`R01_gemini-rotation-cache.md` trong repo, sẽ có commit thứ 2 chỉ sửa dòng Head nếu cần).

## 4. Bảng phân công

| Gói | Tầng | Họ/model |
|---|---|---|
| WP1b (5 việc trong H02) | 🟠 | Claude Sonnet 5 |

Không có sub-agent nào được giao việc.

## 5. Việc KHÔNG làm + lý do

- **Không sửa `run_eval.py` để in thêm `groq=<n>`** (yêu cầu ở việc 3 của H02) và **không sửa `test_golden_set_eval.py`**: `run_eval.py` nằm trong danh sách CẤM chạm §2 của H02, và `test_golden_set_eval.py` (chứa `test_format_llm_stats_line_shape` khớp CHÍNH XÁC chuỗi `"llm gemini=3 cache=2 mock_fallback=1 model=gemini-3.5-flash"`) không nằm trong danh sách ĐƯỢC sửa của H02. Thêm `groq=` vào `format_llm_stats_line` chắc chắn phá test đó (đổi định dạng chuỗi), mà tôi không được phép sửa file test đó để chữa. Đây là mâu thuẫn nội tại giữa mục 3 ("in thêm groq=") và §2 (CẤM `run_eval.py`) + luật "test cũ không giảm" — tôi ưu tiên KHÔNG phá test cũ và KHÔNG chạm file ngoài phạm vi, thay vì tự ý nới quyền. `STATS["groq"]` vẫn tăng đúng trong `llm.py` (đã có test riêng xác nhận); chỉ dòng in của CLI `run_eval.py --llm-stats` là chưa lộ số groq. Số liệu Groq thật của gate 5(c) được lấy bằng cách gọi `run_eval.main()` từ một lệnh `python -c` bọc ngoài (không sửa file nào trong repo) rồi in thêm `llm.STATS` ngay sau — xem mục "Bảng 21 case" và file evidence (dòng cuối `SUPPLEMENTARY_STATS_NOT_FROM_RUN_EVAL_PY` được đánh dấu rõ là KHÔNG phải output gốc của `run_eval.py`).
- **Không đổi `GeminiLLM.generate()`'s standalone contract**: vẫn tự rơi về `MockLLM` khi dùng đứng một mình (không qua `ChainLLM`), giữ đúng test H01 `test_gemini_llm_all_models_429_falls_back_to_mock_shape_without_raising` — để làm được điều này mà vẫn cho `ChainLLM` lấy được tín hiệu "hết model" tôi tách logic thành `_rotate_or_raise` (raise `ProviderExhausted`) dùng chung bởi cả `generate()` (bắt exception, tự rơi Mock) và `ChainLLM` (bắt exception, thử provider kế).
- **Không đổi `.env` thật, không in key** — mọi chỗ log có thể lộ key đã kiểm tra (Groq dùng header `Authorization`, không lộ trong URL của thông báo lỗi httpx, nên evidence không có `gsk_` nào; vẫn chạy `sed` che phòng hờ, xác nhận 0 occurrence).
- **Không tự tuyên bố ĐẠT/KHÔNG ĐẠT cổng đo.**

## 6. Câu hỏi cần người (SO)

1. **Mục 3 của H02 (in `groq=` trong `run_eval.py --llm-stats`) CHƯA làm được** vì mâu thuẫn phạm vi (xem mục 5). SO có muốn mở khoá `run_eval.py` + `test_golden_set_eval.py` cho một patch nhỏ sau (đổi định dạng dòng `llm …` thành có `groq=`, sửa `test_format_llm_stats_line_shape` khớp theo), hay giữ nguyên và chấp nhận số Groq lấy qua `llm.STATS` trực tiếp (đã ghi trong report/evidence) là đủ cho CP3?
2. Eval thật Groq ra kết quả rất sạch: `pass=21/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0`, `groq=10 cache=21 mock_fallback=0` (tốt hơn mục tiêu `pass≥18/21`). Riêng mục tiêu `groq ≥ 40` KHÔNG đạt được về mặt cấu trúc: golden-set 21 case chỉ có tối đa ~31 item từng gọi `get_llm()` (đúng như R01 cũng chỉ đạt `gemini+cache=31<40` với cùng lý do) — 40 có vẻ là con số không khớp với quy mô golden-set hiện tại (14 case gốc mở rộng lên 21, tổng 38 item, ~31 item có gọi LLM). SO xác nhận cách đọc này và chấp nhận `groq(10)+cache(21)=31`, hay có tiêu chí khác tôi chưa nắm?
3. `backend/.runtime/llm-cache.json` (cache Gemini của H01) đã tăng từ 10 lên 13 entry kể từ R01 — rất có thể do server demo (`uvicorn`, đang chạy theo lưu ý của SO) đã phục vụ vài request `LLM_MODE=gemini` thật qua UI trong lúc tôi làm việc. Tôi KHÔNG động vào file này (chỉ đọc để đếm), chỉ ghi nhận ở đây để SO biết đây không phải lỗi/can thiệp từ tôi.

## 7. Tiếp theo

- SO đọc report + `evidence/wp1b/{pytest.txt,eval-groq.txt}`, quyết định câu hỏi 1 (có mở khoá `run_eval.py`/`test_golden_set_eval.py` cho patch nhỏ hiển thị `groq=` hay không).
- Nếu mở khoá: một handoff nhỏ tiếp theo (hoặc tôi làm tiếp nếu được giao) sẽ thêm `groq={stats['groq']}` vào `format_llm_stats_line` và cập nhật đúng 1 test (`test_format_llm_stats_line_shape`) khớp định dạng mới, không đổi logic nào khác.
- Demo (WP2, đang chạy) có thể tiếp tục dùng cache Gemini hiện có; cache Groq (`backend/.runtime/llm-cache-groq.json`, 10 entry) sẵn sàng nếu cần minh hoạ tầng dự phòng.
- WP3 (điền số liệu vào `spec.md` §7 + đồng bộ não) chờ SO chốt cả R01 (đã duyệt) và R02 (report này).

## Bảng 21 case (eval thật, `LLM_MODE=groq`, `LLM_CACHE_PATH=backend/.runtime/llm-cache-groq.json`)

`model` cụ thể theo TỪNG case không tách được từ log (chỉ có 1 dòng thống kê tổng + `LAST_MODEL` cuối cùng); log cho thấy 4 lần 429 đầu (`openai/gpt-oss-120b` ×3, `qwen/qwen3.8-27b` ×1) trước khi rotation ổn định, cuối cùng model thật gần nhất là `openai/gpt-oss-20b`. `llm*` = case có ít nhất 1 item gọi `get_llm()` (path `happy`/`low_confidence`, hoặc `no_grounding` do validator từ chối); `no_llm` = toàn `no_grounding` do retriever không tìm chunk/confidence dưới ngưỡng.

| case | expect | got | model | passed |
|---|---|---|---|---|
| case-01 | happy | happy | groq/cache* | True |
| case-02 | happy | happy | groq/cache* | True |
| case-03 | happy | happy | groq/cache* | True |
| case-04 | happy | happy | groq/cache* | True |
| case-05 | happy | happy | groq/cache* | True |
| case-06 | happy | happy | groq/cache* | True |
| case-07 | happy | happy | groq/cache* | True |
| case-08 | happy | happy | groq/cache* | True |
| case-09 | happy | happy,happy | groq/cache* | True |
| case-10 | no_grounding | no_grounding | no_llm (khả năng cao) | True |
| case-11 | no_grounding | no_grounding | no_llm (khả năng cao) | True |
| case-12 | low_confidence | low_confidence | groq/cache* | True |
| case-13 | low_confidence | low_confidence | groq/cache* | True |
| case-14 | no_grounding | no_grounding | no_llm (khả năng cao) | True |
| case-15 | happy | happy,happy | groq/cache* | True |
| case-16 | low_confidence | low_confidence,low_confidence | groq/cache* | True |
| case-17 | no_grounding | no_grounding | no_llm (khả năng cao) | True |
| case-18 | mixed | happy,no_grounding | groq/cache* | True |
| case-19 | mixed | low_confidence,happy | groq/cache* | True |
| case-20 | mixed | happy,no_grounding,low_confidence | groq/cache* | True |
| case-21 | mixed | happy×8,low_confidence,no_grounding,low_confidence | groq/cache* | True |

Tổng: `pass=21/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0`; `llm.STATS = {"gemini": 0, "groq": 10, "cache": 21, "mock_fallback": 0}`; `LAST_MODEL = "openai/gpt-oss-20b"`; `backend/.runtime/llm-cache-groq.json` có 10 entry (tách biệt hoàn toàn khỏi `llm-cache.json` của Gemini).

Chờ phán quyết SO.
