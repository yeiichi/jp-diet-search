from __future__ import annotations

from typing import Any, Dict, Optional

from .core import _DietCore
from .queries import MeetingListQuery, MeetingQuery, SpeechQuery


class MeetingListEndpoint:
    def __init__(self, core: _DietCore) -> None:
        self._core = core

    def search(self, query: MeetingListQuery, *, limit_total: Optional[int] = None) -> Dict[str, Any]:
        endpoint = f"{self._core.base_url}/meeting_list"
        return self._core.search_records(endpoint=endpoint, record_key="meetingRecord", params=query.to_params(), limit_total=limit_total)

    def search_any(self, text: str, *, maximum_records: int = 100, limit_total: Optional[int] = None) -> Dict[str, Any]:
        q = MeetingListQuery(any=text, maximum_records=maximum_records)
        return self.search(q, limit_total=limit_total)


class MeetingEndpoint:
    def __init__(self, core: _DietCore) -> None:
        self._core = core

    def search(self, query: MeetingQuery, *, limit_total: Optional[int] = None) -> Dict[str, Any]:
        endpoint = f"{self._core.base_url}/meeting"
        return self._core.search_records(endpoint=endpoint, record_key="meetingRecord", params=query.to_params(), limit_total=limit_total)

    def search_any(self, text: str, *, maximum_records: int = 10, limit_total: Optional[int] = None) -> Dict[str, Any]:
        q = MeetingQuery(any=text, maximum_records=maximum_records)
        return self.search(q, limit_total=limit_total)


class SpeechEndpoint:
    def __init__(self, core: _DietCore) -> None:
        self._core = core

    def search(self, query: SpeechQuery, *, limit_total: Optional[int] = None) -> Dict[str, Any]:
        endpoint = f"{self._core.base_url}/speech"
        return self._core.search_records(endpoint=endpoint, record_key="speechRecord", params=query.to_params(), limit_total=limit_total)

    def search_any(self, text: str, *, maximum_records: int = 100, limit_total: Optional[int] = None) -> Dict[str, Any]:
        q = SpeechQuery(any=text, maximum_records=maximum_records)
        return self.search(q, limit_total=limit_total)

    def search_by_speaker(
        self,
        speaker: str,
        *,
        from_date: str | None = None,
        until_date: str | None = None,
        maximum_records: int = 100,
        limit_total: Optional[int] = None,
    ) -> Dict[str, Any]:
        q = SpeechQuery(speaker=speaker, from_date=from_date, until_date=until_date, maximum_records=maximum_records)
        return self.search(q, limit_total=limit_total)
