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
import com.tutorplatform.app.adapters.ApplicationAdapter
import com.tutorplatform.app.model.Application
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class TutorRequestsFragment : Fragment(R.layout.fragment_tutor_requests) {
    private lateinit var adapter: ApplicationAdapter
    private lateinit var progress: ProgressBar

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        progress = view.findViewById(R.id.requests_progress)
        val list = view.findViewById<RecyclerView>(R.id.requests_list)
        list.layoutManager = LinearLayoutManager(requireContext())
        adapter = ApplicationAdapter(
            onAccept = { updateStatus(it, "accepted") },
            onReject = { updateStatus(it, "rejected") }
        )
        list.adapter = adapter

        loadRequests()
    }

    private fun loadRequests() {
        val tutorId = SessionManager(requireContext()).getUserId()
        if (tutorId.isNullOrBlank()) {
            requireContext().toast("Не найден идентификатор репетитора")
            return
        }

        progress.show(true)
        lifecycleScope.launch {
            try {
                val apps = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext())
                        .getApplications(tutorId = tutorId)
                }
                val studentNames = mutableMapOf<String, String>()
                for (app in apps) {
                    if (app.student_id !in studentNames) {
                        try {
                            val profile = withContext(Dispatchers.IO) {
                                ApiClient.dataService(requireContext()).getStudentProfile(app.student_id)
                            }
                            studentNames[app.student_id] = profile.full_name ?: app.student_id
                        } catch (_: Exception) {
                            studentNames[app.student_id] = app.student_id
                        }
                    }
                }
                adapter.setStudentNames(studentNames)
                adapter.submitList(apps)
            } catch (ex: Exception) {
                requireContext().toast("Не удалось загрузить заявки: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }

    private fun updateStatus(application: Application, status: String) {
        progress.show(true)
        lifecycleScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext()).updateApplication(
                        application.id,
                        mapOf("status" to status)
                    )
                }
                loadRequests()
            } catch (ex: Exception) {
                requireContext().toast("Не удалось обновить заявку: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }
}
