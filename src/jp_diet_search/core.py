from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from .exceptions import (
    DietSearchAPIError,
    DietSearchRequestError,
    DietSearchRateLimitError,
    DietSearchParseError,
)

BASE_URL = "https://kokkai.ndl.go.jp/api"


class _DietCore:
    """Internal HTTP + cache + pagination core.

    Public surface of the package should be provided via DietClient + endpoint objects.
    This core intentionally returns *raw JSON dicts* (no response models).
    """

    def __init__(
            self,
            *,
            base_url: str = BASE_URL,
            user_agent: str = "jp-diet-search",
            timeout: float = 20.0,
            sleep_seconds: float = 0.0,
            cache_dir: str | Path | None = None,
            session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.timeout = timeout
        self.sleep_seconds = sleep_seconds

        if cache_dir is not None:
            self.cache_dir = Path(cache_dir).expanduser()
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.cache_dir = None

        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    # ---------------- cache ----------------

    def _cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        payload = {"endpoint": endpoint, "params": dict(sorted(params.items(), key=lambda kv: kv[0]))}
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"{digest}.json"

    def _load_from_cache(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self.cache_dir is None:
            return None
        cache_file = self.cache_dir / self._cache_key(endpoint, params)
        if not cache_file.exists():
            return None
        try:
            with cache_file.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _save_to_cache(self, endpoint: str, params: Dict[str, Any], data: Dict[str, Any]) -> None:
        if self.cache_dir is None:
            return
        cache_file = self.cache_dir / self._cache_key(endpoint, params)
        try:
            with cache_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception:
            # cache failures should never break the client
            return

    # ---------------- request ----------------

    def _request_json(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        cached = self._load_from_cache(endpoint, params)
        if cached is not None:
            return cached

        try:
            r = self.session.get(endpoint, params=params, timeout=self.timeout)
        except requests.RequestException as e:
            raise DietSearchRequestError(f"Request failed: {e}") from e

        # 🔹 NEW: rate limit handling
        if r.status_code == 429:
            body = (r.text or "").strip()
            raise DietSearchRateLimitError(
                f"HTTP 429 (rate limit exceeded) for {endpoint}",
                [body[:500]] if body else None,
            )

        # existing API error handling (unchanged semantics)
        if r.status_code != 200:
            body = (r.text or "").strip()
            raise DietSearchAPIError(
                f"HTTP {r.status_code} for {endpoint}",
                [body[:500]] if body else None,
            )

        # 🔹 NEW: parse-specific exception
        try:
            data = r.json()
        except Exception as e:
            raise DietSearchParseError(
                f"Failed to parse JSON response: {e}"
            ) from e

        self._save_to_cache(endpoint, params, data)
        return data

    # ---------------- validation helpers ----------------

    def check_required_any_condition(self, params: Dict[str, Any]) -> None:
        """Match the original behavior: at least one search condition is required."""
        keys = {
            "nameOfHouse",
            "nameOfMeeting",
            "any",
            "speaker",
            "from",
            "until",
            "speechNumber",
            "speakerPosition",
            "speakerGroup",
            "speakerRole",
            "speechID",
            "issueID",
            "sessionFrom",
            "sessionTo",
            "issueFrom",
            "issueTo",
        }
        if not any(k in params and params[k] not in ("", None) for k in keys):
            # keep message compatible with earlier client.py
            raise DietSearchAPIError("検索条件を指定してください。", [])

    @staticmethod
    def sanitize_limit(limit_total: Optional[int]) -> Optional[int]:
        if limit_total is None:
            return None
        try:
            value = int(limit_total)
        except (TypeError, ValueError):
            raise DietSearchRequestError(f"limit_total must be an int: {limit_total!r}")
        if value <= 0:
            raise DietSearchRequestError(f"limit_total must be positive: {value}")
        return value

    # ---------------- pagination search ----------------

    def search_records(
            self,
            *,
            endpoint: str,
            record_key: str,
            params: Dict[str, Any],
            limit_total: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Fetch pages and aggregate records.

        Returns a dict:
          - endpoint, params
          - totalRecords (if present)
          - retrievedRecords
          - pages
          - records: list[dict]
        """
        self.check_required_any_condition(params)
        limit_total = self.sanitize_limit(limit_total)

        all_records: List[Dict[str, Any]] = []
        pages = 0
        total_records = None

        # Work on a copy so caller's dict isn't mutated
        cur_params = dict(params)

        while True:
            pages += 1
            data = self._request_json(endpoint, cur_params)

            if total_records is None:
                total_records = data.get("totalRecords")

            raw_records = data.get(record_key, []) or []
            if not isinstance(raw_records, list):
                raise DietSearchRequestError(f"Unexpected '{record_key}' shape: {type(raw_records)}")

            for rec in raw_records:
                if isinstance(rec, dict):
                    all_records.append(rec)
                else:
                    # keep non-dict as-is but wrap
                    all_records.append({"value": rec})

                if limit_total is not None and len(all_records) >= limit_total:
                    all_records = all_records[:limit_total]
                    return {
                        "endpoint": endpoint,
                        "params": params,
                        "totalRecords": total_records,
                        "retrievedRecords": len(all_records),
                        "pages": pages,
                        "records": all_records,
                        "truncated": True,
                    }

            next_pos = data.get("nextRecordPosition")
            if not next_pos:
                break

            cur_params["startRecord"] = next_pos

            if self.sleep_seconds:
                time.sleep(self.sleep_seconds)

        return {
            "endpoint": endpoint,
            "params": params,
            "totalRecords": total_records,
            "retrievedRecords": len(all_records),
            "pages": pages,
            "records": all_records,
            "truncated": False,
        }
