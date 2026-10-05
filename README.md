# RPC TCP Application Variant 1


## Общее описание

Прототип веб-приложения с поддержкой удалённого вызова процедур
на основе TCP протокола.

Данные хранятся только в оперативной памяти.


## Используемые технологии

- Python 3.13
- TCP sockets
- XML
- Hypothesis
- Pytest


## Структура проекта


src/

- models.py - модели данных
- database.py - слой доступа к данным
- main.py - консольное управление


## Сущности


### Session

Поля:

- uid
- datetime
- locale


### Prompt

Поля:

- uid
- datetime
- parameter
- session


### Feedback

Поля:

- uid
- datetime
- response
- status
- error
- prompt
- cache_hit
- duration


## Запуск


Активировать окружение:

venv\Scripts\activate


Запуск программы:

python src/main.py


## Возможности


- создание Session
- создание Prompt
- создание Feedback
- просмотр данных
- удаление данных
- соединение таблиц