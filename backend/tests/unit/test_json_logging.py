"""NFR-06: structured JSON logs, one object per line, with a correlation id."""

from __future__ import annotations

import io
import json
import logging

import pytest

from src.config.logging_setup import configure_logging, correlation_id_var


def _records(stream: io.StringIO) -> list[dict[str, object]]:
    return [json.loads(line) for line in stream.getvalue().splitlines() if line]


def test_NFR06_each_log_line_is_one_json_object_with_required_keys(log_stream: io.StringIO) -> None:
    configure_logging("INFO", stream=log_stream)

    logging.getLogger("helpdesk.test").info("hello world")

    records = _records(log_stream)
    assert len(records) == 1
    assert set(records[0]) == {"timestamp", "level", "logger", "message", "correlation_id"}
    assert records[0]["level"] == "INFO"
    assert records[0]["logger"] == "helpdesk.test"
    assert records[0]["message"] == "hello world"
    assert records[0]["correlation_id"] is None


def test_NFR06_timestamp_is_utc_iso_8601(log_stream: io.StringIO) -> None:
    configure_logging("INFO", stream=log_stream)

    logging.getLogger("helpdesk.test").info("tick")

    timestamp = _records(log_stream)[0]["timestamp"]
    assert isinstance(timestamp, str)
    assert timestamp.endswith("+00:00")


def test_NFR06_message_arguments_are_interpolated(log_stream: io.StringIO) -> None:
    configure_logging("INFO", stream=log_stream)

    logging.getLogger("helpdesk.test").info("count=%d", 3)

    assert _records(log_stream)[0]["message"] == "count=3"


def test_NFR06_correlation_id_from_request_context_is_on_every_line(
    log_stream: io.StringIO,
) -> None:
    configure_logging("INFO", stream=log_stream)
    token = correlation_id_var.set("req-abc-123")
    try:
        logger = logging.getLogger("helpdesk.test")
        logger.info("first")
        logger.warning("second")
    finally:
        correlation_id_var.reset(token)

    records = _records(log_stream)
    assert [r["correlation_id"] for r in records] == ["req-abc-123", "req-abc-123"]


def test_NFR06_correlation_id_is_null_once_context_is_reset(log_stream: io.StringIO) -> None:
    configure_logging("INFO", stream=log_stream)
    token = correlation_id_var.set("req-abc-123")
    correlation_id_var.reset(token)

    logging.getLogger("helpdesk.test").info("after request")

    assert _records(log_stream)[0]["correlation_id"] is None


def test_NFR06_configured_level_suppresses_lower_levels(log_stream: io.StringIO) -> None:
    configure_logging("WARNING", stream=log_stream)

    logger = logging.getLogger("helpdesk.test")
    logger.info("quiet")
    logger.warning("loud")

    records = _records(log_stream)
    assert [r["message"] for r in records] == ["loud"]
    assert records[0]["level"] == "WARNING"


def test_NFR06_exception_traceback_is_included_in_the_json_object(
    log_stream: io.StringIO,
) -> None:
    configure_logging("INFO", stream=log_stream)

    try:
        raise ValueError("boom")
    except ValueError:
        logging.getLogger("helpdesk.test").exception("failed")

    record = _records(log_stream)[0]
    assert "ValueError: boom" in str(record["exception"])


def test_NFR06_configuring_twice_does_not_duplicate_lines(log_stream: io.StringIO) -> None:
    configure_logging("INFO", stream=log_stream)
    configure_logging("INFO", stream=log_stream)

    logging.getLogger("helpdesk.test").info("once")

    assert len(_records(log_stream)) == 1


def test_NFR06_unknown_level_is_rejected(log_stream: io.StringIO) -> None:
    with pytest.raises(ValueError):
        configure_logging("LOUD", stream=log_stream)
