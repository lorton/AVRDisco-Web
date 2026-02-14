// AVRDisco Async Web Interface with WebSocket support

let connected = false;
let ws = null;
let wsConnected = false;
let reconnectTimer = null;
const commandHistory = [];
const MAX_HISTORY = 20;

/**
 * Initialize WebSocket connection
 */
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/state`;

    try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket connected');
            wsConnected = true;
            updateWSIndicator(true);

            // Send ping every 30 seconds to keep connection alive
            if (reconnectTimer) {
                clearInterval(reconnectTimer);
            }
            reconnectTimer = setInterval(() => {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: 'ping' }));
                }
            }, 30000);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'state_update') {
                updateStateDisplay(data.state);
                connected = data.connected;
                updateStatus();
            } else if (data.type === 'pong') {
                // Keep-alive response
                console.log('Received pong');
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            wsConnected = false;
            updateWSIndicator(false);
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
            wsConnected = false;
            updateWSIndicator(false);

            // Attempt to reconnect after 3 seconds
            if (reconnectTimer) {
                clearInterval(reconnectTimer);
            }
            setTimeout(initWebSocket, 3000);
        };
    } catch (error) {
        console.error('Failed to create WebSocket:', error);
        wsConnected = false;
        updateWSIndicator(false);

        // Retry connection
        setTimeout(initWebSocket, 3000);
    }
}

/**
 * Update WebSocket indicator
 */
function updateWSIndicator(isConnected) {
    const indicator = document.getElementById('ws-indicator');
    if (indicator) {
        if (isConnected) {
            indicator.classList.add('connected');
        } else {
            indicator.classList.remove('connected');
        }
    }
}

/**
 * Update state display from WebSocket data
 */
function updateStateDisplay(state) {
    // Power
    const powerEl = document.getElementById('state-power');
    if (state.power !== null) {
        powerEl.textContent = state.power ? 'ON' : 'OFF';
        powerEl.className = 'state-value' + (state.power ? '' : ' off');
    } else {
        powerEl.textContent = '--';
        powerEl.className = 'state-value inactive';
    }

    // Volume
    const volumeEl = document.getElementById('state-volume');
    const volumeBar = document.getElementById('volume-bar');
    if (state.volume !== null) {
        volumeEl.textContent = state.volume;
        volumeEl.className = 'state-value';
        // Scale 0-98 to 0-100%
        const percentage = (state.volume / 98) * 100;
        volumeBar.style.width = percentage + '%';
    } else {
        volumeEl.textContent = '--';
        volumeEl.className = 'state-value inactive';
        volumeBar.style.width = '0%';
    }

    // Muted
    const mutedEl = document.getElementById('state-muted');
    if (state.muted !== null) {
        mutedEl.textContent = state.muted ? 'YES' : 'NO';
        mutedEl.className = 'state-value' + (state.muted ? ' off' : '');
    } else {
        mutedEl.textContent = '--';
        mutedEl.className = 'state-value inactive';
    }

    // Input
    const inputEl = document.getElementById('state-input');
    if (state.input_source) {
        inputEl.textContent = state.input_source;
        inputEl.className = 'state-value';
    } else {
        inputEl.textContent = '--';
        inputEl.className = 'state-value inactive';
    }
}

/**
 * Update connection status display
 */
function updateStatus() {
    const statusEl = document.getElementById('status');
    if (connected) {
        statusEl.textContent = 'Connected';
        statusEl.className = 'status connected';
    } else {
        statusEl.textContent = 'Disconnected';
        statusEl.className = 'status disconnected';
    }
}

/**
 * Update feedback display
 */
function updateFeedback(message, isError = false) {
    const feedbackEl = document.getElementById('feedback');
    feedbackEl.textContent = message;
    if (isError) {
        feedbackEl.style.color = '#ff4444';
    } else {
        feedbackEl.style.color = '#ccc';
    }

    // Add to history
    addToHistory(message, !isError);
}

/**
 * Add message to command history
 */
function addToHistory(message, success = true) {
    const timestamp = new Date().toLocaleTimeString();
    commandHistory.unshift({ message, success, timestamp });

    // Limit history size
    if (commandHistory.length > MAX_HISTORY) {
        commandHistory.pop();
    }

    renderHistory();
}

/**
 * Render command history
 */
function renderHistory() {
    const historyEl = document.getElementById('command-history');
    if (!historyEl) return;

    historyEl.innerHTML = commandHistory
        .map(item => `
            <div class="history-item ${item.success ? 'success' : 'error'}">
                <span style="color: #666">[${item.timestamp}]</span> ${item.message}
            </div>
        `)
        .join('');
}

/**
 * Set button loading state
 */
function setButtonLoading(button, loading) {
    if (loading) {
        button.classList.add('loading');
        button.disabled = true;
    } else {
        button.classList.remove('loading');
        button.disabled = false;
    }
}

/**
 * Connect to AVR
 */
async function connect() {
    const button = event.target;
    setButtonLoading(button, true);

    try {
        const response = await fetch('/api/connect', { method: 'POST' });
        const data = await response.json();
        connected = data.connected;
        updateStatus();
        updateFeedback(data.success ? 'Connected to AVR' : 'Failed to connect', !data.success);
    } catch (error) {
        updateFeedback('Connection error: ' + error.message, true);
    } finally {
        setButtonLoading(button, false);
    }
}

/**
 * Disconnect from AVR
 */
async function disconnect() {
    const button = event.target;
    setButtonLoading(button, true);

    try {
        const response = await fetch('/api/disconnect', { method: 'POST' });
        const data = await response.json();
        connected = data.connected;
        updateStatus();
        updateFeedback('Disconnected from AVR');
    } catch (error) {
        updateFeedback('Disconnect error: ' + error.message, true);
    } finally {
        setButtonLoading(button, false);
    }
}

/**
 * Send command to AVR
 */
async function sendCommand(commandName) {
    const button = event.target;
    setButtonLoading(button, true);

    try {
        const response = await fetch(`/api/command/${commandName}`, { method: 'POST' });
        const data = await response.json();
        connected = data.connected;
        updateStatus();

        // State will be updated via WebSocket, but update here as well for immediate feedback
        if (data.state) {
            updateStateDisplay(data.state);
        }

        if (data.success) {
            const message = `Sent: ${data.command}${data.response ? ' | Response: ' + data.response : ''}`;
            updateFeedback(message);
        } else {
            updateFeedback(`Failed: ${data.error || 'Unknown error'}`, true);
        }
    } catch (error) {
        updateFeedback('Command error: ' + error.message, true);
    } finally {
        setButtonLoading(button, false);
    }
}

/**
 * Initialize application
 */
async function init() {
    // Initialize WebSocket connection
    initWebSocket();

    // Check initial status
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        connected = data.connected;
        updateStatus();

        if (data.state) {
            updateStateDisplay(data.state);
        }
    } catch (error) {
        console.error('Failed to get status:', error);
    }

    // Create history element if it doesn't exist
    const feedbackEl = document.getElementById('feedback');
    if (feedbackEl && !document.getElementById('command-history')) {
        const historyEl = document.createElement('div');
        historyEl.id = 'command-history';
        historyEl.className = 'command-history';
        feedbackEl.parentElement.appendChild(historyEl);
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (ws) {
        ws.close();
    }
    if (reconnectTimer) {
        clearInterval(reconnectTimer);
    }
});
