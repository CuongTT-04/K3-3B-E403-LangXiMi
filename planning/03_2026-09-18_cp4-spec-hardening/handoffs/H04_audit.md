# H04 — WP4 THẨM ĐỊNH cô lập WP1 + WP2 (chỉ đọc + chạy lệnh; nhiệm vụ là LÀM ĐỎ)
Vai: worker THẨM ĐỊNH (đọc `.agents/skills/vai-thi-cong/SKILL.md` mục "THẨM ĐỊNH"), tầng 🟠, họ Claude Sonnet. KHÔNG sửa file nào ngoài report của mình.
Bước 0: từ root repo chạy `node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check` (chỉ đọc; ghi exit code).
Thứ tự đọc: `planning/03_2026-09-18_cp4-spec-hardening/plan.md` §2–§3 → `handoffs/H01_backend-diagnosis.md` → `handoffs/H02_golden-set-20.md` → code trong `codebase/backend/app/`, `codebase/backend/eval/run_eval.py`, `codebase/mock-data/golden-set.json`. CẤM đọc `reports/R01_*`, `reports/R02_*` (không thừa kế lời kể của worker).

## 1. Bối cảnh
Hai worker vừa commit trên nhánh hiện tại: WP1 (chẩn đoán dùng `chosen`, Gemini không raise + retry, validator chuẩn hoá khoảng trắng, đáp án củng cố theo chunk id, rẽ nhánh h1/h2) và WP2 (golden set ≥20, `expect_paths`, `--verbose`). Base trước worker: `374230d`.

## 2. Phạm vi
- ĐƯỢC ghi: CHỈ `planning/03_2026-09-18_cp4-spec-hardening/reports/R04_audit.md` và `evidence/wp4/*.txt`. Không sửa code, không commit code; commit riêng report + evidence của mình.
- Đo trên cây hiện tại (`git status --short` phải rỗng trước khi đo; nếu không rỗng ⇒ ghi nhận và vẫn đo, nêu rõ).

## 3. Việc phải làm
1. Chạy lại mọi "xong khi" của H01 (8 việc) và H02 (5 việc) đúng lệnh ghi trong handoff; ghi lệnh + exit code + dòng kết quả nguyên văn. `git diff --stat 374230d..HEAD` và so với phạm vi ĐƯỢC của H01+H02+H03 (spec.md, report/evidence là hợp lệ) — file ngoài phạm vi ⇒ liệt kê.
2. Tự nghĩ và thực hiện ≥3 cách phá KHÁC test hiện có, ví dụ (chọn ≥3, thêm cách của bạn): (a) submit `day01` với `chosen` là chữ không có trong options (vd "Z") ⇒ API không 500, `misconception` không rỗng; (b) `LLM_MODE=gemini GEMINI_API_KEY=fake` + monkeypatch/ngắt mạng (vd `HTTPS_PROXY=http://127.0.0.1:9`) ⇒ `POST /submit` vẫn 200 và item có shape đủ; (c) sửa TẠM một quote trong bộ nhớ (script python gọi `validator.validate` với quote bịa có khoảng trắng lạ) ⇒ vẫn fallback; (d) chứng minh bộ đo mới ĐỎ trên hệ hỏng: tạm ép `answer="A"` hoặc `expect_paths` sai trong bản copy dữ liệu tại thư mục tạm (`DATA_DIR` env) rồi chạy `run_eval.py` ⇒ pass giảm; KHÔNG sửa file trong repo; (e) `run_eval.py --verbose | wc -l` = N+1 với N = số case.
3. Đếm test: `python -m pytest backend -q` tổng/pass/fail/skip; so với 39 pass/0 skip base — không được giảm.
4. Lưu output nguyên văn từng lệnh vào `evidence/wp4/<ten>.txt`.

## 4. Luật
Chỉ đọc + chạy lệnh. Không sửa để "cho xanh". Không tin lời kể. Mọi kết luận kèm lệnh + exit code.

## 5. Tầng
🟠 toàn gói.

## 6. Report
`reports/R04_audit.md`: dòng 1 khai vai (`Vai: worker (vai-thi-cong) · loại: thẩm định · họ/model: … · Bước 0: exit … · hiểu việc: …`); dòng 2–4 `Handoff:`/`Base: 374230d`/`Head: <sha>`; 7 mục (lệnh + exit code · test tổng/pass/fail/skip · `git diff --stat` + SHA + file ngoài phạm vi · bảng phân công · các cách phá đã thử + kết quả (ĐỎ/XANH) · câu hỏi mở · Tiếp theo). Dòng cuối = ĐỀ XUẤT phán quyết `✅ DUYỆT` / `🔁 SỬA: <mục>` / `⛔ DỪNG: <vì sao>` (SO ra phán cuối). Trả lời cuối cho SO = nội dung report.
