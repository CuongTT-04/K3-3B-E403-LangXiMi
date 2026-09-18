# Quality Bar & Bộ Tiêu Chí Đánh Giá (Evaluation Rubric)
**Track D · Đề D2: Học từ lỗi trước**  
**Nhóm:** LangXiMi · Cụm C4 · Phòng E403  
**Phụ trách:** Trần Đình Hinh (Data & Eval Lead)

---

## 1. Định nghĩa 4 chiều chất lượng kiểm chứng được (Verifiable Quality Dimensions)

Mỗi output chẩn đoán và sinh câu hỏi củng cố của AI được đánh giá độc lập qua 4 chiều rõ ràng (nhị phân Pass/Fail hoặc tiêu chí cụ thể để 2 người chấm độc lập đều ra cùng một kết quả):

| STT | Chiều chất lượng | Định nghĩa kiểm chứng được (Pass / Fail) | Ngưỡng vi phạm nghiêm trọng (Critical Failure) |
|---|---|---|---|
| **D1** | **Diagnosis Accuracy** *(Chẩn đoán lỗi sai)* | **PASS:** AI chỉ ra chính xác concept/giả định sai lầm mà học viên mắc phải khi chọn phương án đó.<br>**FAIL:** AI chỉ nói câu vô thưởng vô phạt (ví dụ: *"Bạn đã chọn sai, đáp án đúng là..."*) mà không phân tích được nguyên nhân hiểu nhầm. | Chẩn đoán sai hoàn toàn bản chất hoặc quy chụp học viên sai khi học viên chọn đúng. |
| **D2** | **Citation Groundedness** *(Tính chuẩn xác nguồn trích dẫn)* | **PASS:** Đoạn mã trích dẫn `[Txx-NNN]` tồn tại có thật 100% trong transcript bài giảng tương ứng, và nội dung đoạn trích dẫn trực tiếp minh chứng cho kiến thức đang đề cập.<br>**FAIL:** Bịa số hiệu trích dẫn ảo (Hallucination) hoặc trỏ vào đoạn transcript không hề nhắc đến khái niệm đó. | **Zero-Tolerance:** Bất kỳ case nào bịa đặt trích dẫn `[Txx-xxx]` đều bị tính là lỗi hệ thống nghiêm trọng. |
| **D3** | **Reinforcement Quality** *(Chất lượng câu hỏi củng cố)* | **PASS:** Câu hỏi trắc nghiệm mới sinh ra đáp ứng đủ 4 tiêu chuẩn kỹ thuật:<br>1. Có đề bài rõ ràng, gắn tình huống thực tế.<br>2. Đủ 4 lựa chọn (A, B, C, D) không trùng lặp.<br>3. Duy nhất 1 đáp án đúng không gây tranh cãi.<br>4. Không bị lộ đáp án ngay trong câu hỏi.<br>**FAIL:** Sinh thiếu lựa chọn, có nhiều hơn 1 đáp án đúng, hoặc câu hỏi mơ hồ không giải quyết được. | Sinh câu hỏi sai kiến thức chuyên môn hoặc không có đáp án đúng. |
| **D4** | **Tone & Graceful Fallback** *(Sư phạm & Xử lý biên)* | **PASS:** Giọng văn mang tính khích lệ, nâng đỡ sư phạm, không phán xét/chỉ trích. Khi gặp case không tìm thấy căn cứ (Lớp ①) hoặc ngoài phạm vi (Lớp ③), hệ thống tự động từ chối lịch sự, giải thích lý do và trỏ về tài liệu học tập.<br>**FAIL:** Đưa ra giọng điệu trịch thượng, miệt thị học viên hoặc làm liều khi không có tài liệu. | Cưỡng ép học viên làm thêm bài hoặc bịa thông tin khi ngoài phạm vi bài học. |

---

## 2. Quality Bar chốt cứng (Commit trước 21:00 18/9 - Mốc CP4)

> 🎯 **QUY ĐỊNH QUALITY BAR CỦA NHÓM LANGXIMI:**
> 
> Một lượt chạy kiểm thử toàn bộ Golden Set (20 case) được xem là **ĐẠT CHUẨN (PASS QUALITY BAR)** khi và chỉ khi thỏa mãn đồng thời 3 điều kiện số lượng sau:
> 
> 1. **Tỷ lệ vượt qua tổng thể:** $\ge \mathbf{80\%}$ (ít nhất **16/20** case đạt Pass trên cả 4 chiều chất lượng).
> 2. **Điều kiện cứng về trích dẫn (Zero Hallucination):** $\mathbf{100\%}$ (**20/20** case) tuyệt đối **không bịa đặt trích dẫn** `[Txx-xxx]`. Nếu không có tài liệu, bắt buộc phải trả về trạng thái Fallback (Lớp ①).
> 3. **Xử lý ranh giới ngoài phạm vi (Lớp ③):** $\mathbf{100\%}$ các case ngoài phạm vi phải từ chối đúng chuẩn sư phạm (không vượt thẩm quyền).

---

## 3. Quy trình chạy và ghi nhận kết quả kiểm thử (Eval Workflow)

1. **Lượt đo 1 (Baseline - CP3):** Chạy toàn bộ 20 case qua prototype với lời gọi AI thật. Ghi lại kết quả thực tế vào bảng theo dõi.
2. **Phân tích lỗi (Failure Analysis):** Lọc ra các case Fail, phân loại lỗi theo 4 chiều D1-D4.
3. **Tối ưu Prompt / RAG:** Cải tiến prompt của `Product Lead` hoặc thuật toán truy xuất của `Backend Engineer`.
4. **Chạy lại trọn bộ (Re-test Full Set):** Chạy lại toàn bộ 20 case (không chỉ chạy riêng case bị lỗi) để đảm bảo không bị hiện tượng "sửa chỗ này vỡ chỗ kia" (Prompt Regression).
