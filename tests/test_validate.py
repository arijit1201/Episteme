import datetime as dt
from pathlib import Path

import yaml

import validate

ROOT = Path(__file__).resolve().parent.parent
TODAY = dt.date(2026, 10, 29)
IDS = {"a-source", "b-source"}


def good_source(**overrides):
    src = {
        "id": "a-source",
        "title": "A",
        "url": "https://example.com/a",
        "publisher": "X",
        "kind": "blog",
        "tier": "primary",
        "license": "unknown",
        "status": "unverified",
        "last_verified": None,
    }
    src.update(overrides)
    return src


def page(front: str, body: str = "Body.") -> str:
    return f"---\n{front}\n---\n\n{body}\n"


def test_repo_sources_yaml_is_valid():
    data = yaml.safe_load((ROOT / "sources.yaml").read_text(encoding="utf-8"))
    assert validate.validate_sources(data) == []


def test_repo_passes_validation():
    assert validate.main(["--root", str(ROOT)]) == 0


def test_duplicate_and_bad_ids():
    data = {"sources": [good_source(), good_source(), good_source(id="Bad_ID")]}
    errors = validate.validate_sources(data)
    assert any("duplicate id" in e for e in errors)
    assert any("kebab-case" in e for e in errors)


def test_bad_enum_and_http_url():
    data = {"sources": [good_source(kind="video", url="http://example.com")]}
    errors = validate.validate_sources(data)
    assert any("kind 'video'" in e for e in errors)
    assert any("https://" in e for e in errors)


def test_verified_source_needs_date():
    errors = validate.validate_sources({"sources": [good_source(status="verified")]})
    assert any("needs last_verified" in e for e in errors)


def test_page_without_front_matter_fails():
    errors, _ = validate.validate_page("docs/x.md", "# Title\n", IDS, TODAY)
    assert errors


def test_valid_page_passes():
    text = page(
        "title: T\nstatus: verified\nsources: [a-source]\nlast_verified: 2026-10-01",
        "Claim [src:a-source].",
    )
    assert validate.validate_page("docs/x.md", text, IDS, TODAY) == ([], [])


def test_unknown_marker_and_unlisted_marker():
    text = page(
        "title: T\nstatus: draft\nsources: [a-source]\nlast_verified: null",
        "One [src:nope]. Two [src:b-source].",
    )
    errors, _ = validate.validate_page("docs/x.md", text, IDS, TODAY)
    assert any("unknown source id 'nope'" in e for e in errors)
    assert any("[src:b-source] used but not listed" in e for e in errors)


def test_stale_page_warns():
    text = page("title: T\nstatus: verified\nsources: [a-source]\nlast_verified: 2026-01-01")
    errors, warnings = validate.validate_page("docs/x.md", text, IDS, TODAY)
    assert errors == []
    assert warnings and "stale" in warnings[0]


def test_verified_page_needs_date():
    text = page("title: T\nstatus: verified\nsources: []\nlast_verified: null")
    errors, _ = validate.validate_page("docs/x.md", text, IDS, TODAY)
    assert any("needs last_verified" in e for e in errors)
