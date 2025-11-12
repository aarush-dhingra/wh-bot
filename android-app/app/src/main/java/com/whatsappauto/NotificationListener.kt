package com.whatsappauto

import android.app.Notification
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import kotlinx.coroutines.*

class NotificationListener : NotificationListenerService() {

    private val TAG = "NotificationListener"
    private val WHATSAPP_PACKAGES = listOf(
        "com.whatsapp",           // WhatsApp
        "com.whatsapp.w4b"        // WhatsApp Business
    )
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val processedNotifications = mutableSetOf<String>()  // Track processed notifications

    override fun onNotificationPosted(sbn: StatusBarNotification) {
        val packageName = sbn.packageName

        // Only process WhatsApp notifications (both regular and business)
        if (packageName !in WHATSAPP_PACKAGES) {
            Log.d(TAG, "Ignoring notification from: $packageName")
            return
        }

        // Create unique ID for this notification to prevent duplicates
        val notificationId = "${sbn.key}_${sbn.postTime}"

        // Skip if already processed
        synchronized(processedNotifications) {
            if (processedNotifications.contains(notificationId)) {
                Log.d(TAG, "Skipping duplicate notification: $notificationId")
                return
            }
            processedNotifications.add(notificationId)

            // Keep only last 50 notifications to prevent memory issues
            if (processedNotifications.size > 50) {
                val iterator = processedNotifications.iterator()
                iterator.next()
                iterator.remove()
            }
        }

        Log.d(TAG, "Processing notification from: $packageName")

        // Check if auto-reply is enabled
        val prefs = getSharedPreferences("WhatsAppAutoPrefs", Context.MODE_PRIVATE)
        val isEnabled = prefs.getBoolean("auto_reply_enabled", false)

        if (!isEnabled) {
            Log.d(TAG, "Auto-reply disabled")
            return
        }

        val notification = sbn.notification
        val extras = notification.extras

        // Extract message details
        val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString() ?: ""
        val text = extras.getCharSequence(Notification.EXTRA_TEXT)?.toString() ?: ""

        // Skip if it's a group summary or no text
        if (text.isEmpty() || title.isEmpty()) {
            return
        }

        // Skip messages sent by "You" (our own replies) to prevent infinite loop
        if (title.equals("You", ignoreCase = true)) {
            Log.d(TAG, "Skipping our own message")
            return
        }

        // Skip notifications from groups (optional - you can modify this)
        if (title.contains("@") || text.contains("@")) {
            Log.d(TAG, "Skipping group message")
            return
        }

        Log.d(TAG, "WhatsApp notification from: $title - Message: $text")

        // Get server URL
        val serverUrl = prefs.getString("server_url", "http://192.168.1.100:5000") ?: return

        // Send to AI server and get response
        scope.launch {
            try {
                val aiResponse = ApiClient.sendMessage(serverUrl, text, title)
                Log.d(TAG, "AI Response: $aiResponse")

                // Send reply back to WhatsApp
                sendWhatsAppReply(sbn, aiResponse)

            } catch (e: Exception) {
                Log.e(TAG, "Error processing message", e)
            }
        }
    }

    private fun sendWhatsAppReply(sbn: StatusBarNotification, replyText: String) {
        try {
            val notification = sbn.notification

            // Debug: Log all available actions
            if (notification.actions != null) {
                Log.d(TAG, "Available actions: ${notification.actions.size}")
                notification.actions.forEach { action ->
                    Log.d(TAG, "Action title: ${action.title}")
                }
            } else {
                Log.e(TAG, "No actions available in notification")
                return
            }

            val action = notification.actions?.find {
                it.title.toString().lowercase().contains("reply")
            }

            if (action == null) {
                Log.e(TAG, "No reply action found. Available actions: ${notification.actions?.joinToString { it.title }}")
                return
            }

            Log.d(TAG, "Found reply action: ${action.title}")

            val remoteInputs = action.remoteInputs
            if (remoteInputs.isNullOrEmpty()) {
                Log.e(TAG, "No remote inputs found")
                return
            }

            Log.d(TAG, "Found ${remoteInputs.size} remote inputs")

            val remoteInput = remoteInputs[0]
            val intent = Intent()
            val bundle = Bundle()

            bundle.putCharSequence(remoteInput.resultKey, replyText)
            android.app.RemoteInput.addResultsToIntent(remoteInputs, intent, bundle)

            action.actionIntent.send(this, 0, intent)
            Log.d(TAG, "✓ Reply sent successfully: $replyText")

        } catch (e: Exception) {
            Log.e(TAG, "Error sending reply: ${e.message}", e)
        }
    }

    override fun onNotificationRemoved(sbn: StatusBarNotification) {
        // Not needed for this implementation
    }

    override fun onDestroy() {
        super.onDestroy()
        scope.cancel()
    }
}
