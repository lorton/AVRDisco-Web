"""
Async AVRDisco-Web application using Quart.
"""
from typing import Dict, Any
from quart import Quart, render_template, request, jsonify, websocket
from quart_cors import cors
import logging
import asyncio
import sys
from config import Config
from async_avr_controller import AsyncAVRController, ReceiverState
from avr_commands import AVR_COMMANDS, COMMAND_GROUPS, COMMAND_LABELS
from command_validator import validate_custom_command, sanitize_command

# Initialize config - skip arg parsing if not running as main script
# When imported by ASGI servers (hypercorn, uvicorn, etc.), we're not __main__
# In those cases, use environment variables only
_is_main = __name__ == '__main__'
_is_testing = 'pytest' in sys.modules
config = Config(parse_args=(_is_main and not _is_testing))

# Setup logging with configurable level
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize Quart app
app = Quart(__name__)

# CORS configuration
cors_origins = config.CORS_ORIGINS
if isinstance(cors_origins, list):
    app = cors(app, allow_origin=cors_origins)
elif cors_origins == '*':
    app = cors(app, allow_origin='*')
else:
    app = cors(app, allow_origin=[cors_origins])

# Initialize AVR controller
avr = AsyncAVRController(config.AVR_HOST, config.AVR_PORT, config.AVR_TIMEOUT, config.DEBUG)

# WebSocket clients for state broadcasting
websocket_clients = set()


@app.route('/')
async def index():
    """Render main web interface."""
    return await render_template('async_index.html',
                                command_groups=COMMAND_GROUPS,
                                command_labels=COMMAND_LABELS)


@app.route('/api/connect', methods=['POST'])
async def connect_avr():
    """Connect to AV receiver."""
    success = await avr.connect()
    return jsonify({'success': success, 'connected': avr.connected})


@app.route('/api/disconnect', methods=['POST'])
async def disconnect_avr():
    """Disconnect from AV receiver."""
    await avr.disconnect()
    return jsonify({'success': True, 'connected': avr.connected})


@app.route('/api/status', methods=['GET'])
async def get_status():
    """Get current connection status and receiver state."""
    state = await avr.get_state()
    return jsonify({
        'connected': avr.connected,
        'state': state.to_dict()
    })


@app.route('/api/command/<command_name>', methods=['POST'])
async def send_preset_command(command_name: str):
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
    success, response = await avr.send_and_wait(command)

    # Get updated state
    state = await avr.get_state()

    return jsonify({
        'success': success,
        'command': command,
        'response': response,
        'connected': avr.connected,
        'state': state.to_dict()
    })


@app.route('/api/command', methods=['POST'])
async def send_custom_command():
    """
    Send custom command to AV receiver.

    Request body should contain: {"command": "..."}

    Returns:
        JSON response with success status and command response
    """
    data: Dict[str, Any] = await request.get_json() or {}
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

    success, response = await avr.send_and_wait(sanitized_command)

    # Get updated state
    state = await avr.get_state()

    return jsonify({
        'success': success,
        'response': response,
        'connected': avr.connected,
        'state': state.to_dict()
    })


@app.websocket('/ws/state')
async def websocket_state():
    """
    WebSocket endpoint for real-time state updates.

    Sends state updates to connected clients whenever the receiver state changes.
    """
    # Add this client to the set
    websocket_clients.add(websocket._get_current_object())

    try:
        # Send initial state
        state = await avr.get_state()
        await websocket.send_json({
            'type': 'state_update',
            'state': state.to_dict(),
            'connected': avr.connected
        })

        # Keep connection alive and handle incoming messages
        while True:
            message = await websocket.receive_json()

            # Handle ping/pong for keep-alive
            if message.get('type') == 'ping':
                await websocket.send_json({'type': 'pong'})

    except asyncio.CancelledError:
        pass
    finally:
        # Remove client from set
        websocket_clients.discard(websocket._get_current_object())


async def broadcast_state_update(state: ReceiverState):
    """
    Broadcast state update to all connected WebSocket clients.

    Args:
        state: Updated receiver state
    """
    if not websocket_clients:
        return

    message = {
        'type': 'state_update',
        'state': state.to_dict(),
        'connected': avr.connected
    }

    # Send to all connected clients
    disconnected = set()
    for client in websocket_clients:
        try:
            await client.send_json(message)
        except Exception:
            disconnected.add(client)

    # Remove disconnected clients
    websocket_clients.difference_update(disconnected)


# Register state update callback
avr.add_state_callback(broadcast_state_update)


@app.before_serving
async def startup():
    """Application startup tasks."""
    logging.info("Starting AVRDisco async application")
    logging.info(f"AV Receiver: {config.AVR_HOST}:{config.AVR_PORT}")
    if config.DEBUG:
        logging.info("[DEBUG MODE] Commands will be printed instead of sent to receiver")


@app.after_serving
async def shutdown():
    """Application shutdown tasks."""
    logging.info("Shutting down AVRDisco async application")
    await avr.disconnect()


if __name__ == '__main__':
    import sys

    print(f"Starting DiscoAVR async server...")
    print(f"Web interface: http://{config.HOST}:{config.PORT}")
    print(f"AV Receiver: {config.AVR_HOST}:{config.AVR_PORT}")
    if config.DEBUG:
        print("[DEBUG MODE] Commands will be printed instead of sent to receiver")

    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
