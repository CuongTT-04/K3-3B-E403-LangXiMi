# Sơ đồ Luồng Trải Nghiệm Học Tập Thích Ứng (CP02 Flowchart)

Tài liệu thiết kế hành trình người dùng và luồng quyết định AI cho đề tài: **Khắc phục hổng kiến thức từ câu hỏi trắc nghiệm sai (Track D2 - LangXiMi)**.

---

## 1. Sơ đồ luồng tổng thể (User Journey & AI Decision Tree)

```mermaid
flowchart TD
    Start([Học viên hoàn thành bài Quiz trên VLearn]) --> Submit[Bấm Nộp bài]
    Submit --> ShowResult[Hiển thị Màn hình kết quả tổng quan<br/>Điểm số, câu đúng, câu sai]
    
    ShowResult --> CheckWrong{Có câu trả lời sai không?}
    CheckWrong -- Không có câu sai --> Perfect([Chúc mừng! Nắm vững toàn bộ kiến thức])
    CheckWrong -- Có câu sai --> TriggerAI[Kích hoạt AI Remediation Engine]
    
    TriggerAI --> Retrieve[Truy xuất Transcript bài giảng gốc qua RAG]
    Retrieve --> CheckConfidence{Độ tin cậy & căn cứ tài liệu?}
    
    %% Đường 1: Happy Path
    CheckConfidence -- "Độ tương đồng >= 0.75 (Tự tin cao)" --> HappyPath[1. Happy Path:<br/>Chẩn đoán nguyên nhân hiểu nhầm<br/>+ Trích dẫn Transcript Tag [Txx-xxx]<br/>+ Sinh câu hỏi trắc nghiệm củng cố]
    
    HappyPath --> UserChoice{Học viên hành động}
    UserChoice -- "Làm câu củng cố" --> SolveQuestion[Chọn đáp án & Bấm Kiểm tra]
    SolveQuestion --> QuestionResult[Phản hồi đúng/sai tức thì & Hoàn thành]
    
    %% Nguyên tắc HAX G8 & G9
    UserChoice -- "G8: Gạt bỏ dễ dàng" --> Dismiss([Bấm 'Bỏ qua câu củng cố' / Hoàn thành bài])
    UserChoice -- "G9: Sửa sai hiệu quả" --> FixAI([Bấm 'Tôi bấm nhầm chứ không phải hiểu sai'<br/>AI hủy củng cố])
    
    %% Đường 2: Low-confidence Path
    CheckConfidence -- "Mơ hồ / Có nhiều nguyên nhân hiểu nhầm" --> LowConf[2. Low-Confidence Path G10:<br/>AI đưa ra 2 giả thuyết nhầm lẫn<br/>Học viên chọn đúng tình huống của mình]
    LowConf --> HappyPath
    
    %% Đường 3: No-grounding Path
    CheckConfidence -- "Không tìm thấy căn cứ trong bài giảng" --> NoGround[3. Failure / No-grounding Path G10:<br/>Từ chối sinh câu hỏi ảo<br/>Hiện tóm tắt lý thuyết chung + Nút 'Hỏi TA']
    NoGround --> EndFallback([Kết thúc / Gửi ticket TA])
```

---

## 2. Bảng đối chiếu 4 đường trải nghiệm và vị trí tương tác

| Đường trải nghiệm | Tình huống kích hoạt | Quyết định của hệ thống | Điểm tương tác trên giao diện |
|---|---|---|---|
| **1. Happy Path** | Học viên làm sai câu hỏi có trích dẫn bài giảng chắc chắn ($\ge 0.75$) | AI phân tích vì sao đáp án đã chọn là sai, trích đoạn `[T01-042]` và sinh 1 câu hỏi củng cố mới | Khối card tím củng cố kiến thức: Badge trích dẫn, khung câu hỏi mới, nút nộp câu củng cố |
| **2. Low-confidence (②)** | AI nhận diện học viên có thể sai do đọc thiếu từ hoặc nhầm lẫn khái niệm | AI không vội sinh đề, mà đưa 2 phương án hỏi xác nhận nguyên nhân | Hộp thoại tương tác chọn nguyên nhân: "A. Nhầm định nghĩa" / "B. Đọc lướt bỏ sót từ" |
| **3. Failure / No-grounding (①)** | Câu hỏi không có tài liệu đối chiếu trong slide/transcript | Áp dụng **HAX G10**: Không bịa trích dẫn và không tự sinh câu hỏi ảo; chỉ hiện lý thuyết gốc | Khối cảnh báo màu hổ phách: Thông báo thiếu căn cứ + Nút "Gửi câu hỏi cho Trợ giảng (TA)" |
| **4. User Correction (Sửa/Bỏ qua)** | Học viên cảm thấy mình đã hiểu bài hoặc do bấm nhầm | Áp dụng **HAX G8 & G9**: Thu hồi can thiệp AI ngay lập tức chỉ với 1 click | Nút *"Tôi chỉ bấm nhầm"* (G9) và nút *"Bỏ qua & Kết thúc"* (G8) |

---

## 3. Lý do thiết kế Automation theo Chi phí sai sót (Cost-of-Error)

* **Không chọn Automate:** Nếu để AI tự động ép học viên làm lại toàn bộ hoặc tự động sinh câu hỏi khi không chắc chắn, nguy cơ sinh câu hỏi sai lệch hoặc trích dẫn giả mạo (hallucination) sẽ làm học viên học sai kiến thức thi $\rightarrow$ **Chi phí sai sót rất cao**.
* **Không chọn Augment:** Nếu mỗi câu hỏi củng cố phải chờ giảng viên/TA duyệt bằng tay $\rightarrow$ Học viên phải chờ hàng giờ/ngày, đánh mất "thời điểm vàng" muốn biết đáp án đúng ngay sau khi nộp bài.
* **Chọn Conditional:** AI tự động thực hiện khi có căn cứ vững chắc từ transcript ($\ge 0.75$). Khi mơ hồ hoặc không có căn cứ, hệ thống tự động thu hẹp phạm vi và chuyển giao quyền quyết định cho con người.
