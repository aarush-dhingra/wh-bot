package com.whatsappauto

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.text.TextUtils
import android.widget.Button
import android.widget.EditText
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var statusText: TextView
    private lateinit var serverUrlInput: EditText
    private lateinit var enableSwitch: Switch
    private lateinit var testButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        statusText = findViewById(R.id.statusText)
        serverUrlInput = findViewById(R.id.serverUrlInput)
        enableSwitch = findViewById(R.id.enableSwitch)
        testButton = findViewById(R.id.testButton)

        // Load saved server URL
        val prefs = getSharedPreferences("WhatsAppAutoPrefs", Context.MODE_PRIVATE)
        val savedUrl = prefs.getString("server_url", "http://192.168.1.100:5000")
        serverUrlInput.setText(savedUrl)

        val isEnabled = prefs.getBoolean("auto_reply_enabled", false)
        enableSwitch.isChecked = isEnabled

        // Check notification listener permission
        updateStatus()

        findViewById<Button>(R.id.enableNotificationButton).setOnClickListener {
            openNotificationSettings()
        }

        enableSwitch.setOnCheckedChangeListener { _, isChecked ->
            prefs.edit().putBoolean("auto_reply_enabled", isChecked).apply()
            if (isChecked && !isNotificationServiceEnabled()) {
                Toast.makeText(this, "Please enable notification access first", Toast.LENGTH_SHORT).show()
                enableSwitch.isChecked = false
            }
        }

        serverUrlInput.setOnFocusChangeListener { _, hasFocus ->
            if (!hasFocus) {
                val url = serverUrlInput.text.toString()
                prefs.edit().putString("server_url", url).apply()
            }
        }

        testButton.setOnClickListener {
            testServerConnection()
        }
    }

    override fun onResume() {
        super.onResume()
        updateStatus()
    }

    private fun updateStatus() {
        if (isNotificationServiceEnabled()) {
            statusText.text = "✓ Notification Access Granted"
            statusText.setTextColor(getColor(android.R.color.holo_green_dark))
        } else {
            statusText.text = "✗ Notification Access Required"
            statusText.setTextColor(getColor(android.R.color.holo_red_dark))
        }
    }

    private fun isNotificationServiceEnabled(): Boolean {
        val pkgName = packageName
        val flat = Settings.Secure.getString(
            contentResolver,
            "enabled_notification_listeners"
        )
        if (!TextUtils.isEmpty(flat)) {
            val names = flat.split(":")
            for (name in names) {
                val cn = ComponentName.unflattenFromString(name)
                if (cn != null && TextUtils.equals(pkgName, cn.packageName)) {
                    return true
                }
            }
        }
        return false
    }

    private fun openNotificationSettings() {
        val intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
        startActivity(intent)
    }

    private fun testServerConnection() {
        val url = serverUrlInput.text.toString().trim()

        // Save the URL immediately
        val prefs = getSharedPreferences("WhatsAppAutoPrefs", Context.MODE_PRIVATE)
        prefs.edit().putString("server_url", url).apply()

        Toast.makeText(this, "Testing connection to: $url", Toast.LENGTH_SHORT).show()
        android.util.Log.d("MainActivity", "Testing URL: $url")

        // Test connection in background
        Thread {
            try {
                android.util.Log.d("MainActivity", "Sending request to: $url/chat")
                val response = ApiClient.sendMessage(url, "Test message", "Test sender")
                android.util.Log.d("MainActivity", "Response: $response")
                runOnUiThread {
                    Toast.makeText(this, "Success! Server responded: ${response.substring(0, minOf(50, response.length))}...", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                android.util.Log.e("MainActivity", "Connection failed", e)
                runOnUiThread {
                    Toast.makeText(this, "Connection failed: ${e.javaClass.simpleName} - ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }.start()
    }
}
