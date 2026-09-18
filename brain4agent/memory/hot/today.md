# 📅 Nhật Ký Làm Việc Ngày 2026-09-18 (Session Memory Log)

> Cập nhật lúc: `2026-09-18T14:30:00+07:00` | Phiên bản: `v0.2.2` (Grade A Runtime Verified)

## 🏁 Phiên 2026-09-18 — Hồ sơ #03 CP4: chốt spec.md + gia cố chẩn đoán/Gemini + golden set ≥20

## 🎯 Thành Tựu Cốt Lõi Đạt Được Trong Phiên:
1. **WP1 (backend chẩn đoán/Gemini)**: `chosen` (phương án học viên chọn) luồn từ
   `service.remediate` → `_remediate_one` → `LLM.generate`; validator giữ
   `misconception` của LLM khi không rỗng, so quote sau khi chuẩn hoá khoảng
   trắng; `GeminiLLM.generate` không bao giờ raise (retry đúng 1 lần khi
   Timeout/429/5xx, `ConnectError` fallback ngay — cố ý); đáp án câu củng cố
   MockLLM đặt theo `chunk_id` (không cố định A); `confirm_hypothesis` rẽ
   nhánh explanation theo `h1`/`h2`.
2. **WP2 (golden set)**: `golden-set.json` mở rộng 14 → 21 case (10 happy,
   3 low_confidence, 4 no_grounding, 4 mixed dùng field mới `expect_paths`);
   `run_eval.py` chấm theo item cho case hỗn hợp, thêm `--verbose`.
3. **WP3 (spec.md)**: điền §1–§3, §5, §7–§9 từ nguồn trong repo, quality bar
   khoá "≥90% case đúng path, `citations_invalid=0`, 0 item `no_grounding`
   có trích dẫn"; giữ nguyên §4/§4b/§6.
4. **WP4 (thẩm định cô lập WP1+WP2)**: 5 cách phá (chosen ngoài options,
   Gemini mất mạng, quote bịa whitespace lạ, qid/hypothesis rác, dữ liệu
   golden-set cố tình hỏng qua `DATA_DIR`) — bộ đo mới ĐỎ đúng lúc trên dữ
   liệu hỏng (`pass=16/21` khi hỏng 5 case, `21/21` trên dữ liệu thật), 4
   cách còn lại không lật được (hệ đang xanh thật).
5. **WP5 (phiên này)**: đồng bộ não 6 điểm + gotchas + xoay ký ức + bump
   `v0.2.1` + điền số cuối `spec.md` §7.

## 🧪 Kết Quả Benchmark / Kiểm Thử Thực Chiến (số đo cuối, mock):
- `pytest backend -q` → **49 passed / 0 fail / 0 skip**, exit 0 (base hồ sơ #02: 39).
- `python backend/eval/run_eval.py` → `eval pass=21/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0`.
- `run_eval.py --verbose` → 21 dòng case + 1 dòng tổng = 22 dòng.
- `init_brain.js --check` → exit 0 trước và sau khi sửa não.

## 📁 Phán quyết:
- R01 (WP1) ✅ DUYỆT · R02 (WP2) ✅ DUYỆT · R03 (WP3) ✅ DUYỆT · R04 (WP4, thẩm định WP1+WP2) ✅ DUYỆT.
- Base `374230d` → Head sau WP1–WP4 `011b8b9`. WP5 (não) là commit tiếp theo trong hồ sơ này.

## ⚠️ Bẫy Kỹ Thuật (Gotchas) & Lưu Ý:
- **3 worker chung một `.git/index`, không worktree riêng** ⇒ nhiều lần
  `git commit`/`git add -A` của worker này cuốn theo file đang stage của
  worker khác, hoặc `--amend --no-edit` gộp nhầm vào commit của worker khác
  (thấy ở cả R02 và R03). Mọi lần đều tự phát hiện qua `git show --stat
  HEAD` và tự sửa bằng `git reset --soft HEAD^` / `git restore --staged` /
  `git checkout <sha-cũ> -- <file>` rồi commit lại đúng pathspec — không
  mất dữ liệu, không phải merge conflict thật. Xem chi tiết đầy đủ trong
  `-known-gotchas.md`.
- **`GeminiLLM` chỉ retry `TimeoutException`/429/5xx** — `httpx.ConnectError`
  (mất mạng/DNS) rơi thẳng về `MockLLM` không retry, đúng thiết kế WP1 việc
  4 (đã đối chiếu ở WP4 break-test b), không phải thiếu sót.
- **`validator._fallback_item` chưa có dấu tiếng Việt** ("Chua du can cu de
  chan doan chinh xac...") trong khi phần lớn UI khác đã có dấu ⇒ trải
  nghiệm demo lẫn dấu/không dấu khi rơi vào `no_grounding`. Ghi vào Idea
  Vault để sửa sau (không thuộc phạm vi CP4, không đổi hành vi mã ở WP5).

## 🏁 Phiên 2026-09-18 (tiếp) — Hồ sơ #04: Gemini xoay model khi cạn quota, Groq dự phòng, cache đĩa, số đo AI thật

## 🎯 Thành Tựu Cốt Lõi Đạt Được Trong Phiên:
1. **H01 (Gemini rotation + cache + validator fold)**: `GeminiLLM` xoay
   `GEMINI_MODELS` (429/404/503/JSON hỏng → model kế NGAY, timeout retry 1
   lần cùng model, hết danh sách → `MockLLM`); cache LLM thật trên đĩa
   `backend/.runtime/llm-cache.json` (khoá sha1 prompt version+qid+chosen+
   chunk ids, chỉ cache kết quả thật); `llm.STATS`; `validator._fold` so
   trích dẫn bỏ dấu tiếng Việt (vẫn từ chối đổi từ); `run_eval.py
   --llm-stats/--sleep`.
2. **H02 (Groq dự phòng thứ hai)**: `GroqLLM` (API kiểu OpenAI, xoay
   `GROQ_MODELS`, KHÔNG retry cùng model kể cả timeout, hết danh sách raise
   `ProviderExhausted` nội bộ) + `ChainLLM` (Gemini → Groq → Mock, mỗi
   provider tự rotate qua `_rotate_or_raise`); cache đĩa dùng chung 2
   provider (khoá không chứa tên provider).
3. **H03 (phiên này) — chốt hồ sơ #04**: `run_eval.py --llm-stats` in
   thêm `groq=<n>` vào dòng `llm …`; điền số đo AI thật vào `spec.md` §7
   (Gemini 18/21, Groq 21/21, cả hai `citations_invalid=0`) + 1 dòng §9;
   đồng bộ não 6 điểm + `project-intro.md`/`-data-architecture.md`; bump
   `v0.2.2`; đóng `plan.md` #04.
4. WP2 (video Chrome 23,4s + 8 ảnh, quay với Gemini thật qua cache) đã
   xong trước phiên này, lưu tại
   `planning/04_2026-09-18_gemini-quota-cache/evidence/demo/`.

## 🧪 Kết Quả Benchmark / Kiểm Thử Thực Chiến (số đo cuối):
- `pytest backend -q` (`LLM_MODE=mock`, không gọi mạng) → **75 passed / 0
  fail / 0 skip**, exit 0 (base hồ sơ #03: 49; H01 nâng lên 63; H02 nâng
  lên 75).
- `run_eval.py` (`LLM_MODE=mock`) → `eval pass=21/21 fallback_ok=7/7
  low_conf_ok=7/7 citations_invalid=0`.
- `run_eval.py --llm-stats` (`LLM_MODE=mock`) → dòng `llm gemini=0 groq=0
  cache=0 mock_fallback=0 model=-` trước dòng tổng.
- Eval Gemini THẬT (1 lần, `gemini-3.5/3.6-flash` xoay, cache) →
  `eval pass=18/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0`
  (3 case rớt do validator chặn trích dẫn không khớp — an toàn, không
  phải bug).
- Eval Groq THẬT (1 lần, `openai/gpt-oss-120b→20b`, `qwen3.8-27b`, cache
  riêng `llm-cache-groq.json`) → `eval pass=21/21 fallback_ok=7/7
  low_conf_ok=7/7 citations_invalid=0`.
- `init_brain.js --check` → exit 0 trước và sau khi sửa não.

## 📁 Phán quyết:
- R01 (H01, WP1 xoay Gemini/cache/validator) ✅ DUYỆT.
- R02 (H02, WP1b Groq dự phòng) ✅ DUYỆT.
- R03 (H03, WP3 stats/spec/não — báo cáo này) chờ SO.
- Base hồ sơ #04 `a33e73f` → Head sau H01 `7c01448` → sau H02 `8d8eff7`.

## ⚠️ Bẫy Kỹ Thuật (Gotchas) & Lưu Ý:
- **Gemini free tier 20 request/NGÀY/MODEL riêng biệt** (không chia sẻ),
  `gemini-2.x` đã bị gỡ (404) — luôn dùng danh sách xoay `GEMINI_MODELS`,
  không hardcode 1 model. Xem chi tiết `-known-gotchas.md`.
- **`parts[i].thoughtSignature` xen trước phần tử `text` thật** trong
  response Gemini 3.x — không được lấy cứng `parts[0]`, phải quét tìm key
  `text` (`llm._extract_text`).
- **Groq không có `llama-3.3-70b-versatile`** trên tài khoản này; giới hạn
  1000 request/ngày (chung, không theo model) + 8000 token/phút — luôn
  kèm `--sleep 1` khi eval `LLM_MODE=groq`/`gemini`/`chain` để tránh vượt
  giới hạn phút.
- **`run_eval.py --llm-stats` bị mâu thuẫn phạm vi ở H02** (mục 3 yêu cầu
  in `groq=` nhưng §2 CẤM chạm `run_eval.py`) — H03 mở khoá đúng phần đó
  (chỉ hàm format + 1 test khớp định dạng) theo quyết định của SO sau khi
  duyệt R02.
