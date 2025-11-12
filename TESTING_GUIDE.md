# Complete Testing Guide

This guide walks you through testing each component of the WhatsApp Auto-Reply system.

## Prerequisites

- [ ] Android Studio installed
- [ ] Python 3.8+ installed
- [ ] Android phone with USB debugging enabled
- [ ] Laptop and phone on same WiFi network
- [ ] WhatsApp installed on phone

## Phase 1: AI Server Testing (Laptop)

### Step 1.1: Install Dependencies

Choose either Option A (Ollama - easier) or Option B (Transformers - more control):

**Option A: Ollama Setup (Recommended for Testing)**

```bash
# Install Ollama
# Windows: Download from https://ollama.ai or use winget
winget install Ollama.Ollama

# Pull a model
ollama pull phi3

# Start Ollama
ollama serve
```

Leave this terminal running, open a new one:

```bash
# Install Python dependencies
cd ai-server
pip install flask flask-cors requests

# Start the Ollama server
python server_ollama.py
```

**Option B: Transformers Setup**

```bash
cd ai-server

# Install dependencies
pip install -r requirements.txt

# Install PyTorch with CUDA (for GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Start server (will download ~7GB model on first run)
python server.py
```

### Step 1.2: Verify Server is Running

You should see output like:
```
INFO:__main__:Model loaded successfully!
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.100:5000
```

Note your local IP address (e.g., 192.168.1.100)!

### Step 1.3: Test Server Endpoints

Open a new terminal:

**Test 1: Health Check**
```bash
curl http://localhost:5000/health
```

Expected output:
```json
{
  "status": "online",
  "model_loaded": true,
  "timestamp": "2025-11-11T..."
}
```

**Test 2: Simple Test**
```bash
curl http://localhost:5000/test
```

**Test 3: Chat Endpoint**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Hello, how are you?\", \"sender\": \"TestUser\"}"
```

Expected output:
```json
{
  "response": "Hello! I'm doing well, thanks for asking. How can I help you today?"
}
```

**Test 4: Automated Tests**
```bash
python test_server.py
```

All tests should pass with ✓ marks.

### Step 1.4: Find Your Laptop's IP

**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" under your WiFi adapter (e.g., 192.168.1.100)

**Linux/Mac:**
```bash
hostname -I
```

Write down this IP address!

## Phase 2: Android App Testing

### Step 2.1: Open Project in Android Studio

1. Open Android Studio
2. File → Open
3. Navigate to `wh-bot/android-app`
4. Click OK and wait for Gradle sync

### Step 2.2: Connect Your Phone

1. Enable Developer Options on phone:
   - Settings → About Phone → Tap "Build Number" 7 times

2. Enable USB Debugging:
   - Settings → Developer Options → Enable "USB Debugging"

3. Connect phone via USB cable

4. Accept "Allow USB Debugging" prompt on phone

5. Verify connection in Android Studio:
   - Check device dropdown shows your phone model

### Step 2.3: Build and Install App

Click the green "Run" ▶️ button in Android Studio

Or use terminal:
```bash
cd android-app
./gradlew installDebug
```

App should launch on your phone automatically.

### Step 2.4: Configure the App

On your phone:

1. **Enable Notification Access:**
   - Open the app
   - Click "Enable Notification Access"
   - Find "WhatsApp Auto Reply" in the list
   - Toggle it ON
   - Press back button to return to app
   - Verify status shows: "✓ Notification Access Granted" (green)

2. **Configure Server URL:**
   - In "Server Configuration" section
   - Enter: `http://YOUR_LAPTOP_IP:5000`
   - Example: `http://192.168.1.100:5000`
   - Click "Test Connection"
   - Should see: "Server responded: ..." toast message

3. **If Test Connection Fails:**
   - Verify server is running on laptop
   - Check IP address is correct
   - Ensure phone and laptop on same WiFi
   - Check firewall settings (see below)

### Step 2.5: Firewall Configuration (If Needed)

If connection test fails, open firewall:

**Windows:**
```powershell
netsh advfirewall firewall add rule name="AI Server" dir=in action=allow protocol=TCP localport=5000
```

**Linux:**
```bash
sudo ufw allow 5000/tcp
```

Then test connection again.

## Phase 3: End-to-End Testing

### Step 3.1: Prepare Test Environment

1. **On Laptop:**
   - Server is running
   - Terminal showing server logs

2. **On Phone:**
   - App is configured
   - Keep app open to see status

### Step 3.2: Enable Auto-Reply

1. In the app, toggle "Enable Auto Reply" switch to ON
2. You should see confirmation

### Step 3.3: Configure WhatsApp Notifications

**Important:** WhatsApp must show message content in notifications!

1. Open WhatsApp
2. Settings → Notifications
3. Ensure:
   - "Show notifications" is ON
   - "High priority" is ON
   - "Use high priority notifications" is ON
   - Message preview shows "Show content"

### Step 3.4: Send Test Message

**Option A: From Another Phone**
1. Have someone send you a WhatsApp message
2. Or send from another phone you have access to

**Option B: From WhatsApp Web**
1. Save your number as a contact
2. Send yourself a message via WhatsApp Web

### Step 3.5: Observe the Flow

1. **Message arrives on phone**
2. **Notification appears**
3. **Check laptop terminal** - you should see:
   ```
   INFO:__main__:Received message from John: Hey, how are you?
   INFO:__main__:Generated response: I'm doing great, thanks for asking!
   ```
4. **Wait 2-5 seconds**
5. **Check WhatsApp** - AI response should appear automatically!

### Step 3.6: Check Android Logs

Connect phone to Android Studio and check Logcat:

Filter by: `NotificationListener`

You should see:
```
D/NotificationListener: WhatsApp notification from: John - Message: Hey, how are you?
D/NotificationListener: AI Response: I'm doing great, thanks for asking!
D/NotificationListener: Reply sent: I'm doing great, thanks for asking!
```

## Phase 4: Advanced Testing

### Test 4.1: Multiple Messages

Send multiple messages in quick succession:
- "Hello"
- "How are you?"
- "What's the weather?"

Verify each gets a unique AI response.

### Test 4.2: Different Senders

Have messages from different contacts to verify sender name is passed correctly.

### Test 4.3: Long Messages

Send a very long message (500+ characters) and verify AI responds appropriately.

### Test 4.4: Special Characters

Test with emojis, special characters: "Hello! 😊 How's it going?"

### Test 4.5: Rapid Fire

Send 10 messages rapidly (1 per second) - verify all get responses.

## Troubleshooting Common Issues

### Issue 1: "Connection failed" in app

**Diagnosis:**
```bash
# On laptop, check server is running
curl http://localhost:5000/health

# From phone, test if laptop is reachable
# Use a network scanner app to verify
```

**Solutions:**
- [ ] Restart server
- [ ] Check IP address (may have changed)
- [ ] Verify both devices on same WiFi
- [ ] Check firewall rules
- [ ] Try pinging laptop from phone

### Issue 2: No auto-reply sent

**Check Logcat for errors:**

Common issues:
- "No reply action found" → WhatsApp notification settings issue
- "Auto-reply disabled" → Toggle is off in app
- "Skipping group message" → It's a group chat (intentionally skipped)

**Solutions:**
- [ ] Verify WhatsApp notification content is visible
- [ ] Check "Enable Auto Reply" toggle is ON
- [ ] Restart WhatsApp
- [ ] Re-grant notification access

### Issue 3: Server responding slowly

**Check GPU usage:**
```bash
# On laptop
nvidia-smi
```

**Solutions:**
- [ ] Close other GPU applications
- [ ] Use smaller model (phi3 instead of llama3)
- [ ] Reduce `max_new_tokens` in server.py
- [ ] Try Ollama (generally faster)

### Issue 4: "Model not loaded"

**Solutions:**
- [ ] Wait for model download to complete (first run)
- [ ] Check internet connection
- [ ] Verify enough disk space (~10GB free)
- [ ] Try Ollama instead

### Issue 5: Notification not detected

**Verify notification listener:**
```bash
adb shell dumpsys notification_listener
```

Should show your app in enabled listeners.

**Solutions:**
- [ ] Re-enable notification access
- [ ] Restart phone
- [ ] Reinstall app

## Performance Benchmarks

Expected performance on RTX 4060:

| Model | Response Time | Quality |
|-------|--------------|---------|
| Phi-3 Mini | 1-3 seconds | Good |
| Llama 3.2 | 2-4 seconds | Excellent |
| Mistral | 2-5 seconds | Excellent |

## Monitoring & Debugging

### Monitor Server Activity

```bash
# Watch server logs in real-time
tail -f server.log

# Or just watch the terminal where server is running
```

### Monitor Android App

In Android Studio:
1. View → Tool Windows → Logcat
2. Filter: `package:com.whatsappauto`
3. Set level to "Debug"

### Network Traffic

Use Wireshark or tcpdump to inspect HTTP traffic:
```bash
# On laptop
tcpdump -i wlan0 port 5000
```

## Success Criteria

You've successfully completed testing when:

- [ ] Server starts without errors
- [ ] Health check returns "online"
- [ ] Chat endpoint generates responses
- [ ] Android app installs successfully
- [ ] Notification access granted
- [ ] Connection test passes
- [ ] Receive test WhatsApp message
- [ ] AI auto-reply sent within 5 seconds
- [ ] Response is relevant and coherent

## Next Testing Steps

After basic testing works:

1. **Load Testing:**
   - Send 50+ messages
   - Monitor memory usage
   - Check for crashes

2. **Battery Testing:**
   - Leave enabled for 24 hours
   - Monitor battery drain
   - Check for wakelocks

3. **Edge Cases:**
   - Messages while app closed
   - Messages while phone locked
   - Messages during calls
   - Airplane mode scenarios

4. **Different Message Types:**
   - Voice message notifications
   - Image/video notifications
   - Status updates
   - Group invites

## Cleanup After Testing

```bash
# Stop server
Ctrl+C in server terminal

# Uninstall app from phone
adb uninstall com.whatsappauto

# Or keep it for continued testing!
```

## Getting Help

If you encounter issues:

1. Check server logs
2. Check Android Logcat
3. Verify network connectivity
4. Review firewall settings
5. Ensure all prerequisites are met

Happy testing! 🚀
