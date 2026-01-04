from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

RecordPacking = Literal["json", "xml"]


class BaseQuery(BaseModel):
    """
    Base query object for the Diet Search API.

    This class is intentionally strict (extra="forbid") so typos are caught early.
    """
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    # common paging
    start_record: Optional[int] = Field(default=None, ge=1)
    maximum_records: Optional[int] = Field(default=None, ge=1)
    record_packing: Optional[RecordPacking] = "json"

    # common search conditions (snake_case)
    name_of_house: Optional[str] = None
    name_of_meeting: Optional[str] = None
    any: Optional[str] = None
    speaker: Optional[str] = None
    from_date: Optional[str] = Field(default=None, alias="from")   # allow `from=` in dicts
    until_date: Optional[str] = Field(default=None, alias="until") # allow `until=` in dicts

    # misc flags / range
    supplement_and_appendix: Optional[bool] = None
    contents_and_index: Optional[bool] = None
    search_range: Optional[str] = None
    closing: Optional[bool] = None

    # speech / meeting fields
    speech_number: Optional[int] = None
    speaker_position: Optional[str] = None
    speaker_group: Optional[str] = None
    speaker_role: Optional[str] = None
    speech_id: Optional[str] = None
    issue_id: Optional[str] = None
    session_from: Optional[int] = None
    session_to: Optional[int] = None
    issue_from: Optional[int] = None
    issue_to: Optional[int] = None

    def to_params(self) -> Dict[str, Any]:
        """
        Convert this query to Diet Search API parameter dict.
        """
        data = self.model_dump(by_alias=True, exclude_none=True)

        mapping = {
            "start_record": "startRecord",
            "maximum_records": "maximumRecords",
            "record_packing": "recordPacking",
            "name_of_house": "nameOfHouse",
            "name_of_meeting": "nameOfMeeting",
            "supplement_and_appendix": "supplementAndAppendix",
            "contents_and_index": "contentsAndIndex",
            "search_range": "searchRange",
            "speech_number": "speechNumber",
            "speaker_position": "speakerPosition",
            "speaker_group": "speakerGroup",
            "speaker_role": "speakerRole",
            "speech_id": "speechID",
            "issue_id": "issueID",
            "session_from": "sessionFrom",
            "session_to": "sessionTo",
            "issue_from": "issueFrom",
            "issue_to": "issueTo",
            "from_date": "from",
            "until_date": "until",
        }

        out: Dict[str, Any] = {}
        for k, v in data.items():
            out[mapping.get(k, k)] = v
        return out

    @model_validator(mode="after")
    def require_some_condition(self):
        keys = [
            "name_of_house",
            "name_of_meeting",
            "any",
            "speaker",
            "from_date",
            "until_date",
            "speech_number",
            "speaker_position",
            "speaker_group",
            "speaker_role",
            "speech_id",
            "issue_id",
            "session_from",
            "session_to",
            "issue_from",
            "issue_to",
        ]
        if not any(getattr(self, k) not in (None, "") for k in keys):
            raise ValueError("At least one search condition is required.")
        return self


class MeetingListQuery(BaseQuery):
    @field_validator("maximum_records")
    @classmethod
    def max_100(cls, v):
        if v is not None and v > 100:
            raise ValueError("meeting_list maximum_records must be 1..100")
        return v


class SpeechQuery(BaseQuery):
    @field_validator("maximum_records")
    @classmethod
    def max_100(cls, v):
        if v is not None and v > 100:
            raise ValueError("speech maximum_records must be 1..100")
        return v


class MeetingQuery(BaseQuery):
    @field_validator("maximum_records")
    @classmethod
    def max_10(cls, v):
        if v is not None and v > 10:
            raise ValueError("meeting maximum_records must be 1..10")
        return v
