from __future__ import annotations

from typing import List, Optional, Union
from pydantic import BaseModel, Field

# Allow the API to return strings or integers for some fields
NumberLike = Union[int, str]


class SpeechRecord(BaseModel):
    """発言情報 (speech endpoint, or nested inside meetingRecord)."""

    speech_id: str = Field(alias="speechID")
    issue_id: Optional[str] = Field(default=None, alias="issueID")

    image_kind: Optional[str] = Field(default=None, alias="imageKind")
    search_object: Optional[NumberLike] = Field(default=None, alias="searchObject")

    session: Optional[NumberLike] = None
    name_of_house: Optional[str] = Field(default=None, alias="nameOfHouse")
    name_of_meeting: Optional[str] = Field(default=None, alias="nameOfMeeting")

    issue: Optional[str] = None
    date: Optional[str] = None
    closing: Optional[str] = None

    speech_order: Optional[int] = Field(default=None, alias="speechOrder")
    speaker: Optional[str] = None
    speaker_yomi: Optional[str] = Field(default=None, alias="speakerYomi")
    speaker_group: Optional[str] = Field(default=None, alias="speakerGroup")
    speaker_position: Optional[str] = Field(default=None, alias="speakerPosition")
    speaker_role: Optional[str] = Field(default=None, alias="speakerRole")

    speech: Optional[str] = None

    start_page: Optional[int] = Field(default=None, alias="startPage")

    create_time: Optional[str] = Field(default=None, alias="createTime")
    update_time: Optional[str] = Field(default=None, alias="updateTime")

    speech_url: Optional[str] = Field(default=None, alias="speechURL")
    meeting_url: Optional[str] = Field(default=None, alias="meetingURL")
    pdf_url: Optional[str] = Field(default=None, alias="pdfURL")


class MeetingRecord(BaseModel):
    """会議単位の情報 (meeting_list / meeting endpoints)."""

    issue_id: str = Field(alias="issueID")

    image_kind: Optional[str] = Field(default=None, alias="imageKind")
    search_object: Optional[NumberLike] = Field(default=None, alias="searchObject")

    session: Optional[NumberLike] = None
    name_of_house: Optional[str] = Field(default=None, alias="nameOfHouse")
    name_of_meeting: Optional[str] = Field(default=None, alias="nameOfMeeting")

    issue: Optional[str] = None
    date: Optional[str] = None
    closing: Optional[str] = None

    speech_records: List[SpeechRecord] = Field(default_factory=list, alias="speechRecord")

    meeting_url: Optional[str] = Field(default=None, alias="meetingURL")
    pdf_url: Optional[str] = Field(default=None, alias="pdfURL")


class MeetingListResult(BaseModel):
    """Aggregated result for /meeting_list and /meeting."""

    # No alias needed; we construct this in Python code, not from API JSON.
    number_of_records: int
    records: List[MeetingRecord]


class SpeechSearchResult(BaseModel):
    """Aggregated result for /speech."""

    # Same here: we pass number_of_records=... from client.py
    number_of_records: int
    records: List[SpeechRecord]

