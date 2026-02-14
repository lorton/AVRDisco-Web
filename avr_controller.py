import threading
import time
import logging
from typing import Optional, Tuple
from telnet_client import TelnetClient

# Command separator for multi-line commands
COMMAND_SEPARATOR = '\n'

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 0.5  # seconds
MAX_RETRY_DELAY = 5.0  # seconds


class AVRController:
    def __init__(self, host: str, port: int, timeout: int = 5, debug_mode: bool = False,
                 max_retries: int = MAX_RETRIES):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connection: Optional[TelnetClient] = None
        self.connected = False
        self.lock = threading.Lock()
        self.debug_mode = debug_mode
        self.max_retries = max_retries
        self.retry_count = 0
        self.last_error: Optional[str] = None
        
    def connect(self, retry: bool = True) -> bool:
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
            return True

        attempts = 0
        delay = INITIAL_RETRY_DELAY

        while attempts <= (self.max_retries if retry else 0):
            try:
                with self.lock:
                    if self.connection:
                        self.disconnect()

                    self.connection = TelnetClient(self.host, self.port, self.timeout)
                    self.connection.open()
                    self.connected = True
                    self.retry_count = 0
                    self.last_error = None
                    logging.info(f"Connected to AVR at {self.host}:{self.port}")
                    return True
            except Exception as e:
                self.last_error = str(e)
                attempts += 1
                logging.error(f"Failed to connect to AVR (attempt {attempts}/{self.max_retries + 1}): {e}")
                self.connected = False
                self.connection = None

                if retry and attempts <= self.max_retries:
                    logging.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                    delay = min(delay * 2, MAX_RETRY_DELAY)  # Exponential backoff

        self.retry_count = attempts
        return False
    
    def disconnect(self) -> None:
        """Disconnect from the AV receiver."""
        if self.debug_mode:
            self.connected = False
            print("[DEBUG] Simulating disconnect from AVR")
            return

        try:
            with self.lock:
                if self.connection:
                    self.connection.close()
                    self.connection = None
                self.connected = False
                logging.info("Disconnected from AVR")
        except Exception as e:
            logging.error(f"Error disconnecting: {e}")
            self.connected = False
            self.connection = None
    
    def send_command(self, command: str, retry_on_failure: bool = True) -> Tuple[bool, str]:
        """
        Send a command to the AV receiver with optional retry.

        Args:
            command: Command string to send
            retry_on_failure: Whether to retry connection if sending fails

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.connected:
            if not self.connect(retry=retry_on_failure):
                error_msg = f"Not connected to AVR: {self.last_error or 'Unknown error'}"
                return False, error_msg

        if self.debug_mode:
            print(f"[DEBUG] Would send command: {command}")
            return True, "Debug mode - command printed"

        try:
            with self.lock:
                if not self.connection:
                    return False, "Connection lost"
                command_bytes = (command + '\r').encode('ascii')
                self.connection.write(command_bytes)
                logging.info(f"Sent command: {command}")
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
                if self.connect(retry=True):
                    return self.send_command(command, retry_on_failure=False)

            return False, error_msg
    
    def read_response(self, timeout: int = 2) -> Optional[str]:
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
            with self.lock:
                if not self.connection:
                    return None
                response = self.connection.read_until(b'\r', timeout)
                if response:
                    decoded = response.decode('ascii').strip()
                    logging.info(f"Received response: {decoded}")
                    return decoded
        except Exception as e:
            logging.error(f"Failed to read response: {e}")
            self.connected = False
            self.connection = None
        return None
    
    def send_and_wait(self, command: str, wait_time: float = 1.0) -> Tuple[bool, str]:
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

            success, message = self.send_command(cmd)
            if not success:
                return success, message

            time.sleep(wait_time)
            response = self.read_response()
            if response:
                responses.append(response)

        return True, '; '.join(responses) if responses else "Commands sent"