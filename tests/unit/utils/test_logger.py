import json
import logging

from src.utils.logger import JsonFormatter, logger_config

# --- JsonFormatter ---


def test_json_formatter_output_is_valid_json():
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="src/utils/crud.py",
        lineno=1, msg="hello", args=(), exc_info=None,
    )
    record.correlation_id = "abc123"
    output = JsonFormatter().format(record)
    parsed = json.loads(output)
    assert parsed["message"] == "hello"


def test_json_formatter_contains_required_fields():
    record = logging.LogRecord(
        name="test.module", level=logging.WARNING, pathname="src/utils/crud.py",
        lineno=10, msg="something happened", args=(), exc_info=None,
    )
    record.correlation_id = "xyz789"
    parsed = json.loads(JsonFormatter().format(record))
    assert "timestamp" in parsed
    assert "level" in parsed
    assert "logger" in parsed
    assert "file" in parsed
    assert "func" in parsed
    assert "message" in parsed
    assert "correlation_id" in parsed


def test_json_formatter_short_filename_strips_extension():
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="src/utils/crud.py",
        lineno=1, msg="x", args=(), exc_info=None,
    )
    record.correlation_id = "abc"
    parsed = json.loads(JsonFormatter().format(record))
    assert not parsed["file"].endswith(".py")


def test_json_formatter_correlation_id_fallback():
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="x.py",
        lineno=1, msg="x", args=(), exc_info=None,
    )
    # no correlation_id set — should fall back to "internal"
    parsed = json.loads(JsonFormatter().format(record))
    assert parsed["correlation_id"] == "internal"


def test_json_formatter_level_is_string():
    record = logging.LogRecord(
        name="test", level=logging.ERROR, pathname="x.py",
        lineno=1, msg="err", args=(), exc_info=None,
    )
    record.correlation_id = "id"
    parsed = json.loads(JsonFormatter().format(record))
    assert parsed["level"] == "ERROR"


def test_json_formatter_includes_exc_info(recwarn):
    try:
        raise ValueError("boom")
    except ValueError:
        import sys
        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="test", level=logging.ERROR, pathname="x.py",
        lineno=1, msg="err", args=(), exc_info=exc_info,
    )
    record.correlation_id = "id"
    parsed = json.loads(JsonFormatter().format(record))
    assert "exc_info" in parsed
    assert "ValueError" in parsed["exc_info"]


# --- logger_config ---


def test_logger_config_returns_logger():
    logger = logger_config("test.mocker.a")
    assert isinstance(logger, logging.Logger)


def test_logger_config_has_stream_handler():
    logger = logger_config("test.mocker.b")
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)


def test_logger_config_duplicate_guard():
    logger1 = logger_config("test.mocker.c")
    handler_count = len(logger1.handlers)
    logger2 = logger_config("test.mocker.c")
    assert len(logger2.handlers) == handler_count


def test_logger_config_uses_json_formatter():
    logger = logger_config("test.mocker.d")
    stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
    assert any(isinstance(h.formatter, JsonFormatter) for h in stream_handlers)


def test_logger_config_log_level_from_settings(monkeypatch):
    monkeypatch.setenv("MOCKER_LOG_LEVEL", "DEBUG")

    # use a fresh logger name to avoid duplicate guard
    from src.config import get_settings
    get_settings.cache_clear()

    logger = logger_config("test.mocker.e")
    assert logger.level == logging.DEBUG

    get_settings.cache_clear()
    monkeypatch.delenv("MOCKER_LOG_LEVEL", raising=False)
