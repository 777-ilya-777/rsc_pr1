
from .models import Session, Prompt, Feedback
from . import database


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
    print("0. Выход")


def create_session():
    """Создаёт новую сессию."""
    uid = int(input("UID: "))
    locale = input("Locale: ")

    session = Session(uid, 123456, locale)
    database.create_session(session)

    print("Session создан")


def show_sessions():
    """Выводит все сессии."""
    for session in database.get_sessions():
        print(session.uid, session.datetime, session.locale)


def delete_session():
    """Удаляет сессию по идентификатору."""
    uid = int(input("UID для удаления: "))
    database.delete_session(uid)

    print("Удалено")


def create_prompt():
    """Создаёт новый запрос."""
    uid = int(input("UID: "))
    parameter = input("Parameter: ")

    prompt = Prompt(uid, 123456, parameter, uid)
    database.create_prompt(prompt)

    print("Prompt создан")


def show_prompts():
    """Выводит все запросы."""
    for prompt in database.get_prompts():
        print(prompt.uid, prompt.parameter)


def create_feedback():
    """Создаёт новую запись обратной связи."""
    uid = int(input("UID: "))
    response = input("Response: ")

    feedback = Feedback(
        uid, 123456, response, "success",
        "", uid, 0, 100
    )
    database.create_feedback(feedback)

    print("Feedback создан")


def show_feedbacks():
    """Выводит все записи обратной связи."""
    for feedback in database.get_feedbacks():
        print(feedback.uid, feedback.response, feedback.status)


def show_recent_feedbacks():
    """Выводит результат соединения таблиц."""
    data = database.get_recent_feedbacks()

    for item in data:
        print(item)


def menu():
    """Запускает интерактивное меню приложения."""
    actions = {
        "1": create_session,
        "2": show_sessions,
        "3": delete_session,
        "4": create_prompt,
        "5": show_prompts,
        "6": create_feedback,
        "7": show_feedbacks,
        "8": show_recent_feedbacks,
    }

    while True:
        show_menu()
        choice = input("\nВыберите действие: ")

        if choice == "0":
            print("Выход")
            break

        action = actions.get(choice)

        if action is None:
            print("Неизвестная команда")
        else:
            action()


if __name__ == "__main__":
    menu()
