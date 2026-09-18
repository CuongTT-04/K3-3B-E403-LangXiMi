# AI SPEC — Khắc phục hổng kiến thức từ câu hỏi trắc nghiệm sai (Adaptive Error Remediation) · Nhóm LangXiMi · Cụm C4 · Phòng E403
Hướng: [x] D — Học tập thích ứng & tương tác (Đề D2: Học từ lỗi trước)
Loại: [x] Tối ưu tính năng có sẵn (Màn hình kết quả Quiz VLearn)  [ ] Tính năng mới

## §1. User & Job
- Job executor + workflow (đính kèm worksheet JTBD / ảnh sơ đồ): Học viên vừa nộp quiz ôn tập trên VLearn, có ít nhất một câu sai, đang xem màn hình kết quả. Luồng hiện tại: nộp bài → xem điểm/đúng-sai → tự lật slide hoặc rời phiên học. Luồng đề xuất: nộp bài → chọn câu sai → nhận chẩn đoán có căn cứ → làm một câu củng cố, bỏ qua hoặc nhờ TA.

  ```mermaid
  flowchart TD
      subgraph Current["Luồng hiện tại (Current Baseline)"]
          direction TB
          C1["Học viên làm quiz"] --> C2["Nộp bài"]
          C2 --> C3["Xem tổng điểm & đúng / sai chung chung"]
          C3 --> C4["Tự lần mò lật slide hoặc rời phiên học"]
          C4 --> C5["Lỗ hổng kiến thức vẫn còn nguyên"]
          style C5 fill:#fee2e2,stroke:#ef4444,stroke-width:1px
      end

      subgraph Proposed["Luồng đề xuất (Proposed Adaptive Workflow)"]
          direction TB
          P1["Học viên nộp quiz (có ≥ 1 câu sai)"] --> P2["Xem màn hình kết quả & chọn câu sai"]
          P2 --> P3["Nhận chẩn đoán hiểu nhầm + Căn cứ trích dẫn transcript"]
          P3 --> P4{"Hành động tiếp theo"}
          P4 -->|"Luyện tập"| P5["Làm 1 câu trắc nghiệm củng cố tức thì"]
          P5 --> P6["Khắc phục ngay lỗ hổng kiến thức"]
          P4 -->|"Bỏ qua (HAX G8)"| P7["Tiếp tục phiên học"]
          P4 -->|"Bấm nhầm (HAX G9)"| P8["Đính chính & hủy câu củng cố"]
          P4 -->|"Thiếu căn cứ (Fallback)"| P9["Gửi Ticket nhờ Trợ giảng (TA)"]
          style P6 fill:#dcfce7,stroke:#22c55e,stroke-width:1px
          style P3 fill:#e0f2fe,stroke:#0284c7,stroke-width:1px
      end
  ```
- Core JTBD (không tên sản phẩm/AI trong câu): Khi vừa phát hiện mình trả lời sai, tôi muốn hiểu đúng chỗ mình nhầm và kiểm tra lại ngay, để không mang cùng lỗ hổng sang lần kiểm tra kế tiếp.
- Problem statement (KHÔNG chữ AI): Màn hình kết quả chỉ cho biết đúng hoặc sai. Người học phải tự lần lại tài liệu dài để tìm lý do, nên thường rời đi trước khi hiểu và sửa lỗi.
- Evidence (chuẩn A và/hoặc B — log đầy đủ trong repo): Chuẩn B; chạy `python codebase/eval/mine_evidence.py` khi có data pack được cấp. Script, phép đếm và mã turn ở repo; data gốc không được commit.
  - Số liệu mining / kết quả khảo sát (n = ?, % xác nhận): `tutor_turns.csv` có **13.494 lượt**; `understanding_level` trống **13.474/13.494 (99,85%)**; `ask_probing_question` xuất hiện **28/13.494 (0,21%)**. Có **196 lượt** chứa nhu cầu quiz/ôn tập theo bộ từ khóa. Đây là số lượt, không phải số người duy nhất.
  - ≥5 quote/ví dụ nguyên văn + nguồn:
    1. Turn `T00261`: “dựa vào tài liệu này bạn hãy cho tôi bộ quizz liên quan” → tutor: “Hiện tại tôi không có bộ câu hỏi kiểm tra (quiz) đính kèm trong tài liệu bài giảng...”.
    2. Turn `T00633`: “tóm tắt những ý chính, chi tiết để tôi có thể làm quiz kahoot cuối giờ” → tutor từ chối vì không truy xuất được dạng bài kiểm tra.
    3. Turn `T00804`: “TẠO QUIZ ĐỂ TÔI HIỂU RÕ VÀ ÔN LẠI TOÀN BỘ SLIDE NÀY” → tutor chỉ trả lời lý thuyết, không tạo bài tập tương tác.
    4. Turn `T01520`: “hiện tại vlearn đã có quiz ôn tập ch” → học viên chủ động tìm tính năng quiz trên nền tảng.
    5. Turn `T01545`: “tạo quiz ôn tập” → yêu cầu luyện tập trực tiếp từ người học.
    6. Transcript 04 `[T04-092]`: “Cần tính năng quiz cá nhân hoá để ôn bài theo điểm yếu, chứ làm sai xong trôi qua luôn không nhớ mình sai vì sao.”

## §2. Impact & quyết định chọn
- Bảng impact ≥3 ứng viên (bao nhiêu người · tần suất · tốn gì mỗi lần · khả thi):

  | Ứng viên | Quy mô có chứng cứ | Tần suất | Tốn gì mỗi lần nếu không hỗ trợ | Khả thi |
  |---|---:|---|---|---|
  | A. Khắc phục ngay sau một câu quiz sai **[chọn]** | Học viên có câu sai; chưa đo unique users | Tối đa 1 lần/câu sai | Ước tính 5–15 phút tự dò slide; là giả định cần validation | Cao: quiz, transcript, UI và 4 path đã có |
  | B. Sinh quiz tự do từ toàn bộ tài liệu | 196 lượt yêu cầu quiz/ôn tập; là proxy, không phải người duy nhất | Theo nhu cầu, ngoài ngữ cảnh lỗi | Ước tính 10–20 phút soạn/kiểm tra; là giả định | Trung bình: cần mở rộng phạm vi và kiểm soát chất lượng đề |
  | C. Chat hỏi đáp mở sau buổi học | 13.494 lượt chat là quy mô nền, không tách được nhu cầu này | Nhiều lần/phiên | Tự diễn đạt lại câu hỏi và tự xác minh nguồn | Thấp: dễ trôi phạm vi, khó đảm bảo đúng-sai |

  Các khoảng thời gian là giả định sản phẩm, không phải số đo người dùng; dữ liệu không đủ để suy ra số người duy nhất.
- Ứng viên ĐÃ LOẠI + vì sao: B không bắt đầu từ lỗi vừa xảy ra, tăng rủi ro câu hỏi không bám tài liệu; C quá rộng, khó bảo đảm citation và không giải quyết đúng khoảnh khắc người học vừa thấy mình sai.
- Ứng viên CHỌN + vì sao (bằng số): A bám trực tiếp pain ở `[T04-092]`, tái sử dụng 20 case regression đang có (13 happy, 2 low-confidence, 5 fallback/no-grounding) và không cần xây luồng chat mới.

## §3. Giải pháp tương tự đã nghiên cứu
- [Duolingo Practice](https://blog.duolingo.com/guide-to-duolingo-practice-hub/): flow ôn lại lỗi trước đó theo session; đáng học là bắt đầu từ lỗi thật và đưa bài luyện ngắn; đáng né là chỉ lặp bài mà không giải thích nguồn/quan niệm sai; mình khác ở chỗ giải thích một câu sai vừa xảy ra, gắn transcript và một câu củng cố cùng nguồn.
- [Khanmigo](https://www.khanacademy.org/khanmigo): flow hỗ trợ trong ngữ cảnh bài tập, hướng người học tự suy nghĩ và nhận feedback; đáng học là giữ quyền chủ động của người học; đáng né là chat dài đa chủ đề dễ mơ hồ; mình khác ở chỗ chỉ quyết định sửa ngay/hỏi làm rõ/fallback, không mở chat ngoài câu sai và luôn có đính chính/bỏ qua.

## §4. Thiết kế
- Lát cắt MỘT CÂU (1 user · 1 việc · 1 quyết định AI · 1 kết quả): Khi một học viên vừa nộp quiz và có câu sai, hệ thống quyết định sửa ngay/hỏi làm rõ/fallback theo căn cứ transcript, để học viên hiểu đúng một quan niệm sai và hoàn thành một câu củng cố có nguồn ngay tại màn hình kết quả.
- Non-goals (≥3 thứ KHÔNG build): (1) Không sinh ngân hàng đề ngẫu nhiên cho toàn bộ bài học. (2) Không chấm tự luận, chạy code hay cấp điểm chính thức. (3) Không làm chatbot đa chủ đề ngoài câu sai của quiz. (4) Không thay TA quyết định khi thiếu căn cứ bài giảng.
- Mức prototype nhắm tới: [ ] Sketch [ ] Mock [x] Working — phần nào mock, phần nào thật: API/UI, retriever, validator và MockLLM chạy thật với fixture Day 01; provider OpenAI-compatible/Gemini có thể gọi thật khi có key. Lesson/quiz là mock; chưa chứng minh vận hành production.
- Automation: [ ] augment [x] conditional [ ] automate — lý do theo cost-of-error: confidence `>=0,75` mới trả chẩn đoán/citation/câu củng cố; `0,40–<0,75` đưa đúng 2 giả thuyết và chờ học viên chọn; `<0,40`, không có chunk, LLM lỗi hoặc validator từ chối thì `no_grounding`. Một citation/câu hỏi sai có thể làm người học nạp sai kiến thức, nên thà fallback có hướng dẫn còn hơn tự động hóa toàn phần.
- §4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR, xem guide):

  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | HAX G10 — Thu hẹp phạm vi khi nghi ngờ | `<0,75` không đưa kết luận chắc chắn; `no_grounding` không sinh citation/câu hỏi. |
  | HAX G8 — Gạt bỏ dễ dàng | Có nút “Bỏ qua”/“Kết thúc bài ôn”; không bắt buộc học thêm. |
  | HAX G9 — Hỗ trợ sửa lỗi hiệu quả | “Tôi chọn nhầm chứ không phải hiểu sai” ghi event qua `/api/correction` và hủy câu củng cố. |
  | HAX G11 / PAIR Explainability — Giải thích lý do | Hiển thị ID/quote citation; validator yêu cầu quote là substring của chunk thật. |
  | PAIR — User retains control | Low-confidence chờ người học chọn giả thuyết; TA ticket và dismiss luôn là lối ra. |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8) [bảng theo guide §2.5]

| Tình huống | Lớp | Hành vi mong muốn | Nguyên tắc áp |
|---|---:|---|---|
| `source_id` không tồn tại hoặc quote không nằm trong transcript | ① Nguồn sự thật | Hạ `no_grounding`, xóa citation/reinforcement, mở TA ticket | G10, G11 |
| Có chunk nhưng confidence dưới 0,40 | ① Nguồn sự thật | Không kết luận/câu hỏi mới; chỉ trỏ bài liên quan | G10 |
| Câu có từ “KHÔNG”, không rõ đọc sót hay không hiểu concept | ② Mơ hồ | Hiện hai giả thuyết, chờ xác nhận | G10, user control |
| Một đáp án sai có thể do hai concept gần nhau | ② Mơ hồ | Không quy chụp; người học chọn nguyên nhân trước khi luyện | G9 |
| Hỏi Kubernetes/Blockchain không có trong lesson Day 01 | ③ Ngoài phạm vi | Từ chối an toàn, nói giới hạn và hướng về tài liệu/TA | G10 |
| LLM/API timeout hoặc HTTP 429 | ③ Ngoài phạm vi vận hành | Không màn hình trắng; fallback, cho thử lại/gửi TA | Graceful degradation |
| Nhầm RAG với fine-tuning khi dữ liệu thay đổi hằng ngày | ④ Domain tinh tế | Nêu trade-off, trích đúng đoạn và sinh câu củng cố | G11 |
| Nhầm Product Manager với Project Manager/Owner | ④ Domain tinh tế | Giải thích khác biệt trách nhiệm, không chỉ lộ đáp án | Explainability |
| Bấm nhầm nhưng đã hiểu | ② Mơ hồ | Cho đính chính, dừng remediation và log event | G8, G9 |

Kịch bản đáng sợ nhất: citation có tồn tại nhưng ngữ nghĩa không chứng minh kết luận. Validator hiện chỉ kiểm ID và substring, chưa kiểm entailment; cần chấm tay D2 semantic trước khi tuyên bố chất lượng LLM thật.

## §6. Bốn đường đi của trải nghiệm
- Happy path: `confidence >=0,75` → hiện quan niệm sai, quote `[Txx-xxx]`, một câu củng cố 4 lựa chọn → học viên làm hoặc bỏ qua. · Low-confidence (②): `0,40–<0,75` → nêu chưa chắc, hiện 2 giả thuyết → học viên chọn rồi mới mở remediation đầy đủ. · Failure/không căn cứ (①): không có chunk, citation bị validator từ chối hoặc LLM lỗi → không sinh nội dung có vẻ chắc chắn, gợi ý bài học và TA ticket. · Correction (user sửa): chọn `misclick`/`dismiss` → ghi event, ẩn khối ôn, không ép tiếp tục.
- Khi bị đòi ngoài phạm vi (③): q10/case 14 hoặc unknown case → fallback an toàn, không cố trả lời Kubernetes/Blockchain. · Case đặc thù domain (④): RAG–fine-tuning, tool calling–RAG hoặc PM–Project Manager → giải thích cặp khái niệm kèm citation, không chỉ báo đáp án.

## §7. Kiểm thử
- Chiều chất lượng + định nghĩa kiểm chứng được: D1 Diagnosis accuracy = nêu đúng concept/giả định sai, không chỉ báo đáp án; D2 Citation groundedness = ID/quote hợp lệ và nội dung thực sự nâng đỡ kết luận; D3 Reinforcement quality = tình huống rõ, 4 lựa chọn khác nhau, đúng 1 đáp án, không lộ đáp án; D4 Tone & graceful fallback = giọng hỗ trợ, thiếu căn cứ/ngoài phạm vi thì từ chối và chỉ lối. Runner hiện tự động kiểm path và citation cấu trúc; D1, D2 entailment, D3 uniqueness/độ đúng và D4 tone vẫn cần rubric chấm tay.
- Golden set (≥20 case theo cơ cấu trong guide §2.6, file trong eval/): input runner là [`codebase/mock-data/golden-set.json`](codebase/mock-data/golden-set.json), **20 case** (13 happy, 2 low-confidence, 5 no-grounding); runner là [`codebase/backend/eval/run_eval.py`](codebase/backend/eval/run_eval.py). [`codebase/eval/golden_set.json`](codebase/eval/golden_set.json) là bộ tham khảo trong `eval/`, không phải input runner hiện tại. Tự khai: chưa có case đo biến thể câu hỏi khi sai cùng một câu từ lần thứ hai.
- Quality bar (chốt từ hạn chốt spec của khoá, giữ nguyên sau đó): "Đạt khi ≥80% (ít nhất 16/20) case qua toàn bộ D1–D4, và 100% citation trace được về transcript (`citations_invalid=0`), đồng thời 100% case ngoài phạm vi từ chối an toàn."
- Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6):

  | Lượt | Cấu hình | Kết quả | Diễn giải |
  |---|---|---|---|
  | CP3 baseline, 15:49 18/09 | OpenRouter GPT-4o-mini (log lịch sử) | 20/20; fallback 5/5; low-confidence 2/2; invalid 0 | Chứng minh proxy runner, chưa chứng minh đủ D1–D4. |
  | Xác minh MockLLM | `LLM_MODE=mock` | 20/20; fallback 5/5; low-confidence 2/2; invalid 0 | Regression xác định của pipeline/validator. |
  | Xác minh provider hiện có | LLM thật; HTTP 429 ở q08 | 18/20; fallback 5/5; low-confidence 2/2; invalid 0 | q08 đáng ra happy đã fallback; cần retry quota. |

  Tự khai chưa hoàn thiện: chưa có latency p95/retry-backoff cho 429; runner chưa tách `OOS_total`;. Vì vậy chưa thể tuyên bố LLM thật đạt quality bar đầy đủ.

## §8. Phân công & kế hoạch
- Phân công có tên: spec/prompt — Trần Tuấn Cường; evidence/golden set/quality bar — Trần Đình Hinh; code RAG/provider/validator/fallback — Lê Như Ý; demo/UI/user test — Lê Thị Châm Anh.
- Willing users (≥2 tên) + kế hoạch vòng validation *(bonus, nếu làm)*: Văn Quốc Dũng, Nguyễn Đức Thịnh, Lương Sỹ Khánh. CP5 mời tối thiểu 5 người ngoài nhóm, trong đó ít nhất 2 người trên; giao task làm sai có chủ đích một câu, tìm lý do, làm/bỏ qua câu củng cố; ghi vào `validation/` người dùng, path, thời gian, điểm kẹt, quote nguyên văn và quyết định sửa/giữ.
- Multi-prototype (nếu làm):

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| 17/09/2026 · CP1 | Chốt job executor, conditional automation, willing users | Chatlog và `[T04-092]` cho thấy pain sau câu sai |
| 17/09/2026 · CP2 | Thêm happy, low-confidence, no-grounding, correction | Giảm cost-of-error khi căn cứ yếu; áp G8–G11 |
| 18/09/2026 · 15:49 | Ghi baseline 20 case và raw log | Có mốc đo trước CP4 |
| 18/09/2026 · CP4 | Khóa `P≥16/20 ∧ citations_invalid=0 ∧ outside-scope safe=100%`; tự khai gap eval/validation | Ngăn hạ chuẩn sau khi thấy số; HTTP 429/q08 cho thấy cần tách logic và độ tin cậy provider |

