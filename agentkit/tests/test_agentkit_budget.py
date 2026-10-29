import pytest

from agentkit import Budget, BudgetExceeded, Usage


def test_stops_at_step_limit():
    b = Budget(max_steps=3, max_tokens=10**9, max_spend_usd=10**9)
    for _ in range(3):
        b.start_step()
    with pytest.raises(BudgetExceeded) as exc:
        b.start_step()
    assert exc.value.limit == "steps"
    assert b.steps == 3


def test_stops_at_spend_limit():
    # $1 per million input and $2 per million output; $0.01 cap.
    b = Budget(max_steps=100, max_tokens=10**9, max_spend_usd=0.01, input_price_per_mtok=1, output_price_per_mtok=2)
    b.charge(Usage(input_tokens=2_000, output_tokens=2_000))  # $0.006
    assert b.spend_usd == pytest.approx(0.006)
    with pytest.raises(BudgetExceeded) as exc:
        b.charge(Usage(input_tokens=2_000, output_tokens=2_000))  # $0.012 total
    assert exc.value.limit == "spend"


def test_stops_at_token_limit():
    b = Budget(max_steps=100, max_tokens=1_000, max_spend_usd=10**9)
    b.charge(Usage(input_tokens=400, output_tokens=100))
    with pytest.raises(BudgetExceeded) as exc:
        b.charge(Usage(input_tokens=400, output_tokens=100))
    assert exc.value.limit == "tokens"
