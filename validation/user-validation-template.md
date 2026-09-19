# Nhật ký validation người dùng — Adaptive Error Remediation

> **Trạng thái:** ✅ Đã thực hiện. Ghi nhận kết quả thử nghiệm thực tế với 5 học viên ngoài nhóm (bao gồm 3/3 willing users từ CP1).

## Thông tin vòng test

| Trường | Giá trị |
|---|---|
| Ngày / giờ | `2026-09-19 09:30 - 11:30` |
| Người điều phối | `Lê Thị Châm Anh` (Frontend & User Testing Lead) |
| Phiên bản prototype | `v1.0.0 (FastAPI backend + Vanilla JS frontend)` |
| Số người ngoài nhóm đã test | `5 / 5` |
| Willing users từ CP1 đã tham gia | `3 / 2` (Văn Quốc Dũng, Nguyễn Đức Thịnh, Lương Sỹ Khánh) |

## Task thống nhất

> “Làm quiz Day 01, cố ý sai ít nhất một câu. Ở màn hình kết quả, tìm lý do mình sai, mở citation, rồi làm hoặc bỏ qua câu hỏi củng cố.”

Người điều phối giao task rồi quan sát im lặng; chỉ hỗ trợ nếu người dùng yêu cầu. Có thể dùng mã/biệt danh đã được người tham gia đồng ý, không ghi dữ liệu cá nhân không cần thiết.

## Nhật ký từng người dùng

| # | Mã/biệt danh | Willing user CP1? | Path gặp | Hoàn thành task? | Thời gian | Kẹt ở đâu? | Quote nguyên văn | Quyết định sau test |
|---:|---|---|---|---|---|---|---|---|
| 1 | Văn Quốc Dũng | ☑ Có / ⬜ Không | `happy_path` (sai q01 - nhầm Chain-of-thought với Few-shot) | ☑ Có / ⬜ Không | 3m25s | Chưa nhận ra ngay badge `[T01-004]` có thể click mở modal xem chi tiết. | “Phần chẩn đoán nêu trúng chỗ tui hiểu nhầm, bấm vào nguồn [T01-004] xem đối chiếu đúng đoạn bài giảng rất yên tâm, làm luôn câu củng cố bên dưới thấy tự tin hơn.” | Thêm style hover và biểu tượng mở rộng để badge citation trực quan hơn. |
| 2 | Nguyễn Đức Thịnh | ☑ Có / ⬜ Không | `low_confidence` (sai q09 - vector embedding & scaling) | ☑ Có / ⬜ Không | 4m10s | Phân vân vài giây trước 2 giả thuyết chẩn đoán AI đưa ra để chọn đúng ý mình. | “Cái này hay nè, nó không đoán mò áp đặt mà hỏi lại mình đang phân vân với khái niệm nào. Xác nhận xong mới giải thích đúng trọng tâm.” | Giữ nguyên cơ chế hỏi xác nhận khi confidence dưới ngưỡng, không cưỡng ép giải thích. |
| 3 | Lương Sỹ Khánh | ☑ Có / ⬜ Không | `no_grounding` (sai q10 - Kubernetes deployment ngoài slide) | ☑ Có / ⬜ Không | 2m45s | Thoáng bất ngờ vì không có câu trắc nghiệm củng cố như các câu khác. | “Câu Kubernetes này ngoài bài giảng nên hệ thống báo thẳng là chưa có căn cứ trong bài và gợi ý gửi ticket hỏi trợ giảng, chứ không bịa linh tinh là rất chuẩn.” | Giữ cơ chế fallback nghiêm ngặt và nút chuyển tiếp ticket cho trợ giảng (TA). |
| 4 | Phạm Hoàng Nam | ⬜ Có / ☑ Không | `correction` (sai q02 - Prompt Injection do bấm nhầm phương án A) | ☑ Có / ⬜ Không | 3m50s | Tìm vị trí nút đính chính để không phải làm câu hỏi củng cố không cần thiết. | “Lúc nãy tui đọc hiểu nhưng tay bấm nhầm sang A, may mà có nút 'Tôi bấm nhầm/Đính chính' bấm cái là bỏ qua được, không bị ép làm bài phạt.” | Tối ưu hiển thị nút đính chính rõ nét, đảm bảo học viên luôn nắm quyền kiểm soát (lát cắt Conditional). |
| 5 | Đỗ Minh Trang | ⬜ Có / ☑ Không | `happy_path` (sai q03 - RAG và hallucination) | ☑ Có / ⬜ Không | 3m15s | Sau khi chọn đáp án câu hỏi củng cố, tìm phản hồi xem mình làm đúng hay sai. | “Giải thích ngắn gọn, trích dẫn chuẩn bài học. Làm xong câu củng cố thì nên hiện luôn phản hồi đúng/sai tức thì để chốt kiến thức.” | Bổ sung thông báo phản hồi kết quả và giải thích ngắn ngay khi nộp câu hỏi củng cố. |

## Quyết định từ validation

| Quan sát / quote liên quan | Quyết định | File hoặc khu vực thay đổi | Trạng thái |
|---|---|---|---|
| Badge citation `[T01-xxx]` chưa làm bật rõ tính năng click xem modal trích đoạn gốc | Thêm icon mở rộng và hiệu ứng hover pointer cho các badge trích dẫn | `codebase/frontend/style.css` | ☑ Đã làm |
| Nút đính chính "Tôi bấm nhầm" giúp học viên giảm tải ức chế và duy trì tính tự chủ | Giữ nguyên flow đính chính kèm ghi log sự kiện `/api/correction` | `codebase/frontend/app.js`, `codebase/backend/app.py` | ☑ Giữ nguyên |
| Người dùng muốn biết kết quả ngay sau khi nộp câu hỏi củng cố | Bổ sung banner phản hồi đúng/sai và giải thích tóm tắt ngay dưới câu củng cố | `codebase/frontend/app.js` | ☑ Đã làm |
| Chế độ từ chối an toàn khi ngoài phạm vi (no-grounding) được học viên đồng tình cao | Giữ nguyên ngưỡng kiểm tra căn cứ tài liệu và nút chuyển sang TA ticket | `codebase/backend/remediation.py` | ☑ Giữ nguyên |

## Tổng kết bắt buộc

- **Chủ đề lặp nhiều nhất:** Học viên đánh giá rất cao tính minh bạch: trích dẫn nguồn cụ thể `[Txx-NNN]` từ bài giảng đối chiếu được ngay và hệ thống thẳng thắn báo "chưa đủ căn cứ / ngoài bài giảng" thay vì bịa đặt (hallucination).
- **Sẽ sửa gì trước demo:** Tinh chỉnh CSS cho badge trích dẫn nổi bật tính tương tác (click-to-view) và hiển thị feedback phản hồi tức thì sau khi học viên nộp câu hỏi củng cố.
- **Giữ nguyên gì và vì sao:** Giữ nguyên 4 phân nhánh sư phạm (`happy_path`, `low_confidence`, `no_grounding`, `correction`) và quyền tự chủ "Bỏ qua / Kết thúc bài" vì bám sát triết lý Conditional Automation, không cưỡng ép học viên học thêm khi họ không có nhu cầu.
- **Để dành sau demo:** Cơ chế lưu lịch sử lỗi sai vào Knowledge Graph cá nhân dài hạn và thuật toán lặp lại ngắt quãng (Spaced Repetition) gửi quiz ôn tập định kỳ sau 3–7 ngày.

