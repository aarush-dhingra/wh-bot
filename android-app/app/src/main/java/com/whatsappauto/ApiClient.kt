package com.whatsappauto

import com.google.gson.Gson
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.concurrent.TimeUnit

object ApiClient {

    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .writeTimeout(10, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    private val gson = Gson()
    private val JSON = "application/json; charset=utf-8".toMediaType()

    data class MessageRequest(
        val message: String,
        val sender: String
    )

    data class MessageResponse(
        val response: String
    )

    fun sendMessage(serverUrl: String, message: String, sender: String): String {
        val requestData = MessageRequest(message, sender)
        val json = gson.toJson(requestData)

        val requestBody = json.toRequestBody(JSON)

        val request = Request.Builder()
            .url("$serverUrl/chat")
            .post(requestBody)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Unexpected code $response")

            val responseBody = response.body?.string() ?: throw IOException("Empty response")
            val messageResponse = gson.fromJson(responseBody, MessageResponse::class.java)

            return messageResponse.response
        }
    }
}
