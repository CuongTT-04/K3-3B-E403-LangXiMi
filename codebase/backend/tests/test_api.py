import json

from fastapi.testclient import TestClient

from app.main import app
from app import data

client = TestClient(app)


def _quiz_answer_key():
    quiz = data.load_quiz("day01")
    return {q["id"]: q["answer"] for q in quiz["questions"]}


def _wrong_choice(correct: str) -> str:
    for letter in ["A", "B", "C", "D"]:
        if letter != correct:
            return letter
    raise AssertionError("no wrong option available")


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_quiz_endpoint_does_not_leak_answer():
    resp = client.get("/api/quiz/day01")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["quiz_id"] == "day01"
    assert len(payload["questions"]) == 11
    for q in payload["questions"]:
        assert set(q.keys()) == {"id", "stem", "options"}
        assert "answer" not in q
        assert "concept" not in q
        assert "source_ids" not in q
        assert "misconception_hint" not in q


def test_quiz_endpoint_unknown_id_404():
    resp = client.get("/api/quiz/day99")
    assert resp.status_code == 404


def test_submit_all_correct_skips_remediation():
    answer_key = _quiz_answer_key()
    resp = client.post("/api/quiz/day01/submit", json={"answers": answer_key})
    assert resp.status_code == 200
    body = resp.json()
    assert body["score"] == body["total"] == 11
    assert body["remediation"]["skipped"] is True
    assert body["remediation"]["items"] == []


def test_submit_with_wrong_answers_has_remediation():
    answer_key = _quiz_answer_key()
    answers = dict(answer_key)
    wrong_ids = ["q01", "q03"]
    for qid in wrong_ids:
        answers[qid] = _wrong_choice(answer_key[qid])

    resp = client.post("/api/quiz/day01/submit", json={"answers": answers})
    assert resp.status_code == 200
    body = resp.json()
    assert body["score"] == 9
    assert body["remediation"]["skipped"] is False

    items = body["remediation"]["items"]
    assert len(items) == len(wrong_ids)
    returned_ids = {item["question_id"] for item in items}
    assert returned_ids == set(wrong_ids)

    for item in items:
        assert item["fallback"] is False
        assert len(item["citations"]) > 0
        for citation in item["citations"]:
            assert citation["id"]
            assert citation["quote"]


def test_citations_point_to_real_transcript_text():
    answer_key = _quiz_answer_key()
    answers = dict(answer_key)
    answers["q05"] = _wrong_choice(answer_key["q05"])

    resp = client.post("/api/quiz/day01/submit", json={"answers": answers})
    body = resp.json()
    item = body["remediation"]["items"][0]

    for citation in item["citations"]:
        transcript_resp = client.get(f"/api/transcript/{citation['id']}")
        assert transcript_resp.status_code == 200
        chunk = transcript_resp.json()
        assert citation["quote"] in chunk["text"]


def test_remediate_endpoint_matches_submit_shape():
    resp = client.post(
        "/api/remediate",
        json={"quiz_id": "day01", "wrong_question_ids": ["q07"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["skipped"] is False
    assert len(body["items"]) == 1
    assert body["items"][0]["question_id"] == "q07"
    assert body["items"][0]["path"] == "happy"


def test_submit_covers_all_4_paths_when_all_wrong():
    """q01/q09/q10/q11 are engineered (see mock-data) to hit happy,
    low_confidence and no_grounding respectively when marked wrong."""
    answers = {"q01": "A", "q09": "A", "q10": "B", "q11": "A"}
    resp = client.post("/api/quiz/day01/submit", json={"answers": answers})
    assert resp.status_code == 200
    body = resp.json()
    items = body["remediation"]["items"]
    paths = {item["question_id"]: item["path"] for item in items}

    assert paths["q01"] == "happy"
    assert paths["q09"] == "low_confidence"
    assert paths["q10"] == "no_grounding"
    assert paths["q11"] == "low_confidence"

    low_conf_item = next(item for item in items if item["question_id"] == "q09")
    assert len(low_conf_item["hypotheses"]) == 2
    assert low_conf_item["reinforcement"] == []

    no_ground_item = next(item for item in items if item["question_id"] == "q10")
    assert no_ground_item["citations"] == []
    assert no_ground_item["fallback"] is True


def test_remediate_confirm_returns_happy_item_with_reinforcement():
    resp = client.post(
        "/api/remediate/confirm",
        json={"quiz_id": "day01", "question_id": "q09", "hypothesis_id": "h1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["path"] == "happy"
    assert body["hypotheses"] == []
    assert body["fallback"] is False
    assert len(body["reinforcement"]) > 0


def test_remediate_confirm_unknown_question_404():
    resp = client.post(
        "/api/remediate/confirm",
        json={"quiz_id": "day01", "question_id": "qxx", "hypothesis_id": "h1"},
    )
    assert resp.status_code == 404


def test_correction_endpoint_writes_event(tmp_path, monkeypatch):
    from app import main as main_module

    events_file = tmp_path / "events.jsonl"
    monkeypatch.setattr(main_module, "RUNTIME_DIR", tmp_path)
    monkeypatch.setattr(main_module, "EVENTS_PATH", events_file)

    resp = client.post(
        "/api/correction",
        json={"quiz_id": "day01", "question_id": "q01", "action": "misclick"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

    lines = events_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["type"] == "correction"
    assert event["question_id"] == "q01"
    assert event["action"] == "misclick"


def test_ta_ticket_endpoint_writes_event(tmp_path, monkeypatch):
    from app import main as main_module

    events_file = tmp_path / "events.jsonl"
    monkeypatch.setattr(main_module, "RUNTIME_DIR", tmp_path)
    monkeypatch.setattr(main_module, "EVENTS_PATH", events_file)

    resp = client.post(
        "/api/ta-ticket",
        json={"quiz_id": "day01", "question_id": "q10", "note": "Chua ro concept nay"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

    lines = events_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["type"] == "ta_ticket"
    assert event["question_id"] == "q10"
    assert event["note"] == "Chua ro concept nay"
