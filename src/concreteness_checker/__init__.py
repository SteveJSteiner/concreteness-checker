"""concreteness-checker package."""

from .analyzer import AnalysisReport, FalseFriend, SentenceReport, analyze_text

__all__ = [
    "AnalysisReport",
    "FalseFriend",
    "SentenceReport",
    "analyze_text",
]