# Python 3.14 Compatibility Note

## Current Status

The core AVRDisco-Web application code is **Python 3.14 compatible** after replacing the deprecated `telnetlib` module with a modern socket-based implementation.

## Testing Status

### ✅ Working Tests (14/14 core tests)
- `tests/test_avr_controller.py` - All 10 tests passing
- `tests/test_config.py` - All 4 tests passing

### ⚠️ Known Issue: Flask App Tests

The Flask/SocketIO integration tests (`tests/test_app.py`) cannot currently run on Python 3.14.2 due to an upstream dependency issue:

```
AttributeError: module 'eventlet.green.thread' has no attribute 'start_joinable_thread'
```

**Root Cause:** The `eventlet` library (version 0.35.2) does not yet fully support Python 3.14. This is a known issue in the eventlet project.

**Impact:**
- The application itself may have runtime issues with SocketIO on Python 3.14
- Flask app tests cannot run
- Core functionality (AVR control, config, telnet communication) is fully tested and working

## Recommended Python Versions

**For Production:**
- Python 3.11.x (LTS, fully supported)
- Python 3.12.x (fully supported)
- Python 3.13.x (likely works, needs testing)

**For Development/Testing:**
- Python 3.11 or 3.12 recommended for full test suite

**For Python 3.14:**
- Core functionality works
- Full testing requires eventlet update
- Monitor: https://github.com/eventlet/eventlet/issues

## Workarounds

### Option 1: Use Python 3.11-3.13
```bash
# Using pyenv or similar
pyenv install 3.12.2
pyenv local 3.12.2
pip install -r requirements/test.txt
pytest -v  # All tests will pass
```

### Option 2: Run Core Tests Only (Python 3.14)
```bash
# These tests work on Python 3.14
pytest tests/test_avr_controller.py tests/test_config.py -v
```

### Option 3: Consider Alternative Async Backend
Replace eventlet with one of:
- **gevent** - Similar to eventlet, may have better Python 3.14 support
- **aiohttp + async Flask (Quart)** - Modern async/await pattern
- **gevent-socketio** - Alternative SocketIO implementation

## Future Plans

Monitor eventlet releases and update when Python 3.14 support is added. Alternatively, consider migrating to a more actively maintained async backend as part of Task #14 (Implement async architecture).

## Testing the Application

Even on Python 3.14, you can test the application in debug mode:

```bash
# This works on Python 3.14
python app.py --debug

# Access at http://localhost:5000
# All commands will be printed instead of sent
```

**Note:** The SocketIO functionality may not work correctly on Python 3.14 until eventlet is updated. For production use on Python 3.14, consider removing SocketIO temporarily or using a compatible Python version.
