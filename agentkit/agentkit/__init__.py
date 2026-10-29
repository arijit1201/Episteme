"""Provider-neutral model adapter shared by all starters."""
import logging

from .budget import Budget, BudgetExceeded
from .client import ModelClient, TracingClient
from .config import Config, ConfigError, load_config, make_client
from .redact import RedactingFilter, redact
from .replay import FixtureMissing, RecordingClient, ReplayClient
from .types import Response, ToolCall, ToolSpec, Usage, assistant_message, tool_message, user_message

logging.getLogger("agentkit").addFilter(RedactingFilter())

__all__ = [
    "Budget", "BudgetExceeded", "Config", "ConfigError", "FixtureMissing", "ModelClient",
    "RecordingClient", "RedactingFilter", "ReplayClient", "Response", "ToolCall", "ToolSpec",
    "TracingClient", "Usage", "assistant_message", "load_config", "make_client", "redact",
    "tool_message", "user_message",
]
