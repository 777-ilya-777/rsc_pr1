import subprocess
import time


def test_server_start():

    server = subprocess.Popen(
        [
            "python",
            "-m",
            "src.rpc_server"
        ]
    )

    time.sleep(1)

    assert server.poll() is None

    server.terminate()