# Roadmap & Active Tasks

File này chứa danh sách các tính năng, mục tiêu sắp tới và tình trạng công việc hiện tại.

## Mục tiêu hiện tại (Active)
- [ ] **Chuẩn bị cho CP3** (Hạn 16:00 · 18/9, vẫn đúng — chưa có bằng chứng đã quay): Quay video thao tác 30 giây (dùng nút "⚡ Điền nhanh bài làm") + báo cáo số đo eval từ golden-set.
- [ ] **CP4 21:00 (18/9):** Nộp link `spec.md` đã chốt (hồ sơ #03 xong nội dung; chờ điền nốt 5 dòng ⏳ cần data pack ngoài repo + `GEMINI_API_KEY`).
- [ ] **CP5 22:30 (18/9):** Slide PDF + video dự phòng.
- [ ] **Tích hợp LLM thật**: Thêm `GEMINI_API_KEY` vào `.env` để kích hoạt `LLM_MODE=gemini` qua httpx.

## Tương lai (Upcoming)
- [ ] Mở rộng tính năng và tối ưu giao diện theo phản hồi user testing.

## 💡 Kho Ý Tưởng & Backlog (Idea Vault)
*Nơi lưu trữ các ý tưởng hay, kiến trúc mở rộng chưa ưu tiên làm ngay nhưng cần giữ lại để tham khảo.*
- [ ] Thêm dấu tiếng Việt cho `validator._fallback_item`/`lessons.json`/fallback text nói chung — hiện lẫn dấu/không dấu khi rơi vào `no_grounding` (phát hiện ở hồ sơ #03 WP5).
- [ ] Tách worktree riêng cho mỗi worker song song thay vì dùng chung `.git/index` — tránh commit của worker này cuốn theo file đang stage của worker khác (sự cố lặp lại ở hồ sơ #03, xem `-known-gotchas.md`).
- [ ] Thay retriever keyword-overlap bằng BM25 thật, tính từ `stem`+`options` của câu hỏi thay vì chỉ dựa vào `source_ids` khai sẵn trong mock-data — sát với truy xuất thật hơn khi có dữ liệu ngoài mock.

## Đã hoàn thành (Done)
- [x] **Khởi tạo Bộ Nhớ Não Bộ Chuẩn (v1.0.0):** Thiết lập cấu trúc Đa Tầng brain4agent V5.2 và quy chuẩn quản trị AGENTS.md.
- [x] **Hồ sơ #01** (`planning/01_2026-09-17_mock-data-mvp/`): backend FastAPI + mock-data + validator, 20 test pass, `citations_invalid=0`.
- [x] **Hồ sơ #02** (`planning/02_2026-09-17_frontend-api-wiring/`): nối prototype UI nhóm vào API backend thật, 4 đường đi do data quyết định, hook provider Gemini qua httpx. 39 test pass/0 skip, eval `pass=14/14 fallback_ok=3/3 low_conf_ok=2/2 citations_invalid=0`. Người dùng đã nghiệm thu chạy thử thành công trên browser.
- [x] **Hồ sơ #03** (`planning/03_2026-09-18_cp4-spec-hardening/`): chẩn đoán theo `chosen`, Gemini không raise (retry 1 lần), validator chuẩn hoá khoảng trắng, golden set 14→21 case (+`expect_paths`), điền `spec.md` §1–§3/§5/§7–§9, thẩm định cô lập 5 cách phá (✅ DUYỆT WP1–WP4). Số đo cuối: `pytest backend -q` 49 passed/0 skip; `run_eval.py` → `eval pass=21/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0`.
