Vai: worker (vai-thi-cong) · loại: thi công · họ/model: Claude Sonnet · Bước 0: exit 0 · hiểu việc: mở rộng `golden-set.json` từ 14 lên 21 case (≥10 happy/≥3 low_confidence/≥4 no_grounding/≥3 mixed, số liệu suy từ chạy `service.remediate` thật trên `quiz-day01.json`+`lessons.json`, không đoán); sửa `run_eval.py::_check_case` để case có `expect_paths` chấm theo từng item (path đúng + happy≥1 citation + no_grounding citations=[] + low_confidence đúng 2 hypotheses) và đếm `fallback_ok/low_conf_ok` theo item cho case hỗn hợp, giữ đếm theo case cho case đơn, dòng cuối giữ nguyên định dạng; thêm `--verbose` in 1 dòng/case rồi dòng tổng; cập nhật `test_mockdata.py`/`test_golden_set_eval.py` khớp; phạm vi chỉ 4 file (`golden-set.json`, `run_eval.py`, `test_mockdata.py`, `test_golden_set_eval.py`) + report/evidence; cấm chạm `lessons.json`/`quiz-day01.json`/`app/**`/`frontend/**`/`spec.md`/`docs/**`.
Handoff: planning/03_2026-09-18_cp4-spec-hardening/handoffs/H02_golden-set-20.md
Base: 374230daa56ab45db532af3d044c434c4d8d2ccd
Head: 37569ddbd4a6206190567fc20bcfb14d1e3e2d51

## 1. Lệnh + exit code (nguyên văn)
- `node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check` → `NÃO ĐÃ OK — KHÔNG CẦN NÂNG CẤP THÊM!` → exit 0
- `python -m pytest backend/tests/test_mockdata.py backend/tests/test_golden_set_eval.py -q` → `8 passed in 0.37s` → exit 0
- `python -m pytest backend -q` → `49 passed, 1 warning in 3.21s` → exit 0
- `python backend/eval/run_eval.py` → `eval pass=21/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0` → exit 0
- `python backend/eval/run_eval.py --verbose` → 21 dòng case + 1 dòng tổng = 22 dòng (`| wc -l` → `22`, N=21 nên N+1=22 khớp) → exit 0

## 2. Test tổng/pass/fail/skip
- Phạm vi của tôi (`test_mockdata.py` + `test_golden_set_eval.py`): 8 tổng, 8 pass, 0 fail, 0 skip.
- Toàn `backend -q` (bao gồm việc của worker WP1 song song): 49 tổng, 49 pass, 0 fail, 0 skip, 1 warning (DeprecationWarning `anyio.abc.BlockingPortal` trong `starlette/testclient.py`, không phải do thay đổi của tôi).

## 3. `git diff --stat` + SHA
```
codebase/backend/eval/run_eval.py              | 117 +++++++++++++++++++++----
codebase/backend/tests/test_golden_set_eval.py |  27 +++++-
codebase/backend/tests/test_mockdata.py        |  26 +++++-
codebase/mock-data/golden-set.json             |  94 ++++++++++++++++++++
4 files changed, 244 insertions(+), 20 deletions(-)
```
Base: `374230daa56ab45db532af3d044c434c4d8d2ccd` · Head (commit của tôi): `37569ddbd4a6206190567fc20bcfb14d1e3e2d51`.

## 4. Bảng phân công
| Gói | Tầng | Họ/model | Ghi chú |
|---|---|---|---|
| WP2 (của tôi) | 🟠 | Claude Sonnet | `golden-set.json` + `run_eval.py` + `test_mockdata.py` + `test_golden_set_eval.py`, commit riêng |
| WP1 (worker khác, song song) | 🟠 | không rõ (không thuộc phạm vi tôi) | `app/*.py` + `tests/{test_service,test_validator,test_llm_gemini}.py` — đã thấy thay đổi khi tôi chạy `git status`; `pytest backend -q` toàn bộ vẫn 49/49 xanh nên không có xung đột lộ ra |
| WP3 (worker khác, song song) | 🟠 | không rõ (không thuộc phạm vi tôi) | `spec.md` — đã thấy thay đổi khi `git status`, không đụng |

## 5. Việc KHÔNG làm + lý do
- Không sửa `codebase/mock-data/{lessons,quiz-day01}.json` — cấm tường minh trong handoff (frontend hardcode đáp án autofill).
- Không đụng `codebase/backend/app/**`, `tests/{test_service,test_validator,test_llm_gemini,test_api}.py`, `codebase/frontend/**`, `spec.md`, `docs/**`, `brain4agent/**` — ngoài phạm vi WP2, thuộc worker khác đang chạy song song.
- Không tự tuyên bố ĐẠT cổng nghiệm thu CP4 — đó là việc của WP4 (thẩm định cô lập) và SO.

## 6. Câu hỏi cần người (câu hỏi mở)
- Không phát sinh câu hỏi mở mới. Toàn bộ số liệu case mới (path, citations, hypotheses) đều lấy từ script chạy trực tiếp `app.service.remediate` trên dữ liệu thật (`quiz-day01.json` + `lessons.json`), không suy đoán.

## Bảng cơ cấu case (golden-set.json, 21 case)
| Loại | Số case | case_id |
|---|---|---|
| happy | 10 | case-01..09, case-15 |
| low_confidence | 3 | case-12, case-13, case-16 |
| no_grounding | 4 | case-10, case-11, case-14, case-17 |
| mixed (`expect_paths`) | 4 | case-18 (q01+q10), case-19 (q09+q03), case-20 (q02+q10+q11), case-21 (toàn bộ 11 câu day01) |
| **Tổng** | **21** | |

## Tiếp theo
1. WP4 thẩm định cô lập cần chạy lại `python -m pytest backend/tests/test_mockdata.py backend/tests/test_golden_set_eval.py -q` và `python backend/eval/run_eval.py --verbose` độc lập, tự nghĩ ≥3 cách phá (vd sửa `expect_paths` sai lệch, xoá field `hypotheses`, đổi thứ tự `wrong_question_ids`) để chứng minh bộ đo đỏ đúng lúc.
2. SO gộp kết quả WP1+WP2+WP3 trước cổng nghiệm thu CP4 21:00; `python -m pytest backend -q` hiện 49/49 xanh cả 2 gói song song.
3. Evidence đã lưu tại `planning/03_2026-09-18_cp4-spec-hardening/evidence/wp2/{pytest.txt,eval.txt}` (nguyên văn, có dòng `exit=0`).
4. Không có việc tồn đọng nào trong phạm vi WP2.

Chờ phán quyết SO.
