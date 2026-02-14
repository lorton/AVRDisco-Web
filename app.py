from typing import Dict, Any, Tuple
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
import logging
import time
import sys
from config import Config
from avr_controller import AVRController
from avr_commands import AVR_COMMANDS, COMMAND_GROUPS, COMMAND_LABELS
from command_validator import validate_custom_command, sanitize_command

# Initialize config - skip arg parsing if running under pytest
_is_testing = 'pytest' in sys.modules
config = Config(parse_args=not _is_testing)

# Setup logging with configurable level
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize Flask app
app = Flask(__name__)

# CORS configuration - use environment variable or default to localhost in production
# Set CORS_ORIGINS environment variable to "*" for development or specific origins for production
cors_origins = config.CORS_ORIGINS
socketio = SocketIO(app, cors_allowed_origins=cors_origins)

# Initialize AVR controller
avr = AVRController(config.AVR_HOST, config.AVR_PORT, config.AVR_TIMEOUT, config.DEBUG)

@app.route('/')
def index() -> str:
    """Render main web interface."""
    return render_template('index.html',
                         command_groups=COMMAND_GROUPS,
                         command_labels=COMMAND_LABELS)

@app.route('/api/connect', methods=['POST'])
def connect_avr() -> Response:
    """Connect to AV receiver."""
    success = avr.connect()
    return jsonify({'success': success, 'connected': avr.connected})

@app.route('/api/disconnect', methods=['POST'])
def disconnect_avr() -> Response:
    """Disconnect from AV receiver."""
    avr.disconnect()
    return jsonify({'success': True, 'connected': avr.connected})

@app.route('/api/status', methods=['GET'])
def get_status() -> Response:
    """Get current connection status."""
    return jsonify({'connected': avr.connected})

@app.route('/api/command/<command_name>', methods=['POST'])
def send_preset_command(command_name: str) -> Response:
    """
    Send predefined command to AV receiver.

    Args:
        command_name: Name of command from AVR_COMMANDS

    Returns:
        JSON response with success status and command response
    """
    if command_name not in AVR_COMMANDS:
        return jsonify({'success': False, 'error': 'Unknown command'})

    command = AVR_COMMANDS[command_name]
    success, response = avr.send_and_wait(command)
    return jsonify({
        'success': success,
        'command': command,
        'response': response,
        'connected': avr.connected
    })

@app.route('/api/command', methods=['POST'])
def send_custom_command() -> Response:
    """
    Send custom command to AV receiver.

    Request body should contain: {"command": "..."}

    Returns:
        JSON response with success status and command response
    """
    data: Dict[str, Any] = request.get_json() or {}
    command: str = data.get('command', '')

    if not command:
        return jsonify({'success': False, 'error': 'No command provided'})

    # Validate and sanitize the custom command
    is_valid, error_msg = validate_custom_command(command, allow_multiline=True)
    if not is_valid:
        logging.warning(f"Invalid custom command rejected: {command} - {error_msg}")
        return jsonify({'success': False, 'error': f'Invalid command: {error_msg}'})

    # Sanitize the command (though validation should have caught issues)
    sanitized_command = sanitize_command(command)

    success, response = avr.send_and_wait(sanitized_command)
    return jsonify({
        'success': success,
        'response': response,
        'connected': avr.connected
    })

@socketio.on('connect')
def handle_connect() -> None:
    """Handle SocketIO client connection."""
    logging.info("SocketIO client connected")
    emit('status_update', {
        'connected': avr.connected,
        'timestamp': time.time()
    })


@socketio.on('disconnect')
def handle_disconnect() -> None:
    """Handle SocketIO client disconnection."""
    logging.info("SocketIO client disconnected")


@socketio.on('send_command')
def handle_command(data: Dict[str, Any]) -> None:
    """
    Handle SocketIO command request.

    Args:
        data: Dictionary containing command_name
    """
    command_name = data.get('command_name')
    if not command_name:
        emit('error', {'message': 'No command_name provided'})
        return

    if command_name not in AVR_COMMANDS:
        emit('error', {'message': f'Unknown command: {command_name}'})
        return

    command = AVR_COMMANDS[command_name]
    success, response = avr.send_and_wait(command)
    emit('command_response', {
        'success': success,
        'command_name': command_name,
        'command': command,
        'response': response,
        'connected': avr.connected,
        'timestamp': time.time()
    })


@socketio.on('request_status')
def handle_status_request() -> None:
    """Handle request for current status."""
    emit('status_update', {
        'connected': avr.connected,
        'timestamp': time.time()
    })

if __name__ == '__main__':
    print(f"Starting DiscoAVR server...")
    print(f"Web interface: http://{config.HOST}:{config.PORT}")
    print(f"AV Receiver: {config.AVR_HOST}:{config.AVR_PORT}")
    if config.DEBUG:
        print("[DEBUG MODE] Commands will be printed instead of sent to receiver")
    
    socketio.run(app, 
                host=config.HOST, 
                port=config.PORT, 
                debug=config.DEBUG)