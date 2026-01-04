from __future__ import annotations
from typing import List, Optional


class DietSearchError(Exception):
    """Base exception for jp-diet-search."""
    pass


class DietSearchRequestError(DietSearchError):
    """Client-side errors (invalid params, misuse, parse failures)."""
    pass


class DietSearchParseError(DietSearchRequestError):
    """Raised when API responses cannot be parsed or decoded."""
    pass


class DietSearchAPIError(DietSearchError):
    """Server/API-side errors (HTTP errors, API error payloads)."""

    def __init__(self, message: str, details: Optional[List[str]] = None):
        self.message = message
        self.details = details or []
        super().__init__(self.__str__())

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (details: {'; '.join(self.details)})"
        return self.message


class DietSearchRateLimitError(DietSearchAPIError):
    """Raised when the API signals rate limiting (e.g. HTTP 429)."""
    pass
