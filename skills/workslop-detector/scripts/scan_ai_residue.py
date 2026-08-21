#!/usr/bin/env python3
"""Scan text for high-confidence AI paste residue and supporting AIisms."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PATTERNS = (
    (
        "assistant_offer",
        "high",
        "Assistant offer left in the document",
        re.compile(r"\b(?:would you like me to|i can also|let me know if you(?:'d| would) like me to)\b", re.I),
    ),
    (
        "assistant_delivery",
        "high",
        "Assistant delivery wrapper left in the document",
        re.compile(
            r"^\s*(?:(?:certainly|absolutely|of course)[!,:—-]*\s+)?(?:here(?:'s| is)|below is)\s+(?:a|an|the|your)\s+(?:polished|revised|refined|concise|professional|updated|draft)",
            re.I,
        ),
    ),
    (
        "model_disclaimer",
        "high",
        "Model disclaimer or capability statement left in the document",
        re.compile(r"\b(?:as an ai(?: language model)?|i (?:do not|don't) have access to|i can(?:not|'t) browse)\b", re.I),
    ),
    (
        "chat_role_label",
        "high",
        "Chat role label left in the document",
        re.compile(r"^\s*(?:assistant|chatgpt|claude)\s*:\s*", re.I),
    ),
    (
        "prompt_fragment",
        "high",
        "Prompt or drafting instruction left in the document",
        re.compile(r"^\s*(?:note to (?:the )?(?:user|writer)|instructions?|prompt)\s*:\s*", re.I),
    ),
    (
        "unresolved_placeholder",
        "high",
        "Unresolved drafting placeholder",
        re.compile(
            r"(?:\[(?:insert|add|include|replace|your|company|client|source|citation|statistic|data|date|name)[^\]\n]{0,80}\]|<(?:insert|replace|company|client|source|citation|name)[^>\n]{0,80}>)",
            re.I,
        ),
    ),
    (
        "assistantish_transition",
        "supporting",
        "Common assistant-style transition; not proof by itself",
        re.compile(r"\b(?:it's important to note|in today's rapidly evolving landscape|delve into|multifaceted approach|in conclusion)\b", re.I),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="UTF-8 text or Markdown file")
    parser.add_argument("--json-out", help="Optional output JSON path")
    return parser.parse_args()


def excerpt(line: str, limit: int = 180) -> str:
    cleaned = " ".join(line.strip().split())
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 1] + "…"


def scan(text: str, source: str) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    lines = text.splitlines()
    for line_number, line in enumerate(lines, start=1):
        for pattern_id, confidence, description, pattern in PATTERNS:
            for match in pattern.finditer(line):
                findings.append(
                    {
                        "pattern_id": pattern_id,
                        "confidence": confidence,
                        "description": description,
                        "line": line_number,
                        "match": match.group(0),
                        "excerpt": excerpt(line),
                    }
                )

    high = [item for item in findings if item["confidence"] == "high"]
    supporting = [item for item in findings if item["confidence"] == "supporting"]
    return {
        "source": source,
        "word_count": len(re.findall(r"\b\w[\w’'-]*\b", text)),
        "line_count": len(lines),
        "high_confidence": high,
        "supporting": supporting,
        "summary": {
            "high_confidence_count": len(high),
            "supporting_count": len(supporting),
        },
    }


def main() -> int:
    args = parse_args()
    try:
        text = Path(args.source).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"scan_error: {exc}", file=sys.stderr)
        return 2

    result = scan(text, args.source)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        try:
            output = Path(args.json_out)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8")
        except OSError as exc:
            print(f"write_error: {exc}", file=sys.stderr)
            return 2
    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
