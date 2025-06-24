# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DiscoAVR is a Python web application that provides a mobile-optimized browser interface to control AV receivers over telnet. The application uses Flask for the web server and provides a responsive UI with organized control buttons for common receiver functions including volume control, input selection, zone 2 controls, and surround mode selection.

## Architecture

- **app.py**: Main Flask application with REST API endpoints and SocketIO support
- **config.py**: Configuration management with command-line argument parsing
- **avr_controller.py**: Telnet communication layer for AV receiver control with debug mode support
- **avr_commands.py**: Command mappings, UI groupings, and button labels for receiver controls
- **templates/index.html**: Mobile-optimized web interface with grouped control buttons
- **database.py**: Legacy SQLite database implementation (reference for command mappings)

## Development Commands

### Setup and Running
```bash
# Install dependencies
pip install -r requirements.txt

# Install test dependencies
pip install -r test_requirements.txt

# Run with default settings (localhost:5000, AVR at 192.168.1.100:60128)
python app.py

# Run with custom AV receiver settings
python app.py --avr-host 192.168.1.50 --avr-port 23

# Run on different web server port and host
python app.py --host 0.0.0.0 --port 8080

# Enable debug mode (prints telnet commands instead of sending them)
python app.py --debug
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_avr_controller.py

# Run with coverage (if pytest-cov installed)
pytest --cov=. --cov-report=html
```

### Command Line Options
- `--avr-host`: AV Receiver IP address (default: 192.168.1.100)
- `--avr-port`: AV Receiver telnet port (default: 60128, common for Denon/Marantz)
- `--avr-timeout`: Connection timeout in seconds (default: 5)
- `--host`: Web server host (default: localhost)
- `--port`: Web server port (default: 5000)
- `--debug`: Enable debug mode - prints commands instead of sending via telnet

## Configuration

### AV Receiver Commands
Commands are defined in `avr_commands.py` with three main dictionaries:
- `AVR_COMMANDS`: Maps command names to actual telnet commands (supports multi-line commands with \n)
- `COMMAND_GROUPS`: Organizes commands into UI sections (power, main_volume, zone2_volume, inputs, etc.)
- `COMMAND_LABELS`: Provides human-readable button labels

The default commands are for Denon/Marantz receivers. Commands support multi-line sequences (e.g., "MVUP\nMVUP" for multiple volume steps).

### Adding New Commands
1. Add the command mapping to `AVR_COMMANDS` in avr_commands.py
2. Add it to the appropriate group in `COMMAND_GROUPS`
3. Add a user-friendly label to `COMMAND_LABELS`
4. The UI will automatically include the new command in the appropriate section

### Multi-line Commands
For commands that need to be sent multiple times (like volume adjustments), use newline separation:
```python
'volume_up_5': 'MVUP\nMVUP\nMVUP\nMVUP\nMVUP'
```

## API Endpoints

- `GET /`: Main web interface
- `POST /api/connect`: Connect to AV receiver
- `POST /api/disconnect`: Disconnect from receiver
- `GET /api/status`: Get connection status
- `POST /api/command/<command_name>`: Send predefined command from avr_commands.py
- `POST /api/command`: Send custom command (JSON: {"command": "..."})

## UI Organization

The web interface is organized into logical groups:
- **Power**: On/Off controls
- **Main Volume**: Up/Down/Mute with single and multi-step options (2x3 grid layout)
- **Main Volume Presets**: Quick volume level settings (40, 55, 70)
- **Zone 2 Volume**: Secondary zone controls (identical layout to main volume)
- **Zone 2 Volume Presets**: Quick zone 2 volume settings
- **Input Sources**: Source selection (CD, DVD, Bluetooth, etc.)
- **Surround Modes**: Audio processing modes

## Testing and Debug Mode

### Debug Mode
Run with `--debug` flag to test without an actual receiver:
- Simulates connections
- Prints telnet commands to console instead of sending them
- Returns mock responses
- Useful for UI testing and command verification

### Unit Tests
Tests focus on logic and behavior rather than simple existence checks:
- **test_avr_controller.py**: Tests telnet communication logic, multi-line command handling, debug mode behavior
- **test_app.py**: Tests Flask API endpoints, error handling, command routing
- **test_config.py**: Tests argument parsing and configuration management

### Testing Connection
1. Start the server: `python app.py --avr-host YOUR_RECEIVER_IP --avr-port YOUR_PORT`
2. Open browser to `http://localhost:5000`
3. Click "Connect" to test telnet connection
4. Use control buttons to send commands

## Common Receiver Ports
- Port 23: Standard telnet
- Port 60128: Denon/Marantz receivers (default)
- Port 8102: Some Yamaha models
- Check your receiver's manual for the correct control port