
"""Формирование и чтение TCP-пакетов."""

import struct


VERSION = 1


def create_packet(operation_code, xml_data):
    """Создаёт TCP-пакет с XML-данными."""
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
    """Извлекает данные из TCP-пакета."""
    version, operation_code, size = struct.unpack(
        "<BBI",
        data[:6]
    )

    body = data[6:6 + size]
    xml_data = body.decode("utf-8")

    return (
        version,
        operation_code,
        xml_data
    )
