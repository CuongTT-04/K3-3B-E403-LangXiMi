# R03 — Report WP3: điền spec.md cho CP4

Vai: worker (vai-thi-cong) · loại: THI CÔNG · họ/model: Claude Sonnet · Bước 0: exit 0 · hiểu việc: chỉ điền các mục trống ở `spec.md` (§1, §2, §3, §5, §7, §8, §9), giữ NGUYÊN VĂN §4/§4b/§6 và mọi file khác; mọi số liệu phải có nguồn trong repo (canvas.md/README.md/docs/backend.md/mock-data) hoặc đánh dấu "ước lượng"/⏳, cấm bịa; xong khi `grep -nE '^- .*:\s*$' spec.md` không còn dòng nào (ngoài §4 nếu có), `⏳` được liệt kê đủ, và `git diff --stat` so với base chỉ có `spec.md` + report này.

Handoff: `planning/03_2026-09-18_cp4-spec-hardening/handoffs/H03_spec-fill.md`
Base: 374230d
Head: 5587e6b6edcd4f8a75c2b8b485fa6b05f523f781 (spec.md)

## 1. Lệnh + exit code nguyên văn
- `node ../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check` → `EXITCODE=0` ("NÃO ĐÃ OK — KHÔNG CẦN NÂNG CẤP THÊM!")
- `grep -nE '^- .*:\s*$' spec.md` → không khớp dòng nào, `exit=1`
- `grep -c '⏳' spec.md` → `7`
- `git commit -m "..." -- spec.md` → exit 0, commit `5587e6b`

**Sự cố giữa chừng (đã tự sửa):** Lần `git commit` đầu tiên (không kèm pathspec) đã vô tình gom cả các file đang được worker WP2 stage sẵn (`codebase/backend/eval/run_eval.py`, `test_golden_set_eval.py`, `test_mockdata.py`, `codebase/mock-data/golden-set.json`, `evidence/wp2/*`, `reports/R02_golden-set-20.md`) vào chung 1 commit với `spec.md`. Phát hiện ngay qua `git show --stat HEAD`. Đã sửa bằng `git reset --soft HEAD^` (không mất dữ liệu, chỉ gỡ commit, giữ nguyên trạng thái stage) rồi commit lại đúng cú pháp `git commit -m "..." -- spec.md` để CHỈ commit `spec.md`, trả lại toàn bộ file của WP2 về trạng thái đã stage như trước. Đã xác nhận bằng `git show --stat HEAD` (chỉ 1 file `spec.md`) và `git status --short` (các file WP2 vẫn ở cột stage `M`/`A`, không bị mất).

## 2. Test
Không áp dụng — WP3 chỉ sửa nội dung Markdown (`spec.md`), không có bộ test tự động cho spec.

## 3. `git diff --stat` + SHA
```
git diff --stat 374230d 5587e6b -- spec.md
 spec.md | 83 +++++++++++++++++++++++++++++++++++++++++++++++++++--------------
 1 file changed, 66 insertions(+), 17 deletions(-)
```
Base: `374230d` · Head (commit chứa nội dung): `5587e6b`. Report này (`R03_spec-fill.md`) được `git add` + commit riêng (pathspec) ngay sau, không gộp vào commit trên và không đụng file nào khác.

## 4. Bảng phân công (gói → tầng → họ/model)
| Gói | Tầng | Họ/model |
|---|---|---|
| WP3 (điền spec.md — nhiệm vụ của report này) | 🟠 | Claude Sonnet |
| WP1 (backend: `chosen`, Gemini, validator) | 🟠 | worker khác (song song, không rõ danh tính từ handoff) |
| WP2 (golden set ≥20 case) | 🟠 | worker khác (song song — đã thấy file stage sẵn: `run_eval.py`, `test_golden_set_eval.py`, `test_mockdata.py`, `golden-set.json`, `R02_golden-set-20.md`) |
| WP4 (thẩm định cô lập) | 🟠 | chưa chạy (theo `plan.md` §3) |
| WP5 (đồng bộ não) | 🟢 | tay SO |

## 5. Việc KHÔNG làm + lý do
- Không sửa §4, §4b, §6 của `spec.md` — luật cấm tường minh trong handoff, đã đối chiếu bằng `git diff` để xác nhận không dòng nào trong 3 mục này bị đổi.
- Không chạm `codebase/backend/**`, `codebase/mock-data/golden-set.json`, `docs/backend.md` — ngoài phạm vi WP3, thuộc WP1/WP2 đang chạy song song trên cùng cây.
- Không tự quyết ngưỡng Quality bar — chép nguyên văn "Đạt khi ≥90% case golden set đúng path, `citations_invalid=0`, và 0 item `no_grounding` có trích dẫn" từ quyết định đã khoá trong `plan.md` §2, không tự đổi số.
- Không bịa 4 quote còn thiếu (`T00804`, `T01545`, `T01587`, `[T04-092]`) — canvas.md chỉ trích một phần ("tạo quiz ôn tập", không có câu đầy đủ cho T04-092); đánh dấu ⏳ thay vì suy diễn nguyên văn.
- Không điền số N cuối cùng cho golden set ≥20 case hay bảng kết quả dòng 2/3 ở §7 — số liệu thật do WP1/WP2 tạo ra, SO điền sau; đã ghi ⏳ đúng như handoff yêu cầu.
- Không đụng dòng "```" thừa cuối §9 gốc (artifact có sẵn trong template, không phải "mục trống") — chỉ chèn 3 dòng changelog phía trước nó.

## 6. Câu hỏi mở — danh sách ⏳ (7 chỗ, `grep -n '⏳' spec.md`)
1. §1 Evidence, quote 2: `T00804` — *"tạo quiz ôn tập"* (tutor từ chối) — ⏳ cần trích nguyên văn đầy đủ từ data pack ngoài repo (`tutor_turns.csv`).
2. §1 Evidence, quote 3: `T01545` — cùng nội dung, cùng lý do ⏳.
3. §1 Evidence, quote 4: `T01587` — cùng nội dung, cùng lý do ⏳.
4. §1 Evidence, quote 5: `[T04-092]` (`transcript-04-clean.md`) — chỉ có tóm tắt trong canvas, chưa có câu nguyên văn — ⏳ cần trích từ data pack ngoài repo.
5. §7 Golden set: cơ cấu hiện 14 case (8 happy/2 low_confidence/4 no_grounding) — ⏳ N case (đang mở rộng ≥20, WP2 đang chạy song song, đã thấy file stage).
6. §7 bảng kết quả dòng 2: ⏳ 18/9 sau hồ sơ #03 — chờ WP2 chạy `run_eval.py` xong, SO điền số cuối.
7. §7 bảng kết quả dòng 3: ⏳ Gemini thật (chưa có key) — chờ `GEMINI_API_KEY` (câu hỏi mở đã có ở `plan.md` §5).

## 7. Tiếp theo
1. SO điền số N thật (≥20 case) vào §7 sau khi WP2 hoàn tất `run_eval.py`, thay dòng ⏳ thứ 5–6.
2. Cần người có quyền truy cập `data/vlearn-pack/` trích nguyên văn 4 quote còn thiếu (T00804, T01545, T01587, [T04-092]) để thay ⏳ ở §1.
3. Khi có `GEMINI_API_KEY`, chạy `LLM_MODE=gemini` và điền dòng 3 bảng kết quả §7.
4. WP4 (thẩm định) nên đối chiếu lại §5 sau khi golden set mở rộng ≥20 case, phòng khi case tham chiếu (`q09`–`q11`, case-10…14) đổi số thứ tự.

Chờ phán quyết SO.
