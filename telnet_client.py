"""
Simple telnet client implementation using sockets.
Replacement for deprecated telnetlib module.
"""
import socket
import threading
from typing import Optional


class TelnetClient:
    """Simple synchronous telnet client using raw sockets."""

    def __init__(self, host: str, port: int, timeout: float = 5.0):
        """
        Initialize telnet client.

        Args:
            host: Hostname or IP address
            port: Port number
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket: Optional[socket.socket] = None
        self.lock = threading.Lock()

    def open(self) -> None:
        """Open connection to remote host."""
        with self.lock:
            if self.socket:
                self.close()

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))

    def close(self) -> None:
        """Close the connection."""
        with self.lock:
            if self.socket:
                try:
                    self.socket.close()
                except Exception:
                    pass
                finally:
                    self.socket = None

    def write(self, data: bytes) -> None:
        """
        Write data to the socket.

        Args:
            data: Bytes to send

        Raises:
            ConnectionError: If not connected or send fails
        """
        with self.lock:
            if not self.socket:
                raise ConnectionError("Not connected")
            self.socket.sendall(data)

    def read_until(self, delimiter: bytes, timeout: Optional[float] = None) -> bytes:
        """
        Read data until delimiter is found.

        Args:
            delimiter: Byte sequence to read until
            timeout: Optional timeout override

        Returns:
            Bytes read including delimiter

        Raises:
            ConnectionError: If not connected
            socket.timeout: If timeout occurs
        """
        with self.lock:
            if not self.socket:
                raise ConnectionError("Not connected")

            original_timeout = self.socket.gettimeout()
            if timeout is not None:
                self.socket.settimeout(timeout)

            try:
                buffer = b''
                while delimiter not in buffer:
                    chunk = self.socket.recv(1024)
                    if not chunk:
                        break
                    buffer += chunk
                return buffer
            finally:
                if timeout is not None:
                    self.socket.settimeout(original_timeout)
