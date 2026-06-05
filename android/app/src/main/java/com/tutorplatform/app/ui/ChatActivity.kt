package com.tutorplatform.app.ui

import android.os.Build
import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
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
    private var otherUserId: String = ""
    private var otherUserName: String = ""
    private var tutorId: String = ""
    private var tutorProfileCached: com.tutorplatform.app.model.TutorProfile? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 35) { enableEdgeToEdge() }
        setContentView(R.layout.activity_chat)

        // Настройка Toolbar
        val toolbar = findViewById<Toolbar>(R.id.chat_toolbar)
        setSupportActionBar(toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Чат"

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

        loadOtherParticipant()
        loadMessages()
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }

    private fun loadOtherParticipant() {
        lifecycleScope.launch {
            try {
                val chats = withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@ChatActivity).getChats()
                }
                val chat = chats.find { it.id == chatId } ?: return@launch
                val applicationId = chat.application_id

                val applications = withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@ChatActivity).getApplications()
                }
                val application = applications.find { it.id == applicationId } ?: return@launch

                val myUserId = SessionManager(this@ChatActivity).getUserId() ?: return@launch

                if (myUserId == application.student_id) {
                    val tutorProfile = withContext(Dispatchers.IO) {
                        ApiClient.dataService(this@ChatActivity).getTutorProfile(application.tutor_id)
                    }
                    otherUserId = application.tutor_id
                    otherUserName = tutorProfile.full_name
                    tutorId = application.tutor_id
                    tutorProfileCached = tutorProfile
                } else if (myUserId == application.tutor_id) {
                    val studentProfile = withContext(Dispatchers.IO) {
                        ApiClient.dataService(this@ChatActivity).getStudentProfile(application.student_id)
                    }
                    otherUserId = application.student_id
                    otherUserName = studentProfile.full_name ?: ""
                    tutorId = application.tutor_id
                }

                // Загружаем предмет репетитора для подзаголовка
                val actualTutorProfile = tutorProfileCached
                    ?: withContext(Dispatchers.IO) {
                        ApiClient.dataService(this@ChatActivity).getTutorProfile(tutorId)
                    }
                var subjectName = ""
                if (actualTutorProfile.subject_id != null) {
                    val subjects = withContext(Dispatchers.IO) {
                        ApiClient.dataService(this@ChatActivity).getSubjects(limit = 100)
                    }
                    subjectName = subjects.find { it.id == actualTutorProfile.subject_id }?.name ?: ""
                }

                // Заполняем Toolbar
                supportActionBar?.title = otherUserName
                supportActionBar?.subtitle = subjectName.takeIf { it.isNotBlank() }

            } catch (_: Exception) {
                supportActionBar?.title = "Чат"
            }
        }
    }

    private fun loadMessages() {
        lifecycleScope.launch {
            try {
                val messages = withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@ChatActivity).getMessages(chatId)
                }
                adapter.submitList(messages)
                adapter.setParticipants(
                    myUserId = SessionManager(this@ChatActivity).getUserId() ?: "",
                    otherUserId = otherUserId,
                    otherUserName = otherUserName
                )
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
