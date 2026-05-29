from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


POSITIVE_WORDS = {"love", "great", "helpful", "easy", "fast", "clear", "useful"}
NEGATIVE_WORDS = {"slow", "confusing", "broken", "hard", "missing", "error", "bad", "unclear"}
STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "for",
    "of",
    "in",
    "is",
    "it",
    "with",
    "on",
    "we",
    "are",
    "by",
    "when",
    "would",
    "could",
    "should",
    "but",
}


@dataclass(frozen=True)
class Feedback:
    user_id: str
    segment: str
    text: str
    urgency: int
    impact: int


@dataclass(frozen=True)
class Theme:
    label: str
    count: int
    avg_urgency: float
    avg_impact: float
    sentiment: float
    priority_score: float
    examples: tuple[str, ...]


def load_feedback(path: str | Path) -> list[Feedback]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        return [
            Feedback(
                user_id=row["user_id"],
                segment=row["segment"],
                text=row["text"],
                urgency=int(row["urgency"]),
                impact=int(row["impact"]),
            )
            for row in rows
        ]


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    normalized: set[str] = set()
    for word in words:
        if word.endswith("ing") and len(word) > 5:
            word = word[:-3]
            if word.endswith("us"):
                word += "e"
        elif word.endswith("s") and len(word) > 4:
            word = word[:-1]
        if len(word) > 2 and word not in STOPWORDS:
            normalized.add(word)
    return normalized


def sentiment_score(text: str) -> float:
    words = tokenize(text)
    if not words:
        return 0.0
    pos = len(words & POSITIVE_WORDS)
    neg = len(words & NEGATIVE_WORDS)
    return (pos - neg) / max(1, pos + neg)


def _theme_label(items: list[Feedback]) -> str:
    counts: Counter[str] = Counter()
    for item in items:
        counts.update(tokenize(item.text))
    common = [word for word, _ in counts.most_common(3)]
    return " / ".join(common) if common else "general feedback"


def group_feedback(feedback: list[Feedback], overlap_threshold: float = 0.15) -> list[list[Feedback]]:
    groups: list[list[Feedback]] = []
    group_tokens: list[set[str]] = []

    for item in feedback:
        item_tokens = tokenize(item.text)
        best_index = None
        best_overlap = 0.0
        for index, tokens in enumerate(group_tokens):
            overlap = len(item_tokens & tokens) / max(1, len(item_tokens | tokens))
            if overlap > best_overlap:
                best_index = index
                best_overlap = overlap
        if best_index is not None and best_overlap >= overlap_threshold:
            groups[best_index].append(item)
            group_tokens[best_index] |= item_tokens
        else:
            groups.append([item])
            group_tokens.append(set(item_tokens))
    return groups


def prioritize(feedback: list[Feedback]) -> list[Theme]:
    themes: list[Theme] = []
    for group in group_feedback(feedback):
        count = len(group)
        avg_urgency = sum(item.urgency for item in group) / count
        avg_impact = sum(item.impact for item in group) / count
        sentiment = sum(sentiment_score(item.text) for item in group) / count
        segment_bonus = len({item.segment for item in group}) * 0.2
        priority_score = count * 1.5 + avg_urgency + avg_impact + segment_bonus - min(sentiment, 0)
        themes.append(
            Theme(
                label=_theme_label(group),
                count=count,
                avg_urgency=round(avg_urgency, 2),
                avg_impact=round(avg_impact, 2),
                sentiment=round(sentiment, 2),
                priority_score=round(priority_score, 2),
                examples=tuple(item.text for item in group[:2]),
            )
        )
    return sorted(themes, key=lambda theme: theme.priority_score, reverse=True)


def roadmap_markdown(themes: list[Theme], top: int = 5) -> str:
    lines = ["# Prioritized Product Feedback", ""]
    for index, theme in enumerate(themes[:top], start=1):
        lines.append(f"## {index}. {theme.label}")
        lines.append(f"- Priority score: {theme.priority_score}")
        lines.append(f"- Mentions: {theme.count}")
        lines.append(f"- Avg urgency: {theme.avg_urgency}")
        lines.append(f"- Avg impact: {theme.avg_impact}")
        lines.append(f"- Sentiment: {theme.sentiment}")
        lines.append("- Examples:")
        for example in theme.examples:
            lines.append(f"  - {example}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
