from __future__ import annotations

from dataclasses import asdict, dataclass
import re

from .norms import KNOWN_METAPHOR_DONORS, NORMS, lookup_norm


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "but", "by", "for",
    "from", "had", "has", "have", "he", "her", "hers", "him", "his", "i", "if", "in",
    "into", "is", "it", "its", "itself", "me", "my", "myself", "no", "not", "of", "on",
    "or", "our", "ours", "ourselves", "she", "so", "than", "that", "the", "their", "theirs",
    "them", "themselves", "then", "there", "these", "they", "this", "those", "through", "to",
    "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which",
    "while", "who", "whom", "why", "will", "with", "you", "your", "yours", "yourself",
    "yourselves", "over", "between", "each", "own",
}

SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?", re.MULTILINE)
WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


@dataclass
class FalseFriend:
    word: str
    concreteness: float
    reason: str
    sentence: str


@dataclass
class SentenceReport:
    text: str
    surface_concreteness: float
    grounded_concreteness: float
    scored_words: int
    total_content_words: int
    coverage: float
    false_friends: list[FalseFriend]


@dataclass
class AnalysisReport:
    text_surface_concreteness: float
    text_grounded_concreteness: float
    total_sentences: int
    scored_sentences: int
    coverage: float
    false_friends: list[FalseFriend]
    sentences: list[SentenceReport]
    most_deceptive: list[SentenceReport]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class _TokenScore:
    index: int
    word: str
    score: float
    donor: bool


def _split_sentences(text: str) -> list[str]:
    return [part.strip() for part in SENTENCE_RE.findall(text) if part.strip()]


def _tokenize_content_words(sentence: str) -> list[str]:
    tokens = []
    for match in WORD_RE.finditer(sentence):
        token = match.group(0).lower().replace("'s", "")
        if len(token) <= 1 or token in STOPWORDS:
            continue
        tokens.append(token)
    return tokens


def _scored_tokens(tokens: list[str]) -> list[_TokenScore]:
    scored: list[_TokenScore] = []
    for index, token in enumerate(tokens):
        score = lookup_norm(token, NORMS)
        if score is None:
            continue
        scored.append(_TokenScore(index=index, word=token, score=score, donor=token in KNOWN_METAPHOR_DONORS))
    return scored


def _neighbor_reason(token: _TokenScore, scored: list[_TokenScore]) -> str | None:
    nearby = [candidate.score for candidate in scored if candidate is not token and abs(candidate.index - token.index) <= 2]
    if not nearby:
        return None
    average = sum(nearby) / len(nearby)
    if average < 2.8:
        return f"low-concreteness neighborhood (avg {average:.2f} across nearby content words)"
    return None


def analyze_sentence(sentence: str) -> SentenceReport:
    tokens = _tokenize_content_words(sentence)
    scored = _scored_tokens(tokens)
    total_content = len(tokens)
    scored_words = len(scored)
    coverage = scored_words / total_content if total_content else 0.0

    if not scored:
        return SentenceReport(
            text=sentence,
            surface_concreteness=0.0,
            grounded_concreteness=0.0,
            scored_words=0,
            total_content_words=total_content,
            coverage=coverage,
            false_friends=[],
        )

    donor_tokens = [token for token in scored if token.donor]
    donor_ratio = len(donor_tokens) / scored_words
    flagged: dict[tuple[int, str], FalseFriend] = {}

    if donor_ratio > 0.30 and donor_tokens:
        reason = f"metaphor-saturated sentence ({len(donor_tokens)} concrete metaphors in {scored_words} scored words)"
        for token in donor_tokens:
            flagged[(token.index, token.word)] = FalseFriend(
                word=token.word,
                concreteness=token.score,
                reason=reason,
                sentence=sentence,
            )
    else:
        for token in donor_tokens:
            reason = _neighbor_reason(token, scored)
            if reason is None:
                continue
            flagged[(token.index, token.word)] = FalseFriend(
                word=token.word,
                concreteness=token.score,
                reason=reason,
                sentence=sentence,
            )

    surface = sum(token.score for token in scored) / scored_words
    grounded_total = 0.0
    for token in scored:
        grounded_total += 2.0 if (token.index, token.word) in flagged else token.score
    grounded = grounded_total / scored_words

    return SentenceReport(
        text=sentence,
        surface_concreteness=surface,
        grounded_concreteness=grounded,
        scored_words=scored_words,
        total_content_words=total_content,
        coverage=coverage,
        false_friends=list(flagged.values()),
    )


def analyze_text(text: str) -> AnalysisReport:
    sentences = [analyze_sentence(sentence) for sentence in _split_sentences(text)]
    scored_sentences = [sentence for sentence in sentences if sentence.scored_words > 0]
    total_weight = sum(sentence.scored_words for sentence in scored_sentences)
    if total_weight:
        surface = sum(sentence.surface_concreteness * sentence.scored_words for sentence in scored_sentences) / total_weight
        grounded = sum(sentence.grounded_concreteness * sentence.scored_words for sentence in scored_sentences) / total_weight
    else:
        surface = 0.0
        grounded = 0.0

    total_content_words = sum(sentence.total_content_words for sentence in sentences)
    total_scored_words = sum(sentence.scored_words for sentence in sentences)
    false_friends = [friend for sentence in sentences for friend in sentence.false_friends]

    return AnalysisReport(
        text_surface_concreteness=surface,
        text_grounded_concreteness=grounded,
        total_sentences=len(sentences),
        scored_sentences=len(scored_sentences),
        coverage=(total_scored_words / total_content_words) if total_content_words else 0.0,
        false_friends=false_friends,
        sentences=sentences,
        most_deceptive=sorted(
            scored_sentences,
            key=lambda sentence: sentence.surface_concreteness - sentence.grounded_concreteness,
            reverse=True,
        )[:5],
    )