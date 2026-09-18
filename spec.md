# AI SPEC — Khắc phục hổng kiến thức từ câu hỏi trắc nghiệm sai (Adaptive Error Remediation) · Nhóm LangXiMi · Cụm C4 · Phòng E403
Hướng: [x] D — Học tập thích ứng & tương tác (Đề D2: Học từ lỗi trước)  
Loại: [x] Tối ưu tính năng có sẵn (Màn hình kết quả Quiz VLearn)  [ ] Tính năng mới

---

## §1. User & Job
- Job executor + workflow (đính kèm worksheet JTBD / ảnh sơ đồ): Học viên vừa nộp bài một bộ quiz trắc nghiệm ôn tập trên VLearn (có ≥1 câu trả lời sai), đang xem màn hình kết quả cuối bài. Workflow: nộp bài → xem điểm số tổng quan → (nếu có câu sai) AI tổng hợp các câu sai, chẩn đoán concept bị hiểu nhầm, truy xuất đúng đoạn tài liệu gốc để dẫn giải và sinh câu hỏi trắc nghiệm củng cố thuộc tài liệu đó → học viên nhận giải thích kèm trích dẫn nguồn và làm lại câu củng cố ngay tại màn hình kết quả (nguồn: `canvas.md` dòng 2, 5).
- Core JTBD (không tên sản phẩm/AI trong câu): Khi vừa nộp bài quiz và phát hiện mình trả lời sai, học viên muốn biết ngay mình đã hiểu nhầm điều gì và đọc đúng đoạn tài liệu liên quan, để không phải tự lật lại hàng chục trang slide và không lặp lại lỗi đó ở bài kiểm tra sau.
- Problem statement (KHÔNG chữ AI): Sau khi nộp bài quiz, màn hình chỉ hiện tổng điểm và danh sách đúng/sai chung chung; học viên không biết mình hiểu nhầm chỗ nào và ngại lật lại hàng chục trang slide để tìm, dẫn đến việc hổng kiến thức vẫn còn nguyên và tiếp tục sai ở các bài kiểm tra sau (nguồn: `canvas.md` dòng 3).
- Evidence (chuẩn A và/hoặc B — log đầy đủ trong repo), chi tiết theo 2 mục dưới đây.
  - Số liệu mining / kết quả khảo sát (n = ?, % xác nhận): trong `tutor_turns.csv` (n = 13.494 lượt tutor), nước đi sư phạm `ask_probing_question` chỉ xuất hiện ở 28/13.494 lượt (0,21%); trường `understanding_level` bị bỏ trống ở 13.474/13.494 lượt (99,85%) — tức tutor gần như không có cơ chế kiểm tra/xác nhận đã hiểu bài (nguồn: `canvas.md` dòng 4).
  - ≥5 quote/ví dụ nguyên văn + nguồn:
    1. Lượt `T00261` — *"cho tôi bộ quizz liên quan"* (tutor từ chối) — nguồn: `canvas.md` dòng 4, gốc `tutor_turns.csv`.
    2. Lượt `T00804` — *"tạo quiz ôn tập"* (tutor từ chối) — nguồn: `canvas.md` dòng 4; ⏳ cần trích nguyên văn đầy đủ từ data pack (ngoài repo, `tutor_turns.csv`).
    3. Lượt `T01545` — *"tạo quiz ôn tập"* (tutor từ chối) — nguồn: `canvas.md` dòng 4; ⏳ cần trích nguyên văn đầy đủ từ data pack (ngoài repo, `tutor_turns.csv`).
    4. Lượt `T01587` — *"tạo quiz ôn tập"* (tutor từ chối) — nguồn: `canvas.md` dòng 4; ⏳ cần trích nguyên văn đầy đủ từ data pack (ngoài repo, `tutor_turns.csv`).
    5. `[T04-092]` (`transcript-04-clean.md`) — học viên phản hồi sau giờ chơi Kahoot cần tính năng quiz cá nhân hoá để ôn bài theo điểm yếu — nguồn: `canvas.md` dòng 4; ⏳ cần trích nguyên văn từ data pack (ngoài repo, `transcript-04-clean.md`).

## §2. Impact & quyết định chọn
- Bảng impact ≥3 ứng viên (bao nhiêu người · tần suất · tốn gì mỗi lần · khả thi trong 39h) — xem bảng dưới đây.

| Ứng viên | Bao nhiêu người | Tần suất | Tốn gì mỗi lần | Khả thi trong 39h |
|---|---|---|---|---|
| **A. Giải thích + củng cố ngay tại màn kết quả quiz [CHỌN]** | Ước lượng: đa số học viên có câu sai — vì chỉ 0,21% lượt tutor có `ask_probing_question` và 99,85% lượt bỏ trống `understanding_level` (`canvas.md` dòng 4), gần như không ai được xác nhận đã hiểu bài | Mỗi lần nộp quiz có ≥1 câu sai | 1 lượt gọi LLM chẩn đoán + sinh câu củng cố cho mỗi câu sai (đã đo bằng pipeline: `pytest` 39 pass, `run_eval.py` pass=14/14, xem `docs/backend.md`) | Cao — đã có prototype chạy hết luồng, đủ 4 đường đi |
| **B. Bot sinh đề quiz theo yêu cầu trong chat tutor** | Ít nhất 4 lượt bị từ chối ghi nhận được (`T00261`, `T00804`, `T01545`, `T01587` trên tổng 13.494 lượt) — ước lượng số thực tế cao hơn vì chỉ đếm được lượt từ chối rõ ràng | Ước lượng: phát sinh tự phát trong hội thoại, không đều đặn | Phải sinh đề từ đầu không có ngữ cảnh câu sai cụ thể, cần thêm state quản lý hội thoại nhiều lượt | Thấp — chưa có pipeline hội thoại multi-turn trong 39h, rủi ro bịa đề không có căn cứ transcript |
| **C. Dashboard điểm yếu theo concept cho học viên/TA** | Ước lượng: toàn bộ học viên + TA của lớp | Ước lượng: xem theo tuần hoặc khi TA cần | Cần tổng hợp dữ liệu nhiều lượt quiz theo thời gian, thêm tầng lưu trữ/thống kê | Thấp — cần dữ liệu lịch sử nhiều bài quiz hơn phạm vi 1 bài (`quiz-day01.json`), vượt 39h |

- Ứng viên ĐÃ LOẠI + vì sao: **B** loại vì rủi ro hallucination cao khi sinh đề không neo vào câu sai cụ thể, và không khớp lát cắt "màn hình kết quả" đã chốt ở canvas dòng 5. **C** loại vì cần dữ liệu lịch sử nhiều bài quiz (không chỉ `quiz-day01.json`), không giải quyết pain tức thời ngay lúc học viên đang đứng ở màn kết quả, và vượt phạm vi 39h.
- Ứng viên CHỌN + vì sao (bằng số): **A** — vì 99,85% lượt tutor (13.474/13.494) không hề chốt được `understanding_level` và chỉ 0,21% (28/13.494) có `ask_probing_question`; nghĩa là gần như toàn bộ học viên rời cuộc trò chuyện mà không được xác nhận đã hiểu bài. Màn hình kết quả quiz — nơi học viên vừa thấy câu sai — là điểm chạm rẻ nhất để chèn chẩn đoán + củng cố ngay, không cần xây thêm luồng hội thoại mới (nguồn số liệu: `canvas.md` dòng 4).

## §3. Giải pháp tương tự đã nghiên cứu
*(Desk research — kiến thức chung, không phải số đo từ repo.)*
- **Khan Academy (Mastery Practice — gợi ý sau câu sai):** Flow — sau khi làm sai, hệ thống hiển thị hint tăng dần theo từng bước, kèm video bài giảng liên quan, rồi cho làm lại bài cùng dạng đến khi đạt "mastery". Đáng học: hint tăng dần bám theo đúng bài giảng liên quan, không giải thích chung chung. Đáng né: hint đôi khi generic, không chỉ đúng quan niệm sai cụ thể học viên đang mắc, dễ thành "làm cho có". Mình khác gì: chẩn đoán quan niệm sai cụ thể theo đúng phương án học viên đã chọn (không chỉ theo độ khó chung), trích dẫn nguyên văn transcript bài giảng gốc `[Txx-xxx]`, và từ chối sinh câu hỏi khi không có căn cứ (đường No-grounding) — cơ chế grounding này Khan Academy không công khai.
- **Duolingo (ôn lại lỗi sai / "Mistakes review" + spaced repetition):** Flow — hệ thống gom các câu sai gần đây, đưa vào bài ôn ngắn lặp lại đúng dạng câu đã sai, nhắc lại theo lịch giãn cách (spaced repetition). Đáng học: coi lỗi sai là input để tạo bài tiếp theo, không chỉ báo điểm rồi thôi. Đáng né: không giải thích "vì sao sai" bằng nguồn tài liệu cụ thể, chỉ lặp lại câu hỏi dạng tương tự — học viên có thể đoán mò đến khi đúng mà không thực sự hiểu. Mình khác gì: bắt buộc có bước chẩn đoán + trích dẫn nguồn trước khi cho làm câu củng cố, từ chối rõ ràng khi thiếu căn cứ thay vì cứ lặp lại câu hỏi.
- **Quizlet Learn / Kahoot report (báo cáo sau bài kiểm tra):** Flow — sau bài kiểm tra, xuất báo cáo thống kê câu sai theo chủ đề, xếp hạng độ khó, gợi ý ôn lại. Đáng học: tổng hợp lỗi theo concept giúp nhìn bức tranh chung. Đáng né: chỉ dừng ở thống kê, không sinh câu hỏi mới ngay tại chỗ, không trích dẫn tài liệu gốc — học viên vẫn phải tự đi tìm slide. Mình khác gì: gắn liền chẩn đoán + trích dẫn nguyên văn + câu hỏi củng cố ngay tại thời điểm nộp bài (không phải báo cáo rời rạc sau này), có cơ chế từ chối rõ ràng khi thiếu căn cứ.

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

| Lớp | # | Kịch bản | Câu/case tham chiếu | Hành vi hệ thống mong đợi |
|---|---|---|---|---|
| ① Không có căn cứ trong bài giảng | 1 | Học viên sai câu hỏi về `kubernetes_deployment_pipeline` — concept này hoàn toàn không tồn tại trong `lessons.json` | `q10` (`quiz-day01.json`), `golden-set.json` case-14 | Retriever trả `chunks=[]`, `confidence=0.0` → path `no_grounding`; hiển thị *"Không tìm thấy trích dẫn bài giảng chính thức..."* + nút "Gửi câu hỏi cho TA" |
| ① Không có căn cứ trong bài giảng | 2 | Câu hỏi tuỳ ý (qua `/api/remediate`) thuộc concept `neural_architecture_search`, không có trong index bài giảng | `golden-set.json` case-10 (`qx-unknown-01`) | `chunks=[]` → path `no_grounding`, `citations=[]`, `reinforcement=[]`, `fallback=true` |
| ① Không có căn cứ trong bài giảng | 3 | Câu hỏi tuỳ ý thuộc concept `quantum_computing_basics`, không có trong index bài giảng | `golden-set.json` case-11 (`qx-unknown-02`) | `chunks=[]` → path `no_grounding`, `citations=[]`, `reinforcement=[]`, `fallback=true` |
| ② Mơ hồ nhiều nguyên nhân | 4 | Học viên sai câu về `vector_embedding_scaling`; câu hỏi gài `source_ids` giả (`T99-905/906`, không có thật) buộc retriever rơi vào nhánh overlap từ khoá, `confidence` ước tính ~0.667 | `q09` (`quiz-day01.json`), `golden-set.json` case-12 | path `low_confidence`; hiện hộp thoại 2 giả thuyết nguyên nhân, chờ học viên bấm chọn qua `POST /api/remediate/confirm` trước khi sinh câu củng cố |
| ② Mơ hồ nhiều nguyên nhân | 5 | Học viên sai câu về `hybrid_search_optimization`; câu hỏi gài `source_ids` giả (`T99-911/912`), `confidence` ước tính ~0.667 | `q11` (`quiz-day01.json`), `golden-set.json` case-13 | path `low_confidence`; hiện hộp thoại 2 giả thuyết ("A. Nhầm định nghĩa" / "B. Đọc lướt bỏ sót từ"), chờ xác nhận trước khi sinh câu củng cố |
| ③ Học viên bấm nhầm/đã hiểu | 6 | Học viên bị chấm sai một câu (vd `q01`) nhưng thực ra đã hiểu bài, chỉ bấm nhầm đáp án | `q01` (`quiz-day01.json`) | Học viên bấm *"Tôi chỉ bấm nhầm nút chứ đã nắm rõ kiến thức này"* → `POST /api/correction {action: "misclick"}` → hệ thống hủy khối câu củng cố, ghi `events.jsonl`, cập nhật trạng thái hoàn thành |
| ③ Học viên bấm nhầm/đã hiểu | 7 | Học viên đi hết đường Happy path (vd sai `q03`, nhận câu củng cố) nhưng đang vội, không muốn làm thêm | `q03` (`quiz-day01.json`) | Học viên bấm *"Bỏ qua câu củng cố này" / "Kết thúc bài ôn"* → `POST /api/correction {action: "dismiss"}` → không ép làm thêm, ghi `events.jsonl` |
| ④ LLM bịa trích dẫn hoặc câu củng cố lệch | 8 | LLM (Gemini thật) trả về một citation `id` không tồn tại trong các chunk đã truy xuất được cho câu hỏi | Bất kỳ câu nào ở path `happy`/`low_confidence` (vd `q01`–`q08`, `q09`, `q11`) | `validator.py` phát hiện citation bịa → hạ về path `no_grounding` thay vì hiển thị trích dẫn giả (an toàn hơn là bịa, theo `docs/backend.md`) |
| ④ LLM bịa trích dẫn hoặc câu củng cố lệch | 9 | LLM sinh câu hỏi củng cố (`reinforcement`) có `source_id` không trỏ về citation đã duyệt của item đó (lệch khỏi đoạn bài giảng vừa trích) | Bất kỳ câu nào ở path `happy` (vd `q01`–`q08`) | `validator.py` từ chối, hạ về path `no_grounding`, không hiển thị câu củng cố sai lệch |

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
- Chiều chất lượng + định nghĩa kiểm chứng được (4 tiêu chí dưới đây).
  - **Đúng path** — path trả về (`happy`/`low_confidence`/`no_grounding`) khớp `expect_path` trong golden set.
  - **Trích dẫn nguyên văn** — `citations[].quote` khớp nguyên văn đoạn transcript gốc trong `lessons.json` (validator so sau khi chuẩn hoá khoảng trắng), không bị diễn giải lại.
  - **Câu củng cố trỏ về trích dẫn** — mỗi `reinforcement[].source_id` phải nằm trong danh sách citation đã duyệt của item đó, không lệch sang nguồn khác.
  - **Không bịa khi thiếu căn cứ** — khi `confidence < LOW_CONF_MIN`, `chunks=[]`, hoặc citation không hợp lệ ⇒ bắt buộc path `no_grounding`, `citations=[]`, `reinforcement=[]` (không được vẫn hiện trích dẫn/câu hỏi).
- Golden set (≥20 case theo cơ cấu trong guide §2.6, file trong eval/): đường dẫn `codebase/mock-data/golden-set.json`, chạy bằng `python backend/eval/run_eval.py`. 21 case (10 happy · 3 low_confidence · 4 no_grounding · 4 mixed) — `codebase/mock-data/golden-set.json`.
- Quality bar (chốt từ hạn chốt spec của khoá, giữ nguyên sau đó): "Đạt khi ≥90% case golden set đúng path, `citations_invalid=0`, và 0 item `no_grounding` có trích dẫn"
- Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6), xem bảng dưới đây.

| Ngày | Điều kiện | Kết quả |
|---|---|---|
| 17/9 | `pytest` (39 pass, 0 skip) + `run_eval.py`, `LLM_MODE=mock`, golden set 14 case | `eval pass=14/14 fallback_ok=3/3 low_conf_ok=2/2 citations_invalid=0` |
| 18/9 · mock · 21/21 pass · fallback_ok 7/7 · low_conf_ok 7/7 · citations_invalid 0 | `LLM_MODE=mock`, golden set 21 case (hồ sơ #03) | `eval pass=21/21 fallback_ok=7/7 low_conf_ok=7/7 citations_invalid=0` |
| ⏳ Gemini thật (chưa có key) | `LLM_MODE=gemini` | ⏳ chưa đo được — thiếu `GEMINI_API_KEY` (câu hỏi mở ở `plan.md` §5) |

## §8. Phân công & kế hoạch
- Phân công có tên (theo `canvas.md` dòng 7), xem bảng dưới đây.

| Mảng | Người phụ trách |
|---|---|
| spec | Trần Tuấn Cường (Product Lead — spec, thiết kế luồng sư phạm, output contract) |
| evidence | Trần Đình Hinh (Data & Eval Lead — mining bằng chứng chatlog/transcript, Golden Set, quality bar) |
| prompt | Trần Tuấn Cường (thiết kế system prompt chẩn đoán lỗi & sinh câu hỏi củng cố), phối hợp Lê Như Ý (tích hợp vào code) |
| code | Lê Như Ý (Backend & AI Engineer — pipeline RAG, gọi LLM API, output validator, xử lý fallback) |
| demo | Lê Thị Châm Anh (Frontend & User Testing Lead — giao diện web, điều phối demo/user test) |

- Willing users (≥2 tên) + kế hoạch vòng validation *(bonus, nếu làm)*: `Văn Quốc Dũng`, `Nguyễn Đức Thịnh`, `Lương Sỹ Khánh` (khai theo `canvas.md` dòng 6). Kế hoạch: Lê Thị Châm Anh điều phối vòng validation với ≥5 học viên trong lớp (trong đó ≥2 người là willing user đã khai từ CP1, chọn trong 3 tên trên), giao task cụ thể (làm 1 bộ quiz Day 01 có câu sai, xem phản hồi chẩn đoán + câu củng cố), ghi quote nguyên văn + nhật ký (ai thử · task gì · kẹt ở đâu · quote · quyết định) theo `README.md` gốc mục R6, lưu vào `validation/` tại CP5, cập nhật ≥1 thay đổi vào §9 Changelog.
- Multi-prototype (nếu làm): trục khác biệt của ≥2 phương án + lý do chọn: Không làm — 39h chỉ đủ cho 1 lát cắt (xem `planning/03_2026-09-18_cp4-spec-hardening/plan.md` §2, quyết định xếp PATCH không MINOR, không mở thêm phương án song song).

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| 17/9 CP2 | Thêm §4b (nguyên tắc HAX/PAIR đã áp dụng) + §6 (4 đường đi trải nghiệm); dựng prototype mock bấm được (`codebase/index.html`, `codebase/flowchart.md`) | Mốc CP2 yêu cầu cho thấy luồng hoạt động trước khi gọi AI thật |
| 17/9 hồ sơ #02 | Nối API 4 đường đi (`happy`/`low_confidence`/`no_grounding`/correction) vào frontend thật, thêm `POST /api/correction`, `POST /api/ta-ticket`, hook `LLM_MODE=gemini` | spec §4 đã chốt gọi trực tiếp Gemini API tại CP3; cần chạy end-to-end trước khi đo số (`planning/02_2026-09-17_frontend-api-wiring/plan.md`) |
| 18/9 hồ sơ #03 | Điền §1, §2, §3, §5, §7, §8, §9; khoá Quality bar ("≥90% case golden set đúng path, `citations_invalid=0`, 0 item `no_grounding` có trích dẫn") | CP4 yêu cầu khoá chuẩn "đạt" lúc 21:00 hôm nay, trước khi thấy kết quả cuối cùng (`README.md` mục CP4) |
```
