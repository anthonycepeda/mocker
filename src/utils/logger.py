import json
import logging
import os
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON for Grafana/Loki ingestion.

    Adds ``short_filename`` (basename without extension) and ``correlation_id``
    to every record. ``correlation_id`` is injected by ``CorrelationIdFilter``
    before formatting; falls back to ``"internal"`` when no request context exists.
    """

    def format(self, record: logging.LogRecord) -> str:
        record.short_filename = os.path.splitext(record.filename)[0]
        log_record: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "level": record.levelname,
            "logger": record.name,
            "file": record.short_filename,
            "func": record.funcName,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "internal"),
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def logger_config(module: str) -> logging.Logger:
    """Configure and return a JSON structured logger for the given module.

    - Stdout only — K8s streams logs to Grafana/Loki at cluster level.
    - Log level driven by ``MOCKER_LOG_LEVEL`` env var (default ``INFO``).
    - Correlation ID injected via ``CorrelationIdFilter`` from ``asgi_correlation_id``.
    - Duplicate handler guard — safe to call multiple times for the same module.

    Args:
        module: Logger name — pass ``__name__`` from the calling module.

    Returns:
        Configured ``Logger`` instance.
    """
    from asgi_correlation_id import CorrelationIdFilter

    from src.config import get_settings

    logger = logging.getLogger(module)

    if logger.handlers:  # duplicate handler guard
        return logger

    log_level = getattr(logging, get_settings().log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    handler = logging.StreamHandler()
    handler.addFilter(
        CorrelationIdFilter(name="mocker", uuid_length=10, default_value="internal")
    )
    handler.setFormatter(JsonFormatter())

    logger.addHandler(handler)
    return logger
