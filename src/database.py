
"""Хранение и обработка данных приложения в оперативной памяти."""

import time


sessions = []
prompts = []
feedbacks = []

RECENT_INTERVAL_SECONDS = 9 * 60


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
    for index, session in enumerate(sessions):
        if session.uid == uid:
            updated = session._replace(locale=locale)
            sessions[index] = updated
            return updated

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
    for index, prompt in enumerate(prompts):
        if prompt.uid == uid:
            updated = prompt._replace(parameter=parameter)
            prompts[index] = updated
            return updated

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
    for index, feedback in enumerate(feedbacks):
        if feedback.uid == uid:
            updated = feedback._replace(status=status)
            feedbacks[index] = updated
            return updated

    return None


def get_feedbacks_for_prompt(prompt):
    """Возвращает записи Feedback для указанного Prompt."""
    return [
        feedback
        for feedback in feedbacks
        if feedback.prompt == prompt.uid
    ]


def get_recent_feedbacks():
    """Возвращает результаты запросов за последние 9 минут."""
    time_limit = time.time() - RECENT_INTERVAL_SECONDS

    session_by_uid = {
        session.uid: session
        for session in sessions
    }

    result = []

    for prompt in prompts:
        if prompt.datetime < time_limit:
            continue

        session = session_by_uid.get(prompt.session)
        locale = session.locale if session else None

        for feedback in get_feedbacks_for_prompt(prompt):
            result.append((
                feedback.error,
                prompt.parameter,
                locale
            ))

    return result
