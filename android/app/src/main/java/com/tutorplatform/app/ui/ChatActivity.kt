package com.tutorplatform.app.ui

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.tutorplatform.app.R
import com.tutorplatform.app.SessionManager
import com.tutorplatform.app.adapters.MessageAdapter
import com.tutorplatform.app.model.MessageCreate
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class ChatActivity : AppCompatActivity() {
    private lateinit var adapter: MessageAdapter
    private lateinit var chatId: String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)

        chatId = intent.getStringExtra(EXTRA_CHAT_ID).orEmpty()
        if (chatId.isBlank()) {
            toast("Не найден идентификатор чата")
            finish()
            return
        }

        val list = findViewById<RecyclerView>(R.id.chat_messages)
        list.layoutManager = LinearLayoutManager(this)
        adapter = MessageAdapter()
        list.adapter = adapter

        val input = findViewById<EditText>(R.id.chat_input)
        val send = findViewById<Button>(R.id.chat_send)

        send.setOnClickListener {
            val text = input.text.toString().trim()
            if (text.isBlank()) return@setOnClickListener
            val senderId = SessionManager(this).getUserId() ?: ""
            sendMessage(senderId, text)
            input.setText("")
        }

        loadMessages()
    }

    private fun loadMessages() {
        lifecycleScope.launch {
            try {
                val messages = withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@ChatActivity).getMessages(chatId)
                }
                adapter.submitList(messages)
            } catch (ex: Exception) {
                toast("Не удалось загрузить сообщения: ${ex.message}")
            }
        }
    }

    private fun sendMessage(senderId: String, text: String) {
        lifecycleScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@ChatActivity).sendMessage(
                        MessageCreate(chat_id = chatId, sender_id = senderId, text = text)
                    )
                }
                loadMessages()
            } catch (ex: Exception) {
                toast("Не удалось отправить сообщение: ${ex.message}")
            }
        }
    }

    companion object {
        const val EXTRA_CHAT_ID = "extra_chat_id"
    }
}
