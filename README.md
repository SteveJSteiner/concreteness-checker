# concreteness-checker

Detect false concreteness in prose.

## Prerequisite

[uv](https://docs.astral.sh/uv/getting-started/installation/)

## Usage

```bash
uvx --from git+https://github.com/SteveJSteiner/concreteness-checker concreteness-checker analyze --file doc.md
uvx --from git+https://github.com/SteveJSteiner/concreteness-checker concreteness-checker analyze --text "The pipeline handles edge cases."
cat doc.md | uvx --from git+https://github.com/SteveJSteiner/concreteness-checker concreteness-checker analyze
```
