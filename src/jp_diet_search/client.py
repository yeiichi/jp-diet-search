from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests
from pydantic import ValidationError

from .exceptions import DietSearchAPIError, DietSearchRequestError
from .models import MeetingListResult, MeetingRecord, SpeechRecord, SpeechSearchResult

BASE_URL = "https://kokkai.ndl.go.jp/api"


class DietSearchClient:
    """
    Client for interacting with the Diet Search API.

    This class provides methods to query different endpoints of the Diet Search API,
    offering functionality for searching meeting lists, detailed meetings, or individual
    speeches. It provides options for caching results locally and manages request handling
    to ensure reliable and efficient access.

    Attributes:
        base_url (str): The base URL of the Diet Search API.
        timeout (float): The timeout in seconds for HTTP requests.
        sleep_seconds (float): The delay in seconds between paginated API requests.
        cache_dir (Optional[Path]): Directory for storing cached API responses. If None, caching is disabled.
    """

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = 10.0,
        user_agent: str = "jp-diet-search/0.1.0",
        sleep_seconds: float = 2.0,
        cache_dir: Optional[Union[str, Path]] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.sleep_seconds = sleep_seconds

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})

        if cache_dir is not None:
            self.cache_dir = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.cache_dir = None

    # --------- public API ---------

    def search_meeting_list(
        self,
        limit_total: Optional[int] = None,
        **params: Any,
    ) -> MeetingListResult:
        """/meeting_list : 会議単位簡易出力（本文なし）"""
        endpoint = f"{self.base_url}/meeting_list"
        return self._search_meetings(
            endpoint=endpoint,
            is_full=False,
            params=params,
            limit_total=limit_total,
        )

    def search_meeting(
        self,
        limit_total: Optional[int] = None,
        **params: Any,
    ) -> MeetingListResult:
        """/meeting : 会議単位出力（会議ごとの全文）"""
        endpoint = f"{self.base_url}/meeting"
        return self._search_meetings(
            endpoint=endpoint,
            is_full=True,
            params=params,
            limit_total=limit_total,
        )

    def search_speech(
        self,
        limit_total: Optional[int] = None,
        **params: Any,
    ) -> SpeechSearchResult:
        """/speech : 発言単位出力（発言ごとの全文）"""
        endpoint = f"{self.base_url}/speech"
        return self._search_speeches(
            endpoint=endpoint,
            params=params,
            limit_total=limit_total,
        )

    # --------- cache helpers ---------

    def _cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Stable cache key from endpoint + sorted params."""
        items = sorted(params.items())
        raw = endpoint + "?" + "&".join(f"{k}={v}" for k, v in items)
        h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"{h}.json"

    def _load_from_cache(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
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

    def _save_to_cache(self, endpoint: str, params: Dict[str, Any], data: Dict) -> None:
        if self.cache_dir is None:
            return
        cache_file = self.cache_dir / self._cache_key(endpoint, params)
        try:
            with cache_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception:
            # Cache failures should never break the client
            return

    # --------- low-level HTTP + validation ---------

    def _request_json(self, endpoint: str, params: Dict[str, Any]) -> Dict:
        params = {k: v for k, v in params.items() if v is not None}
        params.setdefault("recordPacking", "json")

        # Try cache first
        cached = self._load_from_cache(endpoint, params)
        if cached is not None:
            return cached

        try:
            resp = self._session.get(endpoint, params=params, timeout=self.timeout)
        except requests.RequestException as e:
            raise DietSearchRequestError(str(e)) from e

        try:
            data = resp.json()
        except ValueError as e:
            raise DietSearchRequestError(f"Non-JSON response: {e}") from e

        if "message" in data and "numberOfRecords" not in data:
            details = data.get("details") or []
            raise DietSearchAPIError(data["message"], details)

        # Save to cache on success
        self._save_to_cache(endpoint, params, data)

        return data

    def _check_required_any_condition(self, params: Dict[str, Any]) -> None:
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
            raise DietSearchAPIError("検索条件を指定してください。", [])

    @staticmethod
    def _sanitize_limit(limit_total: Optional[int]) -> Optional[int]:
        """
        Normalize limit_total:

        - None  -> no limit
        - <= 0  -> no limit (treated as None)
        - > 0   -> integer limit
        """
        if limit_total is None:
            return None
        try:
            value = int(limit_total)
        except (TypeError, ValueError):
            return None
        if value <= 0:
            return None
        return value

    # --------- internal search implementations ---------

    def _search_meetings(
        self,
        endpoint: str,
        is_full: bool,
        params: Dict[str, Any],
        limit_total: Optional[int] = None,
    ) -> MeetingListResult:
        self._check_required_any_condition(params)

        max_rec = 10 if is_full else 100
        params = dict(params)
        params.setdefault("maximumRecords", max_rec)
        params.setdefault("startRecord", 1)

        limit_total = self._sanitize_limit(limit_total)

        all_records: List[MeetingRecord] = []
        total_records: Optional[int] = None

        while True:
            data = self._request_json(endpoint, params)
            number_of_records = int(data.get("numberOfRecords", 0))
            total_records = total_records or number_of_records

            raw_meetings = data.get("meetingRecord", []) or []
            try:
                parsed_meetings = [
                    MeetingRecord.model_validate(m) for m in raw_meetings
                ]
            except ValidationError as e:
                raise DietSearchRequestError(
                    f"Failed to parse meetingRecord: {e}"
                ) from e

            all_records.extend(parsed_meetings)

            if limit_total is not None and len(all_records) >= limit_total:
                all_records = all_records[:limit_total]
                break

            next_pos = data.get("nextRecordPosition")
            if not next_pos:
                break
            if len(all_records) >= number_of_records and limit_total is None:
                break

            params["startRecord"] = next_pos
            time.sleep(self.sleep_seconds)

        return MeetingListResult(
            number_of_records=total_records or 0,
            records=all_records,
        )

    def _search_speeches(
        self,
        endpoint: str,
        params: Dict[str, Any],
        limit_total: Optional[int] = None,
    ) -> SpeechSearchResult:
        self._check_required_any_condition(params)

        params = dict(params)
        params.setdefault("maximumRecords", 100)
        params.setdefault("startRecord", 1)

        limit_total = self._sanitize_limit(limit_total)

        all_records: List[SpeechRecord] = []
        total_records: Optional[int] = None

        while True:
            data = self._request_json(endpoint, params)
            number_of_records = int(data.get("numberOfRecords", 0))
            total_records = total_records or number_of_records

            raw_speeches = data.get("speechRecord", []) or []
            try:
                parsed_speeches = [
                    SpeechRecord.model_validate(s) for s in raw_speeches
                ]
            except ValidationError as e:
                raise DietSearchRequestError(
                    f"Failed to parse speechRecord: {e}"
                ) from e

            all_records.extend(parsed_speeches)

            if limit_total is not None and len(all_records) >= limit_total:
                all_records = all_records[:limit_total]
                break

            next_pos = data.get("nextRecordPosition")
            if not next_pos:
                break
            if len(all_records) >= number_of_records and limit_total is None:
                break

            params["startRecord"] = next_pos
            time.sleep(self.sleep_seconds)

        return SpeechSearchResult(
            number_of_records=total_records or 0,
            records=all_records,
        )
