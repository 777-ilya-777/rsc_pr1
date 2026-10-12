
# Практическая работа №1. Вариант №1

**Дисциплина:** Прикладная разработка серверных частей веб-приложений на языке Python

**Тема:** Разработка прототипа приложения с поддержкой удалённого вызова процедур (RPC) на основе TCP.

## 1. Описание проекта

Проект реализует клиент-серверное приложение на Python.

Обмен между клиентом и сервером осуществляется через TCP.
Данные передаются в формате XML и хранятся только в оперативной
памяти без использования внешней базы данных.

Реализованы три сущности:

- Session — пользовательская сессия.
- Prompt — пользовательский запрос.
- Feedback — результат обработки запроса.

Приложение поддерживает 13 операций с данными, интерактивное
консольное меню, RPC-клиент, RPC-сервер и автоматизированные тесты.

## 2. Используемые технологии

- Python 3.13
- TCP sockets
- XML (ElementTree)
- struct
- NamedTuple
- pytest
- Hypothesis
- coverage.py
- pycodestyle
- radon

## 3. Структура проекта

    rsc_pr1/
    ├── src/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── models.py
    │   ├── database.py
    │   ├── protocol.py
    │   ├── rpc_client.py
    │   ├── rpc_handler.py
    │   └── rpc_server.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_rpc.py
    │   ├── test_integration.py
    │   ├── test_model.py
    │   └── test_protocol_hypothesis.py
    ├── .gitignore
    ├── .coveragerc
    ├── run.bat
    └── README.md

### Назначение файлов

- models.py — модели данных.
- database.py — хранение и обработка записей.
- main.py — интерактивное консольное меню.
- protocol.py — упаковка и распаковка TCP-пакетов.
- rpc_client.py — клиент удалённого вызова процедур.
- rpc_handler.py — обработка XML-команд.
- rpc_server.py — TCP-сервер.
- test_rpc.py — модульные тесты.
- test_integration.py — интеграционные тесты.
- test_model.py — модельное тестирование RPC.
- test_protocol_hypothesis.py — проверки TCP-протокола.

## 4. Этап 1. Модель доступа к данным

### Модели

Записи представлены с помощью NamedTuple.

Session:
- uid — идентификатор.
- datetime — время создания.
- locale — локаль.

Prompt:
- uid — идентификатор.
- datetime — время создания.
- parameter — параметр запроса.
- session — идентификатор сессии.

Feedback:
- uid — идентификатор.
- datetime — время создания.
- response — ответ.
- status — статус.
- error — ошибка.
- prompt — идентификатор запроса.
- cache_hit — показатель использования кэша.
- duration — продолжительность обработки.

### Операции

Session:
1. create_session
2. get_sessions
3. delete_session
4. update_session

Prompt:
5. create_prompt
6. get_prompts
7. delete_prompt
8. update_prompt

Feedback:
9. create_feedback
10. get_feedbacks
11. delete_feedback
12. update_feedback

Соединение данных:
13. get_recent_feedbacks

### JOIN-выборка

Функция get_recent_feedbacks() объединяет записи Session,
Prompt и Feedback.

Выборка использует связи:

- Session.uid = Prompt.session
- Prompt.uid = Feedback.prompt

Учитываются запросы Prompt за последние 9 минут.

Результат содержит:
- Feedback.error
- Prompt.parameter
- Session.locale

Время создания записей хранится в виде Unix timestamp.

### Интерактивный режим

Для запуска консольного меню:

```powershell
python -m src.main
```

В меню представлены операции создания, просмотра,
изменения и удаления записей, а также JOIN-выборка.

Для выхода используется команда 0.

## 5. Этап 2. RPC через TCP

### Архитектура

    RPCClient
        |
        | TCP + XML
        v
    RPCServer
        |
        v
    RPCHandler
        |
        v
    Database
        |
        v
    Session / Prompt / Feedback

Клиент формирует XML-запрос и отправляет его серверу.
Сервер определяет операцию, выполняет необходимую
функцию и возвращает результат в формате XML.

### Формат TCP-запроса

| Поле | Размер |
|---|---|
| Версия протокола | 1 байт |
| Код операции | 1 байт |
| Размер XML | 4 байта |
| Тело XML | Переменная длина |

Заголовок запроса занимает 6 байт.

### Формат TCP-ответа

| Поле | Размер |
|---|---|
| Код операции | 2 байта |
| Размер XML | 5 байт |
| Тело XML | Переменная длина |

Заголовок ответа занимает 7 байт.

Порядок байтов: Little Endian.

### Коды операций

| Код | Метод |
|---|---|
| 1 | create_session |
| 2 | get_sessions |
| 3 | delete_session |
| 4 | update_session |
| 5 | create_prompt |
| 6 | get_prompts |
| 7 | delete_prompt |
| 8 | update_prompt |
| 9 | create_feedback |
| 10 | get_feedbacks |
| 11 | delete_feedback |
| 12 | update_feedback |
| 13 | get_recent_feedbacks |

### Пример XML-запроса

```xml
<request>
    <method>create_session</method>
    <uid>1</uid>
    <locale>ru</locale>
</request>
```

### Пример XML-ответа

```xml
<response>
    <status>success</status>
    <message>Operation completed</message>
    <data>
        <item>
            <uid>1</uid>
            <datetime>1791831114</datetime>
            <locale>ru</locale>
        </item>
    </data>
</response>
```

Значение datetime приведено только для примера.

### Обработка ошибок

Реализована обработка следующих ситуаций:

- Некорректный XML.
- Отсутствующие параметры.
- Неверные числовые значения.
- Неизвестный RPC-метод.
- Несовпадение кода операции.
- Отсутствие записи при обновлении.
- Ошибки при передаче TCP-пакетов.

Запросы и ответы журналируются в стандартный вывод сервера.

## 6. Установка проекта

Все команды ниже выполняются из корневой папки проекта.

### Создание виртуального окружения

```powershell
python -m venv venv
```

### Активация на Windows

```powershell
.\venv\Scripts\Activate.ps1
```

### Установка зависимостей

```powershell
python -m pip install pytest hypothesis coverage pycodestyle radon
```

### Проверка версии Python

```powershell
python --version
```

### Проверка установленных библиотек

```powershell
python -m pip list
```

## 7. Запуск приложения

### Запуск консольного меню

```powershell
python -m src.main
```

### Запуск через скрипт Windows

```powershell
.\run.bat
```

### Запуск RPC-сервера

В первом терминале:

```powershell
python -m src.rpc_server
```

Ожидаемое сообщение:

    RPC server started

### Запуск RPC-клиента

Во втором терминале:

```powershell
python -m src.rpc_client
```

Клиент создаёт Session и получает список Session.

Сервер работает по адресу:

    127.0.0.1:5000

Для остановки сервера:

    Ctrl + C

### Ручная проверка RPC-клиента

Вызов создания Session:

```powershell
python -c "from src.rpc_client import RPCClient; print(RPCClient().create_session(10, 'ru').findtext('status'))"
```

Получение списка Session:

```powershell
python -c "from src.rpc_client import RPCClient; print(RPCClient().get_sessions().findtext('status'))"
```

Перед выполнением этих команд сервер должен быть запущен.

## 8. Этап 3. Автоматизированное тестирование

### Запуск всех тестов

```powershell
python -m pytest
```

### Краткий вывод

```powershell
python -m pytest -q
```

### Подробный вывод

```powershell
python -m pytest -v
```

### Только модульные тесты

```powershell
python -m pytest tests/test_rpc.py -v
```

### Только интеграционные тесты

```powershell
python -m pytest tests/test_integration.py -v
```

### Только модельное тестирование

```powershell
python -m pytest tests/test_model.py -v
```

### Тестирование TCP-протокола с Hypothesis

```powershell
python -m pytest tests/test_protocol_hypothesis.py -v
```

## 9. Model-Based Testing

Модельное тестирование реализовано с помощью
RuleBasedStateMachine из библиотеки Hypothesis.

Тестовая модель хранит ожидаемые состояния Session,
Prompt и Feedback.

Hypothesis генерирует последовательности действий,
которые выполняются через RPC-клиент.

После выполнения действий состояние сервера
сравнивается с состоянием модели.

Проверяются:
- Создание записей.
- Получение записей.
- Изменение записей.
- Удаление записей.
- JOIN-выборка.
- Отсутствующие записи.
- Некорректные идентификаторы.
- Неизвестные методы.
- Повреждённый XML.
- Несовпадение кодов операций.

## 10. Измерение покрытия кода

Для покрытия используется coverage.py.

Измеряются операторы и ветви программы.

### Очистка старых результатов

```powershell
python -m coverage erase
```

### Покрытие только модельных тестов RPC

```powershell
python -m coverage run -m pytest tests/test_model.py -q
```

### Покрытие модельных и property-based тестов

```powershell
python -m coverage run -m pytest tests/test_model.py tests/test_protocol_hypothesis.py -q
```

### Объединение результатов процессов

```powershell
python -m coverage combine
```

### Вывод отчёта

```powershell
python -m coverage report -m
```

### HTML-отчёт

```powershell
python -m coverage html
```

Открытие HTML-отчёта на Windows:

```powershell
start .\htmlcov\index.html
```

### Пример полученного результата

При последней проверке модельных и property-based тестов
получено общее покрытие 93%.

Результат может изменяться при изменении кода
и генерации новых тестовых последовательностей.

## 11. Проверка оформления PEP 8

### Проверка всего исходного кода и тестов

```powershell
python -m pycodestyle src tests --max-line-length=79
```

Если нарушений нет, команда не выводит сообщения.

### Проверка только исходного кода

```powershell
python -m pycodestyle src --max-line-length=79
```

### Проверка только тестов

```powershell
python -m pycodestyle tests --max-line-length=79
```

## 12. Проверка цикломатической сложности

Для анализа используется radon.

### Проверка сложности всех функций

```powershell
python -m radon cc src tests -s
```

### Только исходный код

```powershell
python -m radon cc src -s
```

### Вывод функций с оценкой B и выше

```powershell
python -m radon cc src tests -s -n B
```

Шкала оценок radon:

- A — сложность 1–5.
- B — сложность 6–10.
- C — сложность 11–20.
- D — сложность 21–30.
- E — сложность 31–40.
- F — сложность 41 и выше.

## 13. Работа с Git

### Посмотреть состояние репозитория

```powershell
git status
```

### Посмотреть историю коммитов

```powershell
git log --oneline
```

### Посмотреть изменения

```powershell
git diff
```

### Добавить изменения

```powershell
git add .
```

### Создать коммит

```powershell
git commit -m "test: add model-based RPC tests"
```

### Отправить изменения на GitHub

```powershell
git push origin main
```

### Проверить связь с GitHub

```powershell
git remote -v
```

Используется формат сообщений Conventional Commits.


## 14. Итог

В практической работе реализованы:

- Модель доступа к данным в оперативной памяти.
- Представление записей с помощью NamedTuple.
- Операции CRUD над тремя сущностями.
- JOIN-выборка с фильтрацией по времени.
- Интерактивное консольное управление.
- RPC на основе TCP.
- XML-запросы и XML-ответы.
- Отдельные коды для 13 RPC-операций.
- Класс RPCClient.
- Журналирование запросов и ответов.
- Интеграционные тесты.
- Модельное тестирование Hypothesis.
- Проверки TCP-протокола.
- Измерение покрытия операторов и ветвей.
