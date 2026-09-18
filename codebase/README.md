# Quiz Remediation MVP (mock data)

Hoc vien lam quiz trac nghiem, nop bai, va nhan man ket qua co AI gom cac cau
sai, chan doan concept hieu nham, trich dan doan transcript `[T01-NNN]`, va
sinh cau hoi trac nghiem cung co. Toan bo du lieu la MOCK tu sinh, khong dung
du lieu khoa hoc thuc te nao. Moi cau sai roi vao 1 trong 3 duong di
(`happy` / `low_confidence` / `no_grounding`) quyet dinh boi do tin cay
retrieval -- xem `docs/backend.md`. LLM mac dinh chay o `LLM_MODE=mock`
(khong goi mang); `LLM_MODE=gemini` goi Gemini REST thuc khi co
`GEMINI_API_KEY`, thieu key thi tu roi ve mock.

## Chay thu

```bash
cd codebase
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

Mo trinh duyet: http://127.0.0.1:8000

Sao chep `.env.example` thanh `.env` neu muon doi `LLM_MODE`,
`GEMINI_API_KEY`, `HIGH_CONF_MIN`/`LOW_CONF_MIN` hoac `DATA_DIR` (duong dan
mock-data, tinh tuong doi tu thu muc `backend/`).

## Test va eval

```bash
python -m pytest backend -q
python backend/eval/run_eval.py
```

`run_eval.py` chay toan bo `golden-set.json` qua pipeline retriever + LLM
(mock) + validator, in ra dung mot dong cuoi dang:
`eval pass=N/M fallback_ok=K/L low_conf_ok=P/Q citations_invalid=0`

## Cau truc

- `mock-data/` — `lessons.json` (transcript gia `[T01-NNN]`), `quiz-day01.json`
  (11 cau trac nghiem, 3 cau gai san cho low_confidence/no_grounding),
  `golden-set.json` (bo case danh gia, co field `expect_path`).
- `backend/app/` — FastAPI: `main.py` (endpoints + serve frontend tinh),
  `schemas.py` (Pydantic contract), `data.py` (load mock-data), `retriever.py`
  (truy xuat chunk + confidence theo source_ids roi keyword overlap),
  `llm.py` (MockLLM / GeminiLLM / RealLLM), `validator.py` (kiem tra
  citation/reinforcement, fallback neu sai), `service.py` (map confidence
  sang path, ghep pipeline remediation cho cac cau sai).
- `backend/tests/` — pytest cho schema du lieu, API, retriever, validator,
  service (path mapping), llm gemini (mock httpx, khong goi mang), golden-set.
- `backend/eval/run_eval.py` — chay golden-set, in bao cao mot dong.
- `frontend/` — HTML/JS/CSS thuan (port tu `codebase/index.html` cua nhom),
  khong build step: man quiz -> ket qua -> giai thich theo path -> tom tat.

## API

Chi tiet schema/env/cach bat Gemini: `docs/backend.md`.

- `GET /health`
- `GET /api/quiz/day01`
- `POST /api/quiz/day01/submit` — body `{"answers": {"q01": "A", ...}}`
- `GET /api/transcript/{chunk_id}`
- `POST /api/remediate` — body `{"quiz_id": "day01", "wrong_question_ids": ["q01"]}`
- `POST /api/remediate/confirm` — body `{"quiz_id", "question_id", "hypothesis_id"}`
- `POST /api/correction` — body `{"quiz_id", "question_id", "action": "misclick"|"dismiss"}`
- `POST /api/ta-ticket` — body `{"quiz_id", "question_id", "note"}`
