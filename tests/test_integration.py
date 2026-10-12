
"""Интеграционные тесты RPC-сервера."""

import subprocess
import sys
import time


def test_server_start():
    """Проверяет успешный запуск сервера."""
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "src.rpc_server"
        ]
    )

    try:
        time.sleep(1)
        assert server.poll() is None
    finally:
        server.terminate()
        server.wait()
