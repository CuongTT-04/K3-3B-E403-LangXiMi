# Mã Nguồn Sản Phẩm — LangXiMi AI Quiz Remediation

Thư mục này chứa toàn bộ mã nguồn thực thi của sản phẩm AI theo yêu cầu của Hackathon:

## Cấu trúc thư mục
- **`backend/`**: Mã nguồn Backend viết bằng FastAPI, triển khai luồng RAG, tích hợp LLM thật (OpenRouter GPT-4o-mini / Groq / Gemini), Validator chống ảo giác và hệ thống ghi vết `logs/llm_trace.log`.
- **`frontend/`**: Giao diện người dùng Web (Làm quiz, xem AI chẩn đoán, xem trích dẫn transcript bài giảng, làm câu hỏi củng cố tức thì).
- **`mock-data/`**: Dữ liệu bài giảng (`lessons.json`), đề thi (`quiz-day01.json`), và bộ Golden Set (`golden-set.json`).
- **`eval/`**: Bộ công cụ đánh giá chất lượng tự động (`run_eval.py`).
- **`requirements.txt`**: Danh sách thư viện Python cần cài đặt.

## Hướng dẫn chạy nhanh
```bash
# 1. Cài đặt thư viện
pip install -r codebase/requirements.txt

# 2. Khởi động Backend server
# Trên Windows PowerShell:
$env:PYTHONPATH="codebase/backend"; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Trên Linux/macOS:
PYTHONPATH="codebase/backend" python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 3. Chạy kiểm thử tự động
python -m pytest codebase/backend/tests

# 4. Chạy đánh giá Golden Set
python codebase/eval/run_eval.py
```
Mở trình duyệt tại: `http://127.0.0.1:8000`
