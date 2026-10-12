
from dataclasses import dataclass


class Session:
    """Модель пользовательской сессии."""

    def __init__(self, uid, datetime, locale):
        self.uid = uid
        self.datetime = datetime
        self.locale = locale


class Prompt:
    """Модель пользовательского запроса."""

    def __init__(self, uid, datetime, parameter, session):
        self.uid = uid
        self.datetime = datetime
        self.parameter = parameter
        self.session = session


@dataclass
class Feedback:
    """Модель результата обработки запроса."""

    uid: int
    datetime: int
    response: str
    status: str
    error: str
    prompt: int
    cache_hit: int
    duration: int
