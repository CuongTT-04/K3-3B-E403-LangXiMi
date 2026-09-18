# Master Data Architecture & Flow

Tài liệu thiết kế về cấu trúc dữ liệu, cơ chế lưu trữ bền vững (Persistence Layer) và luồng luân chuyển dữ liệu đa tầng.

## 1. Các Tầng Lưu Trữ (Data Persistence Stores)
- **`codebase/mock-data/*.json`** (nguồn sự thật cho nội dung học tập, đọc
  qua `app/data.py`, đường dẫn tính từ env `DATA_DIR` mặc định `../mock-data`
  tương đối `backend/`):
  - `lessons.json` — 32 chunk transcript giả `[T01-NNN]` (`id, lesson,
    concept, text`).
  - `quiz-day01.json` — 11 câu trắc nghiệm (`id, stem, options, answer,
    concept, source_ids, misconception_hint`); q09/q10/q11 dùng
    `source_ids` giả (`T99-…`) hoặc concept không tồn tại để gài sẵn đường
    đi `low_confidence`/`no_grounding` cho demo.
  - `golden-set.json` — 21 case đánh giá hồi quy (10 `happy`, 3
    `low_confidence`, 4 `no_grounding`, 4 `mixed`): `expect_path`
    (case đơn) hoặc `expect_paths` (map qid→path, case nhiều câu kỳ vọng
    khác nhau), `expected_concepts`, `expected_source_ids_any`,
    `expect_fallback`.
- **`codebase/backend/.runtime/events.jsonl`** — append-only, tạo tự động
  khi cần, gitignored (`codebase/.gitignore`). Mỗi dòng một JSON
  `{"ts", "type": "correction"|"ta_ticket", ...body request}`, ghi bởi
  `POST /api/correction` và `POST /api/ta-ticket` trong `main.py`.
- **Không có DB** — toàn bộ state của một lượt làm bài sống trong request/
  response (stateless) + state phía trình duyệt (`frontend/app.js`).

## 2. Schema & Data Flow
```
mock-data/*.json --data.py--> main.py (FastAPI)
  GET /api/quiz/{id}            -> QuizOut (không lộ answer/concept)
  POST /api/quiz/{id}/submit    -> chấm điểm -> service.remediate()
                                    cho mỗi câu sai (luồn kèm chosen = phương
                                    án học viên đã chọn):
                                      retriever.retrieve_with_confidence()
                                        -> (chunks, confidence)
                                      confidence < LOW_CONF_MIN hoặc
                                        chunks=[] -> path=no_grounding
                                        (validator.fallback_item)
                                      else -> llm.generate(..., chosen=chosen)
                                        -> validator.validate() (so
                                        citations[].quote NGUYÊN VĂN chunk
                                        sau khi chuẩn hoá khoảng trắng)
                                        validate() reject -> path=no_grounding
                                        confidence >= HIGH_CONF_MIN -> path=happy
                                        else -> path=low_confidence (+2 hypotheses,
                                          reinforcement=[] cho tới khi confirm)
                                    -> SubmitOut { score, results, remediation }
  POST /api/remediate/confirm   -> service.confirm_hypothesis() -> item path=happy
  POST /api/correction          -> _append_event() -> events.jsonl
  POST /api/ta-ticket           -> _append_event() -> events.jsonl
  GET /api/transcript/{id}      -> chunk gốc (mở khi bấm badge [T01-NNN])
```
Validator (`app/validator.py`) là chốt cứng cuối trên MỌI nhánh: citation
phải là chuỗi con nguyên văn của chunk, mọi câu củng cố phải trỏ về citation
đã duyệt — sai một trong hai thì hạ về fallback (`path=no_grounding`,
`citations=[]`), không bao giờ trả trích dẫn bịa.
