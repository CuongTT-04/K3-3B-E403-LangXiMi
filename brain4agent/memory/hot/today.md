# 📅 Nhật Ký Làm Việc Ngày 2026-09-18 (Session Memory Log)

> Cập nhật lúc: `2026-09-18T13:40:00+07:00` | Phiên bản: `v0.2.1` (Grade A Runtime Verified)

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
