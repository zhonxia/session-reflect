#!/usr/bin/env python3
"""
Manage the .opencode/experiences.md file: read, append, and validate.

Usage:
  python3 scripts/manage_experience.py read [--path PATH]
  python3 scripts/manage_experience.py append --entry JSON [--path PATH]
  python3 scripts/manage_experience.py validate [--path PATH]

Entry JSON format:
  {"title": "...", "problem": "...", "insight": "...", "apply": "...", "keywords": [...]}
  Only title is required; problem/insight/apply/keywords are optional.
"""

import argparse
import difflib
import json
import os
import re
import sys
from datetime import date


DEFAULT_PATH = ".opencode/experiences.md"
ENTRY_RE = re.compile(
    r"^###\s+(?P<title>.+)$",
    re.MULTILINE,
)

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

FIELD_KEYS = {"问题": "problem", "经验": "insight", "适用": "apply", "关键词": "keywords"}


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


def _parse_fields(body):
    """Parse `- **字段名**：值` lines from entry body."""
    fields = {}
    for line in body.split("\n"):
        line = line.strip()
        m = re.match(r"^-\s+\*\*(.+?)\*\*\s*[：:]\s*(.*)", line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip()
            eng = FIELD_KEYS.get(key, key)
            if eng == "keywords":
                # Parse comma/space-separated tags
                tags = [t.strip() for t in re.split(r"[,\s]+", val) if t.strip()]
                fields[eng] = tags
            else:
                fields[eng] = val
    return fields


def read_experiences(path):
    path = resolve_path(path)
    if not os.path.exists(path):
        return []
    content = load_text(path)

    entries = []
    matches = list(ENTRY_RE.finditer(content))
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        body = content[start:end]
        # Strip trailing whitespace and possible date header contamination
        body = re.split(r"\n## \d{4}-\d{2}-\d{2}\b", body, maxsplit=1)[0]
        body = body.strip()

        entry = {"title": match.group("title").strip()}
        entry.update(_parse_fields(body))
        entries.append(entry)
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
    if not title:
        raise ValueError("title is required")

    result = {"title": title}
    for eng_field in ("problem", "insight", "apply"):
        val = entry.get(eng_field, "")
        if val:
            result[eng_field] = str(val).strip()

    keywords = entry.get("keywords", [])
    if keywords and isinstance(keywords, list):
        result["keywords"] = [str(k).strip() for k in keywords if str(k).strip()]
    elif isinstance(keywords, str):
        result["keywords"] = [k.strip() for k in keywords.split(",") if k.strip()]

    return result


def sensitive_hits(entry):
    text = "\n".join([
        entry.get("title", ""),
        entry.get("problem", ""),
        entry.get("insight", ""),
        entry.get("apply", ""),
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
    for existing in existing_entries:
        existing_title = normalize_text(existing.get("title", ""))
        if similarity(title, existing_title) >= 0.92:
            return existing
        insight = entry.get("insight", "")
        existing_insight = existing.get("insight", "")
        insight_norm = normalize_text(insight)
        existing_insight_norm = normalize_text(existing_insight)
        if min(len(insight_norm), len(existing_insight_norm)) >= 40 and similarity(insight_norm, existing_insight_norm) >= 0.88:
            return existing
    return None


def _field_line(key_cn, value):
    if key_cn == "关键词":
        if isinstance(value, list):
            val_str = ", ".join(value)
        else:
            val_str = str(value)
        if val_str:
            return f"- **{key_cn}**：{val_str}\n"
        return ""
    if value:
        return f"- **{key_cn}**：{value}\n"
    return ""


def format_entry(entry):
    title = entry["title"]
    lines = [f"### {title}\n"]
    cn_keys = {v: k for k, v in FIELD_KEYS.items()}
    for key_cn in ("问题", "经验", "适用", "关键词"):
        eng = FIELD_KEYS[key_cn]
        val = entry.get(eng)
        if val:
            lines.append(_field_line(key_cn, val))
    text = "".join(lines)
    if text.endswith("\n\n"):
        text = text[:-1]
    elif not text.endswith("\n"):
        text += "\n"
    return text


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

    entries = []
    for m in ENTRY_RE.finditer(content):
        start = m.end()
        body = content[start:]
        body = re.split(r"\n## \d{4}-\d{2}-\d{2}\b|\n### ", body, maxsplit=1)[0]
        body = body.strip()
        title = m.group("title").strip()
        if not title:
            errors.append(f"Entry with empty title at position {m.start()}")
        entries.append({"title": title, "body": body})

    for entry in entries:
        fields = _parse_fields(entry["body"])
        if not fields.get("problem") and not fields.get("insight") and not fields.get("apply"):
            errors.append(f"Entry '{entry['title']}' has no recognizable fields")

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
