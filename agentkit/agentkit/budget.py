"""Per-run limits on steps, tokens and estimated spend."""
from __future__ import annotations

from dataclasses import dataclass, field

from .types import Usage


class BudgetExceeded(Exception):
    def __init__(self, limit: str, detail: str):
        super().__init__(f"{limit} limit reached: {detail}")
        self.limit = limit  # "steps" | "tokens" | "spend"


@dataclass
class Budget:
    max_steps: int
    max_tokens: int
    max_spend_usd: float
    # USD per million tokens. None means spend cannot be estimated (only allowed for replay).
    input_price_per_mtok: float | None = None
    output_price_per_mtok: float | None = None
    steps: int = field(default=0, init=False)
    tokens: int = field(default=0, init=False)
    spend_usd: float = field(default=0.0, init=False)

    @classmethod
    def from_config(cls, config) -> "Budget":
        return cls(
            config.max_steps,
            config.max_tokens,
            config.max_spend_usd,
            config.input_price_per_mtok,
            config.output_price_per_mtok,
        )

    def start_step(self) -> None:
        """Call before each model call. Raises once max_steps steps have already run."""
        if self.steps >= self.max_steps:
            raise BudgetExceeded("steps", f"{self.steps} of {self.max_steps} steps used")
        self.steps += 1

    def charge(self, usage: Usage) -> None:
        """Record usage from one call. Raises when a token or spend limit is reached."""
        self.tokens += usage.input_tokens + usage.output_tokens
        if self.input_price_per_mtok is not None and self.output_price_per_mtok is not None:
            self.spend_usd += (
                usage.input_tokens * self.input_price_per_mtok
                + usage.output_tokens * self.output_price_per_mtok
            ) / 1_000_000
        if self.tokens >= self.max_tokens:
            raise BudgetExceeded("tokens", f"{self.tokens} of {self.max_tokens} tokens used")
        if self.spend_usd >= self.max_spend_usd:
            raise BudgetExceeded("spend", f"${self.spend_usd:.4f} of ${self.max_spend_usd:.2f} spent")
