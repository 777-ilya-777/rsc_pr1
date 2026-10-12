
"""Тесты RPC-обработчика и TCP-протокола."""

from src.protocol import create_packet, read_packet
from src.rpc_handler import handle_request


def test_create_session():
    """Проверяет создание сессии через RPC."""
    xml = """
    <request>
        <method>create_session</method>
        <uid>1</uid>
        <locale>ru</locale>
    </request>
    """

    response = handle_request(xml)

    assert "success" in response
    assert "Session created" in response


def test_invalid_xml():
    """Проверяет обработку некорректного XML."""
    xml = """
    <request>
        <method>create_session</method>
    </request_broken>
    """

    response = handle_request(xml)

    assert "Invalid XML" in response


def test_invalid_parameters():
    """Проверяет обработку отсутствующих параметров."""
    xml = """
    <request>
        <method>create_session</method>
    </request>
    """

    response = handle_request(xml)

    assert "Invalid parameters" in response


def test_packet_protocol():
    """Проверяет упаковку и распаковку TCP-пакета."""
    xml = "<test>Hello</test>"

    packet = create_packet(1, xml)
    version, operation, result = read_packet(packet)

    assert version == 1
    assert operation == 1
    assert result == xml
