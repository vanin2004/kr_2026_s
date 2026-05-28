package com.tutorplatform.app.ui.tutor

import android.os.Bundle
import android.view.View
import android.widget.ProgressBar
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.tutorplatform.app.R
import com.tutorplatform.app.SessionManager
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.util.ApiFilters
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class TutorDashboardFragment : Fragment(R.layout.fragment_tutor_dashboard) {
    private lateinit var progress: ProgressBar

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        progress = view.findViewById(R.id.tutor_dashboard_progress)
        loadProfile(view)
    }

    private fun loadProfile(view: View) {
        val tutorId = SessionManager(requireContext()).getUserId()
        if (tutorId.isNullOrBlank()) {
            requireContext().toast("Не найден идентификатор репетитора")
            return
        }

        val ratingView = view.findViewById<TextView>(R.id.tutor_dashboard_rating)
        val efficiencyView = view.findViewById<TextView>(R.id.tutor_dashboard_efficiency)
        val communicationView = view.findViewById<TextView>(R.id.tutor_dashboard_communication)
        val studentsView = view.findViewById<TextView>(R.id.tutor_dashboard_students)

        progress.show(true)
        lifecycleScope.launch {
            try {
                val profiles = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext())
                        .getTutorProfiles(ApiFilters.eq(tutorId))
                }
                val profile = profiles.firstOrNull()
                if (profile != null) {
                    ratingView.text = "Общий рейтинг: ${profile.rating_overall ?: 0.0}"
                    efficiencyView.text = "Эффективность: ${profile.rating_efficiency ?: 0.0}"
                    communicationView.text = "Коммуникация: ${profile.rating_communication ?: 0.0}"
                    studentsView.text = "Активные ученики: ${profile.student_count ?: 0}"
                }
            } catch (ex: Exception) {
                requireContext().toast("Не удалось загрузить профиль: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }
}
