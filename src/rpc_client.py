import socket

from .protocol import create_packet, read_packet


HOST = "127.0.0.1"
PORT = 5000


client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)


client.connect(
    (HOST, PORT)
)


print("Connected to server")


xml_request = """
<request>

    <method>
        create_session
    </method>

    <uid>
        1
    </uid>

    <locale>
        ru
    </locale>

</request>
"""


packet = create_packet(
    1,
    xml_request
)


client.send(
    packet
)


response = client.recv(1024)


version, operation, xml_response = read_packet(response)


print("Server response:")

print(xml_response)


client.close()