# Changelog & Semantic Releases

Tất cả các quyết định kiến trúc và lịch sử nâng cấp phiên bản của dự án.

## [v0.2.1] - 2026-09-18: CP4 Spec Hardening — Chẩn Đoán Theo `chosen` + Golden Set 21 Case
### Added
- `codebase/mock-data/golden-set.json`: mở rộng 14 → 21 case (10 `happy`,
  3 `low_confidence`, 4 `no_grounding`, 4 `mixed` dùng field mới
  `expect_paths` map qid→path cho case nhiều câu kỳ vọng khác nhau).
- `run_eval.py`: chấm theo từng item khi case có `expect_paths` (path đúng +
  happy≥1 citation + no_grounding citations=[] + low_confidence đúng 2
  hypotheses), cờ `--verbose` in 1 dòng/case rồi dòng tổng, dòng tổng giữ
  nguyên định dạng cũ.
### Changed
- `service.remediate`/`_remediate_one`: luồn `chosen` (phương án học viên đã
  chọn) vào `LLM.generate` để chẩn đoán đúng lý do phương án ĐÃ CHỌN sai,
  thay vì chỉ dựa vào đáp án đúng.
- `validator.py`: giữ nguyên `misconception` do LLM trả về khi không rỗng
  (chỉ rơi về `misconception_hint` tĩnh khi thiếu); so `citations[].quote`
  sau khi chuẩn hoá khoảng trắng (`_norm`) để tránh LLM đổi whitespace làm
  fail oan.
- `llm.py` (`GeminiLLM.generate`): không bao giờ raise ra ngoài — lỗi mạng/
  parse retry đúng 1 lần khi `TimeoutException`/429/5xx, còn lại (vd
  `ConnectError`) rơi thẳng về `MockLLM` cùng input (cố ý, không retry vô
  hạn khi mạng đứt hẳn); đáp án câu củng cố của `MockLLM` chọn theo
  `chunk_id` thay vì luôn cố định "A"; `confirm_hypothesis` gắn tiền tố
  explanation khác nhau theo nhánh `h1`/`h2`.
- `spec.md`: điền §1–§3, §5, §7–§9 từ nguồn trong repo (canvas.md,
  README.md, docs/backend.md, mock-data, kết quả eval); giữ nguyên §4/§4b/§6
  đã duyệt; còn 5 dòng `⏳` (quote nguyên văn ngoài repo ở §1, kết quả
  Gemini thật chờ `GEMINI_API_KEY`).
### Notes
- Số đo cuối (mock, hồ sơ #03): `pytest backend -q` → 49 passed / 0 fail /
  0 skip (hồ sơ #02 có 39); `run_eval.py` →
  `eval pass=21/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0`;
  `run_eval.py --verbose` → 22 dòng (21 case + 1 tổng).
- Thẩm định cô lập (WP4, `planning/03_2026-09-18_cp4-spec-hardening/`) thử
  5 cách phá, chứng minh bộ đo mới ĐỎ đúng lúc trên dữ liệu golden-set cố
  tình hỏng (`pass=16/21` qua `DATA_DIR` trỏ thư mục tạm, không đụng file
  repo) — phán quyết ✅ DUYỆT cho WP1+WP2; WP3 (spec.md) và WP5 (não) cũng
  ✅ DUYỆT.
- Sự cố vận hành (không phải bug sản phẩm): 3 worker song song dùng chung
  một `.git/index`, không có worktree riêng ⇒ vài lần `git commit`/`amend`
  của worker này cuốn theo file đang stage của worker khác; mọi lần đều tự
  phát hiện qua `git show --stat HEAD` và tự sửa bằng `git reset --soft
  HEAD^`, không mất dữ liệu. Ghi vào `-known-gotchas.md` để phòng lặp lại.

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
> **Ghi chú:** đây là mốc khung não (`brain4agent/` scaffolding), KHÔNG phải
> version sản phẩm — dòng version sản phẩm bắt đầu và tiếp tục từ `v0.2.0`
> ở trên; số `v1.0.0` ở đây không nằm trên cùng trục SemVer với `current_version`
> trong `state.json`. Xếp cuối file (mốc xa nhất theo thời gian) dù số lớn hơn.
### Added
- Khởi tạo kiến trúc dự án và thiết lập hệ thống Bộ Nhớ Não Bộ `brain4agent/` Đa Tầng thế hệ mới.
