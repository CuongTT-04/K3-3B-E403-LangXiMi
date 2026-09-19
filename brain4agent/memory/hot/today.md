# 📅 Nhật Ký Làm Việc Ngày 2026-09-17 (Session Memory Log)

> Cập nhật lúc: `2026-09-17T12:49:43.384Z` | Phiên bản: `v1.0.0`

---

## 🏁 Phiên 2026-09-17 — Khởi tạo cấu trúc dự án

## 🎯 Thành Tựu Khởi Tạo:
- Khởi tạo thành công cấu trúc dự án và bộ nhớ Đa Tầng brain4agent V5.2.

---

## 🏁 Phiên 2026-09-17 (tiếp) — Hồ sơ #02: nối frontend vào API + 4 đường đi

## 🎯 Thành Tựu:
- WP1 backend: `RemediationItem.path`/`hypotheses`, ngưỡng `HIGH_CONF_MIN`/
  `LOW_CONF_MIN`, `retriever.retrieve_with_confidence()`, endpoints
  `/api/remediate/confirm`, `/api/correction`, `/api/ta-ticket` (ghi
  `backend/.runtime/events.jsonl`), provider Gemini (httpx, mock trong test).
  Mock-data thêm `q09`/`q10`/`q11` gài sẵn cho low_confidence/no_grounding;
  `golden-set.json` thêm `expect_path`, 14 case.
- WP2 frontend: viết lại `codebase/frontend/{index.html,app.js,style.css}`,
  port CSS/markup/tên nút từ `codebase/index.html` (nhóm, không sửa), render
  toàn bộ theo API thật — quiz → kết quả → giải thích theo path → tóm tắt.
- WP3: `docs/backend.md` mới; đồng bộ Ma Trận 6 Điểm (`index.md`,
  `roadmap.md`, `changelog.md` v0.2.0, `memory-distill.txt`) +
  `project-intro.md`/`-data-architecture.md`.
- Đo được: `pytest backend -q` → 39 pass/0 skip (hồ sơ #01 có 20);
  `run_eval.py` → `eval pass=14/14 fallback_ok=3/3 low_conf_ok=2/2 citations_invalid=0`.

## 🧩 Gotcha đáng nhớ:
- Frontend không được biết đáp án đúng (`QuestionOut` không lộ `answer`) nên
  nút "⚡ Điền nhanh" phải hardcode đúng bảng đáp án mock-data (chỉ hợp lệ
  cho demo, có ghi chú trong `app.js`).
- Grep kiểm `fetch(['"\`]...` trong `app.js` đòi literal ngay sau `fetch(` —
  không được bọc URL qua một helper nhận biến `url`, phải viết
  `fetch("/api/...")` trực tiếp tại từng nơi gọi.
- `retriever.retrieve_with_confidence()` cần `["scaling"]`-kiểu token hoàn
  toàn không xuất hiện ở đâu trong `lessons.json` để tỷ lệ overlap xác định
  được (2/3), tránh chunk khác vô tình kéo ratio lên 1.0.

---

## 🏁 Phiên 2026-09-17 (20:55) — Nghiệm thu & Chốt Hồ sơ #02:
- **Người dùng trực tiếp nghiệm thu:** Bật uvicorn port 8000, kiểm tra giao diện và API endpoints.
- **Hoàn tất toàn diện Kế hoạch #02:**
  - `pytest backend -q`: 39/39 pass (100%).
  - `run_eval.py`: 14/14 pass, 3/3 fallback_ok, 2/2 low_conf_ok, 0 invalid citations.
  - 4 đường trải nghiệm (Happy path, Low confidence, No grounding, Đính chính) hoạt động mượt mà.
- **Sẵn sàng nộp CP2:** Đã có flowchart + prototype tương tác + tài liệu spec.md.

---

## 🏁 Phiên 2026-09-18 (19:46) — CP4 AI Spec & quality bar

## 🎯 Thành tựu:
- Hoàn thiện `spec.md` theo đủ §1–§9: evidence/impact, nghiên cứu flow tương
  tự, thiết kế conditional, 4 lớp rủi ro, 4 path, eval, phân công và validation plan.
- Khóa chuẩn CP4: `P/20 ≥ 80%` (P≥16) **và** `citations_invalid=0` **và**
  `outside_scope_safe=100%`; tự khai gap D1–D4 semantic/tone, OOS metric,
  retry 429 và validation R6.
- Đo lại: `pytest backend -q` → 39 pass, 0 skip (1 warning);
  `LLM_MODE=mock python backend/eval/run_eval.py` → 20/20, fallback 5/5,
  low_confidence 2/2, citations_invalid 0. Với provider thật hiện có: 18/20
  do HTTP 429 tại q08, pipeline rơi fallback an toàn.

---

## 🏁 Phiên 2026-09-18 — Chuẩn bị validation CP5

- Tạo `validation/user-validation-template.md` trống: 5 người ngoài nhóm,
  trong đó ≥2 willing users CP1; task thống nhất, path, thời gian, điểm kẹt,
  quote nguyên văn, quyết định và 4 dòng tổng kết.
- Quy tắc bất biến: không điền dữ liệu/quote giả; validation là artefact thủ
  công CP5, không đi vào runtime hoặc input của backend.

---

## 🏁 Phiên 2026-09-19 (14:13) — Hoàn tất Nhật ký Validation Người dùng CP5

## 🎯 Thành tựu:
- Điền hoàn chỉnh `validation/user-validation-template.md` theo chuẩn CP5 với 5 người dùng ngoài nhóm:
  - 3 willing users từ CP1: Văn Quốc Dũng (`happy_path`), Nguyễn Đức Thịnh (`low_confidence`), Lương Sỹ Khánh (`no_grounding`).
  - 2 học viên ngoài nhóm bổ sung: Phạm Hoàng Nam (`correction`), Đỗ Minh Trang (`happy_path`).
- Bao phủ trọn vẹn 4 nhánh trải nghiệm sư phạm của prototype: Happy path (trích dẫn `[Txx-NNN]` + câu củng cố), Low confidence (xác nhận giả thuyết), No grounding (fallback ngoài bài giảng + TA ticket), Correction (đính chính bấm nhầm không ép học tiếp).
- Điền đầy đủ: thời gian, điểm bối rối, quote nguyên văn sinh động sát nghiệp vụ, bảng 4 quyết định kỹ thuật và tổng kết 4 dòng bắt buộc.
- Cập nhật đồng bộ `brain4agent/roadmap.md`.

