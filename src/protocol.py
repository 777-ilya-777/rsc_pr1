
"""Формирование и чтение TCP-пакетов RPC."""

import struct


VERSION = 1
REQUEST_HEADER_SIZE = 6
RESPONSE_HEADER_SIZE = 7

OPERATION_CODES = {
    "create_session": 1,
    "get_sessions": 2,
    "delete_session": 3,
    "update_session": 4,
    "create_prompt": 5,
    "get_prompts": 6,
    "delete_prompt": 7,
    "update_prompt": 8,
    "create_feedback": 9,
    "get_feedbacks": 10,
    "delete_feedback": 11,
    "update_feedback": 12,
    "get_recent_feedbacks": 13,
}


def create_packet(operation_code, xml_data):
    """Формирует пакет запроса RPC."""
    body = xml_data.encode("utf-8")
    size = len(body)

    header = struct.pack(
        "<BBI",
        VERSION,
        operation_code,
        size
    )

    return header + body


def read_packet(data):
    """Разбирает пакет запроса RPC."""
    if len(data) < REQUEST_HEADER_SIZE:
        raise ValueError("Invalid request header")

    version, operation_code, size = struct.unpack(
        "<BBI",
        data[:REQUEST_HEADER_SIZE]
    )

    body = data[REQUEST_HEADER_SIZE:]

    if len(body) != size:
        raise ValueError("Invalid request body size")

    return version, operation_code, body.decode("utf-8")


def create_response_packet(operation_code, xml_data):
    """Формирует пакет ответа RPC."""
    body = xml_data.encode("utf-8")

    operation = operation_code.to_bytes(2, "little")
    size = len(body).to_bytes(5, "little")

    return operation + size + body


def read_response_packet(data):
    """Разбирает пакет ответа RPC."""
    if len(data) < RESPONSE_HEADER_SIZE:
        raise ValueError("Invalid response header")

    operation_code = int.from_bytes(data[:2], "little")
    size = int.from_bytes(data[2:7], "little")
    body = data[RESPONSE_HEADER_SIZE:]

    if len(body) != size:
        raise ValueError("Invalid response body size")

    return operation_code, body.decode("utf-8")
