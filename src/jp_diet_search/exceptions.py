from __future__ import annotations
from typing import List, Optional


class DietSearchError(Exception):
    pass


class DietSearchRequestError(DietSearchError):
    pass


class DietSearchAPIError(DietSearchError):
    def __init__(self, message: str, details: Optional[List[str]] = None):
        self.message = message
        self.details = details or []
        super().__init__(self.__str__())

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (details: {'; '.join(self.details)})"
        return self.message
