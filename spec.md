# AI SPEC — Khắc phục hổng kiến thức từ câu hỏi trắc nghiệm sai (Adaptive Error Remediation) · Nhóm LangXiMi · Cụm C4 · Phòng E403
Hướng: [x] D — Học tập thích ứng & tương tác (Đề D2: Học từ lỗi trước)  
Loại: [x] Tối ưu tính năng có sẵn (Màn hình kết quả Quiz VLearn)  [ ] Tính năng mới

---

## §1. User & Job
- Job executor + workflow (đính kèm worksheet JTBD / ảnh sơ đồ):
- Core JTBD (không tên sản phẩm/AI trong câu):
- Problem statement (KHÔNG chữ AI):
- Evidence (chuẩn A và/hoặc B — log đầy đủ trong repo):
  - Số liệu mining / kết quả khảo sát (n = ?, % xác nhận):
  - ≥5 quote/ví dụ nguyên văn + nguồn:

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

# §7. Kiểm thử
- Chiều chất lượng + định nghĩa kiểm chứng được:
- Golden set (≥20 case theo cơ cấu trong guide §2.6, file trong eval/):
- Quality bar (chốt từ hạn chốt spec của khoá, giữ nguyên sau đó): "Đạt khi ≥ ___% qua bộ, và ___"
- Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6):

## §8. Phân công & kế hoạch
- Phân công có tên: spec / evidence / prompt / code / demo
- Willing users (≥2 tên) + kế hoạch vòng validation *(bonus, nếu làm)*:
- Multi-prototype (nếu làm): trục khác biệt của ≥2 phương án + lý do chọn:

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
```
