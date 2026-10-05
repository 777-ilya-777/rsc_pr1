import socket

from .protocol import read_packet, create_packet
from .rpc_handler import handle_request

HOST = "127.0.0.1"
PORT = 5000


server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)


server.bind(
    (HOST, PORT)
)


server.listen(1)


print("RPC server started")


while True:

    conn, addr = server.accept()

    print(
        "Client connected:",
        addr
    )

    data = conn.recv(1024)


    version, operation, xml = read_packet(data)


    print("Version:", version)

    print("Operation:", operation)

    print("XML:")

    print(xml)


    response = handle_request(xml)

    response_packet = create_packet(
        2,
        response
    )


    conn.send(
        response_packet
    )


    print("Response:")

    print(response)

    conn.close()