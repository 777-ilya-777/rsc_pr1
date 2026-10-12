
"""Клиент для отправки RPC-запросов."""

import socket

from .protocol import create_packet, read_packet


HOST = "127.0.0.1"
PORT = 5000


def main():
    """Подключается к серверу и отправляет XML-запрос."""
    xml_request = """
    <request>
        <method>create_session</method>
        <uid>1</uid>
        <locale>ru</locale>
    </request>
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        print("Connected to server")

        packet = create_packet(1, xml_request)
        client.sendall(packet)

        response = client.recv(1024)
        version, operation, xml_response = read_packet(response)

        print("Server response:")
        print(xml_response)


if __name__ == "__main__":
    main()
