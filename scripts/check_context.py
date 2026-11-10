#!/usr/bin/env python3
"""Mechanical checks for context written for AI agents.

Reports, with line numbers:
  planning-note       TBD, TODO, "add later" and similar notes left in the text
  status-conflict     status lines in one file that disagree (draft and approved)
  environment-term    environment words with no exact value on the same line
  prohibition-only    "never" or "do not" rules with no alternative given

The findings are hints for a reviewer, not verdicts. Standard library only.

Usage: python3 check_context.py FILE [FILE ...]
Exit code: 0 when the files were read (with or without findings), 2 on a usage or read error.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass

PLANNING_NOTE = re.compile(
    r"\b(TBD|TBC|TODO|FIXME|XXX)\b"
    r"|\b(?:add|write|fill in|finish|decide)\b[^.\n]{0,40}?\blater\b"
    r"|\bto be (?:decided|confirmed|determined|added)\b",
    re.IGNORECASE,
)

STATUS_LINE = re.compile(r"^\s*(?:[-*]\s*)?\**status\**\s*:", re.IGNORECASE)
DRAFT_WORDS = re.compile(r"\b(draft|proposed|proposal|not yet approved|for review|work in progress|wip)\b", re.IGNORECASE)
APPROVED_WORDS = re.compile(r"\b(approved|final|accepted|signed off)\b", re.IGNORECASE)
NOT_YET_APPROVED = re.compile(r"\bnot (?:yet |been )?approved\b|\b(?:before|until)\b[^.\n]{0,40}?\b(?:is|are|has been) approved\b", re.IGNORECASE)

ENVIRONMENT_TERM = re.compile(
    r"\b(local development|local environment|locally|non-local|dev environment|development environment"
    r"|in development|test environment|staging|in production|production environment|outside local development)\b",
    re.IGNORECASE,
)
EXACT_VALUE = re.compile(r"`[^`]+`|\"[^\"]+\"|'[^']+'|\b[A-Z][A-Z0-9_]{2,}=\S+")

PROHIBITION = re.compile(r"\b(never|do not|don't|must not|mustn't|should not|shouldn't)\b", re.IGNORECASE)
ALTERNATIVE = re.compile(
    r"\b(instead|rather than|use|ask|stop|report|leave|keep|only|unless|except|prefer|so that|because)\b|[;:]",
    re.IGNORECASE,
)

FENCE = re.compile(r"^\s*(```|~~~)")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True)
class Finding:
    check: str
    path: str
    line: int
    text: str

    def format(self) -> str:
        return f"- Check: {self.check}\n  Location: {self.path}:{self.line}\n  Text: {self.text}"


def _excerpt(line: str, limit: int = 120) -> str:
    text = line.strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _prose_lines(lines: list[str]) -> list[tuple[int, str]]:
    """Lines outside fenced code blocks, numbered from 1."""
    result: list[tuple[int, str]] = []
    in_fence = False
    for number, line in enumerate(lines, start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            result.append((number, line))
    return result


def check_planning_notes(path: str, lines: list[str]) -> list[Finding]:
    return [
        Finding("planning-note", path, number, _excerpt(line))
        for number, line in enumerate(lines, start=1)
        if PLANNING_NOTE.search(line)
    ]


def _status_kind(line: str) -> str | None:
    if NOT_YET_APPROVED.search(line) or DRAFT_WORDS.search(line):
        return "draft"
    if APPROVED_WORDS.search(line):
        return "approved"
    return None


def check_status_conflicts(path: str, lines: list[str]) -> list[Finding]:
    marked: list[tuple[int, str, str]] = []
    for number, line in _prose_lines(lines):
        is_status_line = STATUS_LINE.match(line)
        if is_status_line or NOT_YET_APPROVED.search(line):
            kind = _status_kind(line)
            if kind:
                marked.append((number, line, kind))
    kinds = {kind for _, _, kind in marked}
    if len(kinds) < 2:
        return []
    return [Finding("status-conflict", path, number, f"{kind}: {_excerpt(line)}") for number, line, kind in marked]


def check_environment_terms(path: str, lines: list[str]) -> list[Finding]:
    return [
        Finding("environment-term", path, number, _excerpt(line))
        for number, line in _prose_lines(lines)
        if ENVIRONMENT_TERM.search(line) and not EXACT_VALUE.search(line)
    ]


def check_prohibition_only(path: str, lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    prose = _prose_lines(lines)
    for index, (number, line) in enumerate(prose):
        sentences = SENTENCE_SPLIT.split(line.strip())
        for position, sentence in enumerate(sentences):
            if not PROHIBITION.search(sentence) or ALTERNATIVE.search(sentence):
                continue
            if position + 1 < len(sentences):
                following = sentences[position + 1]
            elif index + 1 < len(prose):
                following = prose[index + 1][1]
            else:
                following = ""
            if ALTERNATIVE.search(following):
                continue
            findings.append(Finding("prohibition-only", path, number, _excerpt(sentence)))
    return findings


CHECKS = (check_planning_notes, check_status_conflicts, check_environment_terms, check_prohibition_only)


def check_text(path: str, text: str) -> list[Finding]:
    lines = text.splitlines()
    findings: list[Finding] = []
    for check in CHECKS:
        findings.extend(check(path, lines))
    return sorted(findings, key=lambda finding: (finding.line, finding.check))


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"-h", "--help"}:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    total = 0
    for path in argv:
        try:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
        except OSError as error:
            print(f"error: cannot read {path}: {error}", file=sys.stderr)
            return 2
        for finding in check_text(path, text):
            print(finding.format())
            total += 1
    print(f"{total} hint(s). These are hints for the reviewer, not findings.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
