# Known Gotchas & Bugs

Tổng hợp các lỗi khó, các lưu ý dị biệt hoặc cách workaround đặc thù của dự án này để AI không dẫm lại vết xe đổ.

## Môi trường & Config
- Frontend không được biết đáp án đúng (`QuestionOut` không lộ `answer`) nên
  nút "⚡ Điền nhanh" phải hardcode đúng bảng đáp án mock-data (chỉ hợp lệ
  cho demo, có ghi chú trong `app.js`).
- Grep kiểm `fetch(['"\`]...` trong `app.js` đòi literal ngay sau `fetch(` —
  không được bọc URL qua một helper nhận biến `url`, phải viết
  `fetch("/api/...")` trực tiếp tại từng nơi gọi.
- `retriever.retrieve_with_confidence()` cần token kiểu `["scaling"]` hoàn
  toàn không xuất hiện ở đâu trong `lessons.json` để tỷ lệ overlap xác định
  được (2/3), tránh chunk khác vô tình kéo ratio lên 1.0.
- **3 worker chung một `.git/index`, không dùng worktree riêng** (hồ sơ #03,
  Bước 0 trỏ hub bằng đường dẫn tương đối `../../brain4agent.release` nên
  không tách worktree được) ⇒ `git commit`/`git add -A` của worker này có
  thể cuốn theo file đang stage của worker khác, hoặc `git commit --amend
  --no-edit` gộp nhầm vào commit vừa được worker khác tạo xen giữa. Cách
  phòng: LUÔN `git commit -- <pathspec tường minh của chính mình>`, KHÔNG
  bao giờ `git add -A`/`git commit -a`/`--amend` khi biết có worker khác
  đang chạy song song; phát hiện bằng `git show --stat HEAD` ngay sau mỗi
  commit; nếu lỡ gộm thì `git reset --soft HEAD^` (không mất staged) rồi
  commit lại đúng pathspec.
- `GeminiLLM.generate` chỉ coi `TimeoutException`/HTTP 429/5xx là lỗi có thể
  retry (đúng 1 lần); `httpx.ConnectError` (mất mạng/DNS/proxy chết) rơi
  thẳng về `MockLLM` KHÔNG retry — đây là hành vi CỐ Ý (demo không được
  chờ lâu khi mạng đứt hẳn), không phải thiếu sót; đã xác nhận lại ở WP4
  hồ sơ #03 (break-test cổng chết).
- Fallback text trong `validator._fallback_item` (`misconception`,
  `explanation`, `fallback_note`) hiện chưa có dấu tiếng Việt (vd "Chua du
  can cu de chan doan..."), trong khi phần lớn nội dung UI khác đã có dấu
  ⇒ trải nghiệm demo lẫn dấu/không dấu khi item rơi vào `no_grounding`.
  Biết trước để không ngạc nhiên khi thấy UI; sửa nằm ngoài phạm vi thi
  công không đổi hành vi mã (đã đưa vào Idea Vault ở `roadmap.md`).
- **Gemini free tier = 20 request/NGÀY cho MỖI model riêng** (không chia sẻ
  quota giữa các model), và model `gemini-2.x` đã bị Google gỡ (404 "no
  longer available") — đừng hardcode 1 model, luôn dùng danh sách xoay
  vòng `GEMINI_MODELS` trong `.env`/`llm.py` (hồ sơ #04). Khi đo eval thật
  nhiều lần trong 1 ngày, model đầu danh sách gần như chắc chắn đã cạn từ
  request trước — đây là hành vi bình thường, không phải lỗi rotation.
- Response JSON của Gemini 3.x có thể xen phần tử `parts[i].thoughtSignature`
  TRƯỚC phần tử chứa `text` thật sự trong `candidates[0].content.parts`
  ⇒ không được lấy cứng `parts[0]`, phải quét tìm phần tử có key `text`
  (`llm._extract_text`, hồ sơ #04). Lấy nhầm `parts[0]` sẽ KeyError/parse
  JSON rỗng, bị hiểu nhầm là model trả lỗi trong khi thực ra gọi thành công.
- Groq (`GroqLLM`) trên tài khoản dự án KHÔNG có model `llama-3.3-70b-
  versatile` (dùng `openai/gpt-oss-120b`/`qwen/qwen3.8-27b`/
  `openai/gpt-oss-20b` thay thế); giới hạn đo được 1000 request/NGÀY (chung,
  không chia theo model như Gemini) + 8000 token/PHÚT — khi chạy
  `run_eval.py --llm-stats` với `LLM_MODE=groq` (hay `gemini`/`chain`) nên
  luôn kèm `--sleep 1` để không vượt giới hạn request/phút giữa các case
  (hồ sơ #04).
