
import xml.etree.ElementTree as xml_tree

from . import database
from .models import Session


def create_response(status, message):
    """Формирует XML-ответ сервера."""
    response = xml_tree.Element("response")

    status_element = xml_tree.SubElement(response, "status")
    status_element.text = status

    message_element = xml_tree.SubElement(response, "message")
    message_element.text = message

    return xml_tree.tostring(response, encoding="unicode")


def create_session(root):
    """Обрабатывает запрос на создание сессии."""
    uid = int(root.find("uid").text.strip())
    locale = root.find("locale").text.strip()

    session = Session(uid, 123456, locale)
    database.create_session(session)

    print(database.get_sessions())

    return create_response("success", "Session created")


def handle_request(xml):
    """Принимает XML-запрос и вызывает нужный обработчик."""
    try:
        root = xml_tree.fromstring(xml)
    except xml_tree.ParseError:
        return create_response("error", "Invalid XML")

    try:
        method = root.find("method").text.strip()

        if method == "create_session":
            return create_session(root)

        return create_response("error", "Unknown method")

    except (AttributeError, TypeError, ValueError):
        return create_response("error", "Invalid parameters")
