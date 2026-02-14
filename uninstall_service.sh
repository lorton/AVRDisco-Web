#!/bin/bash
# AVRDisco-Web Service Uninstaller

set -e

echo "=================================================="
echo "AVRDisco-Web Service Uninstaller"
echo "=================================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please do not run as root/sudo"
    echo "   Run: ./uninstall_service.sh"
    exit 1
fi

# Check if service exists
if [ ! -f "/etc/systemd/system/avrdisco.service" ]; then
    echo "ℹ️  Service is not installed"
    exit 0
fi

echo "This will:"
echo "  - Stop the AVRDisco service"
echo "  - Disable auto-start on boot"
echo "  - Remove the systemd service file"
echo ""
echo "The application files will NOT be deleted."
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Stop service
echo "🛑 Stopping service..."
sudo systemctl stop avrdisco || true

# Disable service
echo "❌ Disabling auto-start..."
sudo systemctl disable avrdisco || true

# Remove service file
echo "🗑️  Removing service file..."
sudo rm /etc/systemd/system/avrdisco.service

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

echo ""
echo "✅ Service uninstalled successfully!"
echo ""
echo "Application files remain at: $(pwd)"
echo "To remove completely: rm -rf $(pwd)"
echo ""
