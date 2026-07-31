#!/usr/bin/env python3
"""
Generate portfolio showcase candidates from a Git repository.

This script is intentionally conservative:
- It never edits the game repository.
- It writes generated observations to data/harvested-commits.json.
- Manual portfolio decisions remain in data/showcase-candidates.json.

Usage:
    python scripts/harvest_git_history.py "C:/path/to/vale-of-iseris-LFS"
    python scripts/harvest_git_history.py "C:/path/to/repo" --since "30 days ago" --limit 250
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

KEYWORDS = {
    "Game design": [
        "combat", "level", "encounter", "mark", "balance", "timed hit",
        "progression", "quest", "overworld", "interaction", "navigation",
    ],
    "Game programming": [
        "system", "service", "provider", "repository", "runtime", "event",
        "bridge", "resolver", "installer", "pipeline", "save", "persistence",
        "shader", "performance", "refactor", "architecture",
    ],
    "Sound design": [
        "audio", "sfx", "fmod", "footstep", "sound", "impact", "reverb",
        "music", "ambience", "voice",
    ],
    "Music": ["music", "score", "theme", "cue", "composer", "combat music"],
    "UI": [
        "ui", "hud", "widget", "menu", "inventory", "interface", "tooltip",
        "dialogue", "dialog", "radial",
    ],
    "Art direction": [
        "lighting", "vfx", "shader", "material", "environment", "sprite",
        "character", "visual", "camera", "water", "foliage",
    ],
}

SHOWCASE_SIGNALS = [
    "add", "implement", "introduce", "complete", "finish", "refactor",
    "redesign", "integrate", "optimize", "fix", "resolve", "support",
    "prototype", "vertical slice",
]

LOW_VALUE_PATTERNS = [
    r"^merge\b",
    r"^chore\b",
    r"^wip\b",
    r"^tmp\b",
    r"^test\b",
    r"typo",
    r"format",
]


def run_git(repo: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout


def classify(text: str, changed_files: Iterable[str]) -> tuple[list[str], int]:
    haystack = f"{text} {' '.join(changed_files)}".lower()
    scores: dict[str, int] = defaultdict(int)

    for discipline, terms in KEYWORDS.items():
        for term in terms:
            if term in haystack:
                scores[discipline] += 2 if term in text.lower() else 1

    signal_score = sum(1 for signal in SHOWCASE_SIGNALS if signal in text.lower())
    technical_bonus = min(3, len(list(changed_files)) // 5)
    score = sum(scores.values()) + signal_score + technical_bonus

    disciplines = [
        discipline
        for discipline, value in sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))
        if value > 0
    ][:4]

    return disciplines, score


def is_low_value(subject: str) -> bool:
    lowered = subject.strip().lower()
    return any(re.search(pattern, lowered) for pattern in LOW_VALUE_PATTERNS)


def parse_log(raw: str) -> list[dict]:
    records = []
    for block in raw.strip("\x1e\n").split("\x1e"):
        if not block.strip():
            continue
        fields = block.strip("\n").split("\x1f")
        if len(fields) < 4:
            continue
        commit, date, subject, body = fields[:4]
        records.append({
            "commit": commit.strip(),
            "date": date.strip(),
            "subject": subject.strip(),
            "body": body.strip(),
        })
    return records


def build_candidate(repo: Path, record: dict, threshold: int) -> dict | None:
    if is_low_value(record["subject"]):
        return None

    changed = [
        line.strip()
        for line in run_git(repo, ["show", "--pretty=format:", "--name-only", record["commit"]]).splitlines()
        if line.strip()
    ]

    text = f'{record["subject"]}\n{record["body"]}'
    disciplines, score = classify(text, changed)
    if score < threshold or not disciplines:
        return None

    rationale = (
        f'This commit may contain portfolio evidence because it touches '
        f'{", ".join(disciplines)} and includes a meaningful implementation or design signal.'
    )

    return {
        "id": f'commit-{record["commit"][:12]}',
        "title": record["subject"],
        "commit": record["commit"],
        "date": record["date"],
        "disciplines": disciplines,
        "status": "agent-detected",
        "rationale": rationale,
        "score": score,
        "changed_files": changed[:20],
        "suggested_output": suggest_output(disciplines),
        "media_needed": suggest_media(disciplines),
        "tags": infer_tags(text, changed),
    }


def suggest_output(disciplines: list[str]) -> str:
    if len(disciplines) >= 3:
        return "Cross-disciplinary case study with focused versions for each portfolio."
    mapping = {
        "Game design": "Annotated design case study with problem, iterations, and player-facing result.",
        "Game programming": "Technical breakdown with architecture diagram, constraints, and implementation evidence.",
        "Sound design": "Implementation reel with isolated assets and in-context playback.",
        "Music": "Usage-based music reel showing cue function and in-game context.",
        "UI": "Interaction case study with states, motion, hierarchy, and implementation.",
        "Art direction": "Visual development breakdown with comparisons and decision notes.",
    }
    return mapping.get(disciplines[0], "Compact case study with process and final evidence.")


def suggest_media(disciplines: list[str]) -> list[str]:
    media = {"before/after notes"}
    if "Game programming" in disciplines:
        media.update(["architecture diagram", "debug or test evidence"])
    if "Game design" in disciplines:
        media.update(["gameplay clip", "annotated decision map"])
    if "Sound design" in disciplines or "Music" in disciplines:
        media.update(["clean audio export", "in-game capture"])
    if "UI" in disciplines:
        media.update(["state sheet", "interaction recording"])
    if "Art direction" in disciplines:
        media.update(["comparison screenshots", "lighting or visual pass"])
    return sorted(media)


def infer_tags(text: str, changed_files: list[str]) -> list[str]:
    haystack = f"{text} {' '.join(changed_files)}".lower()
    candidates = [
        "combat", "overworld", "persistence", "ui", "audio", "shader",
        "water", "foliage", "dialogue", "inventory", "performance",
        "level design", "timed hit", "marks", "footsteps",
    ]
    return [tag for tag in candidates if tag in haystack][:8]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--since", default="90 days ago")
    parser.add_argument("--limit", type=int, default=400)
    parser.add_argument("--threshold", type=int, default=4)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "harvested-commits.json",
    )
    args = parser.parse_args()

    repo = args.repo.expanduser().resolve()
    if not (repo / ".git").exists():
        raise SystemExit(f"Not a Git repository: {repo}")

    raw = run_git(repo, [
        "log",
        f"--since={args.since}",
        f"-n{args.limit}",
        "--date=short",
        "--pretty=format:%H%x1f%ad%x1f%s%x1f%b%x1e",
    ])

    candidates = []
    for record in parse_log(raw):
        candidate = build_candidate(repo, record, args.threshold)
        if candidate:
            candidates.append(candidate)

    candidates.sort(key=lambda item: (-item["score"], item["date"]), reverse=False)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_repo": str(repo),
        "candidate_count": len(candidates),
        "candidates": candidates,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(candidates)} candidates to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
