# Giới Thiệu Dự Án (Project Overview)

## 1. Mục tiêu (Goals & Objectives)
Quiz Remediation MVP: học viên làm bài trắc nghiệm ôn tập, nộp bài, nhận
chẩn đoán AI cho từng câu sai — chẩn đoán hiểu nhầm ĐẰNG SAU chính phương án
học viên đã chọn (`chosen`, không chỉ dựa vào đáp án đúng), trích dẫn nguyên
văn transcript bài giảng `[T01-NNN]`, sinh câu hỏi trắc nghiệm củng cố. Mọi
câu sai rơi vào 1 trong 3 đường đi tuỳ độ tin cậy truy xuất (`happy` tự tin
cao, `low_confidence` cần học viên xác nhận nguyên nhân, `no_grounding` từ
chối bịa khi không có căn cứ) cộng thêm quyền đính chính/hỏi trợ giảng —
không bao giờ trả về trích dẫn bịa đặt (validator chặn cứng, so quote sau
khi chuẩn hoá khoảng trắng + bỏ dấu tiếng Việt, vẫn từ chối nếu đổi hẳn
một từ). Bộ đánh giá hồi quy (golden-set, 21 case) có
`expect_paths` cho case nhiều câu kỳ vọng khác nhau. Toàn bộ dữ liệu bài
giảng/quiz là MOCK, không dùng nội dung khoá học thật.

## 2. Công nghệ cốt lõi (Tech Stack)
- **Frontend:** HTML/CSS/JS thuần (`codebase/frontend/`), không build step,
  UI port từ prototype clickable của nhóm (`codebase/index.html`).
- **Backend / Engine:** Python 3.13 + FastAPI + Pydantic v2
  (`codebase/backend/app/`) — xem `docs/backend.md`.
- **LLM:** `MockLLM` (deterministic, không gọi mạng, dùng trong test/eval,
  nhận `chosen` để chẩn đoán theo phương án đã chọn) là tầng cuối của một
  CHUỖI provider (`ChainLLM`, `LLM_MODE=gemini|chain|groq`): `GeminiLLM`
  (xoay `GEMINI_MODELS` khi 429/404/503/JSON hỏng, quota free tier 20
  request/ngày/MODEL) → `GroqLLM` (API kiểu OpenAI, xoay `GROQ_MODELS`,
  1000 request/ngày + 8000 token/phút, dự phòng khi Gemini cạn quota) →
  `MockLLM`. Cả hai provider thật đều KHÔNG BAO GIỜ làm sập request; kết
  quả thật (Gemini hoặc Groq) được cache trên đĩa
  (`backend/.runtime/llm-cache*.json`, khoá không phân biệt provider) để
  demo/eval lặp lại không tốn thêm quota. `RealLLM` là stub cho provider
  khác trong tương lai.
- **Data Persistence:** JSON tĩnh trong `codebase/mock-data/` (không DB);
  `codebase/backend/.runtime/events.jsonl` append-only cho log sự kiện
  người dùng (correction/ta-ticket).
