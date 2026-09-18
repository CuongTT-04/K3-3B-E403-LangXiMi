# Giới Thiệu Dự Án (Project Overview)

## 1. Mục tiêu (Goals & Objectives)
Quiz Remediation MVP: học viên làm bài trắc nghiệm ôn tập, nộp bài, nhận
chẩn đoán AI cho từng câu sai — chẩn đoán hiểu nhầm, trích dẫn nguyên văn
transcript bài giảng `[T01-NNN]`, sinh câu hỏi trắc nghiệm củng cố. Mọi câu
sai rơi vào 1 trong 3 đường đi tuỳ độ tin cậy truy xuất (`happy` tự tin cao,
`low_confidence` cần học viên xác nhận nguyên nhân, `no_grounding` từ chối
bịa khi không có căn cứ) cộng thêm quyền đính chính/hỏi trợ giảng — không
bao giờ trả về trích dẫn bịa đặt (validator chặn cứng). Toàn bộ dữ liệu bài
giảng/quiz là MOCK, không dùng nội dung khoá học thật.

## 2. Công nghệ cốt lõi (Tech Stack)
- **Frontend:** HTML/CSS/JS thuần (`codebase/frontend/`), không build step,
  UI port từ prototype clickable của nhóm (`codebase/index.html`).
- **Backend / Engine:** Python 3.13 + FastAPI + Pydantic v2
  (`codebase/backend/app/`) — xem `docs/backend.md`.
- **LLM:** `MockLLM` (deterministic, không gọi mạng, dùng trong test/eval);
  `GeminiLLM` (`LLM_MODE=gemini`, REST qua `httpx`, thiếu key tự rơi về
  mock); `RealLLM` là stub cho provider khác trong tương lai.
- **Data Persistence:** JSON tĩnh trong `codebase/mock-data/` (không DB);
  `codebase/backend/.runtime/events.jsonl` append-only cho log sự kiện
  người dùng (correction/ta-ticket). `validation/` chỉ chứa nhật ký đánh giá
  thủ công sau CP5; không phải dữ liệu runtime và không được điền dữ liệu giả.
