"""Chunk retrieval: prefer explicit source_ids, fall back to keyword overlap.

No vector DB (see plan.md decision log) -- good enough to explain to judges
in a 39h hackathon, same ``retrieve(concept, source_ids) -> chunks`` shape
can be swapped for BM25/embeddings later.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

_WORD_RE = re.compile(r"[a-zA-Z0-9]+")


def _tokenize(text: str) -> set:
    return set(_WORD_RE.findall(text.lower()))


def retrieve_with_confidence(
    concept: str,
    source_ids: List[str],
    lessons_by_id: Dict[str, dict],
    all_lessons: List[dict],
    limit: int = 3,
) -> Tuple[List[dict], float]:
    """Return the chunks backing a question's concept plus a 0..1 confidence.

    1. If any of ``source_ids`` exist in the index, return those (in order)
       with confidence 1.0 -- the question author explicitly grounded it.
    2. Otherwise score every chunk by keyword overlap between ``concept``
       and the chunk's concept/text, keep the top ``limit``. Confidence is
       the fraction of the concept's own keywords that show up in the
       best-matching chunk (concept field + text combined).
    3. If nothing matches at all, return ([], 0.0) so callers can fall back.
    """
    found = [lessons_by_id[sid] for sid in source_ids if sid in lessons_by_id]
    if found:
        return found, 1.0

    concept_tokens = _tokenize(concept.replace("_", " "))
    if not concept_tokens:
        return [], 0.0

    scored = []
    for chunk in all_lessons:
        chunk_concept_tokens = _tokenize(chunk["concept"].replace("_", " "))
        chunk_text_tokens = _tokenize(chunk["text"])
        concept_overlap = len(concept_tokens & chunk_concept_tokens)
        text_overlap = len(concept_tokens & chunk_text_tokens)
        score = 2 * concept_overlap + text_overlap
        if score > 0:
            overlap_tokens = concept_tokens & (chunk_concept_tokens | chunk_text_tokens)
            ratio = len(overlap_tokens) / len(concept_tokens)
            scored.append((score, ratio, chunk))

    if not scored:
        return [], 0.0

    scored.sort(key=lambda triple: -triple[0])
    top = scored[:limit]
    chunks = [chunk for _, _, chunk in top]
    confidence = top[0][1]
    return chunks, confidence


def retrieve(
    concept: str,
    source_ids: List[str],
    lessons_by_id: Dict[str, dict],
    all_lessons: List[dict],
    limit: int = 3,
) -> List[dict]:
    """Backwards-compatible chunks-only lookup. See ``retrieve_with_confidence``."""
    chunks, _confidence = retrieve_with_confidence(
        concept, source_ids, lessons_by_id, all_lessons, limit
    )
    return chunks
