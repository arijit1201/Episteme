#!/usr/bin/env python3
"""Check that a drafted page paraphrases a source instead of copying it.

Usage:
    python scripts/check_overlap.py PAGE.md SOURCE.txt [--max-run 15] [--max-ratio 0.10]

PAGE.md is the draft. SOURCE.txt is the fetched source text (kept in .cache/, never committed).

Reports
  longest_run   longest run of consecutive words shared by page and source (quotes excluded)
  ratio         fraction of the page's 8-word sequences that also appear in the source
  long_quotes   quoted passages in the page that are 15 words or longer

Fails (exit 1) if longest_run >= --max-run, ratio > --max-ratio, or any long quote exists.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

WORD_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
QUOTE_RE = re.compile(r"[\"“]([^\"”]+)[\"”]")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
MARKER_RE = re.compile(r"\[src:[a-z0-9-]+\]")
NGRAM = 8


def words(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def strip_page(text: str) -> tuple[str, list[str]]:
    """Remove front matter, code blocks and source markers. Return (text without quotes, quotes)."""
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            text = text[end + 4 :]
    text = FENCE_RE.sub(" ", text)
    text = MARKER_RE.sub(" ", text)
    quotes = QUOTE_RE.findall(text)
    text = QUOTE_RE.sub(" ", text)
    return text, quotes


def ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def longest_shared_run(a: list[str], b: list[str]) -> int:
    """Length of the longest run of consecutive words present in both lists (binary search on n)."""
    lo, hi = 0, min(len(a), len(b))
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ngrams(a, mid) & ngrams(b, mid):
            lo = mid
        else:
            hi = mid - 1
    return lo


@dataclass
class Report:
    longest_run: int
    ratio: float
    long_quotes: list[str] = field(default_factory=list)

    def failures(self, max_run: int, max_ratio: float) -> list[str]:
        out = []
        if self.longest_run >= max_run:
            out.append(f"longest shared run is {self.longest_run} words (limit {max_run - 1})")
        if self.ratio > max_ratio:
            out.append(f"{self.ratio:.1%} of {NGRAM}-word sequences appear in the source (limit {max_ratio:.0%})")
        for q in self.long_quotes:
            out.append(f"quote of {len(words(q))} words is too long: \"{q[:60]}...\"")
        return out


def analyze(page_text: str, source_text: str, quote_limit: int = 15) -> Report:
    body, quotes = strip_page(page_text)
    page_tokens = words(body)
    source_tokens = words(source_text)
    run = longest_shared_run(page_tokens, source_tokens)
    page_grams = ngrams(page_tokens, NGRAM)
    ratio = len(page_grams & ngrams(source_tokens, NGRAM)) / len(page_grams) if page_grams else 0.0
    long_quotes = [q for q in quotes if len(words(q)) >= quote_limit]
    return Report(longest_run=run, ratio=ratio, long_quotes=long_quotes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("page", type=Path)
    parser.add_argument("source", type=Path)
    parser.add_argument("--max-run", type=int, default=15)
    parser.add_argument("--max-ratio", type=float, default=0.10)
    args = parser.parse_args(argv)

    report = analyze(args.page.read_text(encoding="utf-8"), args.source.read_text(encoding="utf-8"))
    print(f"longest_run={report.longest_run} ratio={report.ratio:.3f} long_quotes={len(report.long_quotes)}")
    problems = report.failures(args.max_run, args.max_ratio)
    for p in problems:
        print(f"FAIL {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
