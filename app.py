from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import logging
from config import Config
from avr_controller import AVRController
from avr_commands import AVR_COMMANDS, COMMAND_GROUPS, COMMAND_LABELS

# Initialize config
config = Config()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize AVR controller
avr = AVRController(config.AVR_HOST, config.AVR_PORT, config.AVR_TIMEOUT, config.DEBUG)

@app.route('/')
def index():
    return render_template('index.html', 
                         command_groups=COMMAND_GROUPS, 
                         command_labels=COMMAND_LABELS)

@app.route('/api/connect', methods=['POST'])
def connect_avr():
    success = avr.connect()
    return jsonify({'success': success, 'connected': avr.connected})

@app.route('/api/disconnect', methods=['POST'])
def disconnect_avr():
    avr.disconnect()
    return jsonify({'success': True, 'connected': avr.connected})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({'connected': avr.connected})

@app.route('/api/command/<command_name>', methods=['POST'])
def send_preset_command(command_name):
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
def send_custom_command():
    data = request.get_json()
    command = data.get('command', '')
    
    if not command:
        return jsonify({'success': False, 'error': 'No command provided'})
    
    success, response = avr.send_and_wait(command)
    return jsonify({
        'success': success,
        'response': response,
        'connected': avr.connected
    })

@socketio.on('connect')
def handle_connect():
    emit('status', {'connected': avr.connected})

@socketio.on('send_command')
def handle_command(data):
    command_name = data.get('command_name')
    if command_name and command_name in AVR_COMMANDS:
        command = AVR_COMMANDS[command_name]
        success, response = avr.send_and_wait(command)
        emit('command_response', {
            'success': success,
            'command_name': command_name,
            'command': command,
            'response': response,
            'connected': avr.connected
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