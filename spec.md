# AI SPEC — Khắc phục hổng kiến thức từ câu hỏi trắc nghiệm sai (Adaptive Error Remediation) · Nhóm LangXiMi · Cụm C4 · Phòng E403
Hướng: [x] D — Học tập thích ứng & tương tác (Đề D2: Học từ lỗi trước)  
Loại: [x] Tối ưu tính năng có sẵn (Màn hình kết quả Quiz VLearn)  [ ] Tính năng mới

---

## §1. User & Job
- **Job executor + workflow:** Học viên vừa nộp bài một bộ quiz trắc nghiệm ôn tập trên VLearn (có $\ge 1$ câu trả lời sai), đang xem màn hình kết quả cuối bài.
- **Core JTBD:** Khắc phục ngay các lỗ hổng kiến thức từ các câu hỏi làm sai trước khi kết thúc phiên học, mà không phải tự lật tìm thủ công hàng chục trang slide.
- **Problem statement:** Sau khi nộp bài quiz, hệ thống chỉ hiển thị tổng điểm và danh sách đúng/sai chung chung; người học không biết mình hiểu nhầm ở khái niệm nào và ngại lật lại hàng trăm trang tài liệu để tìm kiếm, dẫn đến việc hổng kiến thức vẫn còn nguyên và tiếp tục lặp lại lỗi sai ở các bài kiểm tra sau.
- **Evidence (Chuẩn B — kiểm chứng qua script `eval/mine_evidence.py` trên `tutor_turns.csv`):**
  - **Số liệu mining:**
    - Tổng số lượt tương tác trong chatlog: **13.494 lượt**.
    - Trường `understanding_level` (mức độ hiểu bài) bị bỏ trống tới **13.474 / 13.494 lượt (99,85%)**.
    - Nước đi sư phạm đào sâu kiểm tra hiểu bài (`ask_probing_question`) chỉ xuất hiện **28 / 13.494 lượt (0,21%)**.
    - Nhu cầu đòi làm bài tập/quiz ôn tập củng cố kiến thức: **196 lượt** trong chatlog, nhưng hệ thống gia sư hiện tại không thể sinh câu hỏi củng cố thích ứng.
  - **≥5 quote nguyên văn + nguồn:**
    1. Turn `T00261`: *"dựa vào tài liệu này bạn hãy cho tôi bộ quizz liên quan"* $\rightarrow$ Tutor từ chối: *"Hiện tại tôi không có bộ câu hỏi kiểm tra (quiz) đính kèm trong tài liệu bài giảng..."*
    2. Turn `T00633`: *"tóm tắt những ý chính, chi tiết để tôi có thể làm quiz kahoot cuối giờ"* $\rightarrow$ Tutor từ chối do không truy xuất được dạng bài kiểm tra.
    3. Turn `T00804`: *"TẠO QUIZ ĐỂ TÔI HIỂU RÕ VÀ ÔN LẠI TOÀN BỘ SLIDE NÀY"* $\rightarrow$ Tutor chỉ trả lời lý thuyết, không sinh được bài tập tương tác.
    4. Turn `T01520`: *"hiện tại vlearn đã có quiz ôn tập ch"* $\rightarrow$ Nhu cầu thực tế học viên tìm kiếm tính năng quiz trên nền tảng.
    5. Transcript 04 (`[T04-092]`): *"Cần tính năng quiz cá nhân hoá để ôn bài theo điểm yếu, chứ làm sai xong trôi qua luôn không nhớ mình sai vì sao."*

## §2. Impact & quyết định chọn
- Bảng impact ≥3 ứng viên (bao nhiêu người · tần suất · tốn gì mỗi lần · khả thi):
- Ứng viên ĐÃ LOẠI + vì sao:
- Ứng viên CHỌN + vì sao (bằng số):

## §3. Giải pháp tương tự đã nghiên cứu
- [Sản phẩm 1]: flow / đáng học / đáng né / mình khác gì
- [Sản phẩm 2]: ...

## §4. Thiết kế
- **Lát cắt MỘT CÂU:** *Khi học viên nộp bài trắc nghiệm có câu sai trên VLearn, AI chẩn đoán quan niệm sai lầm cụ thể đằng sau phương án học viên đã chọn, trích dẫn chính xác đoạn bài giảng gốc [Txx-xxx], và tạo ngay 1 câu hỏi trắc nghiệm củng cố tương ứng để học viên luyện tập và khắc phục lỗ hổng kiến thức ngay tại màn hình kết quả.*
- **Non-goals (3 thứ KHÔNG build):**
  1. KHÔNG build hệ thống sinh đề trắc nghiệm ngẫu nhiên toàn bộ bài học.
  2. KHÔNG build tính năng chấm điểm tự luận hoặc chạy thử code trong quiz.
  3. KHÔNG build chatbot trò chuyện tự do đa chủ đề ngoài phạm vi câu hỏi bị sai.
- **Mức prototype nhắm tới:** `[x] Mock`
  - *Phần mock:* Dữ liệu bài quiz ban đầu và danh mục câu hỏi mẫu được giả lập qua fixture JSON.
  - *Phần thật (CP2):* Luồng giao diện web bấm tương tác hoàn chỉnh từ làm quiz $\rightarrow$ nộp bài $\rightarrow$ kích hoạt AI chẩn đoán $\rightarrow$ hiển thị phân tích lỗi kèm trích dẫn $\rightarrow$ làm câu hỏi củng cố $\rightarrow$ xử lý rẽ nhánh. (Tại CP3, quyết định AI lõi sẽ gọi trực tiếp Gemini API).
- **Automation:** `[x] Conditional`
  - *Lý do theo Cost-of-error:*
    - **Nếu chọn Automate hoàn toàn:** Chi phí sai sót rất đắt (high cost-of-error). Nếu AI bịa đặt tài liệu (hallucination) hoặc sinh câu hỏi củng cố sai kiến thức chuyên môn, học viên sẽ nạp sai kiến thức và trượt bài thi chính thức mà không tự phát hiện được.
    - **Nếu chọn Augment (chờ người duyệt):** Mất đi tính tức thì (immediacy) của việc giải tỏa thắc mắc ngay lúc nộp bài.
    - **Chọn Conditional (Có điều kiện):** AI chỉ tự động phân tích và sinh câu hỏi củng cố khi truy xuất được căn cứ transcript bài giảng `[Txx-xxx]` với độ tương đồng cao ($\ge 0.75$). Khi độ tự tin thấp hoặc không có nguồn căn cứ, hệ thống tự động fallback (thu hẹp phạm vi, chỉ dẫn chiếu bài học chung hoặc chuyển cho TA), đồng thời cung cấp nút "Bỏ qua" để học viên luôn làm chủ.

### §4b. Nguyên tắc đã áp dụng (HAX Toolkit / PAIR Guidebook)
| Nguyên tắc | Áp cụ thể vào đâu trong prototype |
|---|---|
| **G10: Thu hẹp phạm vi khi nghi ngờ (BẮT BUỘC)** *(HAX G10 / PAIR)* | Khi AI không tìm thấy đoạn transcript đối chiếu chắc chắn trong bài giảng ($<0.75$ match), hệ thống **tuyệt đối không bịa câu hỏi mới**, mà tự động thu hẹp phạm vi: chỉ hiển thị phần tóm tắt khái niệm chung và trỏ về bài học số X, kèm tùy chọn "Nhờ TA giải đáp". |
| **G8: Gạt bỏ dễ dàng** *(HAX G8)* | Ở mỗi khối câu hỏi củng cố do AI sinh, luôn có nút **"Bỏ qua câu củng cố này"** hoặc **"Kết thúc bài ôn"** rõ ràng (1 click), giúp học viên không bị cưỡng ép làm thêm bài nếu đang vội. |
| **G9: Hỗ trợ sửa lỗi hiệu quả** *(HAX G9)* | Bên cạnh phần chẩn đoán của AI, cung cấp nút **"Tôi chọn nhầm chứ không phải hiểu sai"** để học viên điều chỉnh nhận định của AI, ngăn AI đưa ra câu hỏi củng cố không cần thiết. |
| **G11: Giải thích rõ lý do** *(HAX G11 / PAIR Explainability)* | Mọi kết quả giải thích lỗi sai đều gắn nhãn nguồn gốc rõ ràng (Badge `[T01-042]` tương ứng với phút/dòng trong bài giảng) và giải thích logic tương phản: *"Bạn chọn A (Fine-tuning), nhưng bài giảng chỉ ra rằng..."*. |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8) [bảng theo guide §2.5]

## §6. Bốn đường đi của trải nghiệm (User Journey Paths)
1. **Happy path (Đường thuận lợi - Tự tin cao):**
   - Học viên chọn sai câu hỏi số 2 về *"RAG vs Fine-tuning"*.
   - AI phát hiện chọn nhầm phương án C (Fine-tuning khi cần cập nhật dữ liệu hàng ngày).
   - Hệ thống chẩn đoán: Hiểu nhầm về chi phí cập nhật kiến thức.
   - Trích dẫn ngay Transcript `[T01-042]`: *"Fine-tuning tốn kém chi phí tính toán và không phù hợp với dữ liệu biến động liên tục theo ngày; RAG mới là giải pháp tối ưu..."*.
   - AI sinh ngay 1 câu hỏi củng cố dạng tình huống thực tế. Học viên bấm chọn, đúng $\rightarrow$ Khắc phục thành công.
2. **Low-confidence path (Đường tự tin thấp - Lớp ②):**
   - AI không chắc chắn học viên sai do đọc thiếu đề hay sai do bản chất kiến thức.
   - Giao diện hiển thị: *"Hệ thống nhận thấy có 2 nguyên nhân bạn chọn đáp án này: (1) Nhầm lẫn định nghĩa; (2) Đọc lướt bỏ sót từ 'KHÔNG'. Bạn gặp trường hợp nào?"* $\rightarrow$ Học viên bấm chọn để AI đưa ra câu củng cố đúng trọng tâm.
3. **Failure / No-grounding path (Đường không căn cứ - Lớp ①):**
   - Không tìm thấy đoạn transcript tương ứng trong bài giảng với độ tương đồng đủ cao.
   - Hệ thống hiển thị: *"Không tìm thấy trích dẫn bài giảng chính thức để đối chiếu câu hỏi này. Để đảm bảo tính chính xác, AI không tự sinh câu hỏi mới."* Kèm nút: *"Gửi câu hỏi này cho TA hỗ trợ"*.
4. **Correction path (Đường người dùng can thiệp sửa):**
   - Học viên bấm nút *"Tôi chỉ bấm nhầm nút chứ đã nắm rõ kiến thức này"* $\rightarrow$ AI ghi nhận, hủy khối câu hỏi củng cố và cập nhật lại trạng thái hoàn thành.

## §7. Kiểm thử & Đánh giá chất lượng (Eval)
- **Chiều chất lượng + định nghĩa kiểm chứng được:**
  1. **D1 · Diagnosis Accuracy:** PASS nếu AI chỉ ra đúng giả định/concept sai của lựa chọn; FAIL nếu chỉ phán chung chung "bạn làm sai rồi".
  2. **D2 · Citation Groundedness (Zero-tolerance):** PASS nếu trích dẫn `[Txx-xxx]` có thật trong transcript và đối chiếu đúng kiến thức; FAIL nếu bịa trích dẫn ảo (Hallucination).
  3. **D3 · Reinforcement Question Quality:** PASS nếu câu hỏi củng cố mới có tình huống thực tế, đủ 4 lựa chọn, duy nhất 1 đáp án đúng, không lộ đáp án trong đề.
  4. **D4 · Tone & Graceful Fallback:** PASS nếu giọng văn nâng đỡ sư phạm; khi gặp case thiếu nguồn (Lớp ①) hoặc ngoài phạm vi (Lớp ③) phải từ chối lịch sự và hướng dẫn xem tài liệu.
- **Golden set:** Bộ 20 case chuẩn hóa lưu tại `eval/golden_set.json` (chi tiết tiêu chí tại `eval/quality_bar.md`):
  - 8 case phủ đủ 4 lớp chỗ khó (Lớp ① Nguồn sự thật, Lớp ② Mơ hồ, Lớp ③ Ngoài phạm vi, Lớp ④ Hiểu nhầm domain tinh tế).
  - 10 case thường (Happy path bám sát bộ câu hỏi Day 01).
  - 2 case hiếm (Sai toàn bộ 4/4 câu hoặc Đúng toàn bộ 4/4 câu).
  - $\ge 10$ case trích xuất và phát triển trực tiếp từ chatlog thật.
- **Quality bar (chốt cứng trước CP4, giữ nguyên sau đó):**
  - **Đạt khi $\ge 80\%$ (16/20 case)** vượt qua toàn bộ 4 chiều chất lượng.
  - **$100\%$ (20/20 case)** đạt tiêu chuẩn **Citation Groundedness** (Tuyệt đối không bịa số hiệu trích dẫn).
  - **$100\%$ case ngoài phạm vi** từ chối thành công và giữ đúng vai trò sư phạm.
- **Kết quả các lượt chạy (Chi tiết tại [`codebase/eval/first_eval_report.md`](codebase/eval/first_eval_report.md)):**

| Lượt chạy | Ngày đo | Mô hình / Phiên bản | Tỷ lệ Đạt tổng | Grounded Citation | Ghi chú / Nguyên nhân chính |
|---|---|---|---|---|---|
| Lượt 1 (Baseline CP3) | 18/9 - 15:49 | GPT-4o-mini (OpenRouter API) + RAG Pipeline | **20/20 (100.0%)** | **100% (0 bịa đặt)** | Đạt Quality Bar ($\ge 80\%$). Fallback chuẩn 5/5, Low-confidence 2/2, ghi vết tại `eval_run_1789721355.json` |
| Lượt 2 (CP4 Freeze) | 18/9 - 16:00 | GPT-4o-mini + Parallel ThreadPool | **20/20 (100.0%)** | **100% (0 bịa đặt)** | Khóa cứng Quality Bar, độ trễ tối ưu ~3.5s - 4.5s cho luồng nhiều câu sai |

## §8. Phân công & kế hoạch
- Phân công có tên: spec / evidence / prompt / code / demo
- Willing users (≥2 tên) + kế hoạch vòng validation *(bonus, nếu làm)*:
- Multi-prototype (nếu làm): trục khác biệt của ≥2 phương án + lý do chọn:

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
```
