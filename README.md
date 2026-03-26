# concreteness-checker

Detect false concreteness in prose.

False concreteness is text that sounds grounded — because it uses words like *pipeline*, *handle*, *layer*, *bridge* — but contains no observable referent. The writing feels concrete. Nothing in it is. This tool finds it.

## Prerequisite

[uv](https://docs.astral.sh/uv/getting-started/installation/)

## Usage

```bash
# Analyze a file
uvx --from git+https://github.com/SteveJSteiner/concreteness-checker concreteness-checker analyze --file doc.md

# Analyze a passage directly
uvx --from git+https://github.com/SteveJSteiner/concreteness-checker concreteness-checker analyze --text "The pipeline handles edge cases through a layered filter."

# Pipe text on stdin
cat doc.md | uvx --from git+https://github.com/SteveJSteiner/concreteness-checker concreteness-checker analyze

# Machine-readable output
uvx --from git+https://github.com/SteveJSteiner/concreteness-checker concreteness-checker analyze --file doc.md --format json
```

## How it works

### Pass 1 — the tool

The tool runs a lexical concreteness analysis. Every content word in the text is looked up in a bundled norms lexicon of ~8,000 words. Each word has a score from 1 (purely abstract: *ontology*, *sufficiency*) to 5 (directly perceivable: *dog*, *chair*, *brick*). Words not in the lexicon are skipped.

Two averages are computed:

- **Surface concreteness**: the raw average of scored words
- **Grounded concreteness**: the same average, but with *false friends* discounted to 2.0

A *false friend* is a word with a high concreteness score that is probably being used metaphorically. The tool identifies false friends using a list of known metaphor donors — words like *pipeline*, *handle*, *thread*, *layer*, *bridge*, *hook*, *root*, *stack*, *scaffold* — and checks whether they appear in a metaphor-saturated context. Two triggers:

1. More than 30% of the scored words in a sentence are metaphor donors
2. A metaphor donor appears in a neighborhood of low-concreteness words (average score < 2.8 among all scored words within two content-word positions on either side)

The **concreteness gap** (surface minus grounded) is the primary signal. A gap above 0.3 indicates metaphorical inflation. A gap near zero means the surface score is honest.

The tool is deliberately aggressive. It over-flags so you can inspect suspicious sentences rather than trust the surface wording.

### Pass 2 — your job

The tool produces the list; you do the interrogation. For each flagged sentence, attempt:

1. **Name a specific instance** — not a type, an actual one
2. **Describe what you would observe** — what changes, in what order
3. **State a falsifying condition** — what would make the claim wrong

If all three succeed with specifics, the sentence is grounded. If the instance produces another type-level description, the sentence is floating. Not every flag is a defect — dead metaphors like *thread pool* or *pipeline* may be appropriate for a given technical audience.

## Reading the output

```
============================================================
CONCRETENESS ANALYSIS
============================================================

Surface concreteness:  4.06 / 5.00
Grounded concreteness: 2.43 / 5.00
Concreteness gap:      1.63
Vocabulary coverage:   75%
Sentences analyzed:    1 / 1

------------------------------------------------------------
PER-SENTENCE SCORES (abbreviated)
------------------------------------------------------------
  [4.1/2.4]  The pipeline handles edge cases by routing data through a filter layer.

------------------------------------------------------------
FALSE FRIENDS (5 found)
------------------------------------------------------------
  'handles' (raw: 4.6) — metaphor-saturated sentence (5 concrete metaphors in 6 scored words)
  'edge' (raw: 4.1) — metaphor-saturated sentence (5 concrete metaphors in 6 scored words)
  'routing' (raw: 3.2) — metaphor-saturated sentence (5 concrete metaphors in 6 scored words)
  'filter' (raw: 4.2) — metaphor-saturated sentence (5 concrete metaphors in 6 scored words)
  'layer' (raw: 3.7) — metaphor-saturated sentence (5 concrete metaphors in 6 scored words)

This sentence sounds concrete but isn't — the gap of 1.63 is the signal.
```

The per-sentence format is `[surface/grounded]`. Vocabulary coverage below 50% means many words in the text are outside the lexicon — treat the scores as directional, not precise.

Key thresholds:

| Signal | Meaning |
|---|---|
| Gap > 0.3 | Metaphorical inflation |
| Surface > 3.5, Grounded < 3.0 | Dangerous zone — sounds concrete, isn't |
| Surface < 2.5 | Overtly abstract (at least honest about it) |

## Options

```
concreteness-checker analyze [OPTIONS]

  -f, --file FILE          Path to a text or Markdown file
  -t, --text TEXT          Inline text to analyze
      --format [text|json] Output format (default: text)
      --help               Show this message and exit
```

Input may be provided via `--file`, `--text`, or stdin. If you specify `--file` or `--text`, any data on stdin will be ignored.

## Norms lexicon

The bundled lexicon contains 8,078 words (mean score: 3.70). Coverage by band:

| Score range | Words |
|---|---|
| 4.5–5.0 | 2,936 |
| 4.0–4.49 | 1,156 |
| 3.0–3.99 | 1,554 |
| 2.0–2.99 | 1,643 |
| 1.0–1.99 | 789 |

Inflected forms (plurals, past tense, present participle, comparatives, adverbs) are generated automatically from each base form in `norms.py`.
