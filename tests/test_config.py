import pytest
import sys
from unittest.mock import patch
from config import Config


class TestConfig:
    """Test configuration management"""

    def test_default_config_values(self):
        """Test default configuration values"""
        with patch.object(sys, 'argv', ['app.py']):
            config = Config()
            
            assert config.AVR_HOST == '192.168.1.100'
            assert config.AVR_PORT == 60128
            assert config.AVR_TIMEOUT == 5
            assert config.HOST == 'localhost'
            assert config.PORT == 5000
            assert config.DEBUG == False

    def test_command_line_args(self):
        """Test command line argument parsing"""
        test_args = [
            'app.py',
            '--avr-host', '192.168.1.50',
            '--avr-port', '23',
            '--avr-timeout', '10',
            '--host', '0.0.0.0',
            '--port', '8080',
            '--debug'
        ]
        
        with patch.object(sys, 'argv', test_args):
            config = Config()
            
            assert config.AVR_HOST == '192.168.1.50'
            assert config.AVR_PORT == 23
            assert config.AVR_TIMEOUT == 10
            assert config.HOST == '0.0.0.0'
            assert config.PORT == 8080
            assert config.DEBUG == True

    def test_environment_variables(self):
        """Test environment variable configuration"""
        env_vars = {
            'AVR_HOST': '192.168.1.200',
            'AVR_PORT': '8102',
            'HOST': '127.0.0.1',
            'PORT': '3000'
        }
        
        with patch.dict('os.environ', env_vars):
            with patch.object(sys, 'argv', ['app.py']):
                config = Config()
                
                assert config.AVR_HOST == '192.168.1.200'
                assert config.AVR_PORT == 8102
                assert config.HOST == '127.0.0.1'
                assert config.PORT == 3000

    def test_command_line_overrides_env(self):
        """Test that command line args override environment variables"""
        env_vars = {
            'AVR_HOST': '192.168.1.200',
            'AVR_PORT': '8102'
        }
        
        test_args = [
            'app.py',
            '--avr-host', '192.168.1.50',
            '--avr-port', '23'
        ]
        
        with patch.dict('os.environ', env_vars):
            with patch.object(sys, 'argv', test_args):
                config = Config()
                
                assert config.AVR_HOST == '192.168.1.50'
                assert config.AVR_PORT == 23