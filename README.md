# WhatsApp Auto-Reply with Local AI

This project enables automatic WhatsApp message responses using a locally hosted AI model on your laptop.

## Architecture

```
Android Phone (WhatsApp)
    ↓
Notification Listener Service
    ↓
HTTP Request to Local Server
    ↓
AI Model (Phi-3 Mini / Ollama)
    ↓
AI Response
    ↓
Android Auto-Reply via Intent
```

## System Requirements

### Laptop (AI Server)
- Windows/Linux/Mac
- NVIDIA GPU (RTX 4060 or better recommended)
- 8GB+ RAM
- Python 3.8+
- CUDA installed (for GPU acceleration)

### Android Phone
- Android 7.0+ (API 24+)
- Same WiFi network as laptop

## Installation Guide

### Part 1: Setup AI Server (Laptop)

#### Option A: Using Transformers (Phi-3)

1. **Install Python dependencies:**
   ```bash
   cd ai-server
   pip install -r requirements.txt
   ```

2. **Install CUDA (if not already installed):**
   - Download from: https://developer.nvidia.com/cuda-downloads
   - Install PyTorch with CUDA:
     ```bash
     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
     ```

3. **Run the server:**
   ```bash
   python server.py
   ```

   First run will download the Phi-3 model (~7GB). Wait for "Model loaded successfully!"

#### Option B: Using Ollama (Easier, Recommended for Testing)

1. **Install Ollama:**
   - Windows: Download from https://ollama.ai
   - Or use: `winget install Ollama.Ollama`

2. **Pull a lightweight model:**
   ```bash
   ollama pull phi3
   ```
   Or try other models:
   ```bash
   ollama pull llama3.2
   ollama pull mistral
   ```

3. **Run Ollama:**
   ```bash
   ollama serve
   ```

4. **Run the Ollama-based server:**
   ```bash
   cd ai-server
   pip install flask flask-cors requests
   python server_ollama.py
   ```

5. **Test the server:**
   ```bash
   python test_server.py
   ```

### Part 2: Find Your Laptop's IP Address

**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" under your WiFi adapter (e.g., 192.168.1.100)

**Linux/Mac:**
```bash
ifconfig
```
or
```bash
ip addr show
```

**Important:** Make sure your phone and laptop are on the same WiFi network!

### Part 3: Setup Android App

1. **Open Android Studio**

2. **Import the project:**
   - File → Open
   - Select the `android-app` folder

3. **Connect your Android phone:**
   - Enable Developer Options on your phone:
     - Go to Settings → About Phone
     - Tap "Build Number" 7 times
   - Enable USB Debugging:
     - Settings → Developer Options → USB Debugging
   - Connect via USB

4. **Build and install:**
   - Click the green "Run" button in Android Studio
   - Or use command line:
     ```bash
     cd android-app
     ./gradlew installDebug
     ```

### Part 4: Configure the App

1. **Open the app on your phone**

2. **Enable Notification Access:**
   - Click "Enable Notification Access"
   - Find "WhatsApp Auto Reply" in the list
   - Toggle it ON
   - Go back to the app

3. **Configure Server URL:**
   - Enter your laptop's IP and port
   - Example: `http://192.168.1.100:5000`
   - Click "Test Connection" to verify

4. **Enable Auto-Reply:**
   - Toggle "Enable Auto Reply" switch
   - You're all set!

## Testing

### Test 1: Server Health Check

```bash
curl http://localhost:5000/health
```

Should return JSON with status "online"

### Test 2: Chat Endpoint

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "sender": "TestUser"}'
```

Should return an AI-generated response

### Test 3: End-to-End Test

1. Make sure the server is running on your laptop
2. Make sure the Android app is configured and enabled
3. Send yourself a WhatsApp message from another phone
4. Wait a few seconds
5. You should see an AI-generated reply!

## Firewall Configuration

If the connection fails, you may need to allow port 5000:

**Windows Firewall:**
```powershell
netsh advfirewall firewall add rule name="AI Server" dir=in action=allow protocol=TCP localport=5000
```

**Linux (ufw):**
```bash
sudo ufw allow 5000/tcp
```

## Troubleshooting

### "Connection failed" in Android app
- Check if server is running: `curl http://localhost:5000/health`
- Verify IP address is correct
- Check firewall settings
- Make sure both devices are on same WiFi

### "No reply action found" in logs
- WhatsApp needs to be configured to show message previews
- Go to Settings → Notifications → Enable "Show content"

### Model running slow
- Check if GPU is being used: Look for "Using device: cuda" in logs
- If on CPU, install CUDA and PyTorch with GPU support
- Try Ollama with smaller models (phi3 or llama3.2)

### Out of memory errors
- Use smaller model (phi3 instead of larger models)
- Reduce `max_new_tokens` in server.py
- Close other GPU-intensive applications

## Customization

### Change AI Response Style

Edit the prompt in `server.py` or `server_ollama.py`:

```python
prompt = f"""You are a helpful assistant. Be casual and friendly.

Message from {sender}: {message}

Response:"""
```

### Add Conversation Context

Modify the server to store message history and include it in prompts.

### Filter Messages

In `NotificationListener.kt`, add conditions:

```kotlin
// Skip group messages
if (title.contains("@")) return

// Skip messages from specific contacts
if (sender in listOf("Boss", "Mom")) return

// Only reply to specific contacts
if (sender !in listOf("Friend1", "Friend2")) return
```

## Project Structure

```
wh-bot/
├── android-app/              # Android application
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/com/whatsappauto/
│   │   │   │   ├── MainActivity.kt        # Main UI
│   │   │   │   ├── NotificationListener.kt # Notification service
│   │   │   │   └── ApiClient.kt           # HTTP client
│   │   │   ├── AndroidManifest.xml
│   │   │   └── res/layout/
│   │   └── build.gradle
│   └── build.gradle
└── ai-server/                # AI server
    ├── server.py             # Transformers-based server
    ├── server_ollama.py      # Ollama-based server
    ├── test_server.py        # Test script
    └── requirements.txt      # Python dependencies
```

## Security & Privacy Notes

⚠️ **Important:**
- This is a TEST/DEVELOPMENT project
- The server is accessible to anyone on your local network
- No authentication or encryption
- All messages are sent to the AI server
- For production use, add:
  - HTTPS/SSL encryption
  - API authentication
  - Message filtering/moderation
  - Rate limiting
  - User consent mechanisms

## Performance Tips

1. **Keep responses short:** Limit `max_new_tokens` to 50-150
2. **Use quantized models:** 4-bit or 8-bit quantization reduces memory
3. **Batch processing:** If handling multiple messages
4. **Cache frequently:** Cache common responses
5. **Use Ollama:** Generally faster than raw transformers for small models

## Next Steps for Production

- [ ] Add HTTPS support
- [ ] Implement API authentication
- [ ] Add conversation memory/context
- [ ] Create response filtering (profanity, etc.)
- [ ] Add analytics/logging dashboard
- [ ] Implement user whitelist/blacklist
- [ ] Add scheduling (auto-reply only during certain hours)
- [ ] Create web dashboard for configuration
- [ ] Add support for images/media
- [ ] Implement group chat handling

## License

This is a test/educational project. Use responsibly and in compliance with WhatsApp's Terms of Service.
