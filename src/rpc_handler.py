
"""Обработка RPC-запросов в формате XML."""

import time
import xml.etree.ElementTree as xml_tree

from . import database
from .models import Feedback, Prompt, Session


JOIN_FIELDS = ("error", "parameter", "locale")


def create_response(status, message, data=None):
    """Формирует XML-ответ RPC-сервера."""
    root = xml_tree.Element("response")
    xml_tree.SubElement(root, "status").text = status
    xml_tree.SubElement(root, "message").text = message

    if data is not None:
        data_element = xml_tree.SubElement(root, "data")
        append_data(data_element, data)

    return xml_tree.tostring(root, encoding="unicode")


def append_data(parent, data):
    """Добавляет результаты операции в XML."""
    records = data if isinstance(data, list) else [data]

    for record in records:
        item = xml_tree.SubElement(parent, "item")

        if hasattr(record, "_asdict"):
            append_fields(item, record._asdict())
        elif isinstance(record, tuple):
            fields = dict(zip(JOIN_FIELDS, record))
            append_fields(item, fields)
        else:
            item.text = str(record)


def append_fields(parent, fields):
    """Добавляет именованные поля записи в XML."""
    for name, value in fields.items():
        element = xml_tree.SubElement(parent, name)
        element.text = "" if value is None else str(value)


def get_value(root, name):
    """Возвращает обязательный XML-параметр."""
    element = root.find(name)

    if element is None:
        raise ValueError(f"Missing parameter: {name}")

    return (element.text or "").strip()


def get_int(root, name):
    """Возвращает целочисленный XML-параметр."""
    return int(get_value(root, name))


def create_session(root):
    """Создаёт пользовательскую сессию."""
    session = Session(
        get_int(root, "uid"),
        int(time.time()),
        get_value(root, "locale")
    )

    return database.create_session(session)


def get_sessions(root):
    """Возвращает все пользовательские сессии."""
    return database.get_sessions()


def delete_session(root):
    """Удаляет пользовательскую сессию."""
    database.delete_session(get_int(root, "uid"))
    return "Session deleted"


def update_session(root):
    """Изменяет локаль пользовательской сессии."""
    return database.update_session(
        get_int(root, "uid"),
        get_value(root, "locale")
    )


def create_prompt(root):
    """Создаёт пользовательский запрос."""
    prompt = Prompt(
        get_int(root, "uid"),
        int(time.time()),
        get_value(root, "parameter"),
        get_int(root, "session")
    )

    return database.create_prompt(prompt)


def get_prompts(root):
    """Возвращает все пользовательские запросы."""
    return database.get_prompts()


def delete_prompt(root):
    """Удаляет пользовательский запрос."""
    database.delete_prompt(get_int(root, "uid"))
    return "Prompt deleted"


def update_prompt(root):
    """Изменяет параметр пользовательского запроса."""
    return database.update_prompt(
        get_int(root, "uid"),
        get_value(root, "parameter")
    )


def create_feedback(root):
    """Создаёт запись обратной связи."""
    feedback = Feedback(
        get_int(root, "uid"),
        int(time.time()),
        get_value(root, "response"),
        get_value(root, "status"),
        get_value(root, "error"),
        get_int(root, "prompt"),
        get_int(root, "cache_hit"),
        get_int(root, "duration")
    )

    return database.create_feedback(feedback)


def get_feedbacks(root):
    """Возвращает все записи обратной связи."""
    return database.get_feedbacks()


def delete_feedback(root):
    """Удаляет запись обратной связи."""
    database.delete_feedback(get_int(root, "uid"))
    return "Feedback deleted"


def update_feedback(root):
    """Изменяет статус записи обратной связи."""
    return database.update_feedback(
        get_int(root, "uid"),
        get_value(root, "status")
    )


def get_recent_feedbacks(root):
    """Выполняет JOIN-выборку за последние 9 минут."""
    return database.get_recent_feedbacks()


RPC_METHODS = {
    "create_session": create_session,
    "get_sessions": get_sessions,
    "delete_session": delete_session,
    "update_session": update_session,
    "create_prompt": create_prompt,
    "get_prompts": get_prompts,
    "delete_prompt": delete_prompt,
    "update_prompt": update_prompt,
    "create_feedback": create_feedback,
    "get_feedbacks": get_feedbacks,
    "delete_feedback": delete_feedback,
    "update_feedback": update_feedback,
    "get_recent_feedbacks": get_recent_feedbacks,
}


def handle_request(xml):
    """Определяет и выполняет запрошенную RPC-операцию."""
    try:
        root = xml_tree.fromstring(xml)
    except xml_tree.ParseError:
        return create_response("error", "Invalid XML")

    try:
        method = get_value(root, "method")
        handler = RPC_METHODS.get(method)

        if handler is None:
            return create_response("error", "Unknown method")

        result = handler(root)

        if result is None:
            return create_response("error", "Record not found")

        return create_response("success", "Operation completed", result)

    except (ValueError, TypeError, OverflowError) as error:
        return create_response("error", str(error))
