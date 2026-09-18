# Roadmap & Active Tasks

File này chứa danh sách các tính năng, mục tiêu sắp tới và tình trạng công việc hiện tại.

## Mục tiêu hiện tại (Active)
- [ ] **Tích hợp LLM thật**: Thêm `GEMINI_API_KEY` vào `.env` để kích hoạt `LLM_MODE=gemini` qua httpx.

## Tương lai (Upcoming)
- [ ] Mở rộng tính năng và tối ưu giao diện theo phản hồi user testing.
- [ ] Chuẩn bị CP5: slide PDF, video dự phòng và validation ngoài nhóm (5 người; mẫu `validation/user-validation-template.md` đã sẵn sàng, hiện chưa có evidence R6).

## 💡 Kho Ý Tưởng & Backlog (Idea Vault)
*Nơi lưu trữ các ý tưởng hay, kiến trúc mở rộng chưa ưu tiên làm ngay nhưng cần giữ lại để tham khảo.*
- [ ] Ý tưởng mở rộng 1
- [ ] Thay retriever keyword-overlap bằng embedding/BM25 thật khi có thời gian (retriever.py đã giữ shape `retrieve(concept, source_ids) -> chunks` để dễ đổi).

## Đã hoàn thành (Done)
- [x] **Khởi tạo Bộ Nhớ Não Bộ Chuẩn (v1.0.0):** Thiết lập cấu trúc Đa Tầng brain4agent V5.2 và quy chuẩn quản trị AGENTS.md.
- [x] **Hồ sơ #01** (`planning/01_2026-09-17_mock-data-mvp/`): backend FastAPI + mock-data + validator, 20 test pass, `citations_invalid=0`.
- [x] **Hồ sơ #02** (`planning/02_2026-09-17_frontend-api-wiring/`): nối prototype UI nhóm vào API backend thật, 4 đường đi do data quyết định, hook provider Gemini qua httpx. 39 test pass/0 skip, eval `pass=14/14 fallback_ok=3/3 low_conf_ok=2/2 citations_invalid=0`. Người dùng đã nghiệm thu chạy thử thành công trên browser.
- [x] **CP4 — AI Spec & quality bar** (18/09/2026): hoàn thiện `spec.md` §1–§9 và khóa `P≥16/20 ∧ invalid citation=0 ∧ outside-scope safe=100%`. Golden set hiện có 20 case; MockLLM đo 20/20, provider thật đo 18/20 vì HTTP 429 ở q08. Tự khai: chưa chấm đầy đủ D1–D4 ngữ nghĩa/tone và chưa có validation R6.
