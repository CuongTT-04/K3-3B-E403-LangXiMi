# Báo Cáo Đo Lường Lượt Đầu (Baseline Evaluation Report - CP3 & CP4)
**Track D · Đề D2: Học từ lỗi trước**  
**Nhóm:** LangXiMi · Cụm C4 · Phòng E403  
**Phụ trách:** Trần Đình Hinh (Data & Eval Lead) & Trần Tuấn Cường (Product Lead)  
**Thời gian đo:** 18/09/2026 - 15:49  
**Tệp nhật ký máy đọc (Raw Run Log):** `eval/run_results/eval_run_1789721355.json`

---

## 1. Bảng tổng hợp số đo định lượng (Quantitative Summary Table)

| Chỉ số đo lường | Kết quả thực tế (Baseline Run) | Ngưỡng cam kết (Quality Bar) | Đánh giá nghiệm thu |
|---|:---:|:---:|:---:|
| **Tổng số case kiểm thử** | **20 case** | Tối thiểu 20 case | ✅ Đạt số lượng |
| **Số case ĐẠT (PASS)** | **20 / 20** | $\ge 16 / 20$ case | ✅ **VƯỢT CHUẨN** |
| **Số case THẤT BẠI (FAIL)** | **0 / 20** | $\le 4 / 20$ case | ✅ Hoàn hảo |
| **Tỷ lệ phần trăm (% Pass)** | **100.0%** | $\ge \mathbf{80.0\%}$ | ✅ **PASS QUALITY BAR** |
| **Số case Fallback an toàn (Lớp ① & ③)** | **5 / 5 (100%)** | $100\%$ không bịa đặt | ✅ Đạt chuẩn |
| **Số case Nghi vấn / Cần xác nhận (Lớp ②)** | **2 / 2 (100%)** | $100\%$ thu hẹp phạm vi | ✅ Đạt HAX G10 |
| **Trích dẫn ảo (Hallucination)** | **0 (Zero-tolerance)** | 0 case | ✅ Tuyệt đối không ảo giác |

---

## 2. Chi tiết phân bố 20 case theo Taxonomy 4 Lớp Chỗ Khó

| Nhóm kịch bản / Lớp chỗ khó | Mã Case | Số lượng | Tỷ lệ Đạt | Hành vi hệ thống đã kiểm chứng |
|---|---|:---:|:---:|---|
| **Lớp ①: Nguồn sự thật (Thiếu căn cứ)** | Case 10, 11, 19 | 3 case | 3/3 (100%) | Tự động chuyển đường `no_grounding`, không bịa đặt trích dẫn ảo, cung cấp nút gửi TA. |
| **Lớp ②: Mơ hồ / Thiếu thông tin** | Case 12, 13 | 2 case | 2/2 (100%) | Tự động rẽ nhánh `low_confidence`, đưa ra 2 giả thuyết hiểu nhầm để học viên chọn (HAX G10). |
| **Lớp ③: Ngoài phạm vi / Thẩm quyền** | Case 14, 18 | 2 case | 2/2 (100%) | Nhận diện câu hỏi ngoài phạm vi bài học (Kubernetes, Blockchain), từ chối an toàn và hướng dẫn quay lại bài giảng. |
| **Lớp ④: Đặc thù Domain tinh tế** | Case 01, 02, 05, 06 | 4 case | 4/4 (100%) | Phân biệt rạch ròi các cặp khái niệm dễ nhầm: *Chain-of-thought* vs *Few-shot*, *Prompt injection* vs *Hallucination*, *Tool calling* vs *RAG*. |
| **Thường gặp (Happy Path Day 01)** | Case 03, 04, 07, 08, 09, 15, 16, 17 | 8 case | 8/8 (100%) | Chẩn đoán đúng trọng tâm, trích dẫn transcript `[Txx-xxx]` chuẩn xác có dấu, sinh câu hỏi củng cố 4 lựa chọn. |
| **Edge Case (Sai liên tiếp nhiều câu)** | Case 20 | 1 case | 1/1 (100%) | Xử lý song song đồng thời 4 câu sai qua ThreadPoolExecutor trong ~4 giây, không bị nghẽn hay tràn bộ nhớ. |

---

## 3. Phân tích trường hợp sai lệch & Rủi ro tiềm ẩn (Failure & Edge-Case Analysis)

Mặc dù bộ 20 case đạt tỷ lệ Pass 100% nhờ bộ kiểm duyệt `validator.py` và tập dữ liệu `mock-data/lessons.json` đã chuẩn hóa có dấu, nhóm ghi nhận **3 rủi ro kỹ thuật tiềm ẩn** cần theo dõi khi chạy mô hình AI thật ở quy mô lớn:

1. **Rủi ro Timeout khi học viên làm sai $\ge 5$ câu cùng lúc:**
   - *Hiện tượng:* Nếu chạy tuần tự từng câu hỏi qua LLM, mỗi câu mất ~1.5 - 2s thì 5 câu sẽ mất 8 - 10s khiến giao diện có cảm giác bị đơ.
   - *Biện pháp đã xử lý:* Đã đưa luồng gọi AI vào `ThreadPoolExecutor(max_workers=5)` để xử lý song song, ép toàn bộ thời gian phản hồi xuống chỉ còn **~3.5 - 4.5 giây**.
2. **Rủi ro sai lệch trích dẫn do dấu tiếng Việt (Diacritics Mismatch):**
   - *Hiện tượng:* Ban đầu các câu trích dẫn trong bài giảng gốc thiếu dấu khiến câu trích dẫn của AI sinh ra có dấu bị `validator` từ chối nhầm.
   - *Biện pháp đã xử lý:* Toàn bộ 32 chunk bài giảng trong `mock-data/lessons.json` đã được chuẩn hóa thêm dấu tiếng Việt 100%, bảo đảm việc so khớp `_is_substring` đạt độ chính xác tuyệt đối.
3. **Rủi ro cạn hạn ngạch (Rate Limit / Quota Exhaustion) khi chấm thi:**
   - *Hiện tượng:* Gọi liên tục có thể bị nhà cung cấp API trả về lỗi HTTP 429.
   - *Biện pháp đã xử lý:* Đã thiết kế cơ chế fallback an toàn: nếu API gặp sự cố hoặc mất mạng, hệ thống tự động fallback về chẩn đoán quy tắc có cấu trúc, tuyệt đối không làm crash ứng dụng hay hiển thị màn hình trắng cho giám khảo.
