import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from avr_controller import AVRController


class TestFlaskApp:
    """Test Flask application logic"""

    def setup_method(self):
        """Set up test fixtures"""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()

    def teardown_method(self):
        """Clean up after tests"""
        self.ctx.pop()

    def test_index_page_loads(self):
        """Test that index page loads successfully"""
        response = self.client.get('/')
        assert response.status_code == 200
        assert b'DiscoAVR' in response.data

    @patch('app.avr')
    def test_connect_endpoint_success(self, mock_avr):
        """Test successful connection endpoint"""
        mock_avr.connect.return_value = True
        mock_avr.connected = True
        
        response = self.client.post('/api/connect')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == True
        assert data['connected'] == True
        mock_avr.connect.assert_called_once()

    @patch('app.avr')
    def test_connect_endpoint_failure(self, mock_avr):
        """Test failed connection endpoint"""
        mock_avr.connect.return_value = False
        mock_avr.connected = False
        
        response = self.client.post('/api/connect')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == False
        assert data['connected'] == False

    @patch('app.avr')
    def test_disconnect_endpoint(self, mock_avr):
        """Test disconnect endpoint"""
        mock_avr.connected = False
        
        response = self.client.post('/api/disconnect')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == True
        assert data['connected'] == False
        mock_avr.disconnect.assert_called_once()

    @patch('app.avr')
    def test_status_endpoint(self, mock_avr):
        """Test status endpoint"""
        mock_avr.connected = True
        
        response = self.client.get('/api/status')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['connected'] == True

    @patch('app.avr')
    def test_preset_command_success(self, mock_avr):
        """Test sending preset command successfully"""
        mock_avr.send_and_wait.return_value = (True, "PWON")
        mock_avr.connected = True
        
        response = self.client.post('/api/command/power_on')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == True
        assert data['command'] == 'PWON'
        assert data['response'] == 'PWON'
        assert data['connected'] == True
        mock_avr.send_and_wait.assert_called_once_with('PWON')

    @patch('app.avr')
    def test_preset_command_failure(self, mock_avr):
        """Test sending preset command failure"""
        mock_avr.send_and_wait.return_value = (False, "Connection error")
        mock_avr.connected = False
        
        response = self.client.post('/api/command/power_on')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == False
        assert data['connected'] == False

    def test_unknown_preset_command(self):
        """Test sending unknown preset command"""
        response = self.client.post('/api/command/unknown_command')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == False
        assert data['error'] == 'Unknown command'

    @patch('app.avr')
    def test_custom_command_success(self, mock_avr):
        """Test sending custom command successfully"""
        mock_avr.send_and_wait.return_value = (True, "Custom response")
        mock_avr.connected = True
        
        response = self.client.post('/api/command', 
                                  data=json.dumps({'command': 'CUSTOM'}),
                                  content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == True
        assert data['response'] == 'Custom response'
        mock_avr.send_and_wait.assert_called_once_with('CUSTOM')

    def test_custom_command_no_command(self):
        """Test sending custom command without command parameter"""
        response = self.client.post('/api/command', 
                                  data=json.dumps({}),
                                  content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == False
        assert data['error'] == 'No command provided'

    @patch('app.avr')
    def test_multi_line_command_handling(self, mock_avr):
        """Test that multi-line commands are handled properly"""
        mock_avr.send_and_wait.return_value = (True, "MVUP; MVUP; MVUP")
        mock_avr.connected = True
        
        response = self.client.post('/api/command/volume_up_5')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] == True
        # Should call send_and_wait with the multi-line command
        mock_avr.send_and_wait.assert_called_once_with('MVUP\nMVUP\nMVUP\nMVUP\nMVUP')