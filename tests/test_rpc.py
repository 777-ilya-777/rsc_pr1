from src.rpc_handler import handle_request



def test_create_session():

    xml = """
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


    response = handle_request(xml)


    assert "success" in response
    assert "Session created" in response



def test_invalid_xml():

    xml = """
    <request>
        <method>
            create_session
        </request>
    """


    response = handle_request(xml)


    assert "Invalid XML" in response


from src.protocol import create_packet, read_packet



def test_packet_protocol():

    xml = "<test>Hello</test>"


    packet = create_packet(
        1,
        xml
    )


    version, operation, result = read_packet(packet)


    assert version == 1
    assert operation == 1
    assert result == xml