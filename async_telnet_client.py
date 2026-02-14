"""
Async telnet client implementation using asyncio.
"""
import asyncio
from typing import Optional


class AsyncTelnetClient:
    """Asynchronous telnet client using asyncio."""

    def __init__(self, host: str, port: int, timeout: float = 5.0):
        """
        Initialize async telnet client.

        Args:
            host: Hostname or IP address
            port: Port number
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()

    async def open(self) -> None:
        """Open connection to remote host."""
        async with self._lock:
            if self.writer:
                await self.close()

            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout
            )

    async def close(self) -> None:
        """Close the connection."""
        async with self._lock:
            if self.writer:
                try:
                    self.writer.close()
                    await self.writer.wait_closed()
                except Exception:
                    pass
                finally:
                    self.writer = None
                    self.reader = None

    async def write(self, data: bytes) -> None:
        """
        Write data to the stream.

        Args:
            data: Bytes to send

        Raises:
            ConnectionError: If not connected or send fails
        """
        async with self._lock:
            if not self.writer:
                raise ConnectionError("Not connected")
            self.writer.write(data)
            await self.writer.drain()

    async def read_until(self, delimiter: bytes, timeout: Optional[float] = None) -> bytes:
        """
        Read data until delimiter is found.

        Args:
            delimiter: Byte sequence to read until
            timeout: Optional timeout override

        Returns:
            Bytes read including delimiter

        Raises:
            ConnectionError: If not connected
            asyncio.TimeoutError: If timeout occurs
        """
        async with self._lock:
            if not self.reader:
                raise ConnectionError("Not connected")

            read_timeout = timeout if timeout is not None else self.timeout

            try:
                data = await asyncio.wait_for(
                    self.reader.readuntil(delimiter),
                    timeout=read_timeout
                )
                return data
            except asyncio.LimitOverrunError:
                # Delimiter not found within limit, read what we can
                data = await asyncio.wait_for(
                    self.reader.read(8192),
                    timeout=read_timeout
                )
                return data

    async def readline(self, timeout: Optional[float] = None) -> bytes:
        """
        Read a single line.

        Args:
            timeout: Optional timeout override

        Returns:
            Bytes read including newline

        Raises:
            ConnectionError: If not connected
            asyncio.TimeoutError: If timeout occurs
        """
        async with self._lock:
            if not self.reader:
                raise ConnectionError("Not connected")

            read_timeout = timeout if timeout is not None else self.timeout

            data = await asyncio.wait_for(
                self.reader.readline(),
                timeout=read_timeout
            )
            return data
