# Raspberry Pi Setup Guide

Complete guide for installing AVRDisco-Web as a systemd service on Raspberry Pi (Debian/Raspbian).

## Important: Username and Path Configuration

The systemd service needs to know:
1. **Your username** (default: `pi`)
2. **Installation directory** (default: `/home/pi/AVRDisco-Web`)

**Two ways to handle this:**

✅ **Recommended:** Use `./install_service.sh` - automatically detects your setup
📝 **Manual:** Edit `avrdisco.service` to match your username/path (see Step 7)

## Prerequisites

- Raspberry Pi (any model with network)
- Raspbian/Debian OS installed
- Network connection
- AV receiver on same network

## Quick Setup

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# 2. Clone repository
cd ~
git clone https://github.com/lorton/AVRDisco-Web.git
cd AVRDisco-Web

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies (async version)
pip install -r requirements/async.txt

# 5. Configure your receiver
cp .env.example .env
nano .env  # Edit with your receiver's IP address

# 6. Test it works
python async_app.py --debug
# Press Ctrl+C to stop after testing

# 7. Install as systemd service
sudo cp avrdisco.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable avrdisco
sudo systemctl start avrdisco

# 8. Check status
sudo systemctl status avrdisco
```

Access at: **http://[raspberry-pi-ip]:5000**

## Detailed Installation

### Step 1: System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

### Step 2: Clone Repository

```bash
cd /home/pi
git clone https://github.com/lorton/AVRDisco-Web.git
cd AVRDisco-Web
```

### Step 3: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Your prompt should now show `(venv)`.

### Step 4: Install Python Dependencies

**For Async Version (Recommended):**
```bash
pip install -r requirements/async.txt
```

**For Standard Version:**
```bash
pip install -r requirements.txt
```

### Step 5: Configuration

Create and edit the configuration file:

```bash
cp .env.example .env
nano .env
```

Edit these values:
```bash
# Your AV receiver's IP address
AVR_HOST=192.168.1.100

# Your receiver's telnet port (60128 for Denon/Marantz, 23 for others)
AVR_PORT=60128

# Web server port (default: 5000)
PORT=5000

# Allowed CORS origins (use * for development, specific URLs for production)
CORS_ORIGINS=*

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Debug mode (true/false) - set to false for production
DEBUG=false
```

Save with `Ctrl+X`, then `Y`, then `Enter`.

### Step 6: Test Installation

```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Test in debug mode (no receiver needed)
python async_app.py --debug
```

Open browser to `http://[raspberry-pi-ip]:5000` and verify it loads.
Press `Ctrl+C` to stop.

### Step 7: Install Systemd Service

You have two options: automated installation or manual setup.

#### Option A: Automated Installation (Recommended)

Use the installation script which automatically detects your username and directory:

```bash
./install_service.sh
```

The script will:
- Detect your username and installation directory
- Customize the service file automatically
- Install and enable the service
- Show you the access URL

#### Option B: Manual Installation

If you need to install manually or customize further:

**1. Edit the service file for your setup:**

```bash
# Make a copy
cp avrdisco.service avrdisco.service.custom

# Edit the custom file
nano avrdisco.service.custom
```

**Update these lines** to match your setup:
```ini
# Change 'pi' to your username
User=yourusername
Group=yourusername

# Change '/home/pi/AVRDisco-Web' to your installation path
WorkingDirectory=/home/yourusername/AVRDisco-Web
Environment="PATH=/home/yourusername/AVRDisco-Web/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=-/home/yourusername/AVRDisco-Web/.env
ExecStart=/home/yourusername/AVRDisco-Web/venv/bin/hypercorn async_app:app --bind 0.0.0.0:5000 --workers 2
```

**2. Install the customized service:**
```bash
# Copy customized service file
sudo cp avrdisco.service.custom /etc/systemd/system/avrdisco.service

# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable avrdisco

# Start the service now
sudo systemctl start avrdisco
```

#### Different Installation Locations

**If you installed in `/opt` instead of `/home/pi`:**
```bash
# Example for /opt/AVRDisco-Web
User=yourusername
WorkingDirectory=/opt/AVRDisco-Web
Environment="PATH=/opt/AVRDisco-Web/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=-/opt/AVRDisco-Web/.env
ExecStart=/opt/AVRDisco-Web/venv/bin/hypercorn async_app:app --bind 0.0.0.0:5000 --workers 2
```

**If you're using a system user (no home directory):**
```bash
# Example for dedicated avrdisco user
User=avrdisco
Group=avrdisco
WorkingDirectory=/var/lib/avrdisco
Environment="PATH=/var/lib/avrdisco/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=-/var/lib/avrdisco/.env
ExecStart=/var/lib/avrdisco/venv/bin/hypercorn async_app:app --bind 0.0.0.0:5000 --workers 2
```

### Step 8: Verify Service is Running

```bash
# Check service status
sudo systemctl status avrdisco

# Should show:
# ● avrdisco.service - AVRDisco Web Interface for AV Receiver Control
#    Loaded: loaded (/etc/systemd/system/avrdisco.service; enabled)
#    Active: active (running)
```

## Service Management

### Common Commands

```bash
# Start service
sudo systemctl start avrdisco

# Stop service
sudo systemctl stop avrdisco

# Restart service
sudo systemctl restart avrdisco

# Check status
sudo systemctl status avrdisco

# Enable auto-start on boot
sudo systemctl enable avrdisco

# Disable auto-start on boot
sudo systemctl disable avrdisco

# View logs (live)
sudo journalctl -u avrdisco -f

# View logs (last 100 lines)
sudo journalctl -u avrdisco -n 100

# View logs since boot
sudo journalctl -u avrdisco -b
```

### Service Auto-Restart

The service is configured to automatically restart if it crashes:
- **Restart Policy:** Always restart
- **Restart Delay:** 10 seconds
- **Max Retries:** 3 attempts in 60 seconds

If the service fails 3 times in 60 seconds, it will stop trying. Check logs:
```bash
sudo journalctl -u avrdisco -n 50
```

## Updating the Application

```bash
# 1. Stop the service
sudo systemctl stop avrdisco

# 2. Navigate to directory
cd /home/pi/AVRDisco-Web

# 3. Pull latest changes
git pull origin main

# 4. Activate virtual environment
source venv/bin/activate

# 5. Update dependencies
pip install --upgrade -r requirements/async.txt

# 6. Restart service
sudo systemctl start avrdisco

# 7. Check status
sudo systemctl status avrdisco
```

## Troubleshooting

### Service Won't Start

**Check service status:**
```bash
sudo systemctl status avrdisco
```

**Check logs:**
```bash
sudo journalctl -u avrdisco -n 50
```

**Common issues:**

1. **Wrong username or path in service file:**
   ```bash
   # Error: "Failed to determine user credentials"
   # or "Failed to execute command: No such file or directory"

   # Check what's in the service file
   grep -E 'User=|WorkingDirectory=|ExecStart=' /etc/systemd/system/avrdisco.service

   # If paths are wrong, reinstall with install_service.sh
   # OR manually edit:
   sudo nano /etc/systemd/system/avrdisco.service
   # Update User, Group, WorkingDirectory, and ExecStart paths

   # Then reload and restart
   sudo systemctl daemon-reload
   sudo systemctl restart avrdisco
   ```

2. **Port already in use:**
   ```bash
   # Find what's using port 5000
   sudo lsof -i :5000

   # Kill the process or change PORT in .env
   ```

3. **Virtual environment missing:**
   ```bash
   cd /home/pi/AVRDisco-Web  # Or your installation directory
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements/async.txt
   ```

4. **Permissions error:**
   ```bash
   # Fix ownership (replace 'pi' with your username and path with your installation)
   sudo chown -R pi:pi /home/pi/AVRDisco-Web

   # If you installed in /opt or another location:
   sudo chown -R yourusername:yourusername /your/installation/path
   ```

5. **Python module not found:**
   ```bash
   source venv/bin/activate
   pip install -r requirements/async.txt
   sudo systemctl restart avrdisco
   ```

6. **User doesn't exist:**
   ```bash
   # If service file references wrong user
   # Check current user:
   whoami

   # Edit service file with correct username:
   sudo nano /etc/systemd/system/avrdisco.service
   # Change User= and Group= lines

   sudo systemctl daemon-reload
   sudo systemctl restart avrdisco
   ```

### Can't Connect to Receiver

**Test telnet connection manually:**
```bash
telnet 192.168.1.100 60128
# Should connect. Press Ctrl+] then type 'quit' to exit
```

**Check receiver settings:**
- Network control enabled in receiver settings
- Correct IP address in `.env`
- Correct port (60128 for Denon/Marantz, 23 for standard telnet)
- Receiver and Pi on same network

### Web Interface Not Loading

**Check service is running:**
```bash
sudo systemctl status avrdisco
```

**Test locally on Pi:**
```bash
curl http://localhost:5000
```

**Check firewall:**
```bash
# If using ufw
sudo ufw allow 5000/tcp
sudo ufw reload
```

**Find Pi's IP address:**
```bash
hostname -I
```

## Network Configuration

### Static IP (Recommended)

Set a static IP for your Raspberry Pi:

```bash
sudo nano /etc/dhcpcd.conf
```

Add at the end:
```
interface eth0
static ip_address=192.168.1.50/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# Or for WiFi:
interface wlan0
static ip_address=192.168.1.50/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Reboot:
```bash
sudo reboot
```

### Access from Other Devices

Once running, access from any device on your network:
- Computer: `http://192.168.1.50:5000`
- Phone: `http://192.168.1.50:5000`
- Tablet: `http://192.168.1.50:5000`

Bookmark it on your phone for quick access!

## Performance Tuning

### For Raspberry Pi Zero/1

Use fewer workers:
```bash
sudo nano /etc/systemd/system/avrdisco.service
```

Change:
```
ExecStart=/home/pi/AVRDisco-Web/venv/bin/hypercorn async_app:app --bind 0.0.0.0:5000 --workers 1
```

### For Raspberry Pi 4/5

Can use more workers:
```
ExecStart=/home/pi/AVRDisco-Web/venv/bin/hypercorn async_app:app --bind 0.0.0.0:5000 --workers 4
```

After changes:
```bash
sudo systemctl daemon-reload
sudo systemctl restart avrdisco
```

## Adding HTTPS (Optional)

For secure access with Let's Encrypt:

```bash
# Install certbot
sudo apt install certbot

# Get certificate (requires domain name)
sudo certbot certonly --standalone -d avr.yourdomain.com

# Update service file
sudo nano /etc/systemd/system/avrdisco.service
```

Change ExecStart to:
```
ExecStart=/home/pi/AVRDisco-Web/venv/bin/hypercorn async_app:app \
  --bind 0.0.0.0:443 \
  --certfile /etc/letsencrypt/live/avr.yourdomain.com/fullchain.pem \
  --keyfile /etc/letsencrypt/live/avr.yourdomain.com/privkey.pem
```

Note: Requires port forwarding and domain name. Most home users won't need this.

## Autostart on Specific Network

Only start service when connected to home WiFi:

```bash
sudo nano /etc/systemd/system/avrdisco.service
```

Add under `[Unit]`:
```
ConditionPathExists=/sys/class/net/wlan0/operstate
```

## Monitoring

### System Resource Usage

```bash
# CPU and memory usage
htop

# Just the AVRDisco process
ps aux | grep hypercorn
```

### Log Rotation

Logs are automatically rotated by systemd. Configure retention:

```bash
sudo nano /etc/systemd/journald.conf
```

Set:
```
SystemMaxUse=100M
```

Restart journald:
```bash
sudo systemctl restart systemd-journald
```

## Uninstall

```bash
# Stop and disable service
sudo systemctl stop avrdisco
sudo systemctl disable avrdisco

# Remove service file
sudo rm /etc/systemd/system/avrdisco.service
sudo systemctl daemon-reload

# Remove application (optional)
rm -rf /home/pi/AVRDisco-Web
```

## Tips

1. **Bookmark on Phone:** Add to home screen for app-like experience
2. **Use Static IP:** Prevents IP address from changing
3. **Monitor Logs:** Check occasionally for errors
4. **Keep Updated:** Pull latest improvements from GitHub
5. **Backup .env:** Save your configuration before updates

## Support

- GitHub Issues: https://github.com/lorton/AVRDisco-Web/issues
- Documentation: See README.md and other docs in repository
- Logs: `sudo journalctl -u avrdisco -f`

## Quick Reference

### Service Commands
```bash
# Service commands
sudo systemctl {start|stop|restart|status} avrdisco

# View logs
sudo journalctl -u avrdisco -f

# Update app
cd /home/pi/AVRDisco-Web && git pull && sudo systemctl restart avrdisco

# Find IP
hostname -I

# Test connection
curl http://localhost:5000
```

### Common Installation Paths

**Default (user: pi, home directory):**
```bash
User=pi
WorkingDirectory=/home/pi/AVRDisco-Web
ExecStart=/home/pi/AVRDisco-Web/venv/bin/hypercorn async_app:app ...
```

**Different username (e.g., john):**
```bash
User=john
WorkingDirectory=/home/john/AVRDisco-Web
ExecStart=/home/john/AVRDisco-Web/venv/bin/hypercorn async_app:app ...
```

**System-wide installation (/opt):**
```bash
User=youruser
WorkingDirectory=/opt/AVRDisco-Web
ExecStart=/opt/AVRDisco-Web/venv/bin/hypercorn async_app:app ...
```

**Dedicated user (no login):**
```bash
User=avrdisco
Group=avrdisco
WorkingDirectory=/var/lib/avrdisco
ExecStart=/var/lib/avrdisco/venv/bin/hypercorn async_app:app ...
```

### Verify Service Configuration

```bash
# Check what user/path is configured
grep -E 'User=|WorkingDirectory=|ExecStart=' /etc/systemd/system/avrdisco.service

# Check if user exists
id USERNAME

# Check if directory exists
ls -la /path/to/AVRDisco-Web

# Check virtual environment
ls /path/to/AVRDisco-Web/venv/bin/hypercorn
```

Enjoy your automated AV receiver control! 🎵
