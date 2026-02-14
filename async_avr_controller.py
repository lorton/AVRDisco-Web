"""
Async AVR controller with state tracking.
"""
import asyncio
import logging
import re
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from async_telnet_client import AsyncTelnetClient

# Command separator for multi-line commands
COMMAND_SEPARATOR = '\n'

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 0.5  # seconds
MAX_RETRY_DELAY = 5.0  # seconds

# State polling interval
STATE_POLL_INTERVAL = 2.0  # seconds


@dataclass
class ReceiverState:
    """Current state of the AV receiver."""
    power: Optional[bool] = None
    volume: Optional[int] = None  # 0-98 (Denon scale: 00-98)
    muted: Optional[bool] = None
    input_source: Optional[str] = None
    surround_mode: Optional[str] = None
    zone2_power: Optional[bool] = None
    zone2_volume: Optional[int] = None
    zone2_muted: Optional[bool] = None
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            'power': self.power,
            'volume': self.volume,
            'muted': self.muted,
            'input_source': self.input_source,
            'surround_mode': self.surround_mode,
            'zone2_power': self.zone2_power,
            'zone2_volume': self.zone2_volume,
            'zone2_muted': self.zone2_muted,
            'last_updated': self.last_updated.isoformat()
        }


class AsyncAVRController:
    """Async AVR controller with state tracking."""

    def __init__(self, host: str, port: int, timeout: int = 5, debug_mode: bool = False,
                 max_retries: int = MAX_RETRIES):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connection: Optional[AsyncTelnetClient] = None
        self.connected = False
        self.debug_mode = debug_mode
        self.max_retries = max_retries
        self.retry_count = 0
        self.last_error: Optional[str] = None

        # State tracking
        self.state = ReceiverState()
        self._state_lock = asyncio.Lock()
        self._polling_task: Optional[asyncio.Task] = None
        self._state_update_callbacks = []

    def add_state_callback(self, callback):
        """Add callback to be called when state updates."""
        self._state_update_callbacks.append(callback)

    def remove_state_callback(self, callback):
        """Remove state update callback."""
        if callback in self._state_update_callbacks:
            self._state_update_callbacks.remove(callback)

    async def _notify_state_update(self):
        """Notify all callbacks of state update."""
        for callback in self._state_update_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.state)
                else:
                    callback(self.state)
            except Exception as e:
                logging.error(f"Error in state update callback: {e}")

    async def connect(self, retry: bool = True) -> bool:
        """
        Connect to the AV receiver with optional retry logic.

        Args:
            retry: Whether to retry on failure with exponential backoff

        Returns:
            True if connection successful, False otherwise
        """
        if self.debug_mode:
            self.connected = True
            self.retry_count = 0
            print(f"[DEBUG] Simulating connection to AVR at {self.host}:{self.port}")
            # Start polling in debug mode
            await self._start_polling()
            return True

        attempts = 0
        delay = INITIAL_RETRY_DELAY

        while attempts <= (self.max_retries if retry else 0):
            try:
                if self.connection:
                    await self.disconnect()

                self.connection = AsyncTelnetClient(self.host, self.port, self.timeout)
                await self.connection.open()
                self.connected = True
                self.retry_count = 0
                self.last_error = None
                logging.info(f"Connected to AVR at {self.host}:{self.port}")

                # Start state polling
                await self._start_polling()

                # Request initial state
                await self._request_initial_state()

                return True
            except Exception as e:
                self.last_error = str(e)
                attempts += 1
                logging.error(f"Failed to connect to AVR (attempt {attempts}/{self.max_retries + 1}): {e}")
                self.connected = False
                self.connection = None

                if retry and attempts <= self.max_retries:
                    logging.info(f"Retrying in {delay:.1f} seconds...")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, MAX_RETRY_DELAY)

        self.retry_count = attempts
        return False

    async def disconnect(self) -> None:
        """Disconnect from the AV receiver."""
        # Stop polling
        await self._stop_polling()

        if self.debug_mode:
            self.connected = False
            print("[DEBUG] Simulating disconnect from AVR")
            return

        try:
            if self.connection:
                await self.connection.close()
                self.connection = None
            self.connected = False
            logging.info("Disconnected from AVR")
        except Exception as e:
            logging.error(f"Error disconnecting: {e}")
            self.connected = False
            self.connection = None

    async def send_command(self, command: str, retry_on_failure: bool = True) -> Tuple[bool, str]:
        """
        Send a command to the AV receiver with optional retry.

        Args:
            command: Command string to send
            retry_on_failure: Whether to retry connection if sending fails

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.connected:
            if not await self.connect(retry=retry_on_failure):
                error_msg = f"Not connected to AVR: {self.last_error or 'Unknown error'}"
                return False, error_msg

        if self.debug_mode:
            print(f"[DEBUG] Would send command: {command}")
            # Simulate state changes in debug mode
            await self._simulate_state_change(command)
            return True, "Debug mode - command printed"

        try:
            if not self.connection:
                return False, "Connection lost"
            command_bytes = (command + '\r').encode('ascii')
            await self.connection.write(command_bytes)
            logging.info(f"Sent command: {command}")

            # Try to read response for state update
            await self._try_read_response(command)

            return True, "Command sent"
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Failed to send command '{command}': {error_msg}")
            self.connected = False
            self.connection = None
            self.last_error = error_msg

            # Try to reconnect and resend if retry is enabled
            if retry_on_failure and self.retry_count < self.max_retries:
                logging.info("Attempting to reconnect and resend command...")
                if await self.connect(retry=True):
                    return await self.send_command(command, retry_on_failure=False)

            return False, error_msg

    async def read_response(self, timeout: int = 2) -> Optional[str]:
        """
        Read response from AV receiver.

        Args:
            timeout: Read timeout in seconds

        Returns:
            Decoded response string or None if no response
        """
        if not self.connected:
            return None

        if self.debug_mode:
            return "DEBUG: Simulated response"

        try:
            if not self.connection:
                return None
            response = await self.connection.read_until(b'\r', timeout)
            if response:
                decoded = response.decode('ascii').strip()
                logging.info(f"Received response: {decoded}")
                # Update state based on response
                await self._update_state_from_response(decoded)
                return decoded
        except asyncio.TimeoutError:
            # Timeout is expected when there's no response
            pass
        except Exception as e:
            logging.error(f"Failed to read response: {e}")
            self.connected = False
            self.connection = None
        return None

    async def send_and_wait(self, command: str, wait_time: float = 0.5) -> Tuple[bool, str]:
        """
        Send command and wait for response - handles multi-line commands.

        Args:
            command: Command string (can contain multiple commands separated by COMMAND_SEPARATOR)
            wait_time: Time to wait between commands in seconds

        Returns:
            Tuple of (success: bool, response: str)
        """
        # Handle multi-line commands (separated by COMMAND_SEPARATOR)
        commands = command.split(COMMAND_SEPARATOR)
        responses = []

        for cmd in commands:
            cmd = cmd.strip()
            if not cmd:
                continue

            success, message = await self.send_command(cmd)
            if not success:
                return success, message

            await asyncio.sleep(wait_time)
            response = await self.read_response()
            if response:
                responses.append(response)

        return True, '; '.join(responses) if responses else "Commands sent"

    async def _try_read_response(self, command: str, timeout: float = 1.0):
        """Try to read response after sending command."""
        try:
            response = await self.read_response(timeout)
            if response:
                logging.debug(f"Read response for '{command}': {response}")
                await self._update_state_from_response(response)
            else:
                logging.debug(f"No response received for '{command}'")
        except Exception as e:
            logging.debug(f"Error reading response for '{command}': {e}")
            pass  # Ignore errors reading response

    async def _update_state_from_response(self, response: str):
        """Update state from receiver response."""
        async with self._state_lock:
            updated = False

            # Power state
            if response == 'PWON':
                self.state.power = True
                updated = True
            elif response == 'PWSTANDBY':
                self.state.power = False
                updated = True

            # Volume (format: MV50 = volume 50)
            if response.startswith('MV') and len(response) >= 3:
                try:
                    vol_str = response[2:4]
                    if vol_str.isdigit():
                        self.state.volume = int(vol_str)
                        updated = True
                        logging.debug(f"Updated volume from response '{response}': {self.state.volume}")
                except (ValueError, IndexError):
                    pass

            # Mute
            if response == 'MUON':
                self.state.muted = True
                updated = True
            elif response == 'MUOFF':
                self.state.muted = False
                updated = True

            # Input source (format: SICD, SIDVD, etc.)
            if response.startswith('SI'):
                self.state.input_source = response[2:]
                updated = True

            # Surround mode (format: MSSTEREO, MSMOVIE, etc.)
            if response.startswith('MS'):
                self.state.surround_mode = response[2:]
                updated = True

            # Zone 2 power
            if response == 'Z2ON':
                self.state.zone2_power = True
                updated = True
            elif response == 'Z2OFF':
                self.state.zone2_power = False
                updated = True

            # Zone 2 volume
            if response.startswith('Z2') and len(response) >= 3:
                try:
                    vol_str = response[2:4]
                    if vol_str.isdigit():
                        self.state.zone2_volume = int(vol_str)
                        updated = True
                except (ValueError, IndexError):
                    pass

            # Zone 2 mute
            if response == 'Z2MUON':
                self.state.zone2_muted = True
                updated = True
            elif response == 'Z2MUOFF':
                self.state.zone2_muted = False
                updated = True

            if updated:
                self.state.last_updated = datetime.now()
                logging.debug(f"State updated, notifying {len(self._state_update_callbacks)} callbacks")
                await self._notify_state_update()

    async def _simulate_state_change(self, command: str):
        """Simulate state changes in debug mode."""
        async with self._state_lock:
            if command == 'PWON':
                self.state.power = True
            elif command == 'PWSTANDBY':
                self.state.power = False
            elif command == 'MVUP':
                self.state.volume = min(98, (self.state.volume or 50) + 1)
            elif command == 'MVDOWN':
                self.state.volume = max(0, (self.state.volume or 50) - 1)
            elif command.startswith('MV') and len(command) >= 3:
                # Volume set command (e.g., MV67)
                try:
                    vol = int(command[2:4])
                    self.state.volume = vol
                except (ValueError, IndexError):
                    pass
            elif command == 'MUON':
                self.state.muted = True
            elif command == 'MUOFF':
                self.state.muted = False
            elif command.startswith('SI'):
                self.state.input_source = command[2:]
            elif command.startswith('MS'):
                self.state.surround_mode = command[2:]
            elif command.startswith('Z2') and len(command) >= 3:
                # Zone 2 commands
                if command == 'Z2MUON':
                    self.state.zone2_muted = True
                elif command == 'Z2MUOFF':
                    self.state.zone2_muted = False
                else:
                    # Zone 2 volume (e.g., Z267)
                    try:
                        vol = int(command[2:4])
                        self.state.zone2_volume = vol
                    except (ValueError, IndexError):
                        pass

            self.state.last_updated = datetime.now()
            await self._notify_state_update()

    async def _request_initial_state(self):
        """Request initial state from receiver."""
        if not self.connected or self.debug_mode:
            return

        # Request current status (queries that return state)
        queries = ['MV?', 'MU?', 'PW?', 'SI?']

        try:
            if not self.connection:
                return

            # Send all queries quickly
            for query in queries:
                command_bytes = (query + '\r').encode('ascii')
                await self.connection.write(command_bytes)
                logging.debug(f"Sent query: {query}")
                await asyncio.sleep(0.05)  # Small delay between queries

            # Now read all responses for a period of time
            # The receiver will send back multiple responses
            read_deadline = asyncio.get_event_loop().time() + 1.0  # Read for up to 1 second

            while asyncio.get_event_loop().time() < read_deadline:
                try:
                    response = await self.connection.read_until(b'\r', timeout=0.2)
                    if response:
                        decoded = response.decode('ascii').strip()
                        logging.debug(f"Poll response: {decoded}")
                        await self._update_state_from_response(decoded)
                except asyncio.TimeoutError:
                    # No more responses, we're done
                    break
                except Exception as e:
                    logging.debug(f"Error reading poll response: {e}")
                    break

        except Exception as e:
            logging.debug(f"Error in state polling: {e}")
            pass  # Ignore errors during state query

    async def _poll_state(self):
        """Poll receiver state periodically."""
        logging.debug("State polling started")
        while self.connected:
            try:
                logging.debug("Polling receiver state...")
                await self._request_initial_state()
                await asyncio.sleep(STATE_POLL_INTERVAL)
            except asyncio.CancelledError:
                logging.debug("State polling cancelled")
                break
            except Exception as e:
                logging.error(f"Error polling state: {e}")
                await asyncio.sleep(STATE_POLL_INTERVAL)

    async def _start_polling(self):
        """Start state polling task."""
        if self._polling_task is None or self._polling_task.done():
            self._polling_task = asyncio.create_task(self._poll_state())

    async def _stop_polling(self):
        """Stop state polling task."""
        if self._polling_task and not self._polling_task.done():
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
            self._polling_task = None

    async def get_state(self) -> ReceiverState:
        """Get current receiver state."""
        async with self._state_lock:
            return self.state
