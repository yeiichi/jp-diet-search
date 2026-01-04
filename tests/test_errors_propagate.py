from __future__ import annotations

import pytest

from jp_diet_search import DietClient
from jp_diet_search.queries import MeetingListQuery
from jp_diet_search.exceptions import (
    DietSearchAPIError,
    DietSearchParseError,
    DietSearchRateLimitError,
)


class RaisingCore:
    """Core stub that raises on any method call."""
    def __init__(self, exc: Exception):
        self._exc = exc
        # if endpoints read some non-call attributes, provide safe defaults
        self.base_url = "https://example.invalid"
        self.sleep_seconds = 0

    def __getattr__(self, name: str):
        def _raise(*args, **kwargs):
            raise self._exc
        return _raise


def _make_client_with_core(core) -> DietClient:
    client = DietClient.__new__(DietClient)

    # wire endpoints the same way __init__ would
    from jp_diet_search.endpoints import MeetingListEndpoint, MeetingEndpoint, SpeechEndpoint

    client._core = core
    client.meeting_list = MeetingListEndpoint(core)
    client.meeting = MeetingEndpoint(core)
    client.speech = SpeechEndpoint(core)
    return client


def test_rate_limit_error_propagates():
    client = _make_client_with_core(RaisingCore(DietSearchRateLimitError("rate limited")))
    q = MeetingListQuery(any="x", maximum_records=1)
    with pytest.raises(DietSearchRateLimitError):
        client.meeting_list.search(q)


def test_api_error_propagates():
    client = _make_client_with_core(RaisingCore(DietSearchAPIError("api failed")))
    q = MeetingListQuery(any="x", maximum_records=1)
    with pytest.raises(DietSearchAPIError):
        client.meeting_list.search(q)


def test_parse_error_propagates():
    client = _make_client_with_core(RaisingCore(DietSearchParseError("bad json")))
    q = MeetingListQuery(any="x", maximum_records=1)
    with pytest.raises(DietSearchParseError):
        client.meeting_list.search(q)
