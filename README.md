# pytranslate

Translate files for free using different APIs

## Requirements

- Python 3.12+

## Installation

```bash
python -m pip install uv
uv venv .venv && . .venv/bin/activate
uv sync --frozen
```

## Supported
### File extension
- ASS (Advanced Substation Alpha)

### API

- Google
- Deepl

## Docker

```bash
docker run -it --rm -v /path/to/file.ass:/app/file.ass ghcr.io/maxime1907/pytranslate:master
```
