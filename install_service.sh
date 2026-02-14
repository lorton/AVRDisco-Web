#!/bin/bash
# AVRDisco-Web Service Installer for Raspberry Pi
# Run this script to install as a systemd service

set -e

echo "=================================================="
echo "AVRDisco-Web Service Installer"
echo "=================================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please do not run as root/sudo"
    echo "   Run: ./install_service.sh"
    exit 1
fi

# Check we're in the right directory
if [ ! -f "avrdisco.service" ]; then
    echo "❌ Error: avrdisco.service not found"
    echo "   Please run this script from the AVRDisco-Web directory"
    exit 1
fi

# Get current directory and user
INSTALL_DIR=$(pwd)
CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn)

echo "📋 Installation Configuration:"
echo "   Directory: $INSTALL_DIR"
echo "   User:      $CURRENT_USER"
echo "   Group:     $CURRENT_GROUP"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements/async.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Configuration file not found"
    echo "   Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env with your receiver's IP address"
    echo "   Run: nano .env"
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

# Create customized service file with actual paths
echo "🔧 Customizing service file for your installation..."
SERVICE_FILE="/tmp/avrdisco.service"

# Replace placeholders with actual values
sed "s|/home/pi/AVRDisco-Web|$INSTALL_DIR|g" avrdisco.service > "$SERVICE_FILE"
sed -i "s|User=pi|User=$CURRENT_USER|g" "$SERVICE_FILE"
sed -i "s|Group=pi|Group=$CURRENT_GROUP|g" "$SERVICE_FILE"

echo "   ✓ User:              pi → $CURRENT_USER"
echo "   ✓ Group:             pi → $CURRENT_GROUP"
echo "   ✓ WorkingDirectory:  /home/pi/AVRDisco-Web → $INSTALL_DIR"
echo "   ✓ ExecStart path:    Updated"
echo "   ✓ Environment PATH:  Updated"
echo ""

# Install service
echo ""
echo "🔧 Installing systemd service..."
sudo cp "$SERVICE_FILE" /etc/systemd/system/avrdisco.service
rm "$SERVICE_FILE"

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Enable service
echo "✅ Enabling auto-start on boot..."
sudo systemctl enable avrdisco

# Start service
echo "🚀 Starting service..."
sudo systemctl start avrdisco

# Wait a moment for startup
sleep 2

# Check status
echo ""
echo "=================================================="
echo "Installation Complete!"
echo "=================================================="
echo ""

if sudo systemctl is-active --quiet avrdisco; then
    echo "✅ Service is running!"
    echo ""
    echo "🌐 Access the web interface:"
    echo "   http://$(hostname -I | awk '{print $1}'):5000"
    echo ""
    echo "📋 Useful commands:"
    echo "   sudo systemctl status avrdisco    # Check status"
    echo "   sudo systemctl restart avrdisco   # Restart"
    echo "   sudo systemctl stop avrdisco      # Stop"
    echo "   sudo journalctl -u avrdisco -f    # View logs"
    echo ""
else
    echo "⚠️  Service is not running. Check status:"
    echo "   sudo systemctl status avrdisco"
    echo "   sudo journalctl -u avrdisco -n 50"
    echo ""
fi

echo "📖 For more info, see RASPBERRY_PI_SETUP.md"
echo ""
