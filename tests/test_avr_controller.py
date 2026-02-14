import pytest
from unittest.mock import Mock, patch
from avr_controller import AVRController


class TestAVRControllerLogic:
    """Test AVR controller logic and behavior"""

    def setup_method(self):
        """Set up test fixtures"""
        self.controller = AVRController('192.168.1.100', 60128, 5)
        self.debug_controller = AVRController('192.168.1.100', 60128, 5, debug_mode=True)

    def test_debug_mode_bypasses_telnet(self):
        """Test that debug mode doesn't actually create telnet connections"""
        result = self.debug_controller.connect()
        
        assert result == True
        assert self.debug_controller.connected == True
        # In debug mode, no actual telnet connection should be created
        assert self.debug_controller.connection is None

    @patch('avr_controller.TelnetClient')
    def test_auto_connect_on_send_command(self, mock_telnet_class):
        """Test that send_command automatically connects when needed"""
        mock_connection = Mock()
        mock_telnet_class.return_value = mock_connection

        # Start disconnected
        assert self.controller.connected == False

        success, message = self.controller.send_command('PWON')

        # Should auto-connect and succeed
        assert success == True
        assert self.controller.connected == True
        mock_telnet_class.assert_called_once()

    @patch('avr_controller.TelnetClient')
    def test_connection_failure_handling(self, mock_telnet_class):
        """Test proper handling of connection failures"""
        mock_connection = Mock()
        mock_connection.open.side_effect = Exception("Network unreachable")
        mock_telnet_class.return_value = mock_connection

        success, message = self.controller.send_command('PWON')

        assert success == False
        # Updated: error message now includes details (improved behavior)
        assert "Not connected to AVR" in message
        assert "Network unreachable" in message
        assert self.controller.connected == False

    @patch('avr_controller.TelnetClient')
    def test_command_encoding_with_carriage_return(self, mock_telnet_class):
        """Test that commands are properly encoded with carriage return"""
        mock_connection = Mock()
        mock_telnet_class.return_value = mock_connection
        self.controller.connect()

        self.controller.send_command('PWON')

        # Should send command with \r and proper encoding
        mock_connection.write.assert_called_once_with(b'PWON\r')

    @patch('avr_controller.TelnetClient')
    def test_multi_line_command_processing(self, mock_telnet_class):
        """Test that multi-line commands are split and sent separately"""
        mock_connection = Mock()
        mock_connection.read_until.side_effect = [b'MVUP\r', b'MVUP\r', b'MVUP\r']
        mock_telnet_class.return_value = mock_connection
        self.controller.connect()

        success, response = self.controller.send_and_wait('MVUP\nMVUP\nMVUP')

        assert success == True
        assert response == 'MVUP; MVUP; MVUP'
        # Should have sent 3 separate commands
        assert mock_connection.write.call_count == 3
        mock_connection.write.assert_any_call(b'MVUP\r')

    @patch('avr_controller.TelnetClient')
    def test_empty_lines_in_multi_command_ignored(self, mock_telnet_class):
        """Test that empty lines in multi-line commands are ignored"""
        mock_connection = Mock()
        mock_connection.read_until.side_effect = [b'MVUP\r', b'MVUP\r']
        mock_telnet_class.return_value = mock_connection
        self.controller.connect()

        # Command with empty lines should only send non-empty commands
        success, response = self.controller.send_and_wait('MVUP\n\nMVUP\n')

        assert success == True
        # Should only send 2 commands, ignoring empty lines
        assert mock_connection.write.call_count == 2

    def test_debug_mode_command_printing(self):
        """Test that debug mode prints commands instead of sending them"""
        self.debug_controller.connect()
        
        # Should not raise exceptions and return success
        success, message = self.debug_controller.send_command('PWON')
        
        assert success == True
        assert message == "Debug mode - command printed"

    @patch('avr_controller.TelnetClient')
    def test_connection_error_during_send_sets_disconnected(self, mock_telnet_class):
        """Test that connection errors during send properly set disconnected state"""
        mock_connection = Mock()
        mock_connection.write.side_effect = Exception("Connection lost")
        mock_telnet_class.return_value = mock_connection
        self.controller.connect()

        success, message = self.controller.send_command('PWON')

        assert success == False
        assert self.controller.connected == False

    @patch('avr_controller.TelnetClient')
    def test_multi_command_failure_stops_execution(self, mock_telnet_class):
        """Test that if one command in a multi-command sequence fails, execution stops"""
        # Disable retry logic for this test by setting max_retries=0
        controller = AVRController('192.168.1.100', 60128, 5, max_retries=0)

        mock_connection = Mock()
        # First command succeeds, second fails
        def side_effect_send(*args):
            if mock_connection.write.call_count == 1:
                return
            else:
                raise Exception("Connection lost")

        mock_connection.write.side_effect = side_effect_send
        mock_telnet_class.return_value = mock_connection
        controller.connect()

        success, message = controller.send_and_wait('MVUP\nMVUP\nMVUP')

        assert success == False
        # Should stop after first failure, not attempt remaining commands
        assert mock_connection.write.call_count == 2

    @patch('avr_controller.TelnetClient')
    def test_response_decoding_strips_whitespace(self, mock_telnet_class):
        """Test that responses are properly decoded and whitespace stripped"""
        mock_connection = Mock()
        mock_connection.read_until.return_value = b'  PWON  \r\n'
        mock_telnet_class.return_value = mock_connection
        self.controller.connect()

        response = self.controller.read_response()

        assert response == 'PWON'  # Should be stripped of whitespace