# Backend — Quiz Remediation MVP

FastAPI service tại `codebase/backend/app/`, dữ liệu mock tại
`codebase/mock-data/`, frontend tĩnh (vanilla JS) tại `codebase/frontend/`
được `main.py` mount ở `/`.

## Chạy thử

```bash
cd codebase
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

Mở `http://127.0.0.1:8000`. Sao chép `.env.example` thành `.env` nếu muốn
đổi `LLM_MODE`, `GEMINI_API_KEY`, `HIGH_CONF_MIN`/`LOW_CONF_MIN` hoặc
`DATA_DIR`.

## Test và eval

```bash
python -m pytest backend -q
python backend/eval/run_eval.py
```

`run_eval.py` in đúng một dòng cuối:
`eval pass=N/M fallback_ok=K/L low_conf_ok=P/Q citations_invalid=0`

## 4 đường đi (item.path) — quyết định bởi retriever confidence

`retriever.retrieve_with_confidence()` trả `(chunks, confidence)`:
- khớp `source_ids` có thật trong `lessons.json` → `confidence = 1.0`.
- không khớp `source_ids` → tính theo tỷ lệ overlap từ khoá giữa `concept`
  của câu hỏi và (concept + text) của chunk tốt nhất, `confidence ∈ [0, 1)`.
- không tìm được chunk nào → `confidence = 0.0`, `chunks = []`.

`service._remediate_one()` map `confidence` sang `path` (ngưỡng đọc từ env,
xem `.env.example`):

| confidence | path | citations | hypotheses | reinforcement |
|---|---|---|---|---|
| `>= HIGH_CONF_MIN` (mặc định 0.75) | `happy` | có | `[]` | có ngay |
| `LOW_CONF_MIN <= c < HIGH_CONF_MIN` (mặc định 0.4–0.75) | `low_confidence` | có | đúng 2 phần tử | `[]` — chờ `POST /api/remediate/confirm` |
| `< LOW_CONF_MIN`, `chunks == []`, hoặc validator từ chối citation | `no_grounding` | `[]` | `[]` | `[]` |

`validator.py` vẫn là chốt cứng cuối: bất kỳ citation bịa hoặc câu củng cố
không trỏ về citation đã duyệt → hạ về `no_grounding` (an toàn hơn là bịa).
So khớp `quote` bỏ qua dấu tiếng Việt và hoa/thường (`validator._fold`:
chuẩn hoá khoảng trắng → NFD → bỏ ký tự category `Mn` → `đ/Đ`→`d` → lower)
vì `lessons.json` không có dấu nhưng LLM hay thêm dấu vào trích dẫn; đổi hẳn
một TỪ vẫn bị từ chối, chỉ dấu/hoa-thường/khoảng trắng được bỏ qua.
`eval/run_eval.py` dùng lại đúng logic này (`validator.quote_matches`) khi
tự đếm `citations_invalid`, để không báo sai một trích dẫn hợp lệ (theo
validator) là "invalid".

Mock-data cố ý gài 3 câu hỏi để demo bấm ra đủ 3 đường đi:
- `q09`, `q11` (`quiz-day01.json`) dùng `source_ids` giả (`T99-…`, không có
  trong `lessons.json`) để buộc retriever rơi vào nhánh overlap từ khoá,
  cho ra `confidence` xác định ~0.667 → `low_confidence`.
- `q10` dùng `concept` hoàn toàn không có trong `lessons.json`
  (`kubernetes_deployment_pipeline`) → `chunks = []` → `no_grounding`.

Đường đi thứ 4 (đính chính/bỏ qua) không phải một `path` — nó là hành động
người học thực hiện TRÊN một item (bất kỳ path nào) qua `POST /api/correction`.

## API

| Method | Path | Body | Trả về |
|---|---|---|---|
| GET | `/health` | — | `{"status": "ok"}` |
| GET | `/api/quiz/{quiz_id}` | — | `QuizOut` (không lộ đáp án/concept) |
| POST | `/api/quiz/{quiz_id}/submit` | `{"answers": {"q01": "A", ...}}` | `SubmitOut` (score, results, remediation) |
| GET | `/api/transcript/{chunk_id}` | — | chunk gốc `{id, lesson, concept, text}` |
| POST | `/api/remediate` | `{"quiz_id", "wrong_question_ids": [...]}` | `RemediationOut` (dùng lại pipeline cho câu tuỳ ý) |
| POST | `/api/remediate/confirm` | `{"quiz_id", "question_id", "hypothesis_id"}` | `RemediationItem` đầy đủ, `path="happy"` |
| POST | `/api/correction` | `{"quiz_id", "question_id", "action": "misclick"\|"dismiss"}` | `{"status": "ok"}`, ghi `events.jsonl` |
| POST | `/api/ta-ticket` | `{"quiz_id", "question_id", "note"}` | `{"status": "ok"}`, ghi `events.jsonl` |

## Schema (`app/schemas.py`)

`RemediationItem` = `question_id, concept, misconception, explanation,
citations[{id, quote}], reinforcement[{stem, options, answer, source_id}],
confidence, fallback, fallback_note, path, hypotheses[{id, label}]`.
`hypotheses` luôn đúng 2 phần tử khi `path="low_confidence"`, `[]` mọi
trường hợp khác. Mọi field cũ của hồ sơ #01 giữ nguyên tên/kiểu.

`misconception` nay được chẩn đoán dựa trên phương án học viên **đã chọn**
(`chosen`, luồn từ `results` → `service._remediate_one` →
`LLM.generate(question, chunks, distractor_pool, chosen=...)`): LLM (Mock
hoặc Gemini) nhận cả `stem`/`options`/đáp án đúng/`chosen` và trả về field
`"misconception"` nói rõ vì sao phương án đã chọn sai; `validator.py` giữ
nguyên giá trị này nếu là chuỗi không rỗng, chỉ rơi về `misconception_hint`
tĩnh khi LLM không trả field đó (ví dụ item fallback).

## Env (`.env.example`)

`LLM_MODE=mock|real|gemini|chain|groq` (`gemini`/`chain` = chuỗi Gemini→Groq→
Mock đầy đủ, xem bên dưới; `groq` = chỉ Groq→Mock, bỏ qua Gemini) ·
`GEMINI_API_KEY` · `GEMINI_MODEL` (legacy, optional: khi đặt thì được đưa
lên đầu danh sách xoay vòng) · `GEMINI_MODELS` (danh sách phẩy, xem bên
dưới) · `GROQ_API_KEY` · `GROQ_MODEL` (legacy, như `GEMINI_MODEL`) ·
`GROQ_MODELS` (danh sách phẩy) · `LLM_CACHE` (`off` để tắt cache đĩa) ·
`LLM_CACHE_PATH` (đè đường dẫn file cache, test dùng `tmp_path`) ·
`HIGH_CONF_MIN` (mặc định `0.75`) · `LOW_CONF_MIN` (mặc định `0.4`) ·
`DATA_DIR` (mặc định `../mock-data`, tính từ `backend/`).

## Bật Gemini thật (`LLM_MODE=gemini`)

`app/llm.py`'s `GeminiLLM` gọi REST
`https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
qua `httpx.Client`, parse JSON từ phần tử của `candidates[0].content.parts`
có key `text` (Gemini 3.x xen `thoughtSignature` trước phần trả lời, nên
không thể lấy cứng `parts[0]`), tự gỡ fence ```` ```json ```` nếu có. Thiếu
`GEMINI_API_KEY` → `logging.warning` rồi tự rơi về `MockLLM`, không bao giờ
crash demo.

### Xoay model khi hết quota (20 request/ngày/model)

Gói Gemini miễn phí giới hạn **20 request/NGÀY cho MỖI model**. `GeminiLLM`
nhận một **danh sách** model (`GEMINI_MODELS`, mặc định
`gemini-3.5-flash,gemini-3.6-flash,gemini-3.5-flash-lite,gemini-3.7-flash,
gemini-3.8-flash,gemini-3.1-flash-lite`; nếu đặt `GEMINI_MODEL` thì model đó
được đưa lên đầu danh sách, bỏ trùng) và thử từng model theo thứ tự trong
`generate()`:

- 429 / 404 / 503 / lỗi HTTP khác / JSON trả về không parse được → chuyển
  sang model kế tiếp NGAY, không retry lại cùng model.
- `httpx.TimeoutException` → retry đúng 1 lần trên CÙNG model, nếu vẫn lỗi
  mới chuyển model kế tiếp.
- Hết cả danh sách vẫn lỗi → rơi về `MockLLM().generate(...)` với cùng input
  (kể cả `chosen`); demo không bao giờ trả 500 hay raise.
- Model gọi thành công được đưa lên đầu danh sách của **instance** đó, nên
  lần `generate()` kế tiếp trên cùng instance ưu tiên thử lại model vừa
  thành công trước.

`logger.warning` được ghi mỗi lần chuyển model hoặc rơi về mock. Test
(`tests/test_llm_gemini.py`) monkeypatch `httpx.Client.post`, không gọi
mạng thật.

### Cache LLM trên đĩa

Mỗi câu trả lời THẬT (không phải mock fallback) từ Gemini được cache vào
`backend/.runtime/llm-cache.json` (dict; thư mục đã gitignored), khoá là
sha1 của `{"v": PROMPT_VERSION, "qid": question["id"], "chosen": chosen,
"chunks": sorted(chunk ids)}` (`PROMPT_VERSION` là hằng số trong `llm.py`,
tăng khi đổi nội dung prompt để tránh trả lời cũ theo prompt cũ). Cache hit
→ không gọi mạng, trả bản sao dict đã lưu. Đặt `LLM_CACHE=off` để tắt hẳn
cache (mọi lần gọi đều ra mạng); `LLM_CACHE_PATH` đè đường dẫn file (test
luôn trỏ vào `tmp_path`). Kết quả rơi về `MockLLM` KHÔNG bao giờ được cache.

Trước demo, "warm" cache bằng cách chạy 1 lần với dữ liệu thật:

```bash
cd codebase
LLM_MODE=gemini python backend/eval/run_eval.py --llm-stats --verbose --sleep 2
```

Lần chạy tiếp theo (kể cả lúc demo, kể cả mất mạng) sẽ đọc từ cache thay vì
gọi lại Gemini, miễn `backend/.runtime/llm-cache.json` không bị xoá.

### Groq làm tầng dự phòng thứ hai (sau Gemini, trước Mock)

Spec #4 chốt Gemini là AI lõi; khi quota Gemini cạn (hoặc thiếu key),
`GroqLLM` (API kiểu OpenAI: `POST
https://api.groq.com/openai/v1/chat/completions`, header `Authorization:
Bearer <key>`, `choices[0].message.content` là chuỗi JSON) là tầng dự
phòng thứ hai trước khi rơi về `MockLLM`. Giới hạn đo được: **1000
request/NGÀY** (không tính theo từng model như Gemini) và **8000
token/PHÚT**; model `llama-3.3-70b-versatile` KHÔNG dùng được trên tài
khoản này. `GroqLLM` xoay `GROQ_MODELS` (mặc định
`openai/gpt-oss-120b,qwen/qwen3.8-27b,openai/gpt-oss-20b`; `GROQ_MODEL` nếu
đặt được đưa lên đầu) giống hệt cơ chế Gemini, NGOẠI TRỪ: mọi lỗi (kể cả
timeout) chuyển model kế NGAY, không retry lại cùng model một lần nào.

`get_llm()` build chuỗi provider theo `LLM_MODE`:

| `LLM_MODE` | Chuỗi provider |
|---|---|
| `gemini` hoặc `chain` | `ChainLLM([GeminiLLM nếu có GEMINI_API_KEY, GroqLLM nếu có GROQ_API_KEY])` → hết chuỗi ⇒ `MockLLM` (thiếu cả 2 key ⇒ thẳng `MockLLM`) |
| `groq` | `ChainLLM([GroqLLM])` nếu có `GROQ_API_KEY` (bỏ qua Gemini dù có key), ngược lại `MockLLM` |

`ChainLLM.generate()` thử từng provider theo thứ tự qua `_rotate_or_raise`
(rotate hết model riêng của provider đó rồi raise `ProviderExhausted` nội
bộ nếu vẫn lỗi) và chỉ rơi về `MockLLM` khi CẢ chuỗi cạn; không bao giờ
raise ra ngoài. `GeminiLLM.generate()` dùng standalone (không qua chain,
như trước H02) vẫn tự rơi về `MockLLM` một mình như cũ (không hồi quy H01);
`GroqLLM.generate()` thì raise `ProviderExhausted` thẳng — không có hợp
đồng standalone cũ nào cần giữ.

Cache đĩa của H01 (mục trên) áp dụng cho MỌI kết quả thật, không phân biệt
Gemini hay Groq — khoá cache không chứa tên provider, nên một câu trả lời
Groq cũng làm cache-hit cho một lần gọi Gemini-trước sau đó với cùng input.

### Đếm provider (`llm.STATS`) và `run_eval.py --llm-stats`

`app/llm.py` giữ biến module-level `STATS = {"gemini": 0, "groq": 0,
"cache": 0, "mock_fallback": 0}` (tăng đúng nhánh trong
`GeminiLLM`/`GroqLLM`/`ChainLLM`) và `LAST_MODEL` (model thật gần nhất gọi
thành công, Gemini hoặc Groq); `llm.reset_stats()` đặt lại tất cả về
0/`None`. KHÔNG field nào trong số này lộ ra schema `RemediationItem`.

`eval/run_eval.py --llm-stats` gọi `reset_stats()` trước khi chạy golden-set
rồi in thêm một dòng NGAY TRƯỚC dòng tổng:

```
llm gemini=<n> cache=<n> mock_fallback=<n> model=<last_model hoặc "-">
eval pass=N/M fallback_ok=K/L low_conf_ok=P/Q citations_invalid=0
```

**Lưu ý (H02):** dòng `llm …` ở trên CHƯA có `groq=<n>` — `run_eval.py` nằm
trong danh sách CẤM chạm của handoff H02 (`test_golden_set_eval.py`, nơi
test khớp đúng định dạng dòng này, cũng vậy), nên số liệu Groq thật của lần
eval `LLM_MODE=groq` được lấy từ `llm.STATS["groq"]` trực tiếp (xem
`planning/04_2026-09-18_gemini-quota-cache/reports/R02_groq-provider.md`),
không phải từ dòng in của CLI. Xem "Câu hỏi cần người" trong report đó để
SO quyết định có mở khoá 2 file trên cho một patch nhỏ sau này hay không.

`--sleep <giây>` (mặc định `0`) nghỉ giữa các case của golden-set để tránh
vượt giới hạn request/phút khi chạy với `LLM_MODE=gemini` hoặc
`LLM_MODE=groq` (khuyến nghị `--sleep 1` cho Groq, `--sleep 2` cho Gemini).

## Sự kiện (`backend/.runtime/events.jsonl`)

`POST /api/correction` và `POST /api/ta-ticket` append một dòng JSON
(`{"ts", "type", ...body}`) vào `codebase/backend/.runtime/events.jsonl`.
Thư mục `.runtime/` được `codebase/.gitignore` bỏ qua, tự tạo nếu chưa có.
Đây là số đo thô cho hành vi R6 (người học tự đính chính / cần TA).

## Cấu trúc

- `mock-data/` — `lessons.json` (32 chunk `[T01-NNN]`), `quiz-day01.json`
  (11 câu, q09/q10/q11 gài sẵn cho low_confidence/no_grounding),
  `golden-set.json` (14 case, có field `expect_path`).
- `backend/app/` — `main.py` (endpoints + serve frontend tĩnh),
  `schemas.py`, `data.py`, `retriever.py` (chunk + confidence),
  `llm.py` (Mock/Real/Gemini/Groq/Chain), `validator.py`, `service.py`
  (map path).
- `backend/tests/` — pytest cho schema, API, retriever, validator, service
  (path mapping), llm gemini (`test_llm_gemini.py`, mock httpx), llm groq +
  chain (`test_llm_groq.py`, mock httpx), golden-set.
- `backend/eval/run_eval.py` — chạy golden-set, in báo cáo một dòng.
- `frontend/` — HTML/JS/CSS thuần (port từ `codebase/index.html` của
  nhóm), không build step: quiz → kết quả → giải thích theo path → tóm tắt.
