# Quick Start Guide

## Fastest Way to Get Started (Ollama Method)

### 1. Setup Server (5 minutes)

```bash
# Install Ollama (Windows)
winget install Ollama.Ollama

# Pull lightweight model
ollama pull phi3

# Start Ollama (keep this running)
ollama serve
```

New terminal:
```bash
# Install Python packages
cd ai-server
pip install flask flask-cors requests

# Start server
python server_ollama.py
```

### 2. Get Your IP Address

**Windows:**
```bash
ipconfig
```
Note the IPv4 address (e.g., 192.168.1.100)

### 3. Setup Android App (10 minutes)

```bash
# Open in Android Studio
cd android-app
# Click Run button in Android Studio
```

### 4. Configure on Phone

1. Enable Notification Access (click button in app)
2. Enter server URL: `http://YOUR_IP:5000`
3. Test Connection
4. Toggle "Enable Auto Reply"

### 5. Test It!

Send yourself a WhatsApp message from another phone. You should get an AI reply in ~3-5 seconds!

## Troubleshooting Quick Fixes

**Connection failed?**
```bash
# Windows: Allow port 5000
netsh advfirewall firewall add rule name="AI Server" dir=in action=allow protocol=TCP localport=5000
```

**No auto-reply?**
- Check WhatsApp Settings → Notifications → Show content is enabled
- Make sure notification access is granted
- Verify server is running (check terminal)

## Full Documentation

See [README.md](README.md) for complete setup guide.
See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing instructions.
