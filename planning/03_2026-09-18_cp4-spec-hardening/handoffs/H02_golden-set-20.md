# H02 — WP2 Golden set ≥20 case + `expect_paths` + `run_eval.py --verbose`
Vai: worker THI CÔNG (đọc `.agents/skills/vai-thi-cong/SKILL.md`), tầng 🟠, họ Claude Sonnet.
Bước 0: từ root repo chạy `node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check` (chỉ đọc; ghi exit code vào report).
Thứ tự đọc: `planning/03_2026-09-18_cp4-spec-hardening/plan.md` §2 → `docs/backend.md` (mục 4 đường đi) → `codebase/mock-data/golden-set.json` → `codebase/backend/eval/run_eval.py` → `codebase/backend/tests/{test_mockdata,test_golden_set_eval}.py`.

## 1. Bối cảnh
Golden set hiện 14 case (9 happy, 2 low_confidence, 3 no_grounding), mỗi case một `expect_path` áp cho MỌI item. Spec §7 (CP4, hạn 21:00 hôm nay) đòi ≥20 case. Quiz `day01` có 11 câu: q01–q08 happy (source_ids thật), q09/q11 low_confidence (source_ids giả, overlap ~0.667), q10 no_grounding (concept không có trong lessons). Câu hỏi lạ (`qx-…`) ⇒ no_grounding.

## 2. Phạm vi
- ĐƯỢC sửa: `codebase/mock-data/golden-set.json` · `codebase/backend/eval/run_eval.py` · `codebase/backend/tests/test_mockdata.py` · `codebase/backend/tests/test_golden_set_eval.py` · `planning/03_*/reports/R02_golden-set-20.md` · `planning/03_*/evidence/wp2/*.txt`.
- CẤM chạm: `codebase/mock-data/{lessons,quiz-day01}.json` · `codebase/backend/app/**` · `codebase/frontend/**` · `spec.md` · `docs/**` · `brain4agent/**`.
- Một worker khác đang sửa `app/*.py` và `tests/{test_service,test_validator,test_llm_gemini,test_api}.py` song song trên cùng cây — KHÔNG đụng; `git add` TƯỜNG MINH từng file của mình; commit ở CUỐI; gặp `index.lock` thì đợi 5s rồi thử lại. Nếu pytest đỏ ở test KHÔNG thuộc phạm vi bạn (do worker kia đang dở) ⇒ ghi vào report, KHÔNG sửa, vẫn commit nếu test trong phạm vi bạn xanh.

## 3. Việc phải làm
1. Mở rộng `golden-set.json` lên ≥20 case, đánh số tiếp `case-15…`. Cơ cấu tối thiểu: ≥10 happy · ≥3 low_confidence · ≥4 no_grounding · ≥3 case HỖN HỢP nhiều câu thuộc ≥2 path khác nhau (vd `q01+q10`, `q09+q03`, `q02+q10+q11`, tất cả 11 câu). Mỗi case giữ đủ field cũ (`case_id, wrong_question_ids, expected_concepts, expected_source_ids_any, expect_fallback, expect_path`). Case hỗn hợp: thêm `expect_paths` = map qid→path cho TỪNG câu; `expect_path` của case hỗn hợp = `"mixed"`; `expect_fallback` = true nếu có ≥1 câu no_grounding.
   Xong khi: `python -c "import json;g=json.load(open('codebase/mock-data/golden-set.json',encoding='utf-8'));print(len(g))"` ≥ 20.
2. `run_eval.py::_check_case`: nếu case có `expect_paths` ⇒ `path_ok = all(item["path"] == expect_paths[item["question_id"]])` cho mọi item, item happy phải có ≥1 citation, item no_grounding phải `citations == []`, item low_confidence phải có đúng 2 hypotheses; `passed = path_ok`. Case không có `expect_paths` giữ nguyên logic cũ. Bộ đếm `fallback_ok/fallback_total` và `low_conf_ok/low_conf_total` đếm THEO ITEM cho case hỗn hợp (mỗi item no_grounding/low_confidence là 1 đơn vị) và giữ nguyên cách đếm theo case cho case đơn. Dòng cuối GIỮ NGUYÊN định dạng `eval pass=N/M fallback_ok=K/L low_conf_ok=P/Q citations_invalid=0`.
   Xong khi: `python backend/eval/run_eval.py` (từ `codebase/`) in dòng cuối `pass=N/N` với N≥20, `citations_invalid=0`, exit 0.
3. Cờ `--verbose`: in trước dòng cuối mỗi case một dòng `case-XX expect=<path> got=<path1,path2,…> passed=<True/False>`. Không cờ ⇒ chỉ một dòng như cũ.
   Xong khi: `python backend/eval/run_eval.py --verbose | wc -l` = N+1.
4. `test_mockdata.py`: `test_golden_set_schema_valid` chấp nhận `expect_path == "mixed"` khi có `expect_paths`; thêm assert `len(golden) >= 20`; `test_golden_set_expect_path_consistent_with_fallback` xử lý case hỗn hợp (fallback == any(path==no_grounding)). `test_golden_set_eval.py`: thêm test `--verbose` in N+1 dòng (gọi hàm, không spawn process nếu được).
   Xong khi: `python -m pytest backend/tests/test_mockdata.py backend/tests/test_golden_set_eval.py -q` exit 0, 0 skip.
5. Cổng đo cuối: `python -m pytest backend -q` (ghi kết quả dù test ngoài phạm vi đỏ) · `python backend/eval/run_eval.py --verbose`. Lưu nguyên văn vào `evidence/wp2/pytest.txt`, `evidence/wp2/eval.txt`.

## 4. Luật
- Không sửa `lessons.json`/`quiz-day01.json` (frontend hardcode đáp án autofill). Không `git add -A`. Commit 1 lần tiếng Anh, vd `test(eval): grow golden set to 20 cases with mixed-path expectations and --verbose`. KHÔNG push.
- Số kỳ vọng trong case phải suy từ data thật (đọc `quiz-day01.json`, `lessons.json`), không đoán.

## 5. Tầng
Cả gói 🟠.

## 6. Report
Viết `planning/03_2026-09-18_cp4-spec-hardening/reports/R02_golden-set-20.md`: dòng 1 khai vai (`Vai: worker (vai-thi-cong) · loại: thi công · họ/model: … · Bước 0: exit … · hiểu việc: …`); dòng 2–4 `Handoff:`/`Base: 374230d`/`Head: <sha>`; 7 mục: lệnh + exit code · test tổng/pass/fail/skip · `git diff --stat` + SHA · bảng phân công · việc KHÔNG làm · câu hỏi mở · Tiếp theo 4 dòng. Kèm bảng cơ cấu case (happy/low/no/mixed = ?). Dòng cuối: `Chờ phán quyết SO`. Trả lời cuối cho SO = nội dung report.
