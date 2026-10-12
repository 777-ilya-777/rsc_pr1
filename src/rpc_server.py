
"""TCP-сервер для обработки RPC-запросов."""

import socket
import struct
import xml.etree.ElementTree as xml_tree

from .protocol import (
    OPERATION_CODES,
    REQUEST_HEADER_SIZE,
    VERSION,
    create_response_packet,
)
from .rpc_handler import create_response, handle_request


HOST = "127.0.0.1"
PORT = 5000
MAX_BODY_SIZE = 1024 * 1024
SHUTDOWN_CODE = 0
SHUTDOWN_REQUEST = "<shutdown/>"


def receive_exactly(conn, size):
    """Получает указанное количество байтов."""
    data = bytearray()

    while len(data) < size:
        chunk = conn.recv(size - len(data))

        if not chunk:
            raise ConnectionError("Connection closed")

        data.extend(chunk)

    return bytes(data)


def receive_request(conn):
    """Получает и разбирает RPC-запрос."""
    header = receive_exactly(conn, REQUEST_HEADER_SIZE)
    version, operation, size = struct.unpack("<BBI", header)

    if version != VERSION:
        raise ValueError("Unsupported protocol version")

    if size > MAX_BODY_SIZE:
        raise ValueError("Request too large")

    body = receive_exactly(conn, size)
    xml = body.decode("utf-8")

    return version, operation, xml


def process_request(operation, xml):
    """Проверяет код операции и обрабатывает XML."""
    try:
        root = xml_tree.fromstring(xml)
    except xml_tree.ParseError:
        return handle_request(xml)

    method = root.findtext("method")
    method = method.strip() if method else ""
    expected_code = OPERATION_CODES.get(method)

    if expected_code is None:
        return create_response("error", "Unknown method")

    if operation != expected_code:
        return create_response("error", "Operation code mismatch")

    return handle_request(xml)


def handle_client(conn, addr):
    """Обрабатывает подключение RPC-клиента."""
    print("Client connected:", addr, flush=True)

    try:
        version, operation, xml = receive_request(conn)

        if operation == SHUTDOWN_CODE and xml == SHUTDOWN_REQUEST:
            response = create_response("success", "Server stopping")
            conn.sendall(create_response_packet(operation, response))
            return True

        print("Version:", version)
        print("Operation:", operation)
        print("Request:", xml)

        response = process_request(operation, xml)
        packet = create_response_packet(operation, response)
        conn.sendall(packet)

        print("Response:", response)
    except (ConnectionError, OSError, ValueError) as error:
        print("RPC error:", error)

    return False


def main():
    """Запускает TCP-сервер."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)

        print("RPC server started", flush=True)

        while True:
            conn, addr = server.accept()

            with conn:
                should_stop = handle_client(conn, addr)

            if should_stop:
                print("RPC server stopped", flush=True)
                break


if __name__ == "__main__":
    main()
