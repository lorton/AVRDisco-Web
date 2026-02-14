// AVRDisco Web Interface JavaScript

let connected = false;
const commandHistory = [];
const MAX_HISTORY = 20;

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
function init() {
    // Check initial status
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            connected = data.connected;
            updateStatus();
        })
        .catch(error => {
            console.error('Failed to get status:', error);
        });

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
