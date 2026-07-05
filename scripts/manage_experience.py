#!/usr/bin/env python3
"""
Manage the .opencode/experiences.md file: read, append, and validate.

Usage:
  python3 scripts/manage_experience.py read [--path PATH]
  python3 scripts/manage_experience.py append --entry JSON [--path PATH]
  python3 scripts/manage_experience.py validate [--path PATH]

Entry JSON format:
  {"title": "Short title", "content": "One-sentence insight"}
"""

import argparse
import difflib
import json
import os
import re
import sys
from datetime import date


DEFAULT_PATH = ".opencode/experiences.md"
ENTRY_SEP = " — "

SENSITIVE_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    (
        "secret assignment",
        re.compile(
            r"\b(api[_-]?key|secret|token|password|passwd|pwd|access[_-]?token|refresh[_-]?token)\b\s*[:=]\s*['\"]?[^'\"\s]{8,}",
            re.IGNORECASE,
        ),
    ),
    ("openai key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("aws access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
]


def resolve_path(path):
    cwd = os.getcwd()
    if os.path.isabs(path):
        return path
    return os.path.join(cwd, path)


def load_text(path):
    with open(path, "r") as f:
        return f.read()


def write_text(path, content):
    with open(path, "w") as f:
        f.write(content)


def read_experiences(path):
    path = resolve_path(path)
    if not os.path.exists(path):
        return []
    content = load_text(path)

    entries = []
    lines = content.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if ENTRY_SEP in stripped:
            # Skip lines that are clearly not entries: headings, blank lines
            if stripped.startswith("#") or stripped.startswith("-") or stripped.startswith(">") or stripped.startswith("```"):
                continue
            parts = stripped.split(ENTRY_SEP, 1)
            title = parts[0].strip()
            content_text = parts[1].strip()
            if title and content_text:
                entries.append({
                    "title": title,
                    "content": content_text,
                })
    return entries


def parse_entry(entry):
    if isinstance(entry, str):
        try:
            entry = json.loads(entry)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(entry, dict):
        raise ValueError("entry must be a JSON object")

    title = str(entry.get("title", "")).strip()
    content_text = str(entry.get("content", "")).strip()

    if not title:
        raise ValueError("title is required")
    if not content_text:
        raise ValueError("content is required")

    return {
        "title": title,
        "content": content_text,
    }


def sensitive_hits(entry):
    text = "\n".join([
        entry.get("title", ""),
        entry.get("content", ""),
    ])
    return [name for name, pattern in SENSITIVE_PATTERNS if pattern.search(text)]


def normalize_text(text):
    text = text.lower()
    return re.sub(r"[^\w\u4e00-\u9fff]+", "", text)


def similarity(left, right):
    if not left or not right:
        return 0.0
    return difflib.SequenceMatcher(None, left, right).ratio()


def find_duplicate(entry, existing_entries):
    title = normalize_text(entry["title"])
    content_text = normalize_text(entry["content"])
    for existing in existing_entries:
        existing_title = normalize_text(existing.get("title", ""))
        existing_content = normalize_text(existing.get("content", ""))
        title_ratio = similarity(title, existing_title)
        content_ratio = similarity(content_text, existing_content)
        title_contains = (
            min(len(title), len(existing_title)) >= 8
            and (title in existing_title or existing_title in title)
        )
        if title_ratio >= 0.92 or title_contains:
            return existing
        if min(len(content_text), len(existing_content)) >= 40 and content_ratio >= 0.88:
            return existing
    return None


def format_entry(entry):
    return f"{entry['title']}{ENTRY_SEP}{entry['content']}\n"


def append_entry(path, entry, project_name=None):
    path = resolve_path(path)
    entry = parse_entry(entry)
    hits = sensitive_hits(entry)
    if hits:
        raise ValueError("sensitive content detected: " + ", ".join(hits))

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    existed = os.path.exists(path)
    original_content = load_text(path) if existed else None
    existing_entries = read_experiences(path) if existed else []
    duplicate = find_duplicate(entry, existing_entries)
    if duplicate:
        raise ValueError(
            "duplicate or near-duplicate entry: "
            f"{duplicate.get('title')}"
        )

    if original_content is None:
        content = "# 经验记录\n\n"
        if project_name:
            content += f"项目：{project_name}\n\n"
    else:
        content = original_content

    today = date.today().isoformat()
    date_header = f"## {today}"

    entry_text = format_entry(entry)

    if date_header in content:
        content = content.replace(date_header, date_header + "\n" + entry_text)
    else:
        content = content.rstrip() + "\n\n" + date_header + "\n" + entry_text + "\n"

    write_text(path, content)
    if not validate(path):
        if original_content is None:
            os.remove(path)
        else:
            write_text(path, original_content)
        raise ValueError("validation failed after append; rolled back")

    print(f"Entry added to {path}")
    return True


def validate(path):
    path = resolve_path(path)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return False

    errors = []
    content = load_text(path)
    for name, pattern in SENSITIVE_PATTERNS:
        if pattern.search(content):
            errors.append(f"sensitive content detected: {name}")

    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if ENTRY_SEP in stripped:
            if stripped.startswith("#") or stripped.startswith("-") or stripped.startswith(">") or stripped.startswith("```"):
                continue
            parts = stripped.split(ENTRY_SEP, 1)
            if not parts[0].strip() or not parts[1].strip():
                errors.append(f"Line {i}: entry with empty title or content")

    if errors:
        for e in errors:
            print(f"  WARN: {e}")
        return False
    print(f"Validated {path} - OK")
    return True


def main():
    parser = argparse.ArgumentParser(description="Manage experiences.md file")
    parser.add_argument("action", choices=["read", "append", "validate"])
    parser.add_argument("--path", default=DEFAULT_PATH, help="Path to experiences.md")
    parser.add_argument("--entry", help="JSON string for append action")
    parser.add_argument("--project", help="Project name (used when creating new file)")

    args = parser.parse_args()

    if args.action == "read":
        entries = read_experiences(args.path)
        print(json.dumps(entries, indent=2, ensure_ascii=False))

    elif args.action == "append":
        if not args.entry:
            print("ERROR: --entry is required for append action")
            sys.exit(1)
        try:
            append_entry(args.path, args.entry, args.project)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.action == "validate":
        valid = validate(args.path)
        sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
