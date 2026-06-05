package com.tutorplatform.app.ui.tutor

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
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class TutorStudentsFragment : Fragment(R.layout.fragment_tutor_students) {
    private lateinit var adapter: SimpleItemAdapter
    private lateinit var progress: ProgressBar

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        progress = view.findViewById(R.id.students_progress)
        val list = view.findViewById<RecyclerView>(R.id.students_list)
        list.layoutManager = LinearLayoutManager(requireContext())
        adapter = SimpleItemAdapter()
        list.adapter = adapter

        loadStudents()
    }

    private fun loadStudents() {
        val tutorId = SessionManager(requireContext()).getUserId()
        if (tutorId.isNullOrBlank()) {
            requireContext().toast("Не найден идентификатор репетитора")
            return
        }

        progress.show(true)
        lifecycleScope.launch {
            try {
                val apps = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext()).getApplications(
                        tutorId = tutorId
                    ).filter { it.status == "accepted" }
                }
                val items = apps.map { app ->
                    val name = try {
                        val profile = withContext(Dispatchers.IO) {
                            ApiClient.dataService(requireContext()).getStudentProfile(app.student_id)
                        }
                        profile.full_name ?: app.student_id
                    } catch (_: Exception) {
                        app.student_id
                    }
                    SimpleItem(
                        id = app.id,
                        title = name,
                        subtitle = "Статус: ${mapStatus(app.status)}"
                    )
                }
                adapter.submitList(items)
            } catch (ex: Exception) {
                requireContext().toast("Не удалось загрузить учеников: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }

    private fun mapStatus(status: String): String {
        return when (status) {
            "pending" -> "ожидает"
            "accepted" -> "принята"
            "rejected" -> "отклонена"
            else -> status
        }
    }
}
