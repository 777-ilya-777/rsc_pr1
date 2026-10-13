
"""Модельное тестирование RPC с помощью Hypothesis."""

import socket
import subprocess
import sys
import time
import xml.etree.ElementTree as xml_tree

import pytest
from hypothesis import settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule

from src.protocol import create_packet
from src.rpc_client import RPCClient


HOST = "127.0.0.1"
START_TIMEOUT = 5
SHUTDOWN_REQUEST = "<shutdown/>"


def get_free_port():
    """Выделяет свободный порт для тестового сервера."""
    with socket.socket() as connection:
        connection.bind((HOST, 0))
        return connection.getsockname()[1]


def start_server(port):
    """Запускает отдельный процесс RPC-сервера."""
    command = (
        "import src.rpc_server as server\n"
        f"server.PORT = {port}\n"
        "server.main()"
    )

    return subprocess.Popen(
        [sys.executable, "-c", command],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def wait_for_server(process, port):
    """Ожидает готовности RPC-сервера."""
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


def stop_server(process, port):
    """Корректно останавливает тестовый RPC-сервер."""
    try:
        if process.poll() is None:
            packet = create_packet(0, SHUTDOWN_REQUEST)

            with socket.create_connection((HOST, port), 2) as conn:
                conn.sendall(packet)

            process.wait(timeout=5)
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def read_records(response, fields):
    """Преобразует XML-записи в список словарей."""
    result = []

    for item in response.findall("data/item"):
        record = {
            field: item.findtext(field, "")
            for field in fields
        }
        result.append(record)

    return result


class RPCStateMachine(RuleBasedStateMachine):
    """Сравнивает модель данных с реальным RPC-сервером."""

    def __init__(self):
        super().__init__()

        self.port = get_free_port()
        self.process = start_server(self.port)
        self.client = RPCClient(host=HOST, port=self.port)
        self.next_uid = 1
        self.sessions = {}
        self.prompts = {}
        self.feedbacks = {}

        try:
            wait_for_server(self.process, self.port)
        except Exception:
            self.process.terminate()
            self.process.wait()
            raise

    def new_uid(self):
        """Генерирует уникальный идентификатор."""
        uid = self.next_uid
        self.next_uid += 1
        return uid

    def check_sessions(self):
        """Сравнивает сессии сервера с моделью."""
        response = self.client.get_sessions()
        records = read_records(response, ("uid", "locale"))

        expected = [
            {"uid": str(uid), "locale": locale}
            for uid, locale in self.sessions.items()
        ]

        assert records == expected

    def check_prompts(self):
        """Сравнивает запросы сервера с моделью."""
        response = self.client.get_prompts()
        records = read_records(
            response, ("uid", "parameter", "session")
        )

        expected = [
            {
                "uid": str(uid),
                "parameter": data[0],
                "session": str(data[1])
            }
            for uid, data in self.prompts.items()
        ]

        assert records == expected

    def check_feedbacks(self):
        """Сравнивает обратную связь с моделью."""
        response = self.client.get_feedbacks()
        records = read_records(
            response, ("uid", "status", "prompt")
        )

        expected = [
            {
                "uid": str(uid),
                "status": data[0],
                "prompt": str(data[1])
            }
            for uid, data in self.feedbacks.items()
        ]

        assert records == expected

    @rule(locale=st.sampled_from(["ru", "en", "fr", ""]))
    def session_cycle(self, locale):
        """Проверяет создание, чтение, изменение и удаление."""
        uid = self.new_uid()

        self.client.create_session(uid, locale)
        self.sessions[uid] = locale
        self.check_sessions()

        self.client.update_session(uid, "de")
        self.sessions[uid] = "de"
        self.check_sessions()

        self.client.delete_session(uid)
        del self.sessions[uid]
        self.check_sessions()

    @rule(parameter=st.text(
        alphabet="abc123", min_size=1, max_size=12
    ))
    def prompt_cycle(self, parameter):
        """Проверяет полный цикл операций с Prompt."""
        session_uid = self.new_uid()
        prompt_uid = self.new_uid()

        self.client.create_session(session_uid, "ru")
        self.sessions[session_uid] = "ru"

        self.client.create_prompt(
            prompt_uid, parameter, session_uid
        )
        self.prompts[prompt_uid] = (parameter, session_uid)
        self.check_prompts()

        self.client.update_prompt(prompt_uid, "updated")
        self.prompts[prompt_uid] = ("updated", session_uid)
        self.check_prompts()

        self.client.delete_prompt(prompt_uid)
        del self.prompts[prompt_uid]
        self.check_prompts()

    @rule(status=st.sampled_from([
        "success", "failed", "pending"
    ]))
    def feedback_cycle(self, status):
        """Проверяет полный цикл операций с Feedback."""
        session_uid = self.new_uid()
        prompt_uid = self.new_uid()
        feedback_uid = self.new_uid()

        self.client.create_session(session_uid, "ru")
        self.sessions[session_uid] = "ru"

        self.client.create_prompt(prompt_uid, "test", session_uid)
        self.prompts[prompt_uid] = ("test", session_uid)

        self.client.create_feedback(
            feedback_uid, "answer", status,
            "", prompt_uid, 0, 100
        )
        self.feedbacks[feedback_uid] = (status, prompt_uid)
        self.check_feedbacks()

        self.client.update_feedback(feedback_uid, "updated")
        self.feedbacks[feedback_uid] = ("updated", prompt_uid)
        self.check_feedbacks()

        result = self.client.get_recent_feedbacks()
        records = read_records(
            result, ("error", "parameter", "locale")
        )

        assert {
            "error": "",
            "parameter": "test",
            "locale": "ru"
        } in records

        self.client.delete_feedback(feedback_uid)
        del self.feedbacks[feedback_uid]
        self.check_feedbacks()

    @rule()
    def missing_session(self):
        """Проверяет обновление отсутствующей Session."""
        uid = self.new_uid()

        with pytest.raises(ValueError, match="Record not found"):
            self.client.update_session(uid, "ru")

    @rule()
    def missing_prompt(self):
        """Проверяет обновление отсутствующего Prompt."""
        uid = self.new_uid()

        with pytest.raises(ValueError, match="Record not found"):
            self.client.update_prompt(uid, "test")

    @rule()
    def missing_feedback(self):
        """Проверяет обновление отсутствующего Feedback."""
        uid = self.new_uid()

        with pytest.raises(ValueError, match="Record not found"):
            self.client.update_feedback(uid, "failed")

    @rule(uid=st.text(
        alphabet="abcxyz", min_size=1, max_size=5
    ))
    def invalid_uid(self, uid):
        """Проверяет отклонение нечислового UID."""
        with pytest.raises(ValueError):
            self.client.create_session(uid, "ru")

    @rule()
    def unknown_method(self):
        """Проверяет неизвестный RPC-метод."""
        xml = "<request><method>unknown</method></request>"
        response = self.client._send_request(0, xml)
        root = xml_tree.fromstring(response)

        assert root.findtext("status") == "error"
        assert root.findtext("message") == "Unknown method"

    @rule()
    def invalid_xml(self):
        """Проверяет обработку повреждённого XML."""
        response = self.client._send_request(1, "<request>")
        root = xml_tree.fromstring(response)

        assert root.findtext("status") == "error"
        assert root.findtext("message") == "Invalid XML"

    @rule()
    def operation_mismatch(self):
        """Проверяет несовпадение кода операции."""
        xml = (
            "<request><method>create_session</method>"
            "<uid>1</uid><locale>ru</locale></request>"
        )
        response = self.client._send_request(5, xml)
        root = xml_tree.fromstring(response)

        assert root.findtext("status") == "error"
        assert root.findtext("message") == "Operation code mismatch"

    @invariant()
    def check_model_state(self):
        """Проверяет состояние после каждого действия."""
        self.check_sessions()
        self.check_prompts()
        self.check_feedbacks()

        response = self.client.get_recent_feedbacks()
        assert response.findtext("status") == "success"

    def teardown(self):
        """Останавливает сервер после тестирования."""
        stop_server(self.process, self.port)


TestRPCStateMachine = RPCStateMachine.TestCase
TestRPCStateMachine.settings = settings(
    max_examples=30,
    stateful_step_count=12,
    deadline=None
)
