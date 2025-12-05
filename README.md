# jp-diet-search

Python client & CLI for the National Diet Library "Kokkai Kaigiroku Kensaku System" (国会会議録検索システム).

## Features

- High-level Python client with Pydantic models  
- Automatic pagination handling  
- Safe exploration tools:
  - `--dry-run` (metadata only)
  - `--limit-total N` (cap total collected results)
  - `--since YYYY` (shortcut for `--from YYYY-01-01`)
- Multiple output formats:
  - JSON
  - JSONL
  - CSV
- Optional on-disk caching (`--cache-dir`)
- Full CLI:
  - `speech`
  - `meeting`
  - `meeting-list`

---

## Installation

```bash
pip install -e .
```

---

## Development Workflow

```bash
python -m compileall src   # Step 1: verify syntax for entire project
pip install -e .           # Step 2: install
pytest                     # Step 3: run tests
```

---

## CLI Usage

### Basic search

```bash
jp-diet-search speech --any 科学技術 --limit-total 10 --pretty
```

### Dry-run (safe size check)

```bash
jp-diet-search speech --any 科学技術 --dry-run
```

Output example:

```json
{
  "numberOfRecords": 75644,
  "note": "dry-run: records not included"
}
```

### Since shortcut

```bash
jp-diet-search speech --any 科学技術 --since 2024 --dry-run
```

Equivalent to:

```bash
--from 2024-01-01
```

### CSV output

```bash
jp-diet-search speech --any 科学技術 --limit-total 5 --format csv > result.csv
```

### Use caching

```bash
jp-diet-search speech --any 科学技術 --cache-dir .cache_jp_diet --limit-total 20
```

---

## Python API

```python
from jp_diet_search import DietSearchClient

client = DietSearchClient(cache_dir=".cache")

res = client.search_speech(any="科学技術", limit_total=5)

print(res.number_of_records)
for s in res.records:
    print(s.speaker, s.date)
```

---

## Project Structure

```
jp-diet-search/
  src/
    jp_diet_search/
      client.py
      cli.py
      models.py
      exceptions.py
  tests/
  README.md
  pyproject.toml
  Makefile
```

---

## License

MIT License.
