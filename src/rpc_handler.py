from .models import Session
from . import database
import xml.etree.ElementTree as ET



def handle_request(xml):

    try:
        root = ET.fromstring(xml)

    except Exception:

        return """
        <response>
            <status>error</status>
            <message>
                Invalid XML
            </message>
        </response>
        """


    method = root.find("method").text.strip()


    if method == "create_session":

        uid = int(
            root.find("uid").text.strip()
        )

        locale = (
            root.find("locale").text.strip()
        )


        session = Session(
            uid,
            123456,
            locale
        )


        database.create_session(
            session
        )

        print(database.get_sessions())


        return """
        <response>
            <status>success</status>
            <message>
                Session created
            </message>
        </response>
        """


    return """
    <response>
        <status>error</status>
        <message>
            Unknown method
        </message>
    </response>
    """