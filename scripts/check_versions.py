#!/usr/bin/env python3
"""Flag pinned Python dependencies that have fallen behind the latest release on PyPI.

Scans requirements*.txt and pyproject.toml under the given paths (default: starters/ and agentkit/).
Only exact pins (name==version) are checked.

  minor  latest release has the same major version but a higher minor version -> warning
  major  latest release has a higher major version (or a higher minor on 0.x)   -> warning, error with --strict

Network failures are reported as warnings so CI does not fail on a PyPI outage.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

from packaging.version import InvalidVersion, Version

ROOT = Path(__file__).resolve().parent.parent
PIN_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])?\s*==\s*([^\s;#,]+)")


def parse_requirements(text: str) -> dict[str, str]:
    pins = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0]
        m = PIN_RE.match(line)
        if m:
            pins[m.group(1).lower()] = m.group(2)
    return pins


def parse_pyproject(text: str) -> dict[str, str]:
    data = tomllib.loads(text)
    deps = list(data.get("project", {}).get("dependencies", []))
    for group in data.get("project", {}).get("optional-dependencies", {}).values():
        deps += group
    for group in data.get("dependency-groups", {}).values():
        deps += [d for d in group if isinstance(d, str)]
    return parse_requirements("\n".join(deps))


def compare(pinned: str, latest: str) -> str:
    """Return 'ok', 'minor' or 'major'. 0.x minor bumps count as major (breaking by convention)."""
    p, l = Version(pinned), Version(latest)
    if l <= p:
        return "ok"
    if l.major > p.major:
        return "major"
    if p.major == 0 and l.minor > p.minor:
        return "major"
    if l.minor > p.minor:
        return "minor"
    return "ok"


def latest_version(name: str, timeout: float = 10.0) -> str:
    url = f"https://pypi.org/pypi/{name}/json"
    with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 (fixed https host)
        return json.load(resp)["info"]["version"]


def collect(paths: list[Path]) -> dict[Path, dict[str, str]]:
    found: dict[Path, dict[str, str]] = {}
    for base in paths:
        if not base.exists():
            continue
        for f in sorted(base.rglob("requirements*.txt")):
            found[f] = parse_requirements(f.read_text(encoding="utf-8"))
        for f in sorted(base.rglob("pyproject.toml")):
            found[f] = parse_pyproject(f.read_text(encoding="utf-8"))
    return {f: pins for f, pins in found.items() if pins}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path, default=[ROOT / "starters", ROOT / "agentkit"])
    parser.add_argument("--strict", action="store_true", help="fail on major-version lag")
    args = parser.parse_args(argv)

    files = collect(args.paths)
    if not files:
        print("No pinned dependencies found. Nothing to check.")
        return 0

    errors = 0
    cache: dict[str, str | None] = {}
    for f, pins in files.items():
        for name, pinned in sorted(pins.items()):
            if name not in cache:
                try:
                    cache[name] = latest_version(name)
                except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
                    print(f"WARN  {name}: could not reach PyPI ({exc.__class__.__name__})")
                    cache[name] = None
            latest = cache[name]
            if latest is None:
                continue
            try:
                lag = compare(pinned, latest)
            except InvalidVersion:
                print(f"WARN  {f}: {name}=={pinned} is not a valid version")
                continue
            if lag == "ok":
                continue
            level = "ERROR" if (lag == "major" and args.strict) else "WARN "
            errors += level == "ERROR"
            print(f"{level} {f}: {name}=={pinned} is behind {latest} ({lag})")

    print(f"Checked {sum(len(p) for p in files.values())} pins in {len(files)} files.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
