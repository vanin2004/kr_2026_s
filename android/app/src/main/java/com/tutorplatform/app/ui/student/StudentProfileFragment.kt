package com.tutorplatform.app.ui.student

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
import com.tutorplatform.app.util.ApiFilters
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class StudentProfileFragment : Fragment(R.layout.fragment_student_profile) {
    private lateinit var nameInput: EditText
    private lateinit var progress: ProgressBar

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        nameInput = view.findViewById(R.id.student_profile_name)
        progress = view.findViewById(R.id.student_profile_progress)

        view.findViewById<Button>(R.id.student_profile_save).setOnClickListener { saveProfile() }
        view.findViewById<Button>(R.id.student_profile_logout).setOnClickListener { logout() }

        loadProfile()
    }

    private fun loadProfile() {
        val studentId = SessionManager(requireContext()).getUserId()
        if (studentId.isNullOrBlank()) {
            requireContext().toast("Не найден идентификатор ученика")
            return
        }

        progress.show(true)
        lifecycleScope.launch {
            try {
                val profiles = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext())
                        .getStudentProfiles(ApiFilters.eq(studentId))
                }
                val profile = profiles.firstOrNull()
                if (profile != null) {
                    nameInput.setText(profile.full_name)
                }
            } catch (ex: Exception) {
                requireContext().toast("Не удалось загрузить профиль: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }

    private fun saveProfile() {
        val studentId = SessionManager(requireContext()).getUserId()
        if (studentId.isNullOrBlank()) {
            requireContext().toast("Не найден идентификатор ученика")
            return
        }

        progress.show(true)
        lifecycleScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext()).updateStudentProfile(
                        ApiFilters.eq(studentId),
                        mapOf("full_name" to nameInput.text.toString().trim())
                    )
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
