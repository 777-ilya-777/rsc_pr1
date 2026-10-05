from models import Session, Prompt, Feedback
import database


def menu():

    while True:

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


        choice = input("\nВыберите действие: ")


        if choice == "1":

            uid = int(input("UID: "))
            locale = input("Locale: ")


            session = Session(
                uid,
                123456,
                locale
            )


            database.create_session(session)


            print("Session создан")


        elif choice == "2":

            sessions = database.get_sessions()


            for s in sessions:

                print(
                    s.uid,
                    s.datetime,
                    s.locale
                )


        elif choice == "3":

            uid = int(input("UID для удаления: "))

            database.delete_session(uid)

            print("Удалено")


        elif choice == "4":

            uid = int(input("UID: "))

            parameter = input("Parameter: ")


            prompt = Prompt(
                uid,
                123456,
                parameter,
                uid
            )


            database.create_prompt(prompt)


            print("Prompt создан")


        elif choice == "5":

            for p in database.get_prompts():

                print(
                    p.uid,
                    p.parameter
                )


        elif choice == "6":

            uid = int(input("UID: "))

            response = input("Response: ")


            feedback = Feedback(
                uid,
                123456,
                response,
                "success",
                "",
                uid,
                0,
                100
            )


            database.create_feedback(feedback)


            print("Feedback создан")


        elif choice == "7":

            for f in database.get_feedbacks():

                print(
                    f.uid,
                    f.response,
                    f.status
                )

        elif choice == "8":


            data = database.get_recent_feedbacks()


            for item in data:

                print(item)



        elif choice == "0":

            print("Выход")

            break


        else:

            print("Неизвестная команда")



if __name__ == "__main__":

    menu()