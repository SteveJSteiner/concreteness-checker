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

Two-pass detection of false concreteness.

## Pass 1 — run the tool

```bash
uvx --from git+https://github.com/SteveJSteiner/concreteness-checker concreteness-checker analyze --file document.md
```

## How to read the output

- **Surface concreteness**: the raw average concreteness score of the scored content words in the text
- **Grounded concreteness**: the same average after flagged false friends are discounted to a low grounding score
- **Concreteness gap**: `surface - grounded`; a larger gap means the prose sounds more concrete than it really is
- **False friends**: words with concrete sensory associations that are probably being used metaphorically in context
- **Vocabulary coverage**: how much of the text matched the built-in norms lexicon

Key numbers:
- Gap > 0.3: metaphorical inflation
- Surface > 3.5, Grounded < 3.0: THE DANGEROUS ZONE — sounds concrete, isn't
- Surface < 2.5: overtly abstract (honest about it)
- Multiple false friends in one sentence: likely metaphor-saturated prose rather than genuinely sensory description

## Pass 2 — interrogate flagged sentences

For each flagged sentence, the LLM attempts:

1. **Name a specific instance** — not a type, an actual one
2. **Describe what you'd observe** — what changes, in what order
3. **State a falsifying condition** — what would make this wrong

Grade each:
- **Grounded**: all three succeed with specifics
- **Metaphorically grounded**: instance exists but observation is figurative  
- **Floating**: instance attempt produces another type-level description
- **Load-bearing vague**: does real argumentative work but specifics unresolvable

Example:
CLAIM: "The settlement machinery handles topology changes through witness tokens."
Instance: [attempt] → "When a SeamClaim changes from Admissible to Promoted..."
Observation: [attempt] → "the witness token records which GraspContext evaluated it"
Falsification: "If you replayed without that context, the Promoted field would be empty"
Grade: METAPHORICALLY GROUNDED — "machinery" and "handles" are figurative but the
instance is real and the falsification works.

## Calibration note

The tool is deliberately aggressive. It is designed to over-flag metaphorical concreteness so an LLM can inspect suspicious sentences rather than trust the surface wording.

Dead metaphors such as "thread pool", "pipeline", or "layer" may be perfectly acceptable for a given technical audience. A flag is not automatically a defect; it is a prompt to check whether the sentence cashes out in specifics.