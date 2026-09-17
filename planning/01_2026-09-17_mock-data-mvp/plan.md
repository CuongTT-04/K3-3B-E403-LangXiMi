# Kế hoạch #01 — Mock-data MVP: quiz → nộp → giải thích & câu củng cố (chạy được end-to-end)

## 1. Metadata
- Trạng thái: ✅ WP0–WP3 DUYỆT (2026-09-17 20:35) · WP4 chuyển sang hồ sơ #02
- Loại: PATCH (≤1 ngày công) → ngoại lệ §3.2.5: chỉ `plan.md`
- Ngày tạo: 2026-09-17 · SO: super orchestrator (Fable) · Worker: 🟠 Sonnet
- Phạm vi: `codebase/` (mới) · `planning/01_*` · `docs/backend.md`

## 2. Nhật ký quyết định
| Giờ | Quyết định | Vì sao | Chỗ có thể lật + chi phí lật |
|---|---|---|---|
| 2026-09-17 20:10 | Stack: Python 3.13 + FastAPI + uvicorn; frontend HTML/JS tĩnh do FastAPI serve | Máy có Python 3.13, không cần build step, demo chạy bằng 1 lệnh | Đổi sang React sau: chỉ thay `codebase/frontend/`, API giữ nguyên |
| 2026-09-17 20:10 | LLM chạy chế độ `LLM_MODE=mock` (mặc định), có hook `real` chờ API key | Chưa có API key; cần chạy end-to-end trước | Điền key + `LLM_MODE=real` trong `.env`, không sửa contract |
| 2026-09-17 20:10 | Mock data tự sinh 100%: transcript giả có ID `[T01-NNN]`, quiz giả 8 câu, KHÔNG dùng data khoá học | Fixture thật thuộc dữ liệu bảo mật (luật bảo mật điều 2-3) | Khi có data thật: thay file trong thư mục ngoài repo qua `DATA_DIR`, cùng schema |
| 2026-09-17 20:10 | Retriever = keyword overlap đơn giản theo concept, không vector DB | 39 giờ hackathon, cần giải thích được với giám khảo | Nâng BM25/embedding sau, cùng interface `retrieve(concept) -> chunks` |
| 2026-09-17 20:10 | Validator bắt buộc: citation phải tồn tại trong index; câu củng cố phải trỏ về citation; không căn cứ ⇒ fallback không sinh quiz | Đúng canvas dòng 6 (Conditional, không bịa) | Không lật |

| 2026-09-17 20:35 | Phán quyết WP0–WP3: `✅ DUYỆT`. SO đo lại: `pytest` 20 pass/0 skip exit 0 · `run_eval.py` → `eval pass=11/11 fallback_ok=2/2 citations_invalid=0` exit 0 | Số đo khớp report worker | — |
| 2026-09-17 20:35 | `codebase/index.html` + `codebase/flowchart.md` là prototype CP2 của nhóm (nhánh `dev`, commit 7d3d8a3/b636176), GIỮ NGUYÊN làm bằng chứng CP2; KHÔNG xoá, KHÔNG sửa | Path invariant + bằng chứng nộp mốc | — |
| 2026-09-17 20:35 | Thiết kế UI của nhóm (4 đường đi, nút "Tôi bấm nhầm", "Bỏ qua", "Hỏi TA", hộp chọn 2 nguyên nhân) là nguồn chân lý UI; `codebase/frontend/` của worker #01 sẽ được thay bằng bản nối API theo thiết kế đó — hồ sơ #02 | spec.md §4b/§6 và flowchart.md đã chốt cho CP2 | Lật = giữ UI worker #01, chi phí thấp nhưng lệch spec |
| 2026-09-17 20:35 | WP4 (docs + đồng bộ não) gộp vào hồ sơ #02 để đồng bộ một lần sau khi nối API | Tránh đồng bộ não 2 lần trong 1 giờ | — |

### Quyết định bị thay thế
- 20:10 "LLM hook `real` chờ API key" → 20:35: spec.md §4 chốt **Gemini API** tại CP3 ⇒ hook đổi tên `LLM_MODE=gemini`, biến `GEMINI_API_KEY` (hồ sơ #02).

## 3. Work Packages
| WP | Việc | Tầng | Xong khi |
|---|---|---|---|
| WP0 | Scaffold `codebase/backend`, `codebase/frontend`, `codebase/mock-data`, README chạy 1 lệnh | 🟢 | `GET /health` → 200 |
| WP1 | Mock data: `lessons.json` (≥30 chunk `[T01-NNN]`, 4 concept), `quiz-day01.json` (8 câu MCQ, mỗi câu → concept → ≥2 chunk id), `golden-set.json` (≥10 case) | 🟠 | Test schema xanh |
| WP2 | Backend: contract JSON, retriever, mock LLM, validator + fallback, endpoints | 🟠 | pytest xanh, 1 lượt submit trả remediation hợp lệ |
| WP3 | Frontend: màn quiz → nộp → kết quả → giải thích + trích dẫn + quiz củng cố → nút Bỏ qua/Kết thúc, Làm lại, Tôi vẫn chưa hiểu | 🟠 | Bấm được hết luồng trong trình duyệt |
| WP4 | `docs/backend.md` + đồng bộ não | 🟢 | Ma trận 6 điểm |

## 4. Checklist thực thi
- [x] WP0 · [x] WP1 · [x] WP2 · [x] WP3 · [~] WP4 → hồ sơ #02
- [ ] Cổng nghiệm thu: `python -m pytest codebase/backend -q` exit 0 · `curl /health` 200 · luồng bấm tay OK
  (worker đã verify pytest exit 0, curl /health 200, curl submit 8 câu sai → remediation không rỗng, static frontend serve 200; CHƯA click-through bằng browser thật vì worker không có browser tool — cần người/SO xác nhận nốt phần này.)

## 5. Câu hỏi mở (cần người)
- LLM provider + API key để bật `LLM_MODE=real`.
- WP4 (`docs/backend.md` + đồng bộ não) không thuộc tầng được giao cho worker này (chỉ WP0-WP3) — cần giao lại hoặc SO tự làm.
- Cổng nghiệm thu "luồng bấm tay OK" cần người có browser thật xác nhận; worker chỉ verify được qua curl + đọc code.
