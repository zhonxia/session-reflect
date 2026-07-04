#!/usr/bin/env python3
"""
Analyze opencode session history from SQLite database.
Outputs structured summary for Claude to incorporate into reflection.

Usage:
  python3 scripts/analyze_history.py [--db PATH] [--session SESSION_ID] [--limit N]

If --session is provided, analyzes only that session.
Otherwise, analyzes recent sessions (--limit N, default 5).
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone


def get_db_path():
    default_path = os.path.expanduser("~/.local/share/opencode/opencode.db")
    alt_path = os.path.expanduser(
        "~/Library/Application Support/opencode/opencode.db"
    )
    if os.path.exists(default_path):
        return default_path
    if os.path.exists(alt_path):
        return alt_path
    return None


def connect_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def parse_ts(ts):
    """Parse unix ms timestamp to readable datetime."""
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M"
    )


def get_recent_sessions(conn, limit=5):
    return conn.execute(
        """
        SELECT id, project_id, title, agent, model, path,
               time_created, time_updated, cost, tokens_input, tokens_output,
               tokens_reasoning, tokens_cache_read, tokens_cache_write
        FROM session
        WHERE title != ''
        ORDER BY time_created DESC
        LIMIT ?
    """,
        (limit,),
    ).fetchall()


def get_session_by_id(conn, session_id):
    return conn.execute(
        """
        SELECT id, project_id, title, agent, model, path,
               time_created, time_updated, cost, tokens_input, tokens_output,
               tokens_reasoning, tokens_cache_read, tokens_cache_write
        FROM session
        WHERE id = ?
    """,
        (session_id,),
    ).fetchone()


def get_session_messages(conn, session_id):
    return conn.execute(
        """
        SELECT m.id, m.time_created, m.data as msg_data,
               p.data as part_data
        FROM message m
        JOIN part p ON p.message_id = m.id
        WHERE m.session_id = ?
        ORDER BY m.time_created, p.rowid
    """,
        (session_id,),
    ).fetchall()


def extract_user_text(rows):
    """Extract user text messages from message/part rows."""
    texts = []
    for row in rows:
        msg_data = json.loads(row["msg_data"])
        role = msg_data.get("role", "")
        if role != "user":
            continue
        part_data = json.loads(row["part_data"])
        if part_data.get("type") == "text":
            texts.append(part_data["text"])
    return texts


def extract_tool_calls(rows):
    """Extract assistant tool usage patterns."""
    tool_counts = {}
    for row in rows:
        msg_data = json.loads(row["msg_data"])
        role = msg_data.get("role", "")
        if role != "assistant":
            continue
        part_data = json.loads(row["part_data"])
        if part_data.get("type") == "tool":
            tool_name = part_data.get("tool", "unknown")
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
    return tool_counts


def count_user_assistant_messages(rows):
    user_count = 0
    assistant_count = 0
    seen_msgs = set()
    for row in rows:
        msg_id = row["id"]
        if msg_id in seen_msgs:
            continue
        seen_msgs.add(msg_id)
        msg_data = json.loads(row["msg_data"])
        role = msg_data.get("role", "")
        if role == "user":
            user_count += 1
        elif role == "assistant":
            assistant_count += 1
    return user_count, assistant_count


def analyze_session(conn, session):
    rows = get_session_messages(conn, session["id"])
    user_texts = extract_user_text(rows)
    tool_calls = extract_tool_calls(rows)
    user_count, assistant_count = count_user_assistant_messages(rows)

    return {
        "session_id": session["id"],
        "title": session["title"],
        "agent": session["agent"],
        "model": json.loads(session["model"]) if session["model"] else {},
        "path": session["path"],
        "time_created": parse_ts(session["time_created"]),
        "time_updated": parse_ts(session["time_updated"]),
        "cost": session["cost"],
        "tokens_input": session["tokens_input"],
        "tokens_output": session["tokens_output"],
        "tokens_reasoning": session["tokens_reasoning"],
        "user_turns": user_count,
        "assistant_turns": assistant_count,
        "tool_calls": tool_calls,
        "user_queries": user_texts,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze opencode session history"
    )
    parser.add_argument("--db", help="Path to opencode.db")
    parser.add_argument("--session", help="Analyze specific session ID")
    parser.add_argument(
        "--limit", type=int, default=5, help="Number of recent sessions (default: 5)"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output raw JSON"
    )
    args = parser.parse_args()

    db_path = args.db or get_db_path()
    if not db_path or not os.path.exists(db_path):
        print("ERROR: opencode.db not found. Use --db to specify path.")
        sys.exit(1)

    conn = connect_db(db_path)

    if args.session:
        session = get_session_by_id(conn, args.session)
        if not session:
            print(f"ERROR: Session {args.session} not found.")
            sys.exit(1)
        sessions = [session]
    else:
        sessions = get_recent_sessions(conn, limit=args.limit)

    results = [analyze_session(conn, s) for s in sessions]

    conn.close()

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    print("=== Session History Analysis ===\n")
    for r in results:
        print(f"## {r['title']}")
        print(f"  Agent: {r['agent']}  |  Model: {r['model'].get('id','?')}")
        print(f"  Time: {r['time_created']}  |  Cost: ${r['cost']:.4f}")
        print(f"  Turns: {r['user_turns']} user / {r['assistant_turns']} assistant")
        print(f"  Tokens: {r['tokens_input']} in / {r['tokens_output']} out")
        if r["tool_calls"]:
            print(f"  Tools: {r['tool_calls']}")
        print()


if __name__ == "__main__":
    main()
