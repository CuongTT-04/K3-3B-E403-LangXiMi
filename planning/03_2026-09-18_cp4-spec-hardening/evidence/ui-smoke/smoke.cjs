const { JSDOM } = require("jsdom");
const fs = require("fs");
const BASE = "http://127.0.0.1:8000";
const FE = "D:/mini-hackathon/K3-3B-E403-LangXiMi/codebase/frontend/";
const html = fs.readFileSync(FE + "index.html", "utf8").replace('<script src="/app.js"></script>', "");
const dom = new JSDOM(html, { url: BASE + "/", runScripts: "outside-only", pretendToBeVisual: true });
const { window } = dom;
window.fetch = (url, opts) => fetch(BASE + url, opts);
window.scrollTo = () => {};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const until = async (fn, label, ms = 8000) => { const t = Date.now(); while (Date.now() - t < ms) { if (fn()) return; await sleep(50); } throw new Error("timeout: " + label); };
(async () => {
  window.eval(fs.readFileSync(FE + "app.js", "utf8"));
  const d = window.document;
  await until(() => d.querySelectorAll("#quiz-questions .question-box").length > 0, "quiz loaded");
  const questions = d.querySelectorAll("#quiz-questions .question-box").length;
  d.getElementById("btn-autofill").click();
  await until(() => !d.getElementById("btn-submit").disabled, "submit enabled");
  d.getElementById("btn-submit").click();
  await until(() => !d.getElementById("screen-result").classList.contains("hidden"), "result screen");
  const score = d.getElementById("score-title").textContent;
  d.getElementById("btn-view-remediation").click();
  await until(() => d.querySelectorAll("#remediation-list .remediation-card").length > 0, "remediation cards");
  const cardsEl = [...d.querySelectorAll("#remediation-list .remediation-card")];
  const kind = (c) => c.querySelector(".grounding-quote") ? "happy" : c.querySelector(".hypothesis-box") ? "low_confidence" : c.querySelector(".no-grounding-box") ? "no_grounding" : "?";
  const before = cardsEl.map((c) => ({ q: c.querySelector("h3").textContent.slice(0, 32), path: kind(c), rf: c.querySelectorAll(".remedy-quiz").length, misc: (c.querySelector(".ai-remediation-box p") || {}).textContent?.slice(0, 60) }));
  // Path 2: confirm hypothesis h2 on first low_confidence card
  const low = cardsEl.find((c) => kind(c) === "low_confidence");
  low.querySelectorAll(".hypothesis-btn")[1].click();
  await until(() => low.querySelector(".grounding-quote"), "low -> happy after confirm");
  const afterConfirm = low.querySelector(".ai-remediation-box p:nth-of-type(2)")?.textContent.slice(0, 60);
  // Path 4: misclick correction on first happy card
  const happy = cardsEl.find((c) => kind(c) === "happy");
  happy.querySelector(".btn-outline-danger").click();
  await until(() => happy.querySelector(".ai-remediation-box").classList.contains("withdrawn"), "withdrawn");
  // Path 3: TA ticket on no_grounding card
  const nog = cardsEl.find((c) => kind(c) === "no_grounding");
  nog.querySelector(".no-grounding-box button").click();
  await until(() => !d.getElementById("ta-modal").classList.contains("hidden"), "ta modal");
  d.getElementById("ta-note").value = "smoke";
  d.getElementById("btn-send-ta").click();
  await until(() => nog.querySelector(".no-grounding-box button").disabled, "ta sent");
  // Path 1: answer reinforcement in second happy card (pick the correct letter from API to check toast)
  const happy2 = cardsEl.filter((c) => kind(c) === "happy")[1];
  const rq = happy2.querySelector(".remedy-quiz");
  rq.querySelector("input[type=radio]").checked = true;
  rq.querySelector("button.btn-primary").click();
  const rfToast = rq.querySelector(".toast").textContent;
  d.getElementById("btn-finish").click();
  await until(() => !d.getElementById("screen-summary").classList.contains("hidden"), "summary");
  const summary = [...d.querySelectorAll(".summary-list li")].map((li) => li.textContent).join(" | ");
  console.log(JSON.stringify({ questions, score, paths: before.map((b) => b.q.slice(0, 8) + "→" + b.path), miscSample: before[0].misc, afterConfirm, rfToast, summary }, null, 1));
})().catch((e) => { console.error("FAIL", e.message); process.exit(1); });
