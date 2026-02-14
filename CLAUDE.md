# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DiscoAVR is a Python web application that provides a mobile-optimized browser interface to control AV receivers over telnet. The application uses Flask for the web server and provides a responsive UI with organized control buttons for common receiver functions including volume control, input selection, zone 2 controls, and surround mode selection.

## Architecture

### Standard (Synchronous) Version
- **app.py**: Main Flask application with REST API endpoints and SocketIO support
- **avr_controller.py**: Telnet communication layer using modern socket-based implementation with retry logic and exponential backoff
- **telnet_client.py**: Modern replacement for deprecated telnetlib module using raw sockets
- **templates/index.html**: Mobile-optimized web interface with improved UX and accessibility
- **static/js/app.js**: Frontend JavaScript with loading states and command history

### Async Version (NEW - with Real-time State Tracking)
- **async_app.py**: Quart (async Flask) application with WebSocket support for real-time updates
- **async_avr_controller.py**: Async AVR controller with state tracking, polling, and callbacks
- **async_telnet_client.py**: Async telnet client using asyncio streams
- **templates/async_index.html**: Template with live state display and WebSocket integration
- **static/js/async_app.js**: Frontend with WebSocket support for real-time state updates

### Shared Components
- **config.py**: Configuration management with command-line arguments, environment variables, and .env file support
- **avr_commands.py**: Command mappings, UI groupings, and button labels for receiver controls (fully type-hinted)
- **command_validator.py**: Command validation and sanitization utilities for security
- **static/css/style.css**: Extracted CSS with mobile-first responsive design
- **database.py**: Legacy SQLite database implementation (reference for command mappings)

## Development Commands

### Setup and Running

#### Standard Version
```bash
# Install dependencies (choose based on environment)
pip install -r requirements.txt              # Base dependencies
pip install -r requirements/dev.txt          # Development (includes testing, linting, type checking)
pip install -r requirements/test.txt         # Testing only
pip install -r requirements/prod.txt         # Production (includes gunicorn)

# Optional: Copy and configure .env file
cp .env.example .env
# Edit .env with your settings

# Run with default settings (localhost:5000, AVR at 192.168.1.100:60128)
python app.py

# Run with custom AV receiver settings
python app.py --avr-host 192.168.1.50 --avr-port 23

# Run on different web server port and host
python app.py --host 0.0.0.0 --port 8080

# Configure CORS for production (comma-separated origins or "*" for development)
python app.py --cors-origins "http://example.com,https://example.com"

# Set logging level
python app.py --log-level DEBUG

# Enable debug mode (prints telnet commands instead of sending them)
python app.py --debug

# Production deployment with gunicorn
gunicorn -k eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

#### Async Version (Recommended - with Real-time State Tracking)
```bash
# Install async dependencies
pip install -r requirements/async.txt

# Run async version
python async_app.py

# With custom settings
python async_app.py --avr-host 192.168.1.50 --port 8000

# Production deployment with hypercorn (ASGI server)
hypercorn async_app:app --bind 0.0.0.0:5000 --workers 4
```

See [ASYNC_VERSION.md](ASYNC_VERSION.md) for complete async documentation.

### Testing
```bash
# Install test dependencies
pip install -r requirements/test.txt

# Run all tests
pytest

# Run specific test file
pytest tests/test_avr_controller.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run with verbose output
pytest -v

# Type checking with mypy
mypy app.py avr_controller.py config.py avr_commands.py command_validator.py

# Code formatting with black
black .

# Linting with flake8
flake8 .

# Import sorting with isort
isort .
```

### Command Line Options
- `--avr-host`: AV Receiver IP address (default: 192.168.1.100, env: AVR_HOST)
- `--avr-port`: AV Receiver telnet port (default: 60128, env: AVR_PORT)
- `--avr-timeout`: Connection timeout in seconds (default: 5, env: AVR_TIMEOUT)
- `--host`: Web server host (default: localhost, env: HOST)
- `--port`: Web server port (default: 5000, env: PORT)
- `--cors-origins`: CORS allowed origins - comma-separated or "*" (default: http://localhost:5000, env: CORS_ORIGINS)
- `--log-level`: Logging level - DEBUG/INFO/WARNING/ERROR/CRITICAL (default: INFO, env: LOG_LEVEL)
- `--debug`: Enable debug mode - prints commands instead of sending via telnet (env: DEBUG=true)

All options can be configured via command-line arguments, environment variables, or .env file.

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

### Raspberry Pi Deployment

For production deployment on Raspberry Pi with systemd service (auto-start on boot):

```bash
# Complete setup guide in RASPBERRY_PI_SETUP.md

# Quick install
sudo cp avrdisco.service /etc/systemd/system/
sudo systemctl enable avrdisco
sudo systemctl start avrdisco

# Service management
sudo systemctl status avrdisco
sudo journalctl -u avrdisco -f
```

See **[RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md)** for complete installation guide.

## Common Receiver Ports
- Port 23: Standard telnet
- Port 60128: Denon/Marantz receivers (default)
- Port 8102: Some Yamaha models
- Check your receiver's manual for the correct control port