
"""RPC-клиент для взаимодействия с TCP-сервером."""

import socket
import xml.etree.ElementTree as xml_tree

from .protocol import (
    OPERATION_CODES,
    RESPONSE_HEADER_SIZE,
    create_packet,
    read_response_packet,
)


HOST = "127.0.0.1"
PORT = 5000
MAX_RESPONSE_SIZE = 1024 * 1024
FEEDBACK_METRICS_COUNT = 2


class RPCClient:
    """Клиент удалённого вызова процедур."""

    def __init__(self, host=HOST, port=PORT):
        """Сохраняет адрес RPC-сервера."""
        self.host = host
        self.port = port

    def _receive_exactly(self, connection, size):
        """Получает указанное количество байтов."""
        data = bytearray()

        while len(data) < size:
            chunk = connection.recv(size - len(data))

            if not chunk:
                raise ConnectionError("Server closed connection")

            data.extend(chunk)

        return bytes(data)

    def _receive_response(self, connection):
        """Получает полный ответ RPC."""
        header = self._receive_exactly(
            connection, RESPONSE_HEADER_SIZE
        )

        size = int.from_bytes(header[2:7], "little")

        if size > MAX_RESPONSE_SIZE:
            raise ValueError("Response too large")

        body = self._receive_exactly(connection, size)

        return read_response_packet(header + body)

    def _send_request(self, operation_code, xml_request):
        """Передаёт запрос и проверяет код ответа."""
        packet = create_packet(operation_code, xml_request)

        with socket.create_connection(
            (self.host, self.port)
        ) as connection:
            connection.sendall(packet)
            operation, response = self._receive_response(connection)

        if operation != operation_code:
            raise ValueError("Unexpected operation code")

        return response

    def _call(self, method, **params):
        """Выполняет удалённый вызов RPC."""
        root = xml_tree.Element("request")
        xml_tree.SubElement(root, "method").text = method

        for name, value in params.items():
            xml_tree.SubElement(root, name).text = str(value)

        request = xml_tree.tostring(root, encoding="unicode")
        operation_code = OPERATION_CODES[method]

        response = self._send_request(operation_code, request)
        result = xml_tree.fromstring(response)

        if result.findtext("status") != "success":
            message = result.findtext("message", "RPC error")
            raise ValueError(message)

        return result

    def create_session(self, uid, locale):
        """Создаёт новую сессию."""
        return self._call(
            "create_session",
            uid=uid,
            locale=locale
        )

    def get_sessions(self):
        """Получает все сессии."""
        return self._call("get_sessions")

    def delete_session(self, uid):
        """Удаляет сессию."""
        return self._call("delete_session", uid=uid)

    def update_session(self, uid, locale):
        """Изменяет локаль сессии."""
        return self._call(
            "update_session",
            uid=uid,
            locale=locale
        )

    def create_prompt(self, uid, parameter, session):
        """Создаёт пользовательский запрос."""
        return self._call(
            "create_prompt",
            uid=uid,
            parameter=parameter,
            session=session
        )

    def get_prompts(self):
        """Получает все запросы."""
        return self._call("get_prompts")

    def delete_prompt(self, uid):
        """Удаляет запрос."""
        return self._call("delete_prompt", uid=uid)

    def update_prompt(self, uid, parameter):
        """Изменяет параметр запроса."""
        return self._call(
            "update_prompt",
            uid=uid,
            parameter=parameter
        )

    def create_feedback(
        self, uid, response, status, error, prompt, *metrics
    ):
        """Создаёт запись обратной связи."""
        if len(metrics) != FEEDBACK_METRICS_COUNT:
            raise ValueError("Expected cache_hit and duration")

        cache_hit, duration = metrics

        return self._call(
            "create_feedback",
            uid=uid,
            response=response,
            status=status,
            error=error,
            prompt=prompt,
            cache_hit=cache_hit,
            duration=duration
        )

    def get_feedbacks(self):
        """Получает все записи Feedback."""
        return self._call("get_feedbacks")

    def delete_feedback(self, uid):
        """Удаляет запись Feedback."""
        return self._call("delete_feedback", uid=uid)

    def update_feedback(self, uid, status):
        """Изменяет статус Feedback."""
        return self._call(
            "update_feedback",
            uid=uid,
            status=status
        )

    def get_recent_feedbacks(self):
        """Выполняет JOIN-выборку."""
        return self._call("get_recent_feedbacks")


def main():
    """Демонстрирует взаимодействие с RPC-сервером."""
    client = RPCClient()

    try:
        print("Connecting to RPC server...")

        response = client.create_session(1, "ru")
        print("Create Session:")
        xml_tree.dump(response)

        response = client.get_sessions()
        print("Get Sessions:")
        xml_tree.dump(response)

    except (ConnectionError, OSError, ValueError) as error:
        print("RPC error:", error)


if __name__ == "__main__":
    main()
