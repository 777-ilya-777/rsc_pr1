
"""Тесты RPC-обработчика и TCP-протокола."""

import xml.etree.ElementTree as xml_tree

from src.protocol import create_packet, read_packet
from src.rpc_handler import handle_request


def parse_response(xml):
    """Разбирает XML-ответ RPC-сервера."""
    return xml_tree.fromstring(xml)


def test_create_session():
    """Проверяет создание сессии через RPC."""
    xml = """
    <request>
        <method>create_session</method>
        <uid>1</uid>
        <locale>ru</locale>
    </request>
    """

    response = parse_response(handle_request(xml))

    assert response.findtext("status") == "success"
    assert response.findtext("message") == "Operation completed"
    assert response.findtext("data/item/uid") == "1"
    assert response.findtext("data/item/locale") == "ru"


def test_invalid_xml():
    """Проверяет обработку некорректного XML."""
    xml = """
    <request>
        <method>create_session</method>
    </request_broken>
    """

    response = parse_response(handle_request(xml))

    assert response.findtext("status") == "error"
    assert response.findtext("message") == "Invalid XML"


def test_invalid_parameters():
    """Проверяет обработку отсутствующих параметров."""
    xml = """
    <request>
        <method>create_session</method>
    </request>
    """

    response = parse_response(handle_request(xml))

    assert response.findtext("status") == "error"
    assert response.findtext("message") == "Missing parameter: uid"


def test_unknown_method():
    """Проверяет обработку неизвестного RPC-метода."""
    xml = """
    <request>
        <method>unknown_method</method>
    </request>
    """

    response = parse_response(handle_request(xml))

    assert response.findtext("status") == "error"
    assert response.findtext("message") == "Unknown method"


def test_packet_protocol():
    """Проверяет упаковку и распаковку TCP-запроса."""
    xml = "<test>Hello</test>"

    packet = create_packet(1, xml)
    version, operation, result = read_packet(packet)

    assert version == 1
    assert operation == 1
    assert result == xml
