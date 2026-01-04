from __future__ import annotations

import inspect
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
import requests

import jp_diet_search.core as core_mod

from jp_diet_search.exceptions import (
    DietSearchAPIError,
    DietSearchParseError,
    DietSearchRateLimitError,
    DietSearchRequestError,
)


def _find_core_class_with_request_json():
    for _, obj in vars(core_mod).items():
        if inspect.isclass(obj) and hasattr(obj, "_request_json"):
            return obj
    raise RuntimeError("No class with _request_json found in jp_diet_search.core")


def _make_core_with_session(core_cls, session: requests.Session):
    core = core_cls.__new__(core_cls)
    core.session = session
    core.timeout = 30

    # disable cache
    core._load_from_cache = Mock(return_value=None)
    core._save_to_cache = Mock()
    return core


def _fake_response(*, status_code: int, text: str = "", json_obj=None, json_raises: Exception | None = None):
    r = SimpleNamespace()
    r.status_code = status_code
    r.text = text

    def _json():
        if json_raises is not None:
            raise json_raises
        return json_obj

    r.json = _json
    return r


def test_request_json_raises_request_error_on_requests_exception():
    core_cls = _find_core_class_with_request_json()
    session = Mock(spec=requests.Session)
    session.get.side_effect = requests.RequestException("boom")

    core = _make_core_with_session(core_cls, session)

    with pytest.raises(DietSearchRequestError):
        core._request_json("https://example/api", {"any": "x"})


def test_request_json_raises_rate_limit_on_429():
    core_cls = _find_core_class_with_request_json()
    session = Mock(spec=requests.Session)
    session.get.return_value = _fake_response(status_code=429, text="too many requests")

    core = _make_core_with_session(core_cls, session)

    with pytest.raises(DietSearchRateLimitError):
        core._request_json("https://example/api", {"any": "x"})


def test_request_json_raises_api_error_on_non_200_non_429():
    core_cls = _find_core_class_with_request_json()
    session = Mock(spec=requests.Session)
    session.get.return_value = _fake_response(status_code=500, text="server error")

    core = _make_core_with_session(core_cls, session)

    with pytest.raises(DietSearchAPIError):
        core._request_json("https://example/api", {"any": "x"})


def test_request_json_raises_parse_error_on_bad_json():
    core_cls = _find_core_class_with_request_json()
    session = Mock(spec=requests.Session)
    session.get.return_value = _fake_response(
        status_code=200,
        text='{"not": "json"}',
        json_raises=ValueError("invalid json"),
    )

    core = _make_core_with_session(core_cls, session)

    with pytest.raises(DietSearchParseError):
        core._request_json("https://example/api", {"any": "x"})
