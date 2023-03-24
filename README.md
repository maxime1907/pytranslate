# pytranslate

Free translation service using different APIs

## Requirements

- Python 3.10+

## Installation

```bash
python3 -m venv .venv
. venv/bin/activate
pip install -r requirements.txt
pip install -e .
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
