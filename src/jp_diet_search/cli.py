from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .client import DietClient
from .queries import MeetingListQuery, MeetingQuery, SpeechQuery


def _add_common_client_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--base-url", default="https://kokkai.ndl.go.jp/api", help="API base URL.")
    p.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout in seconds.")
    p.add_argument("--user-agent", default="jp-diet-search", help="User-Agent string.")
    p.add_argument("--sleep-seconds", type=float, default=2.0, help="Sleep seconds between paginated API calls.")
    p.add_argument("--cache-dir", default=None, help="Cache directory path (optional).")
    p.add_argument("--limit-total", type=int, default=None, help="Stop pagination after collecting this many records.")
    p.add_argument(
        "--output",
        default="-",
        help="Output JSON path. Use '-' to write to stdout (default).",
    )
    p.add_argument("--indent", type=int, default=2, help="JSON indent level (default: 2).")
    p.add_argument("--no-ascii", action="store_true", help="Do not escape non-ASCII characters in JSON output.")


def _add_common_query_args(p: argparse.ArgumentParser) -> None:
    # paging / format
    p.add_argument("--start-record", type=int, default=None, help="startRecord (>=1).")
    p.add_argument("--maximum-records", type=int, default=None, help="maximumRecords (meeting:<=10, others:<=100).")
    p.add_argument("--record-packing", choices=["json", "xml"], default="json", help="recordPacking (json/xml).")

    # common search filters
    p.add_argument("--name-of-house", default=None, help="nameOfHouse")
    p.add_argument("--name-of-meeting", default=None, help="nameOfMeeting")
    p.add_argument("--any", default=None, help="Full-text keyword search (any).")
    p.add_argument("--speaker", default=None, help="speaker")

    # dates
    p.add_argument("--from-date", dest="from_date", default=None, help="from (YYYY-MM-DD)")
    p.add_argument("--until-date", dest="until_date", default=None, help="until (YYYY-MM-DD)")

    # flags and ranges
    p.add_argument("--supplement-and-appendix", action="store_true", help="supplementAndAppendix=true")
    p.add_argument("--contents-and-index", action="store_true", help="contentsAndIndex=true")
    p.add_argument("--search-range", default=None, help="searchRange")
    p.add_argument("--closing", action="store_true", help="closing=true")

    # speech-related filters (also accepted by meeting_list per API)
    p.add_argument("--speech-number", type=int, default=None, help="speechNumber")
    p.add_argument("--speaker-position", default=None, help="speakerPosition")
    p.add_argument("--speaker-group", default=None, help="speakerGroup")
    p.add_argument("--speaker-role", default=None, help="speakerRole")
    p.add_argument("--speech-id", dest="speech_id", default=None, help="speechID")
    p.add_argument("--issue-id", dest="issue_id", default=None, help="issueID")
    p.add_argument("--session-from", type=int, default=None, help="sessionFrom")
    p.add_argument("--session-to", type=int, default=None, help="sessionTo")
    p.add_argument("--issue-from", type=int, default=None, help="issueFrom")
    p.add_argument("--issue-to", type=int, default=None, help="issueTo")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="jp-diet-search",
        description="Search the National Diet Library Minutes Search API (国会会議録検索システム).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # meeting_list
    p_ml = sub.add_parser(
        "meeting-list",
        aliases=["meeting_list", "meetinglist"],
        help="Search /meeting_list",
    )
    _add_common_client_args(p_ml)
    _add_common_query_args(p_ml)

    # meeting
    p_m = sub.add_parser(
        "meeting",
        help="Search /meeting (full meeting text; maximumRecords <= 10).",
    )
    _add_common_client_args(p_m)
    _add_common_query_args(p_m)

    # speech
    p_s = sub.add_parser(
        "speech",
        help="Search /speech",
    )
    _add_common_client_args(p_s)
    _add_common_query_args(p_s)

    return p


def _query_kwargs_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    # Only pass fields that are actually set; Query objects validate "at least one condition".
    d: Dict[str, Any] = {}

    # paging/format
    if args.start_record is not None:
        d["start_record"] = args.start_record
    if args.maximum_records is not None:
        d["maximum_records"] = args.maximum_records
    if args.record_packing is not None:
        d["record_packing"] = args.record_packing

    # filters
    for k in [
        "name_of_house",
        "name_of_meeting",
        "any",
        "speaker",
        "from_date",
        "until_date",
        "search_range",
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
    ]:
        v = getattr(args, k, None)
        if v not in (None, ""):
            d[k] = v

    # booleans (only include if True)
    if getattr(args, "supplement_and_appendix", False):
        d["supplement_and_appendix"] = True
    if getattr(args, "contents_and_index", False):
        d["contents_and_index"] = True
    if getattr(args, "closing", False):
        d["closing"] = True

    return d


def _write_json(obj: Any, *, output: str, indent: int, ensure_ascii: bool) -> None:
    # Support pydantic models (v2) and plain dicts.
    if hasattr(obj, "model_dump"):
        payload = obj.model_dump()
    elif hasattr(obj, "dict"):
        payload = obj.dict()  # pragma: no cover (pydantic v1)
    else:
        payload = obj

    text = json.dumps(payload, indent=indent, ensure_ascii=ensure_ascii)
    if output == "-" or output.strip() == "":
        sys.stdout.write(text + "\n")
        return

    out_path = Path(output).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text + "\n", encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    client = DietClient(
        base_url=args.base_url,
        timeout=args.timeout,
        user_agent=args.user_agent,
        sleep_seconds=args.sleep_seconds,
        cache_dir=args.cache_dir,
    )

    q_kwargs = _query_kwargs_from_args(args)

    try:
        if args.cmd in ("meeting-list", "meeting_list", "meetinglist"):
            q = MeetingListQuery(**q_kwargs)
            res = client.meeting_list.search(q, limit_total=args.limit_total)
        elif args.cmd == "meeting":
            q = MeetingQuery(**q_kwargs)
            res = client.meeting.search(q, limit_total=args.limit_total)
        elif args.cmd == "speech":
            q = SpeechQuery(**q_kwargs)
            res = client.speech.search(q, limit_total=args.limit_total)
        else:
            raise RuntimeError(f"Unknown command: {args.cmd}")
    except Exception as e:
        parser.error(str(e))
        return 2

    _write_json(
        res,
        output=args.output,
        indent=args.indent,
        ensure_ascii=not args.no_ascii,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
