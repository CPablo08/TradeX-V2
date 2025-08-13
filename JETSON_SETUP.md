# TradeX Setup for Jetson Devices

This guide will help you set up TradeX on your NVIDIA Jetson device.

## 🚀 Quick Start for Jetson

### 1. Prerequisites
Make sure your Jetson has:
- **Ubuntu 20.04 or 22.04** (recommended)
- **Node.js v16 or higher**
- **Git**

### 2. Install Node.js (if not already installed)
```bash
# Update package list
sudo apt update

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### 3. Clone and Setup TradeX
```bash
# Clone the repository
git clone https://github.com/yourusername/TradeX.git
cd TradeX

# Run the automated setup script
chmod +x setup.sh
./setup.sh
```

### 4. Start TradeX
```bash
# Start the backend server
npm start

# In a new terminal, start the frontend
cd client
npm start
```

### 5. Access the Dashboard
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## 🔧 Jetson-Specific Configuration

### Performance Optimization
For better performance on Jetson:

1. **Increase Node.js memory limit**:
```bash
export NODE_OPTIONS="--max-old-space-size=4096"
```

2. **Add to your .env file**:
```bash
NODE_OPTIONS=--max-old-space-size=4096
```

### Network Configuration
If you want to access TradeX from other devices on your network:

1. **Find your Jetson's IP address**:
```bash
hostname -I
```

2. **Access from other devices**:
- Frontend: http://YOUR_JETSON_IP:3000
- Backend: http://YOUR_JETSON_IP:5000

### Auto-Start on Boot (Optional)
To make TradeX start automatically when your Jetson boots:

1. **Create a systemd service**:
```bash
sudo nano /etc/systemd/system/tradex.service
```

2. **Add the following content**:
```ini
[Unit]
Description=TradeX Trading Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/TradeX
ExecStart=/usr/bin/node server/index.js
Restart=always
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

3. **Enable and start the service**:
```bash
sudo systemctl enable tradex
sudo systemctl start tradex
```

## 🐛 Troubleshooting

### Common Jetson Issues

1. **Out of Memory**:
```bash
# Increase swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

2. **Port Already in Use**:
```bash
# Find and kill processes using ports 3000 or 5000
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:5000 | xargs kill -9
```

3. **Permission Issues**:
```bash
# Fix ownership
sudo chown -R $USER:$USER /path/to/TradeX
```

### Performance Monitoring
Monitor your Jetson's performance while running TradeX:

```bash
# Monitor system resources
htop

# Monitor GPU usage (if applicable)
nvidia-smi

# Monitor disk usage
df -h

# Monitor memory usage
free -h
```

## 📊 Resource Requirements

### Minimum Requirements
- **RAM**: 4GB
- **Storage**: 2GB free space
- **CPU**: 2 cores
- **Network**: Stable internet connection

### Recommended Requirements
- **RAM**: 8GB
- **Storage**: 5GB free space
- **CPU**: 4 cores
- **Network**: High-speed internet connection

## 🔒 Security Considerations

1. **Firewall Configuration**:
```bash
# Allow only necessary ports
sudo ufw allow 3000
sudo ufw allow 5000
sudo ufw enable
```

2. **Regular Updates**:
```bash
# Keep your system updated
sudo apt update && sudo apt upgrade
```

## 📞 Support

If you encounter issues specific to Jetson:
1. Check the main README.md troubleshooting section
2. Verify your Jetson's specifications meet the requirements
3. Check system logs: `journalctl -u tradex` (if using systemd)
4. Create an issue on GitHub with "Jetson" in the title

---

**Happy Trading on Jetson! 🚀💰**
