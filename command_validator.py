"""
Command validation and sanitization utilities for AVR commands.
"""
import re
from typing import Tuple, Optional

# Valid command patterns for Denon/Marantz receivers
# Commands typically consist of 2-10 uppercase letters and optional digits
VALID_COMMAND_PATTERN = re.compile(r'^[A-Z]{2,10}(?:\d{0,3}|UP|DOWN|ON|OFF)?$')

# Maximum command length
MAX_COMMAND_LENGTH = 50

# Dangerous characters that should not appear in commands
FORBIDDEN_CHARS = set('\x00\r\n;|&$`\\<>()[]{}')


def validate_command(command: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a single AVR command.

    Args:
        command: The command string to validate

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not command:
        return False, "Command cannot be empty"

    # Check length
    if len(command) > MAX_COMMAND_LENGTH:
        return False, f"Command exceeds maximum length of {MAX_COMMAND_LENGTH} characters"

    # Check for forbidden characters
    forbidden_found = FORBIDDEN_CHARS.intersection(set(command))
    if forbidden_found:
        return False, f"Command contains forbidden characters: {forbidden_found}"

    # Check against pattern for known good commands
    if not VALID_COMMAND_PATTERN.match(command):
        return False, f"Command '{command}' does not match expected pattern"

    return True, None


def sanitize_command(command: str) -> str:
    """
    Sanitize a command string by removing/escaping potentially dangerous characters.

    Args:
        command: The command string to sanitize

    Returns:
        Sanitized command string
    """
    # Remove any whitespace
    sanitized = command.strip()

    # Remove any control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32)

    # Remove forbidden characters
    sanitized = ''.join(char for char in sanitized if char not in FORBIDDEN_CHARS)

    # Convert to uppercase (standard for Denon/Marantz)
    sanitized = sanitized.upper()

    return sanitized


def validate_and_sanitize(command: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validate and sanitize a command in one step.

    Args:
        command: The command string to process

    Returns:
        Tuple of (is_valid: bool, sanitized_command: str, error_message: Optional[str])
    """
    sanitized = sanitize_command(command)
    is_valid, error_msg = validate_command(sanitized)
    return is_valid, sanitized, error_msg


def validate_custom_command(command: str, allow_multiline: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Validate a custom command which may contain multiple commands.

    Args:
        command: The command string (may contain newlines for multi-command)
        allow_multiline: Whether to allow multi-line commands

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not command:
        return False, "Command cannot be empty"

    # Check total length
    if len(command) > MAX_COMMAND_LENGTH * 10:  # Allow more for multi-line
        return False, "Command sequence is too long"

    # Split into individual commands
    if allow_multiline:
        commands = [cmd.strip() for cmd in command.split('\n') if cmd.strip()]
    else:
        commands = [command]

    # Validate each command
    for cmd in commands:
        is_valid, error_msg = validate_command(cmd)
        if not is_valid:
            return False, f"Invalid command '{cmd}': {error_msg}"

    return True, None
