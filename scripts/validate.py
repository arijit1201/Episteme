#!/usr/bin/env python3
"""Validate sources.yaml and the front matter of every page in docs/.

Checks
  sources.yaml: required fields, allowed values, unique ids, https URLs, date formats,
                verified sources have last_verified.
  docs/*.md:    front matter present (except docs/index.md), required fields,
                every cited source id exists, every [src:id] marker is listed in front matter,
                verified pages have last_verified, stale pages are reported.

Exit code 1 if any error is found. Stale pages are warnings unless --strict is given.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

SOURCE_REQUIRED = ["id", "title", "url", "publisher", "kind", "tier", "license", "status"]
SOURCE_ENUMS = {
    "kind": {"blog", "guide", "docs", "course", "book", "paper", "spec", "repo"},
    "tier": {"primary", "secondary"},
    "license": {"all-rights-reserved", "cc-by-sa-4.0", "cc-by-4.0", "apache-2.0", "mit", "arxiv-default", "unknown"},
    "status": {"unverified", "verified", "dead"},
}
PAGE_REQUIRED = ["title", "status", "sources", "last_verified"]
PAGE_STATUSES = {"draft", "verified"}
STALE_DAYS = 120
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MARKER_RE = re.compile(r"\[src:([a-z0-9-]+)\]")
DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def _as_date(value) -> dt.date | None:
    """Return a date for YYYY-MM-DD values (str or date), else None."""
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def validate_sources(data) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        return ["sources.yaml: top level must be a mapping with a 'sources' list"]

    seen: set[str] = set()
    for i, src in enumerate(data["sources"]):
        where = f"sources[{i}]"
        if not isinstance(src, dict):
            errors.append(f"{where}: must be a mapping")
            continue
        sid = src.get("id")
        if sid:
            where = f"source '{sid}'"
        for field in SOURCE_REQUIRED:
            if src.get(field) in (None, ""):
                errors.append(f"{where}: missing '{field}'")
        if sid is not None:
            if not isinstance(sid, str) or not ID_RE.match(sid):
                errors.append(f"{where}: id must be kebab-case")
            elif sid in seen:
                errors.append(f"{where}: duplicate id")
            else:
                seen.add(sid)
        for field, allowed in SOURCE_ENUMS.items():
            value = src.get(field)
            if value is not None and value not in allowed:
                errors.append(f"{where}: {field} '{value}' not in {sorted(allowed)}")
        url = src.get("url")
        if isinstance(url, str) and not url.startswith("https://"):
            errors.append(f"{where}: url must start with https://")
        published = src.get("published")
        if published is not None and not (
            isinstance(published, (dt.date, int)) or DATE_RE.match(str(published))
        ):
            errors.append(f"{where}: published must be YYYY, YYYY-MM or YYYY-MM-DD")
        last = src.get("last_verified")
        if last is not None and _as_date(last) is None:
            errors.append(f"{where}: last_verified must be YYYY-MM-DD")
        if src.get("status") == "verified" and last is None:
            errors.append(f"{where}: verified source needs last_verified")
    return errors


def split_front_matter(text: str) -> tuple[dict | None, str]:
    """Return (front_matter, body). front_matter is None if the page has none."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    raw = text[4:end]
    body = text[end + 4 :].lstrip("\n")
    loaded = yaml.safe_load(raw)
    return (loaded if isinstance(loaded, dict) else {}), body


def validate_page(
    name: str, text: str, source_ids: set[str], today: dt.date
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        fm, body = split_front_matter(text)
    except yaml.YAMLError as exc:
        return [f"{name}: front matter is not valid YAML ({exc.__class__.__name__})"], []
    if fm is None:
        return [f"{name}: missing front matter (start from templates/page.md)"], []

    for field in PAGE_REQUIRED:
        if field not in fm:
            errors.append(f"{name}: front matter missing '{field}'")

    status = fm.get("status")
    if status is not None and status not in PAGE_STATUSES:
        errors.append(f"{name}: status '{status}' not in {sorted(PAGE_STATUSES)}")

    listed = fm.get("sources") or []
    if not isinstance(listed, list):
        errors.append(f"{name}: 'sources' must be a list of source ids")
        listed = []
    for sid in listed:
        if sid not in source_ids:
            errors.append(f"{name}: unknown source id '{sid}' in front matter")

    for sid in sorted(set(MARKER_RE.findall(body))):
        if sid not in source_ids:
            errors.append(f"{name}: unknown source id '{sid}' in [src:...] marker")
        elif sid not in listed:
            errors.append(f"{name}: [src:{sid}] used but not listed in front matter 'sources'")

    last = fm.get("last_verified")
    last_date = _as_date(last) if last is not None else None
    if last is not None and last_date is None:
        errors.append(f"{name}: last_verified must be YYYY-MM-DD")
    if status == "verified":
        if last_date is None:
            errors.append(f"{name}: verified page needs last_verified")
        elif (today - last_date).days > STALE_DAYS:
            warnings.append(
                f"{name}: stale (last verified {last_date}, more than {STALE_DAYS} days ago)"
            )
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--strict", action="store_true", help="treat stale pages as errors")
    args = parser.parse_args(argv)

    sources_path = args.root / "sources.yaml"
    try:
        data = yaml.safe_load(sources_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"ERROR sources.yaml: cannot load ({exc})")
        return 1

    errors = validate_sources(data)
    source_ids = {
        s["id"] for s in data.get("sources", []) if isinstance(s, dict) and isinstance(s.get("id"), str)
    }

    warnings: list[str] = []
    docs = args.root / "docs"
    today = dt.date.today()
    pages = sorted(docs.rglob("*.md")) if docs.exists() else []
    for page in pages:
        rel = page.relative_to(args.root).as_posix()
        if rel == "docs/index.md":
            continue
        page_errors, page_warnings = validate_page(rel, page.read_text(encoding="utf-8"), source_ids, today)
        errors += page_errors
        warnings += page_warnings

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if args.strict and warnings:
        errors += warnings

    print(f"Checked {len(source_ids)} sources and {len(pages)} pages: {len(errors)} errors, {len(warnings)} warnings.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
