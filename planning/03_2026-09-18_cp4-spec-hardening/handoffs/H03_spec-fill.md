# H03 — WP3 Điền `spec.md` các mục trống cho CP4 (hạn 21:00 18/9)
Vai: worker THI CÔNG (đọc `.agents/skills/vai-thi-cong/SKILL.md`), tầng 🟠, họ Claude Sonnet.
Bước 0: từ root repo chạy `node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check` (chỉ đọc; ghi exit code vào report).
Thứ tự đọc: `planning/03_2026-09-18_cp4-spec-hardening/plan.md` §2 → `spec.md` → `canvas.md` → `README.md` (mục CP3/CP4 và rubric) → `codebase/flowchart.md` → `docs/backend.md` → `codebase/mock-data/quiz-day01.json` → `codebase/mock-data/golden-set.json` → `planning/0{1,2}_*/plan.md`.

## 1. Bối cảnh
`spec.md` là deliverable trung tâm; CP4 khoá "chuẩn đạt" lúc 21:00 hôm nay. Hiện §4, §4b, §6 đã có; §1, §2, §3, §5, §7, §8, §9 trống. Bằng chứng số liệu nằm ở `canvas.md` dòng 4; số đo pipeline hiện tại: `pytest` 39 pass, `run_eval.py` → `eval pass=14/14 fallback_ok=3/3 low_conf_ok=2/2 citations_invalid=0` (mock LLM). Hai worker khác đang mở rộng golden set lên ≥20 và sửa pipeline; số cuối sẽ được SO điền sau.

## 2. Phạm vi
- ĐƯỢC sửa: `spec.md` (CHỈ các mục trống; giữ NGUYÊN VĂN §4, §4b, §6 và tiêu đề) · `planning/03_*/reports/R03_spec-fill.md`.
- CẤM chạm: mọi file khác. KHÔNG `git add` gì ngoài 2 file trên. Commit ở cuối. Worker khác đang commit song song trên cùng cây: gặp `index.lock` thì đợi 5s rồi thử lại.

## 3. Việc phải làm
1. §1 User & Job: job executor + workflow (từ canvas dòng 2, 5); Core JTBD một câu KHÔNG có chữ AI/sản phẩm; Problem statement KHÔNG chữ AI (canvas dòng 3); Evidence: chép đúng số từ canvas dòng 4 (28/13.494 = 0,21%; 13.474/13.494 = 99,85%; các lượt T00261, T00804, T01545, T01587; [T04-092]). Quote nguyên văn: chỉ ghi phần canvas đã trích ("cho tôi bộ quizz liên quan", "tạo quiz ôn tập"); phần còn thiếu ghi `⏳ cần trích nguyên văn từ data pack (ngoài repo)`. CẤM bịa quote hay số.
2. §2 Impact: bảng ≥3 ứng viên (vd: A. giải thích + củng cố tại màn kết quả [CHỌN]; B. bot sinh đề quiz theo yêu cầu trong chat tutor; C. dashboard điểm yếu theo concept cho học viên/TA). Cột "bao nhiêu người · tần suất · tốn gì mỗi lần · khả thi trong 39h": dùng số từ canvas khi có, còn lại ghi rõ "ước lượng" — không giả vờ là số đo. Ứng viên loại + vì sao; ứng viên chọn + vì sao bằng số.
3. §3 Giải pháp tương tự (≥2, desk research, ghi rõ là kiến thức chung): vd Khan Academy (giải thích sau câu sai, gợi ý), Duolingo (ôn lại lỗi sai, spaced repetition), Quizlet Learn/Kahoot report. Mỗi cái: flow / đáng học / đáng né / mình khác gì (khác ở trích dẫn nguyên văn transcript + từ chối khi không có căn cứ).
4. §5 Kiểu lỗi: bảng 4 lớp chỗ khó — ① không có căn cứ trong bài giảng · ② mơ hồ nhiều nguyên nhân · ③ học viên bấm nhầm/đã hiểu · ④ LLM bịa trích dẫn hoặc câu củng cố lệch — mỗi lớp ≥2 kịch bản (tổng ≥8), mỗi kịch bản trỏ về câu thật trong `quiz-day01.json` (q01–q11) hoặc `golden-set.json`, và hành vi hệ thống mong đợi (path/nút).
5. §7 Kiểm thử: chiều chất lượng + định nghĩa kiểm chứng được (đúng path · trích dẫn nguyên văn · câu củng cố trỏ về trích dẫn · không bịa khi thiếu căn cứ); Golden set: đường dẫn `codebase/mock-data/golden-set.json`, lệnh `python backend/eval/run_eval.py`, cơ cấu ghi `⏳ N case (đang mở rộng ≥20)`; **Quality bar (khoá từ CP4):** "Đạt khi ≥90% case golden set đúng path, `citations_invalid=0`, và 0 item `no_grounding` có trích dẫn"; bảng kết quả các lượt chạy: dòng 1 = 17/9 `14/14` (mock), dòng 2 = `⏳ 18/9 sau hồ sơ #03`, dòng 3 = `⏳ Gemini thật (chưa có key)`.
6. §8: phân công có tên theo canvas dòng 7 (spec / evidence / prompt / code / demo); willing users 3 tên từ canvas; kế hoạch validation ≥5 học viên (Châm Anh điều phối, theo README nhóm); multi-prototype: ghi "không làm" nếu không có.
7. §9 Changelog: ≥3 dòng có mốc (17/9 CP2: thêm §4b/§6 + prototype; 17/9 hồ sơ #02: nối API 4 đường đi; 18/9 hồ sơ #03: điền §1–§3,§5,§7–§9, khoá quality bar).
8. Xong khi: `grep -nE '^- .*:\s*$' spec.md` chỉ còn dòng thuộc §4 (nếu có) — tức §1, §2, §7, §8 không còn dòng gạch đầu dòng kết bằng dấu hai chấm trống; `grep -c '⏳' spec.md` ghi vào report cùng danh sách từng dòng ⏳; `git diff --stat` chỉ có `spec.md` + report.

## 4. Luật
- Tiếng Việt có dấu, giữ giọng của spec hiện có. Không đổi §4/§4b/§6. Mọi con số phải có nguồn (canvas.md, README.md, eval) hoặc ghi "ước lượng"/⏳. Commit tiếng Anh, vd `docs(spec): fill user, impact, error taxonomy, testing and assignment sections for CP4`. KHÔNG push.

## 5. Tầng
🟠 (có template + nguồn; không quyết định kiến trúc).

## 6. Report
Viết `planning/03_2026-09-18_cp4-spec-hardening/reports/R03_spec-fill.md`: dòng 1 khai vai; dòng 2–4 `Handoff:`/`Base: 374230d`/`Head: <sha>`; 7 mục (lệnh + exit code · test: ghi "không áp dụng" · `git diff --stat` + SHA · bảng phân công · việc KHÔNG làm · câu hỏi mở gồm DANH SÁCH ⏳ · Tiếp theo 4 dòng). Dòng cuối: `Chờ phán quyết SO`. Trả lời cuối cho SO = nội dung report.
