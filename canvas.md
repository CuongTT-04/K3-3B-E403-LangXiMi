## Track A — tối ưu tutor có sẵn
1. **Track + đề:** D · Đề D2: Học từ lỗi trước 
2. **Job executor:** Học viên vừa nộp bài một bộ quiz trắc nghiệm ôn tập trên VLearn (có >= 1 câu trả lời sai), đang xem màn hình kết quả cuối bài.
3. **Pain:** Sau khi nộp bài quiz, màn hình chỉ hiện tổng điểm và danh sách đúng/sai chung chung; học viên không biết mình hiểu nhầm chỗ nào và ngại lật lại hàng chục trang slide để tìm, dẫn đến việc hổng kiến thức vẫn còn nguyên và tiếp tục sai ở các bài kiểm tra sau.
4. **Bằng chứng đầu:**
    - Trong `tutor_turns.csv`, tutor gần như không có cơ chế kiểm tra và củng cố hiểu bài: nước đi sư phạm ask_probing_question chỉ có 28/13.494 lượt (0,21%); trường understanding_level bị bỏ trống tới 13.474/13.494 lượt (99,85%).
    - Nhu cầu ôn tập bằng quiz của học viên rất lớn nhưng hệ thống chưa đáp ứng được: lượt T00261 ("cho tôi bộ quizz liên quan" ==> tutor từ chối), T00804, T01545, T01587 ("tạo quiz ôn tập" ==> tutor từ chối).
    - `transcript-04-clean.md` ([T04-092]): Học viên phản hồi sau giờ chơi Kahoot cần tính năng quiz cá nhân hoá để ôn bài theo điểm yếu.
5. **Lát cắt:** Học viên vừa nộp xong bộ quiz ôn tập có câu sai · cần khắc phục ngay các lỗ hổng kiến thức trước khi rời đi · ở cuối màn hình kết quả, AI tổng hợp các câu sai, chẩn đoán concept bị hiểu nhầm, truy xuất đúng đoạn tài liệu gốc để dẫn giải và sinh câu hỏi trắc nghiệm tương ứng thuộc tài liệu đó · kết quả là học viên nhận được phản hồi giải thích kèm trích dẫn nguồn và bộ câu hỏi củng cố để luyện tập lại ngay tại màn hình kết quả.
6. **AI tự làm đến đâu:** Có điều kiện (Conditional): Tự động gom các câu sai, truy xuất đoạn transcript [Txx-NNN] và sinh câu hỏi trắc nghiệm củng cố khi độ tin cậy và căn cứ tài liệu rõ ràng. Nếu câu hỏi không tìm thấy tài liệu đối chiếu chắc chắn trong bài giảng, AI chỉ đưa ra giải thích lý thuyết chung và trỏ về bài học, tuyệt đối không tự bịa câu hỏi và không bịa trích dẫn. Học viên có nút "Bỏ qua / Kết thúc bài" để chủ động quyết định luyện thêm hay dừng lại.
*Lý do:* Tránh hiện tượng ảo giác (hallucination) làm sai lệch kiến thức chuyên môn; không cưỡng ép học viên làm thêm bài nếu họ không có thời gian.
**Willing users:** `Văn Quốc Dũng-025105`, `Nguyễn Đức Thịnh 02468`, `Lương Sỹ Khánh 02715`.
7. **Phân công:**    - 
    `Trần Tuấn Cường` — **Product Lead:** Spec, thiết kế luồng sư phạm, system prompt (chẩn đoán lỗi sai & sinh câu hỏi trắc nghiệm củng cố), output contract.
   - ` Trần Đình Hinh ` — **Data & Eval Lead:** Mining bằng chứng số liệu chatlog/transcript, chuẩn bị Fixture mini-quiz Day 01, xây dựng Golden Set (20 case) và bộ tiêu chí đánh giá (quality bar).
   - `Lê Như Ý` — **Backend & AI Engineer:** Xây dựng pipeline RAG truy xuất đoạn transcript `[Txx-NNN]`, gọi LLM API, output validator và xử lý các ca lỗi/fallback.
   - `Lê Thị Châm Anh` — **Frontend & User Testing Lead:** Xây dựng giao diện web (làm quiz → nộp bài → hiển thị giải thích & câu hỏi củng cố ở màn hình kết quả), điều phối user test với ≥5 học viên trong lớp.
