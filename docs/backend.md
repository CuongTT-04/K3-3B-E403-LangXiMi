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

## Env (`.env.example`)

`LLM_MODE=mock|real|gemini` · `GEMINI_API_KEY` · `GEMINI_MODEL` (mặc định
`gemini-2.5-flash`) · `HIGH_CONF_MIN` (mặc định `0.75`) · `LOW_CONF_MIN`
(mặc định `0.4`) · `DATA_DIR` (mặc định `../mock-data`, tính từ `backend/`).

## Bật Gemini thật (`LLM_MODE=gemini`)

`app/llm.py`'s `GeminiLLM` gọi REST
`https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
qua `httpx.Client`, parse JSON từ `candidates[0].content.parts[0].text`
(tự gỡ fence ```` ```json ```` nếu có). Thiếu `GEMINI_API_KEY` →
`logging.warning` rồi tự rơi về `MockLLM`, không bao giờ crash demo. Test
(`tests/test_llm_gemini.py`) monkeypatch `httpx.Client.post`, không gọi
mạng thật.

## Sự kiện (`backend/.runtime/events.jsonl`)

`POST /api/correction` và `POST /api/ta-ticket` append một dòng JSON
(`{"ts", "type", ...body}`) vào `codebase/backend/.runtime/events.jsonl`.
Thư mục `.runtime/` được `codebase/.gitignore` bỏ qua, tự tạo nếu chưa có.
Đây là số đo thô cho hành vi R6 (người học tự đính chính / cần TA).

## Cấu trúc

- `mock-data/` — `lessons.json` (32 chunk `[T01-NNN]`), `quiz-day01.json`
  (11 câu, q09/q10/q11 gài sẵn cho low_confidence/no_grounding),
  `golden-set.json` (**20 case**, có field `expect_path`: 13 `happy`,
  2 `low_confidence`, 5 `no_grounding`).
- `backend/app/` — `main.py` (endpoints + serve frontend tĩnh),
  `schemas.py`, `data.py`, `retriever.py` (chunk + confidence),
  `llm.py` (Mock/Real/Gemini), `validator.py`, `service.py` (map path).
- `backend/tests/` — pytest cho schema, API, retriever, validator, service
  (path mapping), llm gemini (mock httpx), golden-set.
- `backend/eval/run_eval.py` — chạy golden-set, in báo cáo một dòng.
- `frontend/` — HTML/JS/CSS thuần (port từ `codebase/index.html` của
  nhóm), không build step: quiz → kết quả → giải thích theo path → tóm tắt.
