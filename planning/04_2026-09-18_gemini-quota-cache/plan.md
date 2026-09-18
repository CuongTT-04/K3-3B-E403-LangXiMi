# Kế hoạch #04 — Gemini thật cho CP3: xoay model khi hết quota, cache LLM, validator bỏ dấu, số đo thật

## 1. Metadata
- Trạng thái: 🚀 ĐANG PHÓNG (2026-09-18) · Loại: PATCH v0.2.2 (ngoại lệ §3.2.5: chỉ `plan.md`)
- SO: super orchestrator (Fable) · Worker: 🟠 Sonnet · Base: `a33e73f`
- Phạm vi: `codebase/backend/app/{llm.py,validator.py}` · `codebase/backend/eval/run_eval.py` · `codebase/backend/tests/**` · `codebase/.env.example` · `docs/backend.md` · `spec.md` §7 (số đo) · `brain4agent/**` (đồng bộ cuối)
- CẤM chạm: `schemas.py` · `codebase/mock-data/**` · `codebase/frontend/**` · `.env` (chứa key thật, gitignored)

## 2. Nhật ký quyết định
| Giờ | Quyết định | Vì sao | Chỗ có thể lật + chi phí lật |
|---|---|---|---|
| 2026-09-18 11:40 | Đo Gemini thật lần 1 (`gemini-3.5-flash`, 21 case): `eval pass=16/21 fallback_ok=7/7 low_conf_ok=6/7 citations_invalid=0`, 6 phút, nhiều 429 | Số thật cho CP3; `citations_invalid=0` giữ đúng lời hứa không bịa | — |
| 2026-09-18 11:40 | Người dùng chốt: bỏ Tabbit/ego-browser, dùng Chrome (Playwright `channel: chrome`, đã kiểm 153.0) | Yêu cầu trực tiếp | — |
| 2026-09-18 11:45 | Gói miễn phí = 20 request/NGÀY/model. `gemini-3.5-flash` đã cạn. Quyết: `GEMINI_MODELS` là danh sách xoay vòng (`gemini-3.5-flash,gemini-3.6-flash,gemini-3.5-flash-lite,gemini-3.7-flash,gemini-3.8-flash,gemini-3.1-flash-lite`); gặp 429/404 ⇒ chuyển model kế; hết danh sách ⇒ MockLLM. `GEMINI_MODEL` cũ vẫn được nhận (đặt lên đầu danh sách) | 6×20 = 120 request/ngày đủ eval (≈50) + demo | Người dùng nâng gói trả phí ⇒ đặt 1 model |
| 2026-09-18 11:45 | Cache LLM trên đĩa `backend/.runtime/llm-cache.json`, key = sha1(model-family + question_id + chosen + sorted chunk ids + prompt version); hit ⇒ không gọi mạng; `LLM_CACHE=off` để tắt | Demo ngày thi không phụ thuộc mạng/quota; eval chạy lại miễn phí | Xoá file cache để làm mới |
| 2026-09-18 11:45 | Validator so trích dẫn KHÔNG phân biệt dấu tiếng Việt (NFD bỏ tổ hợp dấu + lower) sau khi chuẩn hoá khoảng trắng; vẫn từ chối đổi từ (auditor #03 đã chứng minh fold không lọt từ đổi) | lessons.json không dấu, LLM có xu hướng thêm dấu ⇒ trích dẫn đúng nghĩa bị từ chối oan | Lật = giữ so khớp nguyên văn, chi phí: mất nhiều happy path |
| 2026-09-18 11:45 | `run_eval.py` thêm `--llm-stats`: đếm số item do Gemini thật sinh vs rơi về mock/fallback (đọc `item["provider"]` KHÔNG thêm vào schema — dùng biến đếm module-level trong `llm.py`) | Số đo CP3 phải nói rõ "bao nhiêu câu do AI thật" | — |

### Quyết định bị thay thế
- (chưa có)

## 3. Work Packages
| WP | Việc | Tầng | Handoff | Xong khi |
|---|---|---|---|---|
| WP1 | llm.py: xoay model, cache đĩa, đếm provider; validator fold dấu; eval `--llm-stats`; tests | 🟠 | `handoffs/H01_gemini-rotation-cache.md` | pytest ≥55 pass/0 skip; eval mock `21/21`; eval gemini thật ≥ 18/21 `citations_invalid=0` |
| WP2 | Video Chrome + ảnh 8 màn (Playwright) với Gemini thật qua cache | 🟢 | tay SO | file `.webm` + 8 png trong `evidence/demo/` |
| WP3 | Điền số thật vào spec §7 + đồng bộ não + bump v0.2.2 | 🟢 | tay SO / worker | `--check` exit 0 |

## 4. Checklist thực thi
- [ ] WP1 · [ ] WP2 · [ ] WP3

## 5. Câu hỏi mở (cần người)
- Key Gemini đã dán vào chat ⇒ nên xoay key sau hackathon.
