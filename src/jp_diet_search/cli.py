from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import Any, Dict, List

from .client import DietSearchClient
from .exceptions import DietSearchError


def _common_args(parser: argparse.ArgumentParser) -> None:
    """Add arguments common to all subcommands."""
    parser.add_argument("--any", dest="any", help="検索語 (発言内容等)")
    parser.add_argument("--name-of-meeting", dest="nameOfMeeting", help="会議名")
    parser.add_argument("--speaker", dest="speaker", help="発言者名")
    parser.add_argument(
        "--from",
        dest="from_",
        metavar="YYYY-MM-DD",
        help="開会日付/始点",
    )
    parser.add_argument(
        "--until",
        dest="until",
        metavar="YYYY-MM-DD",
        help="開会日付/終点",
    )
    parser.add_argument(
        "--since",
        dest="since",
        type=int,
        metavar="YYYY",
        help="ショートカット: --from YYYY-01-01 と同等",
    )

    parser.add_argument(
        "--maximum-records",
        dest="maximumRecords",
        type=int,
        help="一回の最大取得件数 (上限は API 仕様を参照)",
    )
    parser.add_argument(
        "--session-from",
        dest="sessionFrom",
        type=int,
        help="国会回次From",
    )
    parser.add_argument(
        "--session-to",
        dest="sessionTo",
        type=int,
        help="国会回次To",
    )

    parser.add_argument(
        "--limit-total",
        dest="limit_total",
        type=int,
        help="ページング全体での最大取得件数 (総件数の上限)",
    )

    parser.add_argument(
        "--cache-dir",
        dest="cache_dir",
        help="オンディスクキャッシュ保存ディレクトリ（任意）",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="件数などのメタ情報のみ表示（本文は取得しない）",
    )

    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["json", "jsonl", "csv"],
        default="json",
        help="出力フォーマット (json / jsonl / csv)",
    )

    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=2.0,
        help="ページング時のインターバル秒 (default: 2.0)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON (json フォーマット時のみ有効)",
    )


def _collect_params(ns: argparse.Namespace) -> Dict[str, Any]:
    """Convert argparse namespace to API parameter dict (excluding limit_total)."""
    params: Dict[str, Any] = {}

    for key in [
        "any",
        "nameOfMeeting",
        "speaker",
        "maximumRecords",
        "sessionFrom",
        "sessionTo",
    ]:
        val = getattr(ns, key, None)
        if val is not None:
            params[key] = val

    # 開始日:
    #   1. --from YYYY-MM-DD が指定されていればそれを優先
    #   2. それがなければ --since YYYY から YYYY-01-01 を組み立て
    if getattr(ns, "from_", None):
        params["from"] = ns.from_
    elif getattr(ns, "since", None):
        params["from"] = f"{ns.since:04d}-01-01"

    # 終了日:
    if getattr(ns, "until", None):
        params["until"] = ns.until

    return params


def _print_output(obj: Any, pretty: bool, fmt: str) -> None:
    """Print data in the selected format."""
    if fmt == "json":
        if pretty:
            json.dump(obj, sys.stdout, ensure_ascii=False, indent=2)
        else:
            json.dump(obj, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        return

    if fmt == "jsonl":
        # Expect list of dicts (but accept single dict too)
        if isinstance(obj, list):
            rows = obj
        else:
            rows = [obj]
        for row in rows:
            json.dump(row, sys.stdout, ensure_ascii=False)
            sys.stdout.write("\n")
        return

    if fmt == "csv":
        # Expect list of dicts (but accept single dict too)
        if isinstance(obj, list):
            rows = obj
        else:
            rows = [obj]

        if not rows:
            return

        fieldnames: List[str] = sorted(
            set().union(*(row.keys() for row in rows))
        )
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        return


def cmd_meeting_list(ns: argparse.Namespace) -> int:
    client = DietSearchClient(
        sleep_seconds=ns.sleep_seconds,
        cache_dir=ns.cache_dir,
    )
    params = _collect_params(ns)

    # Dry-run: only report total count, no records
    if ns.dry_run:
        res = client.search_meeting_list(limit_total=1, **params)
        payload = {
            "numberOfRecords": res.number_of_records,
            "note": "dry-run: records not included",
        }
        _print_output(payload, ns.pretty, "json")
        return 0

    res = client.search_meeting_list(limit_total=ns.limit_total, **params)
    records = [r.model_dump(by_alias=True) for r in res.records]

    if ns.output_format == "json":
        payload = {
            "numberOfRecords": res.number_of_records,
            "meetingRecord": records,
        }
        _print_output(payload, ns.pretty, "json")
    else:
        _print_output(records, ns.pretty, ns.output_format)

    return 0


def cmd_meeting(ns: argparse.Namespace) -> int:
    client = DietSearchClient(
        sleep_seconds=ns.sleep_seconds,
        cache_dir=ns.cache_dir,
    )
    params = _collect_params(ns)

    if ns.dry_run:
        res = client.search_meeting(limit_total=1, **params)
        payload = {
            "numberOfRecords": res.number_of_records,
            "note": "dry-run: records not included",
        }
        _print_output(payload, ns.pretty, "json")
        return 0

    res = client.search_meeting(limit_total=ns.limit_total, **params)
    records = [r.model_dump(by_alias=True) for r in res.records]

    if ns.output_format == "json":
        payload = {
            "numberOfRecords": res.number_of_records,
            "meetingRecord": records,
        }
        _print_output(payload, ns.pretty, "json")
    else:
        _print_output(records, ns.pretty, ns.output_format)

    return 0


def cmd_speech(ns: argparse.Namespace) -> int:
    client = DietSearchClient(
        sleep_seconds=ns.sleep_seconds,
        cache_dir=ns.cache_dir,
    )
    params = _collect_params(ns)

    if ns.dry_run:
        res = client.search_speech(limit_total=1, **params)
        payload = {
            "numberOfRecords": res.number_of_records,
            "note": "dry-run: records not included",
        }
        _print_output(payload, ns.pretty, "json")
        return 0

    res = client.search_speech(limit_total=ns.limit_total, **params)
    records = [r.model_dump(by_alias=True) for r in res.records]

    if ns.output_format == "json":
        payload = {
            "numberOfRecords": res.number_of_records,
            "speechRecord": records,
        }
        _print_output(payload, ns.pretty, "json")
    else:
        _print_output(records, ns.pretty, ns.output_format)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jp-diet-search",
        description="CLI client for the National Diet Minutes Search API",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_ml = sub.add_parser("meeting-list", help="会議単位簡易出力 (meeting_list)")
    _common_args(p_ml)
    p_ml.set_defaults(func=cmd_meeting_list)

    p_m = sub.add_parser("meeting", help="会議単位出力 (meeting)")
    _common_args(p_m)
    p_m.set_defaults(func=cmd_meeting)

    p_s = sub.add_parser("speech", help="発言単位出力 (speech)")
    _common_args(p_s)
    p_s.set_defaults(func=cmd_speech)

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    ns = parser.parse_args(argv)

    try:
        code = ns.func(ns)
    except DietSearchError as e:
        parser.exit(1, f"[ERROR] {e}\n")
    except KeyboardInterrupt:
        parser.exit(130, "[ERROR] Interrupted by user\n")

    parser.exit(code)
