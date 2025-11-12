@echo off
echo Getting Android logs for WhatsApp Auto Reply...
echo.
adb logcat -d | findstr "NotificationListener" > android_logs.txt
echo Logs saved to android_logs.txt
type android_logs.txt
pause
