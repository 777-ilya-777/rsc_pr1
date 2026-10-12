
"""Хранение и обработка данных приложения в оперативной памяти."""

sessions = []
prompts = []
feedbacks = []


def create_session(session):
    """Создаёт новую сессию."""
    sessions.append(session)
    return session


def get_sessions():
    """Возвращает все сессии."""
    return sessions


def delete_session(uid):
    """Удаляет сессию по идентификатору."""
    global sessions
    sessions = [
        session for session in sessions
        if session.uid != uid
    ]


def update_session(uid, locale):
    """Изменяет локаль существующей сессии."""
    for session in sessions:
        if session.uid == uid:
            session.locale = locale
            return session

    return None


def create_prompt(prompt):
    """Создаёт новый запрос."""
    prompts.append(prompt)
    return prompt


def get_prompts():
    """Возвращает все запросы."""
    return prompts


def delete_prompt(uid):
    """Удаляет запрос по идентификатору."""
    global prompts
    prompts = [
        prompt for prompt in prompts
        if prompt.uid != uid
    ]


def update_prompt(uid, parameter):
    """Изменяет параметр существующего запроса."""
    for prompt in prompts:
        if prompt.uid == uid:
            prompt.parameter = parameter
            return prompt

    return None


def create_feedback(feedback):
    """Создаёт новую запись обратной связи."""
    feedbacks.append(feedback)
    return feedback


def get_feedbacks():
    """Возвращает все записи обратной связи."""
    return feedbacks


def delete_feedback(uid):
    """Удаляет запись обратной связи по идентификатору."""
    global feedbacks
    feedbacks = [
        feedback for feedback in feedbacks
        if feedback.uid != uid
    ]


def update_feedback(uid, status):
    """Изменяет статус существующей записи."""
    for feedback in feedbacks:
        if feedback.uid == uid:
            feedback.status = status
            return feedback

    return None


def get_recent_feedbacks():
    """Соединяет записи Session, Prompt и Feedback."""
    result = []

    for session in sessions:
        for prompt in prompts:
            if prompt.session == session.uid:
                for feedback in feedbacks:
                    if feedback.prompt == prompt.uid:
                        result.append((
                            feedback.error,
                            prompt.parameter,
                            session.locale
                        ))

    return result
