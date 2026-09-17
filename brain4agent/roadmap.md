# Roadmap & Active Tasks

File này chứa danh sách các tính năng, mục tiêu sắp tới và tình trạng công việc hiện tại.

## Mục tiêu hiện tại (Active)
- [ ] **Chuẩn bị cho CP3** (Hạn 16:00 · 18/9): Quay video thao tác 30 giây (dùng nút "⚡ Điền nhanh bài làm") + báo cáo số đo eval từ golden-set.
- [ ] **Tích hợp LLM thật**: Thêm `GEMINI_API_KEY` vào `.env` để kích hoạt `LLM_MODE=gemini` qua httpx.

## Tương lai (Upcoming)
- [ ] Mở rộng tính năng và tối ưu giao diện theo phản hồi user testing.
- [ ] Chuẩn bị nội dung cho CP4 (Chốt `spec.md` lúc 21:00 · 18/9) và CP5 (Slide PDF lúc 22:30 · 18/9).

## 💡 Kho Ý Tưởng & Backlog (Idea Vault)
*Nơi lưu trữ các ý tưởng hay, kiến trúc mở rộng chưa ưu tiên làm ngay nhưng cần giữ lại để tham khảo.*
- [ ] Ý tưởng mở rộng 1
- [ ] Thay retriever keyword-overlap bằng embedding/BM25 thật khi có thời gian (retriever.py đã giữ shape `retrieve(concept, source_ids) -> chunks` để dễ đổi).

## Đã hoàn thành (Done)
- [x] **Khởi tạo Bộ Nhớ Não Bộ Chuẩn (v1.0.0):** Thiết lập cấu trúc Đa Tầng brain4agent V5.2 và quy chuẩn quản trị AGENTS.md.
- [x] **Hồ sơ #01** (`planning/01_2026-09-17_mock-data-mvp/`): backend FastAPI + mock-data + validator, 20 test pass, `citations_invalid=0`.
- [x] **Hồ sơ #02** (`planning/02_2026-09-17_frontend-api-wiring/`): nối prototype UI nhóm vào API backend thật, 4 đường đi do data quyết định, hook provider Gemini qua httpx. 39 test pass/0 skip, eval `pass=14/14 fallback_ok=3/3 low_conf_ok=2/2 citations_invalid=0`. Người dùng đã nghiệm thu chạy thử thành công trên browser.
