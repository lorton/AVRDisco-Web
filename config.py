import os
import argparse
from typing import List, Union
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass


class Config:
    """Application configuration from command-line arguments and environment variables."""

    def __init__(self, parse_args: bool = True) -> None:
        """
        Initialize configuration.

        Args:
            parse_args: If True, parse command-line arguments. Set to False for testing.
        """
        if parse_args:
            self.parse_args()
        else:
            # Set defaults for testing
            self._set_defaults()

    def _set_defaults(self) -> None:
        """Set default values without parsing arguments (for testing)."""
        class Args:
            avr_host = os.environ.get('AVR_HOST', '192.168.1.100')
            avr_port = int(os.environ.get('AVR_PORT', '60128'))
            avr_timeout = int(os.environ.get('AVR_TIMEOUT', '5'))
            host = os.environ.get('HOST', 'localhost')
            port = int(os.environ.get('PORT', '5000'))
            cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5000')
            log_level = os.environ.get('LOG_LEVEL', 'INFO')
            debug = os.environ.get('DEBUG', '').lower() == 'true'

        self.args = Args()

    def parse_args(self) -> None:
        """Parse command-line arguments and environment variables."""
        parser = argparse.ArgumentParser(description='DiscoAVR - AV Receiver Web Controller')
        parser.add_argument('--avr-host', default=os.environ.get('AVR_HOST', '192.168.1.100'),
                          help='AV Receiver IP address (default: 192.168.1.100)')
        parser.add_argument('--avr-port', type=int, default=int(os.environ.get('AVR_PORT', 60128)),
                          help='AV Receiver telnet port (default: 60128)')
        parser.add_argument('--avr-timeout', type=int, default=int(os.environ.get('AVR_TIMEOUT', 5)),
                          help='AV Receiver connection timeout (default: 5)')
        parser.add_argument('--host', default=os.environ.get('HOST', 'localhost'),
                          help='Web server host (default: localhost)')
        parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 5000)),
                          help='Web server port (default: 5000)')
        parser.add_argument('--cors-origins', default=os.environ.get('CORS_ORIGINS', 'http://localhost:5000'),
                          help='CORS allowed origins - comma-separated or "*" for all (default: http://localhost:5000)')
        parser.add_argument('--log-level', default=os.environ.get('LOG_LEVEL', 'INFO'),
                          choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                          help='Logging level (default: INFO)')
        parser.add_argument('--debug', action='store_true',
                          default=os.environ.get('DEBUG', '').lower() == 'true',
                          help='Enable debug mode')

        self.args = parser.parse_args()
    
    @property
    def AVR_HOST(self) -> str:
        """AV Receiver hostname or IP address."""
        return self.args.avr_host

    @property
    def AVR_PORT(self) -> int:
        """AV Receiver telnet port."""
        return self.args.avr_port

    @property
    def AVR_TIMEOUT(self) -> int:
        """AV Receiver connection timeout in seconds."""
        return self.args.avr_timeout

    @property
    def HOST(self) -> str:
        """Web server host."""
        return self.args.host

    @property
    def PORT(self) -> int:
        """Web server port."""
        return self.args.port

    @property
    def DEBUG(self) -> bool:
        """Debug mode enabled."""
        return self.args.debug

    @property
    def LOG_LEVEL(self) -> str:
        """Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)."""
        return self.args.log_level

    @property
    def CORS_ORIGINS(self) -> Union[str, List[str]]:
        """
        Parse CORS origins - can be '*' or comma-separated list.

        Returns:
            Either '*' for all origins or list of allowed origin strings
        """
        origins = self.args.cors_origins
        if origins == '*':
            return '*'
        # Split by comma and strip whitespace
        return [origin.strip() for origin in origins.split(',') if origin.strip()]