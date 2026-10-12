
"""TCP-сервер для обработки RPC-запросов."""

import socket

from .protocol import create_packet, read_packet
from .rpc_handler import handle_request


HOST = "127.0.0.1"
PORT = 5000


def handle_client(conn, addr):
    """Обрабатывает подключение клиента."""
    print("Client connected:", addr)

    data = conn.recv(1024)
    version, operation, xml = read_packet(data)

    print("Version:", version)
    print("Operation:", operation)
    print("XML:")
    print(xml)

    response = handle_request(xml)
    response_packet = create_packet(2, response)

    conn.sendall(response_packet)

    print("Response:")
    print(response)


def main():
    """Запускает TCP-сервер."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)

        print("RPC server started")

        while True:
            conn, addr = server.accept()

            with conn:
                handle_client(conn, addr)


if __name__ == "__main__":
    main()
