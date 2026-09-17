# Changelog & Semantic Releases

Tất cả các quyết định kiến trúc và lịch sử nâng cấp phiên bản của dự án.

## [v0.2.0] - 2026-09-17: Frontend API Wiring + 4 Experience Paths
### Added
- `RemediationItem.path` (`happy`/`low_confidence`/`no_grounding`) và
  `hypotheses` (đúng 2 phần tử khi `low_confidence`) trong contract API.
- `retriever.retrieve_with_confidence()` trả thêm confidence 0..1 (1.0 khi
  khớp `source_ids`, tỷ lệ overlap từ khoá khi không khớp).
- Ngưỡng `HIGH_CONF_MIN`/`LOW_CONF_MIN` (env, mặc định 0.75/0.4) map
  confidence sang path trong `service.py`.
- Endpoints mới: `POST /api/remediate/confirm`, `POST /api/correction`,
  `POST /api/ta-ticket` (2 endpoint sau ghi `backend/.runtime/events.jsonl`).
- Provider `GeminiLLM` (`LLM_MODE=gemini`, gọi REST qua `httpx`, thiếu
  `GEMINI_API_KEY` thì tự rơi về `MockLLM`).
- Mock-data: 3 câu hỏi mới (`q09`/`q10`/`q11`) gài sẵn để demo bấm ra đủ
  `low_confidence`/`no_grounding`; `golden-set.json` thêm field
  `expect_path`, 14 case (3 no_grounding, 2 low_confidence).
- Frontend `codebase/frontend/` viết lại hoàn toàn, port CSS/markup/tên nút
  từ prototype CP2 của nhóm (`codebase/index.html`, không sửa file đó),
  render toàn bộ theo API thật: quiz → kết quả → giải thích theo path →
  tóm tắt buổi ôn tập.
- `docs/backend.md`: bảng API, schema, env, cách bật Gemini.
### Changed
- `run_eval.py` in thêm `low_conf_ok=P/Q` vào dòng báo cáo cuối.
- `codebase/README.md` cập nhật API list + cấu trúc (11 câu hỏi, 3 path).
### Notes
- 39 test pass / 0 skip (hồ sơ #01 có 20); eval
  `pass=14/14 fallback_ok=3/3 low_conf_ok=2/2 citations_invalid=0`.

## [v1.0.0] - 2026-09-17: Initial Project Scaffolding
### Added
- Khởi tạo kiến trúc dự án và thiết lập hệ thống Bộ Nhớ Não Bộ `brain4agent/` Đa Tầng thế hệ mới.
