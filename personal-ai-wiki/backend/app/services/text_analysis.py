"""Query analysis for keyword search over Korean and English text.

FTS5's trigram tokenizer gives substring matching (good for Korean, where
particles glue onto nouns: 프로젝트를, 프로젝트의 ...), but cannot match terms
shorter than 3 characters. The search service therefore needs clean, short
terms: we strip common particles and endings and drop filler words. Because
matching is substring based, over-stripping only broadens a match; it never
hides a document.
"""

from __future__ import annotations

import re
import unicodedata

_TOKEN_RE = re.compile(r"[0-9A-Za-z가-힣][0-9A-Za-z가-힣_+#.\-]*")

# Longest first so "에서는" wins over "는".
_SUFFIXES = sorted(
    [
        "으로부터", "에서부터", "하는지", "했는지", "는지", "인지", "이었는데", "했었는데", "하려면", "하는데", "했는데", "했나요", "했어요", "합니다",
        "입니다", "인가요", "인지요", "있나요", "없나요", "해줘요", "해주세요", "해줘", "하나요", "할까요",
        "에게서", "한테서", "으로써", "으로서", "이라고", "에서는", "에서도", "까지는", "부터는", "에게는",
        "이에요", "예요", "에서", "에게", "한테", "께서", "으로", "이랑", "부터", "까지", "처럼", "보다",
        "마다", "조차", "라고", "이나", "이며", "이고", "에는", "과는", "와는", "하는", "하기", "했던",
        "하고", "해서", "하면", "했다", "한다", "인데", "이야", "은", "는", "이", "가", "을", "를", "에",
        "의", "로", "와", "과", "도", "만", "랑", "요",
    ],
    key=len,
    reverse=True,
)

_STOPWORDS = {
    # Korean filler / question words
    "무엇", "뭐", "뭐야", "뭔가", "어떻게", "어떤", "왜", "언제", "어디", "누구", "알려줘", "알려", "설명",
    "설명해줘", "대해", "대해서", "관련", "관련된", "있는", "없는", "그리고", "그런데", "하지만", "그",
    "이것", "저것", "그것", "좀", "정말", "그냥", "내가", "나의", "제가", "저의", "우리", "지금", "혹시",
    "해줘", "주세요", "있어", "있니", "있나", "없어", "같은", "하는", "되는", "된", "할", "수",
    # English
    "the", "a", "an", "is", "are", "was", "were", "what", "how", "why", "when", "where", "who", "of", "to",
    "in", "on", "for", "and", "or", "do", "does", "did", "i", "me", "my", "you", "it", "this", "that",
    "about", "please", "tell", "explain",
}

MAX_TERMS = 8


def _is_hangul(word: str) -> bool:
    return all("가" <= ch <= "힣" for ch in word)


def strip_korean_suffix(word: str) -> str:
    if not _is_hangul(word):
        return word
    for suffix in _SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 2:
            return word[: -len(suffix)]
    return word


def analyze_query(query: str) -> list[str]:
    """Return lowercase search terms (deduplicated, at most MAX_TERMS)."""
    text = unicodedata.normalize("NFC", query).lower()
    terms: list[str] = []
    for raw in _TOKEN_RE.findall(text):
        raw = raw.strip(".-")
        if not raw or raw in _STOPWORDS:
            continue
        term = strip_korean_suffix(raw)
        if term in _STOPWORDS or len(term) < 2:
            continue
        if term not in terms:
            terms.append(term)
        if len(terms) >= MAX_TERMS:
            break
    return terms
