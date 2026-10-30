from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
VERDICTS = {"SUPPORTED", "UNSUPPORTED", "CONTRADICTED", "MISATTRIBUTED", "OPINION_OK"}


def test_planted_errors_reference_known_sources():
    sources = yaml.safe_load((ROOT / "sources.yaml").read_text(encoding="utf-8"))
    ids = {s["id"] for s in sources["sources"]}
    cases = yaml.safe_load((ROOT / "evals/verifier/planted_errors.yaml").read_text(encoding="utf-8"))["cases"]
    case_ids = [c["id"] for c in cases]
    assert len(case_ids) == len(set(case_ids)), "duplicate case ids"
    for c in cases:
        assert c["source"] in ids, f"{c['id']}: unknown source {c['source']}"
        assert c["expected"] in VERDICTS, f"{c['id']}: bad verdict {c['expected']}"
        assert c["claim"].strip()


def test_planted_errors_meet_phase_2_size():
    cases = yaml.safe_load((ROOT / "evals/verifier/planted_errors.yaml").read_text(encoding="utf-8"))["cases"]
    correct = [c for c in cases if c["expected"] in {"SUPPORTED", "OPINION_OK"}]
    wrong = [c for c in cases if c["expected"] not in {"SUPPORTED", "OPINION_OK"}]
    assert len(wrong) >= 20
    assert len(correct) >= 10
