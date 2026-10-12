
"""Модели записей приложения."""

from typing import NamedTuple


class Session(NamedTuple):
    """Данные пользовательской сессии."""

    uid: int
    datetime: int
    locale: str


class Prompt(NamedTuple):
    """Данные пользовательского запроса."""

    uid: int
    datetime: int
    parameter: str
    session: int


class Feedback(NamedTuple):
    """Данные результата обработки запроса."""

    uid: int
    datetime: int
    response: str
    status: str
    error: str
    prompt: int
    cache_hit: int
    duration: int
