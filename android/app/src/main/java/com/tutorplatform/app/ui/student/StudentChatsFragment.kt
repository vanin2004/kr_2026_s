package com.tutorplatform.app.ui.student

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.ProgressBar
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.tutorplatform.app.R
import com.tutorplatform.app.SessionManager
import com.tutorplatform.app.adapters.SimpleItemAdapter
import com.tutorplatform.app.model.SimpleItem
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.ui.ChatActivity
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class StudentChatsFragment : Fragment(R.layout.fragment_student_chats) {
    private lateinit var adapter: SimpleItemAdapter
    private lateinit var progress: ProgressBar

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        progress = view.findViewById(R.id.student_chats_progress)
        val list = view.findViewById<RecyclerView>(R.id.student_chats_list)
        list.layoutManager = LinearLayoutManager(requireContext())
        adapter = SimpleItemAdapter { item ->
            val intent = Intent(requireContext(), ChatActivity::class.java)
            intent.putExtra(ChatActivity.EXTRA_CHAT_ID, item.id)
            startActivity(intent)
        }
        list.adapter = adapter

        loadChats()
    }

    private fun loadChats() {
        progress.show(true)
        lifecycleScope.launch {
            try {
                val chats = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext()).getChats()
                }
                val myUserId = SessionManager(requireContext()).getUserId() ?: ""
                val items = mutableListOf<SimpleItem>()
                for (chat in chats) {
                    try {
                        val apps = withContext(Dispatchers.IO) {
                            ApiClient.dataService(requireContext()).getApplications()
                        }
                        val app = apps.find { it.id == chat.application_id }
                        if (app != null) {
                            val otherUserId = if (app.student_id == myUserId) app.tutor_id else app.student_id
                            val name: String
                            if (app.student_id == myUserId) {
                                val profile = withContext(Dispatchers.IO) {
                                    ApiClient.dataService(requireContext()).getTutorProfile(otherUserId)
                                }
                                name = profile.full_name
                            } else {
                                val profile = withContext(Dispatchers.IO) {
                                    ApiClient.dataService(requireContext()).getStudentProfile(otherUserId)
                                }
                                name = profile.full_name ?: otherUserId
                            }
                            items.add(SimpleItem(
                                id = chat.id,
                                title = name,
                                subtitle = "Статус: ${app.status}"
                            ))
                        } else {
                            items.add(SimpleItem(id = chat.id, title = "Чат", subtitle = chat.id.take(8)))
                        }
                    } catch (_: Exception) {
                        items.add(SimpleItem(id = chat.id, title = "Чат", subtitle = chat.id.take(8)))
                    }
                }
                adapter.submitList(items)
            } catch (ex: Exception) {
                requireContext().toast("Не удалось загрузить чаты: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }
}
