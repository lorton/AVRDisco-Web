# Async Version of AVRDisco-Web

## Overview

The async version of AVRDisco-Web provides significant improvements over the synchronous version:

✅ **Real-time State Tracking** - Polls receiver every 2 seconds for current state
✅ **WebSocket Support** - Real-time updates pushed to all connected clients
✅ **Better Performance** - Non-blocking I/O with asyncio
✅ **Live State Display** - Shows current power, volume, mute, and input status
✅ **Automatic Reconnection** - WebSocket auto-reconnects if connection drops

## New Features

### 1. Receiver State Tracking
- Polls receiver state every 2 seconds
- Tracks: power, volume, mute, input source, surround mode, zone 2 status
- State updates automatically when commands are sent
- Displays current state in real-time UI

### 2. WebSocket Communication
- Persistent WebSocket connection for instant updates
- All connected clients receive state updates simultaneously
- Automatic reconnection with exponential backoff
- Keep-alive ping/pong to maintain connection

### 3. Async Architecture
- Built on Quart (async Flask)
- Async AVR controller with non-blocking I/O
- Better concurrency for multiple simultaneous users
- More efficient resource utilization

## Installation

```bash
# Install async dependencies
pip install -r requirements/async.txt

# Or install everything including async
pip install -r requirements/base.txt -r requirements/async.txt
```

## Running the Async Version

### Development
```bash
python async_app.py

# With custom settings
python async_app.py --avr-host 192.168.1.50 --port 8000
```

### Production with Hypercorn (ASGI server)
```bash
# Install production dependencies
pip install -r requirements/async.txt hypercorn

# Run with hypercorn
hypercorn async_app:app --bind 0.0.0.0:5000

# With multiple workers
hypercorn async_app:app --bind 0.0.0.0:5000 --workers 4

# With HTTPS
hypercorn async_app:app --bind 0.0.0.0:5000 \
  --certfile cert.pem --keyfile key.pem
```

## Architecture

### File Structure
```
async_app.py              # Quart application (replaces app.py)
async_avr_controller.py   # Async AVR controller with state tracking
async_telnet_client.py    # Async telnet client using asyncio
templates/async_index.html # Template with state display and WebSocket
static/js/async_app.js    # JavaScript with WebSocket support
```

### State Tracking Flow

```
┌─────────────────┐
│  AVR Receiver   │
└────────┬────────┘
         │
         │ Telnet (polls every 2s)
         ▼
┌─────────────────────────┐
│ AsyncAVRController      │
│ - Maintains state       │
│ - Parses responses      │
│ - Triggers callbacks    │
└──────────┬──────────────┘
           │
           │ State update callbacks
           ▼
┌─────────────────────────┐
│ Broadcast to WebSocket  │
│ clients                 │
└──────────┬──────────────┘
           │
           │ WebSocket messages
           ▼
┌─────────────────────────┐
│ Browser Clients         │
│ - Update UI in real-time│
│ - Display current state │
└─────────────────────────┘
```

### State Update Triggers

State is updated when:
1. **Polling** - Every 2 seconds, queries receiver for status
2. **Commands** - After sending any command, reads response
3. **Initial Connect** - Requests full state when connecting

### Supported State Fields

```python
class ReceiverState:
    power: bool              # Main zone power on/off
    volume: int              # Volume level (0-98)
    muted: bool              # Mute status
    input_source: str        # Current input (CD, DVD, etc.)
    surround_mode: str       # Current surround mode
    zone2_power: bool        # Zone 2 power
    zone2_volume: int        # Zone 2 volume
    zone2_muted: bool        # Zone 2 mute
    last_updated: datetime   # Timestamp of last update
```

## API Differences from Sync Version

### Enhanced Endpoints

All endpoints return state in addition to standard response:

```javascript
// GET /api/status
{
  "connected": true,
  "state": {
    "power": true,
    "volume": 55,
    "muted": false,
    "input_source": "CD",
    "surround_mode": "STEREO",
    "last_updated": "2026-02-14T10:30:00"
  }
}

// POST /api/command/volume_up
{
  "success": true,
  "command": "MVUP",
  "response": "MVUP",
  "connected": true,
  "state": { /* updated state */ }
}
```

### New WebSocket Endpoint

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:5000/ws/state');

// Receive state updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'state_update') {
    console.log('New state:', data.state);
    console.log('Connected:', data.connected);
  }
};

// Keep-alive ping
ws.send(JSON.stringify({ type: 'ping' }));
// Server responds with { type: 'pong' }
```

## Configuration

Uses the same configuration as the sync version:

```bash
# Environment variables or .env file
AVR_HOST=192.168.1.100
AVR_PORT=60128
AVR_TIMEOUT=5
HOST=localhost
PORT=5000
CORS_ORIGINS=http://localhost:5000
LOG_LEVEL=INFO
DEBUG=false
```

## Performance Comparison

| Feature | Sync Version | Async Version |
|---------|-------------|---------------|
| Concurrent requests | Blocking | Non-blocking |
| State tracking | None | Real-time polling |
| Real-time updates | Manual refresh | WebSocket push |
| Connection handling | Synchronous | Async with retry |
| Resource usage | Higher (threading) | Lower (asyncio) |
| Scalability | Limited | Better |

## Browser Compatibility

WebSocket support required (all modern browsers):
- Chrome 4+
- Firefox 6+
- Safari 5+
- Edge (all versions)
- iOS Safari 4.2+
- Android Browser 4.4+

## Debugging

### Enable Debug Mode
```bash
python async_app.py --debug --log-level DEBUG
```

Debug mode features:
- Prints all commands instead of sending to receiver
- Simulates state changes for testing
- No actual telnet connection required
- Perfect for UI development

### WebSocket Debugging

In browser console:
```javascript
// Check WebSocket connection
console.log('WS connected:', wsConnected);

// View current state
console.log('Current state:', state);

// Monitor WebSocket traffic
ws.addEventListener('message', (event) => {
  console.log('WS message:', JSON.parse(event.data));
});
```

## Migrating from Sync to Async

To use both versions:

1. **Sync version** (original): `python app.py`
2. **Async version** (new): `python async_app.py`

Both can coexist. The async version uses different template and JavaScript files, so there's no conflict.

### Differences to Note

1. **Dependencies**: Async version uses Quart instead of Flask
2. **Server**: Use Hypercorn instead of Gunicorn for production
3. **Templates**: Uses `async_index.html` and `async_app.js`
4. **No SocketIO**: Uses native WebSockets instead of Flask-SocketIO

## Troubleshooting

### WebSocket Connection Fails
- Check CORS settings
- Ensure port is not blocked by firewall
- Verify WebSocket support in reverse proxy (nginx, etc.)

### State Not Updating
- Check receiver is responding to status queries (PW?, MV?, etc.)
- Verify receiver supports telnet status queries
- Check logs for polling errors

### High CPU Usage
- Adjust polling interval (default: 2 seconds)
- Edit `STATE_POLL_INTERVAL` in `async_avr_controller.py`

## Advanced Configuration

### Custom Polling Interval

Edit `async_avr_controller.py`:
```python
STATE_POLL_INTERVAL = 5.0  # Poll every 5 seconds instead of 2
```

### Custom State Queries

Override `_request_initial_state()` method to add custom queries for your receiver model.

## Future Enhancements

- [ ] Configurable polling interval via environment variable
- [ ] State caching to reduce receiver queries
- [ ] Multi-zone support in UI
- [ ] Historical state tracking and graphing
- [ ] Push notifications for state changes

## Conclusion

The async version provides a modern, real-time experience with live state updates and WebSocket support. It's recommended for production use due to better performance and scalability.

Use the sync version if:
- You don't need real-time state tracking
- Your deployment doesn't support WebSockets
- You prefer the simplicity of Flask

Use the async version if:
- You want real-time state display
- Multiple users will access simultaneously
- You need better performance and scalability
