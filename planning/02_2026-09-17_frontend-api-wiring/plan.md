# Kế hoạch #02 — Nối prototype UI của nhóm (CP2) vào API backend + đường đi 4 nhánh + hook Gemini

## 1. Metadata
- Trạng thái: ✅ ĐÃ HOÀN THÀNH (2026-09-17 20:55:00) · Người dùng đã nghiệm thu và xác nhận chạy thử thành công
- Loại: PATCH (≤1 ngày công) → ngoại lệ §3.2.5: chỉ `plan.md`
- Ngày tạo: 2026-09-17 20:35 · SO: super orchestrator (Fable) · Worker: 🟠 Sonnet
- Kế thừa: hồ sơ #01 (contract `RemediationOut`, mock-data, validator)
- Phạm vi: `codebase/backend/**` · `codebase/frontend/**` · `codebase/mock-data/**` · `codebase/README.md` · `docs/backend.md` · `brain4agent/**`
- CẤM chạm: `codebase/index.html` · `codebase/flowchart.md` (bằng chứng CP2 của nhóm) · `spec.md` · `canvas.md` · `README.md` gốc

## 2. Nhật ký quyết định
| Giờ | Quyết định | Vì sao | Chỗ có thể lật + chi phí lật |
|---|---|---|---|
| 2026-09-17 20:35 | Frontend mới tại `codebase/frontend/` lấy nguyên thiết kế/CSS/nút của `codebase/index.html` nhóm, bỏ hardcode, mọi dữ liệu qua API | UI nhóm khớp spec §4b/§6; backend #01 đã có API | Lật = giữ 2 frontend song song, gây rối demo |
| 2026-09-17 20:35 | Contract mở rộng: `item.path ∈ {happy, low_confidence, no_grounding}`; `low_confidence` mang `hypotheses[2]` (id, label); `confidence ≥ 0.75` ⇒ happy, `0.4 ≤ c < 0.75` ⇒ low_confidence, `< 0.4` hoặc chunks=[] ⇒ no_grounding | Ngưỡng 0.75 chốt trong spec §4; mock retriever tính confidence = tỷ lệ overlap | Ngưỡng 0.4 là của SO, đổi bằng env `LOW_CONF_MIN` |
| 2026-09-17 20:35 | Thêm `POST /api/correction` {quiz_id, question_id, action: misclick\|dismiss} và `POST /api/ta-ticket` {quiz_id, question_id, note}; cả hai ghi vào `codebase/backend/.runtime/events.jsonl` (gitignore), trả 200 | Cần cho đường đi 4 (G8/G9) và nút "Hỏi TA"; ghi log để có số đo R6 | Có thể đổi sang DB sau |
| 2026-09-17 20:35 | Mock-data thêm ≥1 câu có concept mơ hồ để tạo được `low_confidence` thật, và giữ ≥1 concept không có trong lessons để tạo `no_grounding` | Demo phải bấm ra đủ 4 đường đi bằng data, không bằng tab giả | — |
| 2026-09-17 20:35 | `LLM_MODE=gemini`: gọi Gemini qua `httpx` REST (`generativelanguage.googleapis.com`, model `gemini-2.5-flash`), đọc `GEMINI_API_KEY`; test KHÔNG gọi mạng (mock httpx). Thiếu key ⇒ log cảnh báo và rơi về mock | spec §4 chốt Gemini tại CP3; chưa có key | Đổi model qua env `GEMINI_MODEL` |
| 2026-09-17 20:35 | Giữ nút "⚡ Điền nhanh bài làm" của nhóm ở màn quiz (điền sai đúng các câu tạo đủ 4 đường đi) | Quay video CP3 30 giây cần nhanh | — |
| 2026-09-17 21:05 | Phán quyết WP1–WP3: `✅ DUYỆT` (máy). SO đo lại: `pytest` 39 pass/0 skip exit 0 · `run_eval.py` → `eval pass=14/14 fallback_ok=3/3 low_conf_ok=2/2 citations_invalid=0` exit 0 · `init_brain.js --check` exit 0 | Số đo khớp report worker | Gate "người bấm tay" còn mở |
| 2026-09-17 21:05 | Người dùng chốt: SO dừng phóng worker; từ đây người dùng tự điều phối theo `planning/` + spec | Yêu cầu trực tiếp | — |
| 2026-09-17 20:55 | Người dùng xác nhận hoàn tất kiểm thử trực tiếp trên browser và duyệt đóng Kế hoạch #02 | Nghiệm thu thực tế | — |

### Quyết định bị thay thế
- (chưa có)

## 3. Work Packages
| WP | Việc | Tầng | Xong khi |
|---|---|---|---|
| WP1 | Backend: mở rộng schema (`path`, `hypotheses`), ngưỡng confidence, endpoints `/api/correction`, `/api/ta-ticket`, provider `gemini` (httpx, mock trong test), cập nhật mock-data + golden-set có case low_confidence | 🟠 | `pytest` ≥ 28 test pass/0 skip; `run_eval.py` in thêm `low_conf_ok=K/L`; `citations_invalid=0` |
| WP2 | Frontend: port UI nhóm sang `codebase/frontend/` (index.html, app.js, style.css), render theo `item.path` từ API; đủ nút: Nộp bài · Điền nhanh · Làm lại · Xem giải thích · Kiểm tra củng cố · Bỏ qua · Tôi bấm nhầm · chọn nguyên nhân (2) · Hỏi TA · Hoàn tất | 🟠 | `curl /` 200; smoke test JS-free: mọi endpoint frontend gọi đều tồn tại trong `main.py` (grep) |
| WP3 | `docs/backend.md` (API table, schema, env) + đồng bộ não 6 điểm + project-intro/-data-architecture (thêm ngôn ngữ Python) | 🟢 | Ma trận 6 điểm đủ; `init_brain.js --check` exit 0 |

## 4. Checklist thực thi
- [x] WP1 · [x] WP2 · [x] WP3
- [x] Cổng nghiệm thu: `python -m pytest backend -q` exit 0/0 skip · `python backend/eval/run_eval.py` một dòng · người bấm tay đủ 4 đường đi trên browser
  (Đã xác nhận: pytest 39/39 pass + eval 1 dòng pass=14/14 fallback_ok=3/3 low_conf_ok=2/2 citations_invalid=0 + server uvicorn chạy port 8000 đã kiểm thử và duyệt bởi người dùng)

## 5. Câu hỏi mở (cần người)
- `GEMINI_API_KEY` để bật `LLM_MODE=gemini` (hiện chạy mock).
- Ai bấm tay xác nhận 4 đường đi trên browser (Châm Anh?).
