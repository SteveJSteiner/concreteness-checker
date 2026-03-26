---
name: concreteness-checker
description: |
  Detect false concreteness in prose. Use when reviewing writing for clarity,
  checking if text is genuinely concrete vs metaphorically inflated, or when
  asked "is this too abstract?", "am I being concrete enough?", "does this
  actually say anything specific?" Trigger for essays, design docs, architecture
  descriptions, philosophical arguments, READMEs, PRDs.
---

# Concreteness Checker

Scores prose for false concreteness: text that sounds grounded through physical metaphor but contains no observable referent. Returns per-sentence concreteness scores and a list of suspect words.

## Commands

Analyze a file:

```bash
uvx --from git+https://github.com/SteveJSteiner/concreteness-checker concreteness-checker analyze --file document.md
```

Analyze a passage directly:

```bash
uvx --from git+https://github.com/SteveJSteiner/concreteness-checker concreteness-checker analyze --text "The pipeline handles edge cases through a layered filter."
```

Pipe text on stdin:

```bash
cat document.md | uvx --from git+https://github.com/SteveJSteiner/concreteness-checker concreteness-checker analyze
```

Get machine-readable output:

```bash
uvx --from git+https://github.com/SteveJSteiner/concreteness-checker concreteness-checker analyze --file document.md --format json
```

## Interpreting output

The tool reports:

- **Surface concreteness**: raw average concreteness score (1–5) of scored content words
- **Grounded concreteness**: same average after false friends are discounted to 2.0
- **Concreteness gap**: surface minus grounded; larger gap means prose sounds more concrete than it is
- **Vocabulary coverage**: fraction of content words matched in the built-in norms lexicon
- **False friends**: high-concreteness words (pipeline, handle, layer, bridge, …) appearing in a metaphor-dense context

Key thresholds:

- Gap > 0.3: likely metaphorical inflation
- Surface > 3.5 and Grounded < 3.0: dangerous zone — sounds concrete, isn't
- Surface < 2.5: overtly abstract (honest about it)
- Multiple false friends in one sentence: prose is probably metaphor-saturated

Relay to the user: the summary line, the concreteness gap value, and each false friend with its sentence.

## Pass 2: interrogating flagged sentences

The tool flags suspect sentences. Interrogating them is your job. For each flagged sentence:

1. **Name a specific instance** — not a type, an actual one
2. **Describe what you would observe** — what changes, in what order
3. **State a falsifying condition** — what would make the claim wrong

Grade each:

- **Grounded**: all three succeed with specifics
- **Metaphorically grounded**: the instance exists but the observation is figurative
- **Floating**: the instance attempt produces another type-level description
- **Load-bearing vague**: does real argumentative work but specifics are unresolvable

## Error handling

- `Error: Invalid value for '--file'` — the path does not exist; check it
- `Error: Provide --file, --text, or pipe text on stdin.` — no input was given; supply one of the three
- `Error: Use either --file or --text, not both.` — remove one of the two options

## What not to do

- Do not run Pass 2 through the tool; it has no LLM component
- Do not treat every flag as a defect — dead metaphors ("thread pool", "pipeline") may be appropriate for a technical audience; a flag is a prompt to check whether the sentence cashes out in specifics
- Do not supply both `--file` and `--text` in the same invocation
