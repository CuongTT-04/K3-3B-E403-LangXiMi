"""LLM interface. ``generate`` never calls the network unless LLM_MODE=gemini.

MockLLM builds a deterministic explanation + reinforcement questions purely
from the retrieved chunks (no API key needed). GeminiLLM calls the real
Gemini REST API via ``httpx`` when ``LLM_MODE=gemini`` and ``GEMINI_API_KEY``
is set; tests mock ``httpx.Client.post`` and never touch the network. If the
key is missing, ``get_llm`` logs a warning and silently falls back to
MockLLM so the demo never breaks for lack of a key. RealLLM is a documented
stub kept for a future non-Gemini provider.
"""
from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
import httpx

load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger(__name__)

GEMINI_URL_TMPL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


def _first_sentence(text: str) -> str:
    """Shortest leading sentence of ``text`` -- always a substring of it."""
    match = re.search(r"^[^.]+\.", text)
    return match.group(0).strip() if match else text.strip()


class LLM:
    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
    ) -> dict:
        raise NotImplementedError


class MockLLM(LLM):
    """Deterministic, no-network mock generation used for the hackathon demo."""

    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
    ) -> dict:
        distractor_pool = distractor_pool or []
        concept = question.get("concept", "")
        misconception = question.get("misconception_hint") or (
            f"Học viên có thể đang hiểu nhầm một phần của khái niệm '{concept}'."
        )

        cited_chunks = chunks[:2]
        citations = [
            {"id": chunk["id"], "quote": _first_sentence(chunk["text"])}
            for chunk in cited_chunks
        ]

        explanation_parts = [
            f"Câu hỏi này liên quan đến khái niệm '{concept}'.",
            misconception,
        ]
        explanation_parts.extend(chunk["text"] for chunk in cited_chunks)
        explanation = " ".join(explanation_parts)

        distractors = [
            c for c in distractor_pool if c.get("concept") != concept
        ]

        reinforcement = []
        for i, chunk in enumerate(cited_chunks):
            wrong_options = distractors[i * 2 : i * 2 + 3]
            options = {"A": _first_sentence(chunk["text"])}
            letters = ["B", "C", "D"]
            for letter, wrong in zip(letters, wrong_options):
                options[letter] = _first_sentence(wrong["text"])
            # Pad with generic distractors if the pool ran short.
            for letter in letters:
                if letter not in options:
                    options[letter] = "Không liên quan đến đoạn trích dẫn này."
            reinforcement.append(
                {
                    "stem": (
                        f"Theo đoạn trích [{chunk['id']}], ý nào sau đây ĐÚNG "
                        f"nhất về khái niệm '{concept}'?"
                    ),
                    "options": options,
                    "answer": "A",
                    "source_id": chunk["id"],
                }
            )

        confidence = 0.9 if len(cited_chunks) >= 2 else 0.6

        return {
            "explanation": explanation,
            "citations": citations,
            "reinforcement": reinforcement,
            "confidence": confidence,
        }


class RealLLM(LLM):
    """Stub for a future non-Gemini provider. Never call the network from here."""

    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
    ) -> dict:
        raise NotImplementedError("Điền LLM_API_KEY và triển khai")


def _build_prompt(question: dict, chunks: List[dict]) -> str:
    concept = question.get("concept", "")
    chunk_lines = "\n".join(f"[{c['id']}] {c['text']}" for c in chunks)
    misconception_hint = question.get("misconception_hint", "")
    hint_line = f"\nGợi ý hiểu nhầm của học viên: {misconception_hint}\n" if misconception_hint else ""
    return (
        "Bạn là trợ giảng AI thông minh chấm bài trắc nghiệm. Dựa CHÍNH XÁC vào các đoạn trích dẫn bài giảng sau (không tự suy diễn hay bịa thêm thông tin ngoài bài giảng), "
        f"hãy giải thích lỗi hiểu nhầm của học viên đối với khái niệm '{concept}' và sinh 1 câu hỏi củng cố.\n"
        f"{hint_line}\n"
        "Hãy trả về DUY NHẤT một JSON object hợp lệ (không kèm markdown ngoài JSON) theo đúng cấu trúc schema sau:\n"
        "{\n"
        '  "explanation": "Lời giải thích rõ ràng, ân cần, chỉ rõ vì sao hiểu nhầm, VIẾT BẰNG TIẾNG VIỆT CÓ ĐẦY ĐỦ DẤU THANH CHUẨN XÁC",\n'
        '  "citations": [{"id": "mã chunk (ví dụ T01-004)", "quote": "câu trích nguyên văn từ đoạn trích dẫn để hệ thống đối chiếu"}],\n'
        '  "reinforcement": [{\n'
        '    "stem": "Câu hỏi trắc nghiệm mới kiểm tra lại hiểu biết, VIẾT BẰNG TIẾNG VIỆT CÓ ĐẦY ĐỦ DẤU THANH",\n'
        '    "options": {\n'
        '      "A": "Đáp án A bằng tiếng Việt có dấu",\n'
        '      "B": "Đáp án B bằng tiếng Việt có dấu",\n'
        '      "C": "Đáp án C bằng tiếng Việt có dấu",\n'
        '      "D": "Đáp án D bằng tiếng Việt có dấu"\n'
        '    },\n'
        '    "answer": "A"|"B"|"C"|"D",\n'
        '    "source_id": "mã chunk tương ứng (phải có trong danh sách citations)"\n'
        '  }],\n'
        '  "confidence": 0.95\n'
        "}\n\n"
        "QUY TẮC BẮT BUỘC:\n"
        "1. NGÔN NGỮ: Toàn bộ nội dung trường 'explanation', 'stem' và 4 lựa chọn trong 'options' BẮT BUỘC PHẢI VIẾT BẰNG TIẾNG VIỆT CÓ DẤU ĐẦY ĐỦ VÀ CHUẨN XÁC (tuyệt đối không viết không dấu).\n"
        "2. KIỂM CHỨNG: Trường 'quote' trong 'citations' phải là một câu sao chép nguyên văn từ đoạn trích dẫn bên dưới để hệ thống kiểm duyệt.\n\n"
        f"Đoạn trích dẫn bài giảng:\n{chunk_lines}"
    )


def _parse_json_text(text: str) -> dict:
    """Best-effort JSON parse -- strips ```json ... ``` fences if present."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        cleaned = re.sub(r"```\s*$", "", cleaned).strip()
    return json.loads(cleaned)


class GeminiLLM(LLM):
    """Calls the real Gemini REST API. Only reachable when a key is set."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
    ) -> dict:
        prompt = _build_prompt(question, chunks)
        url = GEMINI_URL_TMPL.format(model=self.model)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, params={"key": self.api_key}, json=payload)
            resp.raise_for_status()
            body = resp.json()
        text = body["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_json_text(text)


class OpenAICompatibleLLM(LLM):
    """Calls any OpenAI-compatible chat completions API (Groq, OpenRouter, OpenAI, vLLM)."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
    ) -> dict:
        prompt = _build_prompt(question, chunks)
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/CuongTT-04/K3-3B-E403-LangXiMi",
            "X-Title": "LangXiMi Quiz Remediation",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            body = resp.json()
        text = body["choices"][0]["message"]["content"]
        return _parse_json_text(text)


def get_llm() -> LLM:
    mode = os.environ.get("LLM_MODE", "").strip().lower()
    if not mode:
        if os.environ.get("OPENROUTER_API_KEY"):
            mode = "openrouter"
        elif os.environ.get("GROQ_API_KEY"):
            mode = "groq"
        elif os.environ.get("GEMINI_API_KEY"):
            mode = "gemini"
        elif os.environ.get("LLM_API_KEY"):
            mode = "openai"
        else:
            mode = "mock"

    if mode == "mock":
        return MockLLM()
    if mode == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            logging.warning(
                "LLM_MODE=gemini nhung thieu GEMINI_API_KEY -- roi ve MockLLM."
            )
            return MockLLM()
        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        return GeminiLLM(api_key, model)
    if mode in ("groq", "openrouter", "openai", "real"):
        if mode == "groq":
            api_key = os.environ.get("GROQ_API_KEY", "").strip() or os.environ.get("LLM_API_KEY", "").strip()
            model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
            base_url = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        elif mode == "openrouter":
            api_key = os.environ.get("OPENROUTER_API_KEY", "").strip() or os.environ.get("LLM_API_KEY", "").strip()
            model = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
            base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        else:
            api_key = os.environ.get("LLM_API_KEY", "").strip()
            model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
            base_url = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")

        if not api_key:
            logging.warning(f"LLM_MODE={mode} nhung thieu API key -- roi ve MockLLM.")
            return MockLLM()
        return OpenAICompatibleLLM(api_key=api_key, base_url=base_url, model=model)
    raise ValueError(f"Unknown LLM_MODE: {mode}")
