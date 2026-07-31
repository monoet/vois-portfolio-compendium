#!/usr/bin/env python3
"""Append a portfolio reference safely to data/references.json."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "reference"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--creator", default="")
    parser.add_argument("--url", default="")
    parser.add_argument("--disciplines", required=True, help="Comma-separated")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--takeaway", required=True)
    parser.add_argument("--vois-application", required=True)
    parser.add_argument("--tags", default="", help="Comma-separated")
    args = parser.parse_args()

    path = Path(__file__).resolve().parents[1] / "data" / "references.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    entry = {
        "id": slugify(f"{args.creator}-{args.title}"),
        "title": args.title,
        "creator": args.creator,
        "url": args.url,
        "disciplines": [x.strip() for x in args.disciplines.split(",") if x.strip()],
        "status": "inbox",
        "summary": args.summary,
        "takeaway": args.takeaway,
        "vois_application": args.vois_application,
        "tags": [x.strip() for x in args.tags.split(",") if x.strip()],
    }

    existing_ids = {item["id"] for item in payload["references"]}
    if entry["id"] in existing_ids:
        raise SystemExit(f'Duplicate id: {entry["id"]}')

    payload["references"].append(entry)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f'Added {entry["id"]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
