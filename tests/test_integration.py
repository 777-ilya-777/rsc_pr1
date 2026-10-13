
"""Интеграционные тесты всех RPC-методов через TCP."""

import socket
import subprocess
import sys
import time

import pytest

from src.rpc_client import RPCClient


HOST = "127.0.0.1"
START_TIMEOUT = 5
EXPECTED_SESSION_COUNT = 3


def get_free_port():
    """Находит свободный TCP-порт."""
    with socket.socket() as connection:
        connection.bind((HOST, 0))
        return connection.getsockname()[1]


def wait_for_server(process, port):
    """Ожидает запуска RPC-сервера."""
    deadline = time.monotonic() + START_TIMEOUT

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("RPC server stopped")

        try:
            with socket.create_connection((HOST, port), 0.1):
                return
        except OSError:
            time.sleep(0.05)

    raise TimeoutError("RPC server did not start")


@pytest.fixture
def rpc_client():
    """Запускает сервер и предоставляет RPC-клиент."""
    port = get_free_port()
    command = (
        "import src.rpc_server as server\n"
        f"server.PORT = {port}\n"
        "server.main()"
    )

    process = subprocess.Popen(
        [sys.executable, "-c", command],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        wait_for_server(process, port)
        yield RPCClient(host=HOST, port=port)
    finally:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def get_items(response):
    """Извлекает записи из XML-ответа."""
    return response.findall("data/item")


def test_session_operations(rpc_client):
    """Проверяет четыре операции с Session."""
    created = rpc_client.create_session(1, "ru")
    assert created.findtext("status") == "success"

    records = get_items(rpc_client.get_sessions())
    assert len(records) == 1
    assert records[0].findtext("locale") == "ru"

    updated = rpc_client.update_session(1, "en")
    assert updated.findtext("data/item/locale") == "en"

    deleted = rpc_client.delete_session(1)
    assert deleted.findtext("status") == "success"
    assert get_items(rpc_client.get_sessions()) == []


def test_prompt_operations(rpc_client):
    """Проверяет четыре операции с Prompt."""
    rpc_client.create_session(1, "ru")

    created = rpc_client.create_prompt(2, "hello", 1)
    assert created.findtext("status") == "success"

    records = get_items(rpc_client.get_prompts())
    assert len(records) == 1
    assert records[0].findtext("parameter") == "hello"

    updated = rpc_client.update_prompt(2, "updated")
    assert updated.findtext("data/item/parameter") == "updated"

    rpc_client.delete_prompt(2)
    assert get_items(rpc_client.get_prompts()) == []


def test_feedback_operations(rpc_client):
    """Проверяет четыре операции с Feedback."""
    rpc_client.create_session(1, "ru")
    rpc_client.create_prompt(2, "hello", 1)

    created = rpc_client.create_feedback(
        3, "answer", "success", "", 2, 0, 100
    )
    assert created.findtext("status") == "success"

    records = get_items(rpc_client.get_feedbacks())
    assert len(records) == 1
    assert records[0].findtext("response") == "answer"

    updated = rpc_client.update_feedback(3, "failed")
    assert updated.findtext("data/item/status") == "failed"

    rpc_client.delete_feedback(3)
    assert get_items(rpc_client.get_feedbacks()) == []


def test_join_operation(rpc_client):
    """Проверяет JOIN-выборку через TCP."""
    rpc_client.create_session(1, "ru")
    rpc_client.create_prompt(2, "test", 1)

    rpc_client.create_feedback(
        3, "answer", "success", "none", 2, 0, 100
    )

    response = rpc_client.get_recent_feedbacks()

    assert response.findtext("status") == "success"

    records = get_items(response)
    assert len(records) == 1
    assert records[0].findtext("error") == "none"
    assert records[0].findtext("parameter") == "test"
    assert records[0].findtext("locale") == "ru"


def test_empty_join(rpc_client):
    """Проверяет JOIN при отсутствии записей."""
    response = rpc_client.get_recent_feedbacks()

    assert response.findtext("status") == "success"
    assert get_items(response) == []


def test_missing_record(rpc_client):
    """Проверяет ошибку изменения отсутствующей записи."""
    with pytest.raises(ValueError, match="Record not found"):
        rpc_client.update_session(999, "ru")


def test_invalid_parameter(rpc_client):
    """Проверяет ошибку неправильного идентификатора."""
    with pytest.raises(ValueError):
        rpc_client.create_session("invalid", "ru")


def test_multiple_records(rpc_client):
    """Проверяет получение нескольких записей."""
    rpc_client.create_session(1, "ru")
    rpc_client.create_session(2, "en")
    rpc_client.create_session(3, "fr")

    records = get_items(rpc_client.get_sessions())

    assert len(records) == EXPECTED_SESSION_COUNT
    assert [item.findtext("uid") for item in records] == [
        "1", "2", "3"
    ]
