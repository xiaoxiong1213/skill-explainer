#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""List installed skills with their purpose (name + description from SKILL.md).

Usage:
    python list_skills.py <root1> [<root2> ...] [--top-level] [--plain]

    <root1>...   One or more skill root directories to scan recursively.
    --top-level  Only list skills whose SKILL.md sits directly under a root
                 (excludes nested sub-skills / branches).
    --plain      Human-readable text output (default is JSON on stdout).

Output (JSON mode) is a list of entries:
    {"name": str, "description": str, "root": str, "path": str, "level": "top"|"nested"}
"""

import argparse
import json
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*$", re.MULTILINE)
KEY_LINE_RE = re.compile(r"^([A-Za-z0-9_\-]+):\s*(.*)$")
INDENT_RE = re.compile(r"^[ \t]+(\S.*)$")
BULLET_RE = re.compile(r"^[ \t]*[-*+]\s+(.*)$")
QUOTED_RE = re.compile(r'^[\'"](.*)[\'"]$')
# YAML block scalar indicators that should be ignored as the value itself.
SCALAR_HINT_RE = re.compile(r"^[>|][-+]?$")


def strip_quotes(value: str) -> str:
    """Remove a single matching pair of surrounding quotes."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> dict:
    """Extract name and description from YAML frontmatter without a YAML lib."""
    result = {"name": None, "description": None}
    # Frontmatter is the first --- block at the start of the file.
    if not text.startswith("---"):
        return result
    match = FRONTMATTER_RE.search(text, 3)
    if not match:
        return result
    block = text[3:match.start()]
    lines = block.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        key_match = KEY_LINE_RE.match(line)
        if not key_match:
            i += 1
            continue
        key, first_value = key_match.group(1), key_match.group(2).strip()
        i += 1
        if key in ("name", "description"):
            # A lone block scalar indicator (">-", "|", ...) means the actual
            # value starts on the following lines.
            if not first_value or SCALAR_HINT_RE.match(first_value):
                first_value = ""
            if not first_value:
                # Value may start on the following indented / bullet lines.
                parts = []
                while i < len(lines):
                    nxt = lines[i]
                    if not nxt.strip():
                        i += 1
                        continue
                    bullet = BULLET_RE.match(nxt)
                    indent = INDENT_RE.match(nxt)
                    if bullet:
                        parts.append(bullet.group(1).strip())
                        i += 1
                        continue
                    if indent and not KEY_LINE_RE.match(nxt.lstrip()):
                        parts.append(indent.group(1).strip())
                        i += 1
                        continue
                    break
                value = " ".join(parts).strip()
            else:
                # Value on the same line; absorb following indented continuations.
                parts = [first_value]
                while i < len(lines):
                    nxt = lines[i]
                    if not nxt.strip():
                        i += 1
                        continue
                    bullet = BULLET_RE.match(nxt)
                    indent = INDENT_RE.match(nxt)
                    if bullet:
                        parts.append(bullet.group(1).strip())
                        i += 1
                        continue
                    if indent and not KEY_LINE_RE.match(nxt.lstrip()):
                        parts.append(indent.group(1).strip())
                        i += 1
                        continue
                    break
                value = " ".join(parts).strip()
            result[key] = strip_quotes(value)
    return result


def find_skills(roots, top_level_only: bool):
    """Yield (name, description, root, path, level) tuples, deduplicated by path."""
    seen = set()
    for root_str in roots:
        root = Path(root_str)
        if not root.is_dir():
            print(f"warning: not a directory, skipped: {root}", file=sys.stderr)
            continue
        for md in root.rglob("SKILL.md"):
            try:
                resolved = str(md.resolve())
            except OSError:
                resolved = str(md)
            if resolved in seen:
                continue
            seen.add(resolved)
            relative = md.relative_to(root)
            # Top-level: SKILL.md directly under the root (1 part) or directly
            # under a skill folder (2 parts: <skill>/SKILL.md). Deeper = nested.
            is_top = len(relative.parts) <= 2
            if top_level_only and not is_top:
                continue
            try:
                text = md.read_text(encoding="utf-8-sig")
            except (UnicodeDecodeError, OSError):
                try:
                    text = md.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
            meta = parse_frontmatter(text)
            name = meta["name"] or md.parent.name
            description = meta["description"] or ""
            yield {
                "name": name,
                "description": description,
                "root": str(root),
                "path": str(md),
                "level": "top" if is_top else "nested",
            }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", help="skill root directories to scan")
    parser.add_argument("--top-level", action="store_true", help="only top-level skills")
    parser.add_argument("--plain", action="store_true", help="human-readable text output")
    args = parser.parse_args()

    entries = sorted(
        find_skills(args.roots, args.top_level),
        key=lambda e: (e["level"], e["name"].lower(), e["path"]),
    )

    if args.plain:
        for e in entries:
            print(f"[{e['level']}] {e['name']}")
            print(f"    用途: {e['description']}")
            print(f"    位置: {e['path']}")
        return 0

    print(json.dumps(entries, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
