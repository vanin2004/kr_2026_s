package com.tutorplatform.app.ui.tutor

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.tutorplatform.app.R
import com.tutorplatform.app.SessionManager
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.ui.LoginActivity
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class TutorProfileFragment : Fragment(R.layout.fragment_tutor_profile) {
    private lateinit var nameInput: EditText
    private lateinit var subjectInput: EditText
    private lateinit var educationInput: EditText
    private lateinit var rateInput: EditText
    private lateinit var expInput: EditText
    private lateinit var progress: ProgressBar
    private var subjectNameMap: Map<String, String> = emptyMap()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        nameInput = view.findViewById(R.id.tutor_profile_name)
        subjectInput = view.findViewById(R.id.tutor_profile_subject)
        educationInput = view.findViewById(R.id.tutor_profile_education)
        rateInput = view.findViewById(R.id.tutor_profile_rate)
        expInput = view.findViewById(R.id.tutor_profile_experience)
        progress = view.findViewById(R.id.tutor_profile_progress)

        view.findViewById<Button>(R.id.tutor_profile_save).setOnClickListener { saveProfile() }
        view.findViewById<Button>(R.id.tutor_profile_logout).setOnClickListener { logout() }

        lifecycleScope.launch {
            val subjects = withContext(Dispatchers.IO) {
                ApiClient.dataService(requireContext()).getSubjects(limit = 100)
            }
            subjectNameMap = subjects.associate { it.id to it.name }
            loadProfile()
        }
    }

    private fun loadProfile() {
        val tutorId = SessionManager(requireContext()).getUserId()
        if (tutorId.isNullOrBlank()) {
            requireContext().toast("Не найден идентификатор репетитора")
            return
        }

        progress.show(true)
        lifecycleScope.launch {
            try {
                val profile = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext())
                        .getTutorProfile(tutorId)
                }
                nameInput.setText(profile.full_name)
                subjectInput.setText(subjectNameMap[profile.subject_id] ?: profile.subject_id ?: "")
                educationInput.setText(profile.education ?: "")
                rateInput.setText(profile.hourly_rate?.toString() ?: "")
                expInput.setText(profile.experience_years?.toString() ?: "")
            } catch (ex: Exception) {
                requireContext().toast("Не удалось загрузить профиль: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }

    private fun saveProfile() {
        val tutorId = SessionManager(requireContext()).getUserId()
        if (tutorId.isNullOrBlank()) {
            requireContext().toast("Не найден идентификатор репетитора")
            return
        }

        val patch = mapOf(
            "full_name" to nameInput.text.toString().trim(),
            "subject_id" to subjectInput.text.toString().trim().ifBlank { null },
            "education" to educationInput.text.toString().trim(),
            "hourly_rate" to rateInput.text.toString().trim().toIntOrNull(),
            "experience_years" to expInput.text.toString().trim().toIntOrNull()
        )

        progress.show(true)
        lifecycleScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext())
                        .updateTutorProfile(tutorId, patch)
                }
                requireContext().toast("Профиль сохранен")
            } catch (ex: Exception) {
                requireContext().toast("Не удалось сохранить профиль: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }

    private fun logout() {
        SessionManager(requireContext()).clearSession()
        startActivity(Intent(requireContext(), LoginActivity::class.java))
        requireActivity().finish()
    }
}
