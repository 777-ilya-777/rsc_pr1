
"""Интерактивное меню управления данными приложения."""

import time

from . import database
from .models import Feedback, Prompt, Session


def show_menu():
    """Выводит список доступных команд."""
    print("\n===== DATA MODEL =====")
    print("1. Создать Session")
    print("2. Показать Session")
    print("3. Удалить Session")
    print("4. Создать Prompt")
    print("5. Показать Prompt")
    print("6. Создать Feedback")
    print("7. Показать Feedback")
    print("8. Выполнить JOIN выборку")
    print("9. Изменить Session")
    print("10. Удалить Prompt")
    print("11. Изменить Prompt")
    print("12. Удалить Feedback")
    print("13. Изменить Feedback")
    print("0. Выход")


def read_uid():
    """Запрашивает числовой идентификатор."""
    return int(input("UID: "))


def create_session():
    """Создаёт новую пользовательскую сессию."""
    uid = read_uid()
    locale = input("Locale: ")

    session = Session(uid, int(time.time()), locale)
    database.create_session(session)
    print("Session создан")


def show_sessions():
    """Отображает все пользовательские сессии."""
    for session in database.get_sessions():
        print(session)


def delete_session():
    """Удаляет сессию."""
    database.delete_session(read_uid())
    print("Операция удаления выполнена")


def update_session():
    """Изменяет локаль сессии."""
    uid = read_uid()
    locale = input("Новая локаль: ")
    result = database.update_session(uid, locale)
    print(result if result else "Session не найдена")


def create_prompt():
    """Создаёт новый пользовательский запрос."""
    uid = read_uid()
    parameter = input("Parameter: ")
    session_uid = int(input("Session UID: "))

    prompt = Prompt(
        uid, int(time.time()), parameter, session_uid
    )
    database.create_prompt(prompt)
    print("Prompt создан")


def show_prompts():
    """Отображает все пользовательские запросы."""
    for prompt in database.get_prompts():
        print(prompt)


def delete_prompt():
    """Удаляет пользовательский запрос."""
    database.delete_prompt(read_uid())
    print("Операция удаления выполнена")


def update_prompt():
    """Изменяет параметр пользовательского запроса."""
    uid = read_uid()
    parameter = input("Новый параметр: ")
    result = database.update_prompt(uid, parameter)
    print(result if result else "Prompt не найден")


def create_feedback():
    """Создаёт новую запись обратной связи."""
    uid = read_uid()
    prompt_uid = int(input("Prompt UID: "))
    response = input("Response: ")
    status = input("Status: ")
    error = input("Error: ")

    feedback = Feedback(
        uid, int(time.time()), response, status,
        error, prompt_uid, 0, 100
    )
    database.create_feedback(feedback)
    print("Feedback создан")


def show_feedbacks():
    """Отображает все записи обратной связи."""
    for feedback in database.get_feedbacks():
        print(feedback)


def delete_feedback():
    """Удаляет запись обратной связи."""
    database.delete_feedback(read_uid())
    print("Операция удаления выполнена")


def update_feedback():
    """Изменяет статус записи обратной связи."""
    uid = read_uid()
    status = input("Новый статус: ")
    result = database.update_feedback(uid, status)
    print(result if result else "Feedback не найден")


def show_recent_feedbacks():
    """Отображает JOIN-выборку за последние 9 минут."""
    records = database.get_recent_feedbacks()

    if not records:
        print("Подходящие записи отсутствуют")
        return

    for error, parameter, locale in records:
        print(
            f"Error: {error}, Parameter: {parameter}, "
            f"Locale: {locale}"
        )


def execute_command(actions, choice):
    """Выполняет выбранную команду."""
    action = actions.get(choice)

    if action is None:
        print("Неизвестная команда")
        return

    try:
        action()
    except ValueError:
        print("Ошибка: введено некорректное число")


def menu():
    """Запускает интерактивное меню."""
    actions = {
        "1": create_session,
        "2": show_sessions,
        "3": delete_session,
        "4": create_prompt,
        "5": show_prompts,
        "6": create_feedback,
        "7": show_feedbacks,
        "8": show_recent_feedbacks,
        "9": update_session,
        "10": delete_prompt,
        "11": update_prompt,
        "12": delete_feedback,
        "13": update_feedback,
    }

    while True:
        show_menu()
        choice = input("\nВыберите действие: ")

        if choice == "0":
            print("Выход")
            break

        execute_command(actions, choice)


if __name__ == "__main__":
    menu()
