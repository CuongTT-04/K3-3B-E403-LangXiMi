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
