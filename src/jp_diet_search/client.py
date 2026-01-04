from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import requests

from .core import BASE_URL, _DietCore
from .endpoints import MeetingEndpoint, MeetingListEndpoint, SpeechEndpoint
from .queries import MeetingListQuery, MeetingQuery, SpeechQuery


class DietClient:
    """Object API client for the NDL Diet Records API."""

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
        self._core = _DietCore(
            base_url=base_url,
            user_agent=user_agent,
            timeout=timeout,
            sleep_seconds=sleep_seconds,
            cache_dir=cache_dir,
            session=session,
        )

        self.meeting_list = MeetingListEndpoint(self._core)
        self.meeting = MeetingEndpoint(self._core)
        self.speech = SpeechEndpoint(self._core)

    # ---------------- legacy-compatible methods ----------------
    # These keep your original "dict-of-params" calls working, but forward to the object API.

    def search_meeting_list(self, limit_total: Optional[int] = None, **params: Any) -> Dict[str, Any]:
        q = MeetingListQuery.model_validate(params)
        return self.meeting_list.search(q, limit_total=limit_total)

    def search_meeting(self, limit_total: Optional[int] = None, **params: Any) -> Dict[str, Any]:
        q = MeetingQuery.model_validate(params)
        return self.meeting.search(q, limit_total=limit_total)

    def search_speech(self, limit_total: Optional[int] = None, **params: Any) -> Dict[str, Any]:
        q = SpeechQuery.model_validate(params)
        return self.speech.search(q, limit_total=limit_total)


# Backward-compatible alias (if you had this name in older versions)
DietSearchClient = DietClient
