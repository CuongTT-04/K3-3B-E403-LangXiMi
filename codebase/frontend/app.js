// Vanilla JS, no build step. UI strings are Vietnamese; identifiers are English.
// Every screen renders from the live API -- no hardcoded questions/answers,
// except the "Điền nhanh" demo button below, which is allowed to know the
// mock-data answer key on purpose (see comment on AUTOFILL_ANSWERS).
(function () {
  "use strict";

  const QUIZ_ID = "day01";

  const state = {
    quiz: null, // {quiz_id, title, questions:[{id, stem, options}]}
    answers: {}, // qid -> letter
    lastSubmit: null, // SubmitOut
    reinforcedCorrectCount: 0,
    skippedReinforcementCount: 0,
    taSentCount: 0,
  };

  let taModalQuestionId = null;
  const taButtons = {}; // question_id -> button element (to disable after send)

  const screens = {
    quiz: document.getElementById("screen-quiz"),
    result: document.getElementById("screen-result"),
    remediation: document.getElementById("screen-remediation"),
    summary: document.getElementById("screen-summary"),
  };

  function showScreen(name) {
    Object.entries(screens).forEach(([key, el]) => {
      el.classList.toggle("hidden", key !== name);
    });
    window.scrollTo(0, 0);
  }

  function showToast(message, kind) {
    const toast = document.getElementById("global-toast");
    toast.textContent = message;
    toast.className = "toast visible " + (kind === "warning" ? "toast-warning" : "toast-success");
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(() => {
      toast.classList.remove("visible");
    }, 3500);
  }

  const JSON_HEADERS = { "Content-Type": "application/json" };

  // Response post-processing only -- every call site below writes its own
  // literal fetch call with the endpoint path inline, so the path stays
  // grep-able straight out of the source (see planning/02_*/plan.md).
  async function asJson(resp) {
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}`);
    }
    return resp.json();
  }

  // ---------- Man 1: Quiz ----------

  function renderQuiz() {
    document.getElementById("quiz-title").textContent = state.quiz.title;

    const container = document.getElementById("quiz-questions");
    container.innerHTML = "";
    state.quiz.questions.forEach((q, index) => {
      const card = document.createElement("div");
      card.className = "question-box";

      const header = document.createElement("div");
      header.className = "question-header";
      header.textContent = `Câu ${index + 1}. ${q.stem}`;
      card.appendChild(header);

      const optionsWrap = document.createElement("div");
      optionsWrap.className = "options-list";
      Object.entries(q.options).forEach(([letter, text]) => {
        const label = document.createElement("label");
        label.className = "option-label";
        label.id = `opt-${q.id}-${letter}`;

        const input = document.createElement("input");
        input.type = "radio";
        input.name = q.id;
        input.value = letter;
        input.addEventListener("change", () => {
          state.answers[q.id] = letter;
          optionsWrap.querySelectorAll(".option-label").forEach((el) => el.classList.remove("selected"));
          label.classList.add("selected");
          updateSubmitButtonState();
        });

        label.appendChild(input);
        label.appendChild(document.createTextNode(` ${letter}. ${text}`));
        optionsWrap.appendChild(label);
      });
      card.appendChild(optionsWrap);
      container.appendChild(card);
    });
    updateSubmitButtonState();
  }

  function updateSubmitButtonState() {
    const total = state.quiz ? state.quiz.questions.length : 0;
    const answered = Object.keys(state.answers).length;
    document.getElementById("btn-submit").disabled = answered < total;
  }

  // Demo convenience only: picks a KNOWN-wrong letter for q01/q09/q10/q11
  // and the correct letter for everything else, so one click reliably
  // exercises all 3 remediation paths (happy / low_confidence /
  // no_grounding) -- see mock-data/quiz-day01.json for why those 4
  // questions were engineered that way. Frontend cannot compute this from
  // the API alone since QuestionOut never leaks the answer key.
  const AUTOFILL_ANSWERS = {
    q01: "A",
    q02: "B",
    q03: "A",
    q04: "B",
    q05: "B",
    q06: "A",
    q07: "A",
    q08: "B",
    q09: "A",
    q10: "B",
    q11: "A",
  };

  function autoFillAnswers() {
    if (!state.quiz) return;
    state.quiz.questions.forEach((q) => {
      const letter = AUTOFILL_ANSWERS[q.id];
      if (!letter || !q.options[letter]) return;
      const input = document.querySelector(`input[name="${q.id}"][value="${letter}"]`);
      if (!input) return;
      input.checked = true;
      input.dispatchEvent(new Event("change"));
    });
  }

  async function loadQuiz() {
    state.quiz = await asJson(await fetch("/api/quiz/" + QUIZ_ID));
    state.answers = {};
    state.lastSubmit = null;
    state.reinforcedCorrectCount = 0;
    state.skippedReinforcementCount = 0;
    state.taSentCount = 0;
    renderQuiz();
    showScreen("quiz");
  }

  async function submitQuiz() {
    const resp = await fetch("/api/quiz/" + QUIZ_ID + "/submit", {
      method: "POST",
      headers: JSON_HEADERS,
      body: JSON.stringify({ answers: state.answers }),
    });
    state.lastSubmit = await asJson(resp);
    renderResult();
    showScreen("result");
  }

  // ---------- Man 2: Ket qua ----------

  function questionById(qid) {
    return state.quiz.questions.find((q) => q.id === qid);
  }

  function renderResult() {
    const { score, total, results } = state.lastSubmit;
    const wrongCount = results.filter((r) => !r.is_correct).length;

    const circle = document.getElementById("score-circle");
    circle.textContent = `${score}/${total}`;
    circle.classList.toggle("has-wrong", wrongCount > 0);

    document.getElementById("score-title").textContent = `Bạn đạt ${score} / ${total} câu đúng`;
    document.getElementById("score-detail").textContent =
      wrongCount > 0
        ? `Hệ thống phát hiện bạn có ${wrongCount} câu trả lời sai cần ôn lại.`
        : "Bạn không có câu nào sai. Làm rất tốt!";

    const list = document.getElementById("result-list");
    list.innerHTML = "";
    results.forEach((r, index) => {
      const q = questionById(r.qid);
      const row = document.createElement("div");
      row.className = "question-box" + (r.is_correct ? "" : " wrong");

      const top = document.createElement("div");
      top.style.display = "flex";
      top.style.justifyContent = "space-between";
      top.style.alignItems = "center";
      top.style.gap = "8px";

      const label = document.createElement("strong");
      label.textContent = `Câu ${index + 1}. ${q ? q.stem : r.qid}`;
      const badge = document.createElement("span");
      badge.className = "badge-status " + (r.is_correct ? "badge-correct" : "badge-wrong");
      badge.textContent = r.is_correct ? "✓ Đúng" : "✗ Sai";

      top.appendChild(label);
      top.appendChild(badge);
      row.appendChild(top);
      list.appendChild(row);
    });

    const hasRemediation = !state.lastSubmit.remediation.skipped && state.lastSubmit.remediation.items.length > 0;
    document.getElementById("btn-view-remediation").disabled = !hasRemediation;
  }

  // ---------- Man 3: Giai thich & luyen lai ----------

  function renderRemediation() {
    const container = document.getElementById("remediation-list");
    container.innerHTML = "";
    const items = state.lastSubmit.remediation.items;

    items.forEach((item) => {
      container.appendChild(buildRemediationCard(item));
    });
  }

  function buildRemediationCard(item) {
    const question = questionById(item.question_id);
    const card = document.createElement("div");
    card.className = "card remediation-card";

    const title = document.createElement("h3");
    title.textContent = question ? question.stem : item.question_id;
    title.style.marginBottom = "12px";
    card.appendChild(title);

    const box = document.createElement("div");
    box.className = "ai-remediation-box";
    card.appendChild(box);

    renderBoxForPath(box, item, question);
    return card;
  }

  function renderBoxForPath(box, item, question) {
    box.innerHTML = "";

    const header = document.createElement("div");
    header.className = "ai-remediation-header";
    const badge = document.createElement("div");
    badge.className = "ai-badge";
    badge.textContent = "✦ AI Chẩn đoán & Củng cố (Remediation)";
    header.appendChild(badge);
    box.appendChild(header);

    if (item.path === "happy") {
      renderHappyContent(box, item, question);
    } else if (item.path === "low_confidence") {
      renderLowConfidenceContent(box, item, question);
    } else {
      renderNoGroundingContent(box, item, question);
    }

    box.appendChild(buildCorrectionRow(item.question_id, box));
  }

  function renderHappyContent(box, item, question) {
    const diagLabel = document.createElement("div");
    diagLabel.style.fontWeight = "700";
    diagLabel.style.marginBottom = "6px";
    diagLabel.textContent = "Chẩn đoán lỗi hiểu nhầm:";
    box.appendChild(diagLabel);

    const misconception = document.createElement("p");
    misconception.innerHTML = `<strong>Có thể bạn đang hiểu nhầm:</strong> ${item.misconception}`;
    box.appendChild(misconception);

    const explanation = document.createElement("p");
    explanation.style.marginTop = "8px";
    explanation.textContent = item.explanation;
    box.appendChild(explanation);

    item.citations.forEach((citation) => {
      const quote = document.createElement("div");
      quote.className = "grounding-quote";
      const tag = document.createElement("span");
      tag.className = "grounding-tag";
      tag.textContent = `Căn cứ trích dẫn bài giảng [${citation.id}] (bấm để xem đoạn gốc):`;
      const text = document.createElement("div");
      text.textContent = `"${citation.quote}"`;
      quote.appendChild(tag);
      quote.appendChild(text);
      quote.addEventListener("click", () => openTranscript(citation.id));
      box.appendChild(quote);
    });

    item.reinforcement.forEach((rf, idx) => {
      box.appendChild(buildReinforcementBlock(rf, `${item.question_id}-${idx}`));
    });
  }

  function buildReinforcementBlock(rf, key) {
    const wrap = document.createElement("div");
    wrap.className = "remedy-quiz";

    const title = document.createElement("div");
    title.className = "remedy-quiz-title";
    title.textContent = "🎯 Câu hỏi củng cố ngay (Luyện tập để nắm vững):";
    wrap.appendChild(title);

    const stem = document.createElement("p");
    stem.style.marginBottom = "10px";
    stem.textContent = rf.stem;
    wrap.appendChild(stem);

    const optionsWrap = document.createElement("div");
    optionsWrap.className = "options-list";
    Object.entries(rf.options).forEach(([letter, text]) => {
      const label = document.createElement("label");
      label.className = "option-label";
      const input = document.createElement("input");
      input.type = "radio";
      input.name = `rf-${key}`;
      input.value = letter;
      label.appendChild(input);
      label.appendChild(document.createTextNode(` ${letter}. ${text}`));
      optionsWrap.appendChild(label);
    });
    wrap.appendChild(optionsWrap);

    const toast = document.createElement("div");
    toast.className = "toast";

    const actions = document.createElement("div");
    actions.className = "action-bar";
    actions.style.marginTop = "12px";

    const checkBtn = document.createElement("button");
    checkBtn.className = "btn btn-primary btn-sm";
    checkBtn.textContent = "Kiểm tra củng cố";
    checkBtn.addEventListener("click", () => {
      const selected = wrap.querySelector(`input[name="rf-${key}"]:checked`);
      if (!selected) {
        toast.className = "toast visible toast-warning";
        toast.textContent = "Vui lòng chọn 1 đáp án trước khi kiểm tra.";
        return;
      }
      const isCorrect = selected.value === rf.answer;
      toast.className = "toast visible " + (isCorrect ? "toast-success" : "toast-warning");
      if (isCorrect) {
        state.reinforcedCorrectCount += 1;
        toast.textContent = "🎉 Chính xác! Bạn đã củng cố vững kiến thức này.";
      } else {
        toast.textContent = `⚠️ Chưa đúng. Đáp án đúng là ${rf.answer}.`;
      }
      checkBtn.disabled = true;
      skipBtn.disabled = true;
    });

    const skipBtn = document.createElement("button");
    skipBtn.className = "btn btn-secondary btn-sm";
    skipBtn.textContent = "Bỏ qua";
    skipBtn.addEventListener("click", () => {
      state.skippedReinforcementCount += 1;
      wrap.classList.add("withdrawn");
      checkBtn.disabled = true;
      skipBtn.disabled = true;
      toast.className = "toast visible toast-warning";
      toast.textContent = "Đã bỏ qua câu hỏi củng cố này.";
    });

    actions.appendChild(checkBtn);
    actions.appendChild(skipBtn);
    wrap.appendChild(actions);
    wrap.appendChild(toast);

    return wrap;
  }

  function renderLowConfidenceContent(box, item, question) {
    const wrap = document.createElement("div");
    wrap.className = "hypothesis-box";

    const title = document.createElement("div");
    title.className = "hypothesis-title";
    title.textContent = "🔍 AI nhận diện độ tự tin thấp (cần xác nhận nguyên nhân):";
    wrap.appendChild(title);

    const desc = document.createElement("p");
    desc.style.fontSize = "13px";
    desc.textContent =
      "Hệ thống nhận thấy có 2 khả năng khiến bạn chọn sai. Hãy chọn nguyên nhân của bạn để AI hỗ trợ đúng nhất:";
    wrap.appendChild(desc);

    const list = document.createElement("div");
    list.className = "hypothesis-list";
    item.hypotheses.forEach((hyp) => {
      const btn = document.createElement("button");
      btn.className = "btn btn-secondary hypothesis-btn";
      btn.textContent = hyp.label;
      btn.addEventListener("click", async () => {
        list.querySelectorAll("button").forEach((b) => (b.disabled = true));
        try {
          const resp = await fetch("/api/remediate/confirm", {
            method: "POST",
            headers: JSON_HEADERS,
            body: JSON.stringify({
              quiz_id: QUIZ_ID,
              question_id: item.question_id,
              hypothesis_id: hyp.id,
            }),
          });
          const fullItem = await asJson(resp);
          renderBoxForPath(box, fullItem, question);
          showToast("Đã ghi nhận nguyên nhân. Đây là giải thích đầy đủ.");
        } catch (err) {
          list.querySelectorAll("button").forEach((b) => (b.disabled = false));
          showToast("Không xác nhận được nguyên nhân, hãy thử lại.", "warning");
        }
      });
      list.appendChild(btn);
    });
    wrap.appendChild(list);

    box.appendChild(wrap);
  }

  function renderNoGroundingContent(box, item, question) {
    const wrap = document.createElement("div");
    wrap.className = "no-grounding-box";

    const title = document.createElement("div");
    title.className = "no-grounding-title";
    title.textContent = "⚠️ Chưa có căn cứ bài giảng trực tiếp:";
    wrap.appendChild(title);

    const text = document.createElement("p");
    text.className = "no-grounding-text";
    text.textContent =
      "Không tìm thấy trích dẫn bài giảng chính thức cho câu hỏi này. Để tránh hiện tượng ảo giác (hallucination), AI từ chối tự sinh giải thích khi không có căn cứ.";
    wrap.appendChild(text);

    const askBtn = document.createElement("button");
    askBtn.className = "btn btn-primary btn-sm";
    askBtn.textContent = "📩 Gửi câu hỏi này cho Trợ giảng (TA)";
    askBtn.addEventListener("click", () => openTaModal(item.question_id));
    taButtons[item.question_id] = askBtn;
    wrap.appendChild(askBtn);

    box.appendChild(wrap);
  }

  function buildCorrectionRow(questionId, box) {
    const row = document.createElement("div");
    row.className = "correction-row";

    const misclickBtn = document.createElement("button");
    misclickBtn.className = "btn btn-outline-danger btn-sm";
    misclickBtn.textContent = "✕ Tôi chỉ bấm nhầm chứ đã hiểu";
    misclickBtn.addEventListener("click", async () => {
      misclickBtn.disabled = true;
      try {
        const resp = await fetch("/api/correction", {
          method: "POST",
          headers: JSON_HEADERS,
          body: JSON.stringify({
            quiz_id: QUIZ_ID,
            question_id: questionId,
            action: "misclick",
          }),
        });
        await asJson(resp);
        box.classList.add("withdrawn");
        box.querySelectorAll("button, input").forEach((el) => {
          if (el !== misclickBtn) el.disabled = true;
        });
        showToast("Đã ghi nhận: bạn chỉ bấm nhầm. Thẻ này được thu hồi khỏi danh sách cần ôn lại.");
      } catch (err) {
        misclickBtn.disabled = false;
        showToast("Không gửi được đính chính, hãy thử lại.", "warning");
      }
    });
    row.appendChild(misclickBtn);
    return row;
  }

  // ---------- Modal: transcript ----------

  async function openTranscript(chunkId) {
    try {
      const resp = await fetch("/api/transcript/" + encodeURIComponent(chunkId));
      const chunk = await asJson(resp);
      document.getElementById("transcript-modal-title").textContent = `${chunk.id} - ${chunk.lesson}`;
      document.getElementById("transcript-modal-text").textContent = chunk.text;
      document.getElementById("transcript-modal").classList.remove("hidden");
    } catch (err) {
      showToast("Không mở được đoạn trích dẫn gốc.", "warning");
    }
  }

  // ---------- Modal: TA ticket ----------

  function openTaModal(questionId) {
    taModalQuestionId = questionId;
    document.getElementById("ta-note").value = "";
    document.getElementById("ta-modal").classList.remove("hidden");
  }

  function closeTaModal() {
    taModalQuestionId = null;
    document.getElementById("ta-modal").classList.add("hidden");
  }

  async function sendTaTicket() {
    if (!taModalQuestionId) return;
    const note = document.getElementById("ta-note").value.trim();
    const questionId = taModalQuestionId;
    try {
      const resp = await fetch("/api/ta-ticket", {
        method: "POST",
        headers: JSON_HEADERS,
        body: JSON.stringify({
          quiz_id: QUIZ_ID,
          question_id: questionId,
          note: note || "(không có ghi chú)",
        }),
      });
      await asJson(resp);
      state.taSentCount += 1;
      const btn = taButtons[questionId];
      if (btn) {
        btn.disabled = true;
        btn.textContent = "✓ Đã gửi cho Trợ giảng (TA)";
      }
      closeTaModal();
      showToast("Đã gửi câu hỏi đến Trợ giảng (TA).");
    } catch (err) {
      showToast("Không gửi được cho TA, hãy thử lại.", "warning");
    }
  }

  // ---------- Man 4: Tom tat ----------

  function renderSummary() {
    const wrongCount = state.lastSubmit ? state.lastSubmit.results.filter((r) => !r.is_correct).length : 0;

    const content = document.getElementById("summary-content");
    content.innerHTML = "";

    const list = document.createElement("ul");
    list.className = "summary-list";

    const rows = [
      ["Số câu sai", wrongCount],
      ["Số câu đã củng cố đúng", state.reinforcedCorrectCount],
      ["Số câu bỏ qua", state.skippedReinforcementCount],
      ["Số câu đã gửi Trợ giảng (TA)", state.taSentCount],
    ];
    rows.forEach(([label, value]) => {
      const li = document.createElement("li");
      const span = document.createElement("span");
      span.textContent = label;
      const b = document.createElement("b");
      b.textContent = String(value);
      li.appendChild(span);
      li.appendChild(b);
      list.appendChild(li);
    });
    content.appendChild(list);
  }

  function finishSession() {
    renderSummary();
    showScreen("summary");
  }

  // ---------- Wiring ----------

  document.getElementById("btn-autofill").addEventListener("click", autoFillAnswers);
  document.getElementById("btn-submit").addEventListener("click", submitQuiz);

  document.getElementById("btn-retry-from-result").addEventListener("click", loadQuiz);
  document.getElementById("btn-skip").addEventListener("click", finishSession);
  document.getElementById("btn-view-remediation").addEventListener("click", () => {
    renderRemediation();
    showScreen("remediation");
  });

  document.getElementById("btn-retry").addEventListener("click", loadQuiz);
  document.getElementById("btn-finish").addEventListener("click", finishSession);

  document.getElementById("btn-summary-retry").addEventListener("click", loadQuiz);

  document.getElementById("btn-close-transcript").addEventListener("click", () => {
    document.getElementById("transcript-modal").classList.add("hidden");
  });

  document.getElementById("btn-cancel-ta").addEventListener("click", closeTaModal);
  document.getElementById("btn-send-ta").addEventListener("click", sendTaTicket);

  loadQuiz();
})();
