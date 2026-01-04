# jp-diet-search

[![PyPI](https://img.shields.io/pypi/v/jp-diet-search.svg)](https://pypi.org/project/jp-diet-search/)
[![Python](https://img.shields.io/pypi/pyversions/jp-diet-search.svg)](https://pypi.org/project/jp-diet-search/)
[![License](https://img.shields.io/pypi/l/jp-diet-search.svg)](LICENSE)


Python client for the National Diet Library **Kokkai Kaigiroku Kensaku System**
(国会会議録検索システム).

This package provides:

- A **plain-vanilla Object API** for programmatic access
- Robust error handling and safe pagination
- No heavy dependencies or hidden magic

---

## Features

### Python Object API

- Explicit endpoint objects:
  - `client.meeting_list`
  - `client.meeting`
  - `client.speech`
- Typed query objects (`MeetingListQuery`, `MeetingQuery`, `SpeechQuery`)
- Automatic pagination with optional total caps
- Optional on-disk caching

---

## Installation

For development:

```bash
pip install -e .
```

For normal use (after PyPI release):

```bash
pip install jp-diet-search
```

---

## Development Workflow

```bash
python -m compileall src   # Verify syntax
pip install -e .           # Install in editable mode
pytest                     # Run tests
```

---

## Python API (Object API)

### Basic usage

```python
from jp_diet_search import DietClient
from jp_diet_search.queries import SpeechQuery

client = DietClient(cache_dir=".cache")

query = SpeechQuery(
    any="科学技術",
    maximum_records=100,
)

result = client.speech.search(query, limit_total=5)

print(result["numberOfRecords"])
for record in result.get("records", []):
    print(record.get("speaker"), record.get("date"))
```

### Endpoint overview

```python
client.meeting_list.search(MeetingListQuery(...))
client.meeting.search(MeetingQuery(...))
client.speech.search(SpeechQuery(...))
```

Returned values are **raw JSON dictionaries** aggregated across pages.

---

## Project Structure

```
jp-diet-search/
  src/
    jp_diet_search/
      __init__.py
      client.py
      core.py
      endpoints.py
      queries.py
      cli.py
      exceptions.py
      models.py   # reserved (currently unused)
  tests/
  README.md
  pyproject.toml
  Makefile
```

---

## Design Notes

- The public API avoids `**kwargs` bags in favor of explicit query objects.
- Internal HTTP and pagination logic lives in a dedicated core layer.
- `models.py` is intentionally unused for now; responses are returned as raw JSON.
- Console scripts are the primary execution model (no `python -m` required).

---

## License

MIT License.
