"""Keep API keys out of logs, traces and fixtures."""
from __future__ import annotations

import logging
import os
import re
from typing import Mapping

_KEY_PATTERN = re.compile(r"\bsk-[A-Za-z0-9_-]{8,}")
_MIN_SECRET_LEN = 8


def redact(text: str, env: Mapping[str, str] | None = None) -> str:
    """Mask the value of every *_API_KEY env var and anything shaped like an `sk-` key."""
    env = os.environ if env is None else env
    for name, value in env.items():
        if name.endswith("_API_KEY") and len(value) >= _MIN_SECRET_LEN:
            text = text.replace(value, "[REDACTED]")
    return _KEY_PATTERN.sub("[REDACTED]", text)


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(record.getMessage())
        record.args = ()
        return True
