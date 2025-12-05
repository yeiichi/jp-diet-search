"""Client library for the 国会会議録検索システム API."""

from .client import DietSearchClient  # noqa: F401
from .models import (  # noqa: F401
    MeetingListResult,
    MeetingRecord,
    SpeechRecord,
    SpeechSearchResult,
)
from .exceptions import (  # noqa: F401
    DietSearchAPIError,
    DietSearchError,
    DietSearchRequestError,
)

__all__ = [
    "DietSearchClient",
    "MeetingListResult",
    "MeetingRecord",
    "SpeechRecord",
    "SpeechSearchResult",
    "DietSearchError",
    "DietSearchRequestError",
    "DietSearchAPIError",
]

__version__ = "0.1.0"
