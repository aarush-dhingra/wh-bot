# Troubleshooting Guide

## Android Studio Build Issues

### Issue: "Could not resolve dependencies"
**Solution:**
```bash
# In Android Studio Terminal
cd android-app
./gradlew clean
./gradlew build --refresh-dependencies
```

### Issue: "SDK not found"
**Solution:**
1. File → Project Structure → SDK Location
2. Make sure Android SDK location is set
3. Install SDK via SDK Manager if needed

### Issue: Kotlin plugin not found
**Solution:**
1. File → Settings → Plugins
2. Search "Kotlin"
3. Install/Enable Kotlin plugin
4. Restart Android Studio

## App Testing Issues

### Issue: "Notification Access not appearing"
**Solution:**
- Phone Settings → Apps → Special Access → Notification Access
- Find "WhatsApp Auto Reply" and enable it

### Issue: "No reply action found" in logs
**Solution:**
1. Open WhatsApp
2. Settings → Notifications
3. Enable "Show content" or "Show message preview"
4. Make sure priority notifications are ON

### Issue: Connection test fails
**Solution:**
```bash
# 1. Check server is running
curl http://localhost:5000/health

# 2. Find your laptop IP
ipconfig

# 3. Test from phone's browser
# Open: http://YOUR_LAPTOP_IP:5000/test

# 4. Allow firewall (Windows)
netsh advfirewall firewall add rule name="AI Server" dir=in action=allow protocol=TCP localport=5000

# 5. Make sure both on same WiFi
```

### Issue: App crashes on launch
**Solution:**
Check Logcat in Android Studio for crash details:
- View → Tool Windows → Logcat
- Filter by package: com.whatsappauto
- Look for "FATAL EXCEPTION"

### Issue: Auto-reply not working
**Checklist:**
- [ ] Server running? (check terminal)
- [ ] Notification access granted?
- [ ] Auto-reply toggle ON in app?
- [ ] WhatsApp notifications showing content?
- [ ] Both devices on same WiFi?
- [ ] Correct server IP in app?

**Check Android logs:**
```bash
# Using ADB
adb logcat | grep NotificationListener
```

Look for:
- "WhatsApp notification from: ..." (message detected)
- "AI Response: ..." (got response from server)
- "Reply sent: ..." (successfully replied)

### Issue: Slow AI responses
**Solutions:**
- Use smaller model: `ollama pull phi3:mini`
- Reduce max_tokens in server_ollama.py
- Check GPU usage: `nvidia-smi`
- Close other GPU apps

### Issue: Server crashes/errors

**"Module not found" error:**
```bash
pip install flask flask-cors requests
```

**"Ollama not running" error:**
```bash
# Start Ollama
ollama serve

# Or on Windows, check if service is running
services.msc
# Find "Ollama" service
```

**"Model not found" error:**
```bash
# Pull the model again
curl -X POST http://localhost:11434/api/pull -d "{\"name\": \"phi3\"}"
```

## Network Issues

### Can't connect from phone to laptop

**Test steps:**
1. Ping laptop from phone (use Network Tools app)
2. Check firewall rules
3. Verify same WiFi network
4. Try disabling Windows Firewall temporarily to test

**Alternative: Use USB tethering**
1. Connect phone via USB
2. Enable USB tethering on phone
3. Find new laptop IP: `ipconfig`
4. Use that IP in app

## Performance Optimization

### Reduce response time:
Edit `ai-server/server_ollama.py`:
```python
"options": {
    "temperature": 0.7,
    "num_predict": 50  # Reduce from 100
}
```

### Save battery on phone:
- Only enable auto-reply when needed
- Add contact filtering in NotificationListener.kt

### Monitor server:
```bash
# Watch server logs
tail -f ai-server/server.log

# Check Ollama status
curl http://localhost:11434/api/tags
```

## Getting More Help

**Collect debug info:**
```bash
# Server logs
python ai-server/test_server.py > debug_server.txt

# Android logs
adb logcat -d > debug_android.txt

# Network test
curl -v http://YOUR_IP:5000/health > debug_network.txt
```

**Check versions:**
```bash
python --version
pip list | grep -E "flask|requests"
curl http://localhost:11434/api/tags
```

## Common Questions

**Q: Can I use this with other messaging apps?**
A: Yes! Modify the WHATSAPP_PACKAGE constant in NotificationListener.kt to other app package names (e.g., "com.telegram.messenger")

**Q: How do I add conversation memory?**
A: Modify the server to store message history in a dict/database and include it in the prompt.

**Q: Can I customize the AI personality?**
A: Yes! Edit the system prompt in server_ollama.py or server.py.

**Q: Will this drain my laptop battery?**
A: The model runs on GPU which can use power. Consider:
- Only run when laptop is plugged in
- Use a smaller model
- Set shorter response lengths

**Q: Is this secure?**
A: **NO** - this is for testing only. For production:
- Add HTTPS encryption
- Implement authentication
- Add rate limiting
- Filter sensitive data
- Don't expose to internet
