
"""Проверка TCP-протокола с помощью Hypothesis."""

import struct

import pytest
from hypothesis import given, settings, strategies as st

from src.protocol import (
    VERSION,
    REQUEST_HEADER_SIZE,
    RESPONSE_HEADER_SIZE,
    create_packet,
    read_packet,
    create_response_packet,
    read_response_packet,
)


@given(
    operation=st.integers(min_value=0, max_value=255),
    message=st.text(max_size=1000)
)
@settings(max_examples=100)
def test_request_roundtrip(operation, message):
    """Проверяет упаковку и распаковку запроса."""
    packet = create_packet(operation, message)

    version, code, result = read_packet(packet)

    assert version == VERSION
    assert code == operation
    assert result == message


@given(
    operation=st.integers(min_value=0, max_value=65535),
    message=st.text(max_size=1000)
)
@settings(max_examples=100)
def test_response_roundtrip(operation, message):
    """Проверяет упаковку и распаковку ответа."""
    packet = create_response_packet(operation, message)

    code, result = read_response_packet(packet)

    assert code == operation
    assert result == message


@given(message=st.text(max_size=500))
def test_request_body_size(message):
    """Проверяет размер тела запроса."""
    packet = create_packet(1, message)
    body = message.encode("utf-8")

    size = struct.unpack("<I", packet[2:6])[0]

    assert size == len(body)
    assert len(packet) == REQUEST_HEADER_SIZE + len(body)


@given(message=st.text(max_size=500))
def test_response_body_size(message):
    """Проверяет размер тела ответа."""
    packet = create_response_packet(1, message)
    body = message.encode("utf-8")

    size = int.from_bytes(packet[2:7], "little")

    assert size == len(body)
    assert len(packet) == RESPONSE_HEADER_SIZE + len(body)


@given(size=st.integers(min_value=0, max_value=5))
def test_short_request_header(size):
    """Проверяет слишком короткий заголовок запроса."""
    packet = bytes(size)

    with pytest.raises(ValueError, match="Invalid request header"):
        read_packet(packet)


@given(size=st.integers(min_value=0, max_value=6))
def test_short_response_header(size):
    """Проверяет слишком короткий заголовок ответа."""
    packet = bytes(size)

    with pytest.raises(ValueError, match="Invalid response header"):
        read_response_packet(packet)


@given(extra=st.integers(min_value=1, max_value=100))
def test_invalid_request_size(extra):
    """Проверяет несоответствие размера запроса."""
    packet = create_packet(1, "<request/>")
    body = packet[REQUEST_HEADER_SIZE:]

    header = struct.pack(
        "<BBI",
        VERSION,
        1,
        len(body) + extra
    )

    with pytest.raises(ValueError, match="Invalid request body size"):
        read_packet(header + body)


@given(extra=st.integers(min_value=1, max_value=100))
def test_invalid_response_size(extra):
    """Проверяет несоответствие размера ответа."""
    packet = create_response_packet(1, "<response/>")
    body = packet[RESPONSE_HEADER_SIZE:]

    header = (
        (1).to_bytes(2, "little")
        + (len(body) + extra).to_bytes(5, "little")
    )

    with pytest.raises(ValueError, match="Invalid response body size"):
        read_response_packet(header + body)


@given(
    operation=st.integers(min_value=0, max_value=255)
)
def test_empty_request(operation):
    """Проверяет запрос с пустым телом."""
    packet = create_packet(operation, "")

    version, code, message = read_packet(packet)

    assert version == VERSION
    assert code == operation
    assert message == ""


@given(
    operation=st.integers(min_value=0, max_value=65535)
)
def test_empty_response(operation):
    """Проверяет ответ с пустым телом."""
    packet = create_response_packet(operation, "")

    code, message = read_response_packet(packet)

    assert code == operation
    assert message == ""


@given(
    invalid_byte=st.integers(min_value=128, max_value=191)
)
def test_invalid_request_encoding(invalid_byte):
    """Проверяет обработку повреждённого UTF-8."""
    header = struct.pack("<BBI", VERSION, 1, 1)
    packet = header + bytes([invalid_byte])

    with pytest.raises(UnicodeDecodeError):
        read_packet(packet)


@given(
    invalid_byte=st.integers(min_value=128, max_value=191)
)
def test_invalid_response_encoding(invalid_byte):
    """Проверяет повреждённый UTF-8 в ответе."""
    header = (
        (1).to_bytes(2, "little")
        + (1).to_bytes(5, "little")
    )
    packet = header + bytes([invalid_byte])

    with pytest.raises(UnicodeDecodeError):
        read_response_packet(packet)
