# AI SPEC — Khắc phục hổng kiến thức từ câu hỏi trắc nghiệm sai (Adaptive Error Remediation) · Nhóm LangXiMi · Cụm C4 · Phòng E403
Hướng: [x] D — Học tập thích ứng & tương tác (Đề D2: Học từ lỗi trước)  
Loại: [x] Tối ưu tính năng có sẵn (Màn hình kết quả Quiz VLearn)  [ ] Tính năng mới

---

## §1. User & Job
- **Job executor + workflow:** Học viên đang tự học / ôn tập trên hệ thống VLearn qua các bộ mini-quiz trắc nghiệm sau bài giảng.
  - *Workflow hiện tại:* Làm quiz $\rightarrow$ Bấm nộp bài $\rightarrow$ Nhìn tổng điểm và danh sách câu đúng/sai $\rightarrow$ Thấy câu sai nhưng ngại mở lại hàng chục trang slide hoặc video dài để tra cứu $\rightarrow$ Rời màn hình kết quả với lỗ hổng kiến thức chưa được lấp.
- **Core JTBD:** *"Khi tôi làm sai các câu hỏi trắc nghiệm trong bài ôn tập, tôi muốn hiểu ngay nguyên nhân cốt lõi mình hiểu nhầm và được củng cố ngay tại chỗ với tài liệu chuẩn xác, để tôi tự tin không tái phạm sai lầm đó trong bài thi chính thức."* (Tuyệt đối không có tên sản phẩm/AI trong câu).
- **Problem statement:** Học viên sau khi nộp bài trắc nghiệm bị sai không nhận được giải thích sâu về sự hiểu nhầm của bản thân và phải tốn 15-30 phút tự tìm kiếm lại trong bài giảng, dẫn đến việc bỏ qua lỗi sai và tiếp tục lặp lại lỗ hổng kiến thức trong các bài đánh giá quan trọng.
- **Evidence (chuẩn A và/hoặc B — log đầy đủ trong repo):**
  - *Số liệu mining từ `tutor_turns.csv`:*
    - Hành vi sư phạm kiểm tra và củng cố hiểu bài (`ask_probing_question`) của tutor hiện tại gần như biến mất: chỉ xuất hiện **28 / 13.494 lượt (0,21%)**.
    - Cột `understanding_level` bị bỏ trống tới **13.474 / 13.494 lượt (99,85%)** $\rightarrow$ Hệ thống hiện tại hoàn toàn "mù" trước tình trạng hiểu bài của học viên.
    - Học viên có nhu cầu ôn tập và kiểm tra kiến thức rất lớn nhưng trợ lý từ chối: Lượt `T00261` (*"cho tôi bộ quizz liên quan"*) $\rightarrow$ tutor từ chối sinh; các lượt `T00804`, `T01545`, `T01587` (*"tạo quiz ôn tập"*) $\rightarrow$ tutor đều từ chối hoặc trả lời chung chung.
  - *Bằng chứng định tính (Quotes nguyên văn):*
    1. `transcript-04-clean.md` `[T04-092]`: *"Sau khi làm Kahoot xong em sai câu RAG vs Fine-tuning mà không biết tại sao sai, lật lại slide tìm thì ngại quá..."*
    2. `tutor_turns.csv` `[T00261]`: *"Bạn có thể tạo cho mình một bài quiz ngắn để kiểm tra xem mình nắm chắc phần LangChain Agents chưa?"*
    3. Phỏng vấn nhanh học viên tại lớp (Willing user - Văn Quốc Dũng): *"Làm quiz xong thấy chữ Đỏ (Sai) là tụt mood, muốn biết ngay câu đó mình nhầm chỗ nào chứ đọc giải thích kiểu 'A đúng vì A đúng' thì không giải quyết được gì."*
    4. Phỏng vấn nhanh học viên (Willing user - Nguyễn Đức Thịnh): *"Muốn có 1 câu hỏi tương tự để bấm làm lại ngay xem mình đã thực sự hiểu chưa."*
    5. Phỏng vấn nhanh học viên (Willing user - Lương Sỹ Khánh): *"Nếu AI giải thích thì phải chỉ rõ cho mình xem lại ở phút thứ mấy hoặc trang slide nào, chứ AI hay chém gió lung tung."*

---

## §2. Impact & quyết định chọn
- **Bảng impact 3 ứng viên:**
  | Ứng viên | Đối tượng & Quy mô | Tần suất | Chi phí tổn thất mỗi lần | Tính khả thi trong 39h |
  |---|---|---|---|---|
  | **1. Trợ lý chấm điểm tự luận code** | Toàn bộ học viên làm bài tập thực hành lớn | 1-2 lần/tuần | Mất 2-3 ngày chờ TA chấm; sửa bài tốn thời gian | Thấp (phải chạy sandbox code, nhiều ngôn ngữ) |
  | **2. AI sinh toàn bộ bài quiz mới từ slide** | Giảng viên / Học viên tự luyện | Mỗi buổi học | Tốn 30p soạn đề; câu hỏi dễ bị ngô nghê nếu không kiểm duyệt | Trung bình (cần human-in-the-loop duyệt đề) |
  | **3. Khắc phục lỗi sai ngay tại màn hình kết quả Quiz (CHỌN)** | Toàn bộ học viên làm quiz sau mỗi bài giảng (~200 học viên) | Sau mỗi bài quiz (hàng ngày) | Tốn 15-30p tra cứu thủ công, 70% bỏ qua lỗi sai dẫn đến trượt kiểm tra | **Cao** (Lát cắt hẹp, dữ liệu bài giảng rõ ràng, tác động tức thì) |

- **Ứng viên ĐÃ LOẠI:** Ứng viên 1 (Chấm code) bị loại do độ phức tạp kỹ thuật vượt quá khung thời gian 39 giờ và chi phí sai sót (cost-of-error) cao khi chấm sai code học viên. Ứng viên 2 bị loại do giá trị mang lại chỉ dừng ở việc "tạo thêm bài tập" chứ không giải quyết tận gốc nỗi đau "hổng kiến thức từ câu sai".
- **Ứng viên CHỌN + vì sao:** Chọn Ứng viên 3 vì tác động trực tiếp vào khoảnh khắc "dễ tiếp thu nhất" của học viên (ngay khi vừa làm sai và tò mò muốn biết đáp án đúng). Tiết kiệm ~20 phút tra cứu/học viên/bài quiz $\times$ 200 học viên = 4.000 phút học tập hiệu quả mỗi ngày.

---

## §3. Giải pháp tương tự đã nghiên cứu
- **Duolingo:** Khi trả lời sai, Duolingo lập tức cho làm lại vào cuối bài (spaced repetition ngắn hạn). *Đáng học:* Cơ chế củng cố ngay trong phiên học. *Đáng né:* Chỉ hiển thị đáp án đúng mà không giải thích logic tại sao học viên lại chọn đáp án sai đó. *Mình khác:* AI chẩn đoán chính xác khái niệm bị hiểu nhầm và trích dẫn bài giảng gốc `[Txx-xxx]`.
- **Quizlet / Khan Academy:** Cung cấp giải thích cố định (hardcoded explanation). *Đáng né:* Giải thích chung chung cho mọi người dùng, không cá nhân hóa theo phương án cụ thể mà học viên đã chọn nhầm.

---

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

---

## §5. Kiểu lỗi — 4 lớp chỗ khó & kịch bản kiểm thử
| Lớp chỗ khó | Kịch bản cụ thể | Hành vi mong muốn của hệ thống |
|---|---|---|
| **Lớp ①: Không có căn cứ (No-grounding)** | Câu hỏi về công cụ mới không có trong transcript bài giảng Day 01 | Bật fallback G10: Báo chưa có dữ liệu đối chiếu, không bịa câu hỏi, dẫn link tới tài liệu tham khảo chính thức. |
| **Lớp ②: Độ tự tin thấp (Ambiguity)** | Học viên chọn đáp án sai nhưng phương án đó có thể do 2 nguyên nhân khác nhau | Hiển thị 2 khả năng chẩn đoán: *"Có phải bạn đang nhầm giữa X và Y?"* để học viên tự chọn trước khi tạo câu hỏi củng cố. |
| **Lớp ③: Ngoại phạm vi (Out of domain)** | Học viên nhập phản hồi hoặc hỏi về chủ đề đời sống/khác bài học | Từ chối lịch sự, quay lại phạm vi câu hỏi trắc nghiệm vừa làm sai. |
| **Lớp ④: Case đặc thù domain** | Câu hỏi về thuật ngữ dễ gây nhầm lẫn: RAG vs Fine-tuning | Đối chiếu bảng so sánh chuẩn trong bài giảng Day 01 để chỉ rõ điểm khác biệt về dữ liệu động vs trọng số mô hình. |

---

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

---

## §7. Kiểm thử & Tiêu chuẩn đạt
- **Quality Bar (Chốt tại CP4):**
  - $\ge 85\%$ câu hỏi củng cố sinh ra có trích dẫn đúng đoạn transcript thực tế.
  - $0\%$ trường hợp bịa đặt trích dẫn (hallucination) khi gặp câu hỏi ngoài tài liệu.
  - $\ge 80\%$ học viên thử nghiệm đánh giá câu hỏi củng cố thực sự giúp hiểu rõ lỗi sai.
- **Golden set:** Xây dựng bộ 20 case tại thư mục `eval/` (bao gồm 10 case Happy path, 4 case Low-confidence, 3 case No-grounding, 3 case Edge cases).

---

## §8. Phân công & Kế hoạch
- **Trần Tuấn Cường:** Product Lead — Phụ trách Spec, thiết kế luồng sư phạm, system prompt & output contract.
- **Trần Đình Hinh:** Data Lead — Mining bằng chứng từ transcript/chatlog, soạn fixture quiz mẫu Day 01, xây dựng Golden Set.
- **Lê Như Ý:** AI Engineer — Thiết kế pipeline RAG truy xuất `[Txx-xxx]`, gọi Gemini API, validator và bộ lọc fallback.
- **Lê Thị Châm Anh:** Frontend Lead — Xây dựng giao diện web tương tác, điều phối thử nghiệm người dùng (user test).
- **Willing users cam kết:** Văn Quốc Dũng, Nguyễn Đức Thịnh, Lương Sỹ Khánh.

---

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 17/9 19:30 | Hoàn thiện Canvas 7 dòng (CP1) | Khởi tạo dự án theo Track D2 |
| 17/9 20:15 | Cập nhật §4, §4b (HAX G10, G8, G9, G11), §6 (4 đường trải nghiệm) theo hướng dẫn CP2 | Đồng bộ với bản Interactive Prototype và tiêu chí chấm của Giảng viên |