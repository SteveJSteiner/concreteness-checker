from __future__ import annotations

import json
from pathlib import Path
import sys

import click

from .analyzer import AnalysisReport, analyze_text
from .norms import NORMS


def _read_input(filepath: str | None, text: str | None) -> str:
    if filepath and text:
        raise click.UsageError("Use either --file or --text, not both.")
    if filepath:
        return Path(filepath).read_text(encoding="utf-8")
    if text is not None:
        return text
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise click.UsageError("Provide --file, --text, or pipe text on stdin.")


def _render_summary(report: AnalysisReport) -> str:
    if report.total_sentences == 1 and report.sentences:
        sentence = report.sentences[0]
        gap = sentence.surface_concreteness - sentence.grounded_concreteness
        if gap > 0.30 and sentence.false_friends:
            return f"This sentence sounds concrete but isn't — the gap of {gap:.2f} is the signal."
        if sentence.surface_concreteness < 2.5:
            return "This sentence is overtly abstract. No false friends — it doesn't pretend to be concrete."
    text_gap = report.text_surface_concreteness - report.text_grounded_concreteness
    if not report.false_friends and text_gap <= 0.05:
        return "No false friends. No gap. Genuinely concrete."
    if report.false_friends:
        return "Flagged sentences have metaphorically inflated surface concreteness."
    return "No major false-concreteness signal detected."


def _format_text(report: AnalysisReport) -> str:
    gap = report.text_surface_concreteness - report.text_grounded_concreteness
    lines = [
        "============================================================",
        "CONCRETENESS ANALYSIS",
        "============================================================",
        "",
        f"Surface concreteness:  {report.text_surface_concreteness:.2f} / 5.00",
        f"Grounded concreteness: {report.text_grounded_concreteness:.2f} / 5.00",
    ]
    if gap > 0.01:
        lines.append(f"Concreteness gap:      {gap:.2f}")
    lines.extend(
        [
            f"Vocabulary coverage:   {report.coverage * 100:.0f}%",
            f"Sentences analyzed:    {report.scored_sentences} / {report.total_sentences}",
            "",
            "------------------------------------------------------------",
            "PER-SENTENCE SCORES (abbreviated)",
            "------------------------------------------------------------",
        ]
    )

    for sentence in report.sentences:
        lines.append(f"  [{sentence.surface_concreteness:.1f}/{sentence.grounded_concreteness:.1f}]  {sentence.text}")

    if report.false_friends:
        lines.extend(
            [
                "",
                "------------------------------------------------------------",
                f"FALSE FRIENDS ({len(report.false_friends)} found)",
                "------------------------------------------------------------",
            ]
        )
        for friend in report.false_friends:
            lines.append(f"  '{friend.word}' (raw: {friend.concreteness:.1f}) — {friend.reason}")

    lines.extend(["", _render_summary(report)])
    return "\n".join(lines)


@click.group()
def main() -> None:
    """Detect false concreteness in prose."""


@main.command(name="analyze")
@click.option("filepath", "--file", "-f", type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option("text", "--text", "-t", type=str)
@click.option("fmt", "--format", type=click.Choice(["text", "json"], case_sensitive=False), default="text", show_default=True)
def analyze_cmd(filepath: str | None, text: str | None, fmt: str) -> None:
    """Score prose for false concreteness."""
    source = _read_input(filepath, text)
    report = analyze_text(source)
    if fmt == "json":
        click.echo(json.dumps(report.to_dict(), indent=2))
        return
    click.echo(_format_text(report))


@main.command()
def stats() -> None:
    """Print aggregate information about the bundled norms."""
    bands = {
        "4.5-5.0": 0,
        "4.0-4.49": 0,
        "3.0-3.99": 0,
        "2.0-2.99": 0,
        "1.0-1.99": 0,
    }
    total = 0.0
    for score in NORMS.values():
        total += score
        if score >= 4.5:
            bands["4.5-5.0"] += 1
        elif score >= 4.0:
            bands["4.0-4.49"] += 1
        elif score >= 3.0:
            bands["3.0-3.99"] += 1
        elif score >= 2.0:
            bands["2.0-2.99"] += 1
        else:
            bands["1.0-1.99"] += 1

    click.echo(f"total words: {len(NORMS)}")
    for label, count in bands.items():
        click.echo(f"{label}: {count}")
    click.echo(f"mean score: {total / len(NORMS):.2f}")


if __name__ == "__main__":
    main()