#!/usr/bin/env python3
"""
Manage the .opencode/experiences.md file: read, append, and validate.

Usage:
  python3 scripts/manage_experience.py read [--path PATH]
  python3 scripts/manage_experience.py append --entry JSON [--path PATH]
  python3 scripts/manage_experience.py validate [--path PATH]

Entry JSON format:
  {"category": "multi-step|decision|preference|discovery|setup|action",
   "title": "Short title",
   "content": "Detailed description (supports **bold** markers)",
   "tags": ["tag1", "tag2"]}

  The script checks for this structured content pattern in the content field:
  【现象】... 【洞察】... 【价值】... 【行动】...
  If found, it renders them as separate bold lines instead of a single content block.
"""

import argparse
import json
import os
import re
import sys
from datetime import date


DEFAULT_PATH = ".opencode/experiences.md"


def resolve_path(path):
    cwd = os.getcwd()
    if os.path.isabs(path):
        return path
    return os.path.join(cwd, path)


def read_experiences(path):
    path = resolve_path(path)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        content = f.read()

    entries = []
    pattern = re.compile(
        r"### \[(.+?)\] (.+?)\n- \*\*内容\*\*：(.+?)(?=\n### |\n## |\Z)",
        re.DOTALL,
    )
    for match in pattern.finditer(content):
        entries.append(
            {
                "category": match.group(1),
                "title": match.group(2),
                "content": match.group(3).strip(),
            }
        )
    return entries


def format_entry(entry):
    category_labels = {
        "multi-step": "多轮攻坚",
        "decision": "决策记录",
        "preference": "用户偏好",
        "discovery": "实用发现",
        "setup": "个人环境",
        "action": "待办提醒",
    }
    label = category_labels.get(entry["category"], entry["category"])
    tags = ""
    if entry.get("tags"):
        tags = "  `" + " ".join(f"#{t}" for t in entry["tags"]) + "`"

    content = entry.get("content", "")
    # Check for structured content pattern
    import re as re_mod
    sections = re_mod.findall(
        r"【(.+?)】(.+?)(?=【|\Z)", content, re_mod.DOTALL
    )
    if sections:
        lines = [f"### [{label}] {entry['title']}{tags}"]
        for key, val in sections:
            lines.append(f"- **{key.strip()}**：{val.strip()}")
        return "\n".join(lines) + "\n"

    return (
        f"### [{label}] {entry['title']}{tags}\n"
        f"- **内容**：{content}\n"
    )


def append_entry(path, entry, project_name=None):
    path = resolve_path(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if not os.path.exists(path):
        header = "# 经验记录\n\n"
        if project_name:
            header += f"项目：{project_name}\n\n"
        with open(path, "w") as f:
            f.write(header)

    with open(path, "r") as f:
        content = f.read()

    today = date.today().isoformat()
    date_header = f"## {today}"

    entry_text = format_entry(json.loads(entry) if isinstance(entry, str) else entry)

    if date_header in content:
        content = content.replace(
            date_header, date_header + "\n" + entry_text
        )
    else:
        content = content.rstrip() + "\n\n" + date_header + "\n" + entry_text + "\n"

    with open(path, "w") as f:
        f.write(content)

    print(f"Entry added to {path}")
    return True


def validate(path):
    path = resolve_path(path)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return False

    errors = []
    with open(path, "r") as f:
        for i, line in enumerate(f, 1):
            if line.startswith("### [") and "]" not in line:
                errors.append(f"Line {i}: malformed entry header")
            if "**内容**：" in line and not line.strip().endswith("。"):
                if not line.strip().endswith("\n"):
                    pass
    if errors:
        for e in errors:
            print(f"  WARN: {e}")
        return False
    print(f"Validated {path} - OK")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Manage experiences.md file"
    )
    parser.add_argument("action", choices=["read", "append", "validate"])
    parser.add_argument("--path", default=DEFAULT_PATH, help="Path to experiences.md")
    parser.add_argument("--entry", help="JSON string for append action")
    parser.add_argument(
        "--project", help="Project name (used when creating new file)"
    )

    args = parser.parse_args()

    if args.action == "read":
        entries = read_experiences(args.path)
        print(json.dumps(entries, indent=2, ensure_ascii=False))

    elif args.action == "append":
        if not args.entry:
            print("ERROR: --entry is required for append action")
            sys.exit(1)
        append_entry(args.path, args.entry, args.project)

    elif args.action == "validate":
        valid = validate(args.path)
        sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
