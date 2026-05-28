package com.tutorplatform.app.ui.student

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.ProgressBar
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.tutorplatform.app.R
import com.tutorplatform.app.SessionManager
import com.tutorplatform.app.adapters.SimpleItemAdapter
import com.tutorplatform.app.model.SimpleItem
import com.tutorplatform.app.model.TestLibrary
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.ui.TestActivity
import com.tutorplatform.app.util.ApiFilters
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class StudentProgressFragment : Fragment(R.layout.fragment_student_progress) {
    private lateinit var resultsAdapter: SimpleItemAdapter
    private lateinit var testsAdapter: SimpleItemAdapter
    private lateinit var resultsProgress: ProgressBar
    private lateinit var testsProgress: ProgressBar
    private var activeTutorId: String? = null
    private var testsMap: Map<String, TestLibrary> = emptyMap()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        resultsProgress = view.findViewById(R.id.student_results_progress)
        testsProgress = view.findViewById(R.id.student_tests_progress)

        val resultsList = view.findViewById<RecyclerView>(R.id.student_results_list)
        resultsList.layoutManager = LinearLayoutManager(requireContext())
        resultsAdapter = SimpleItemAdapter()
        resultsList.adapter = resultsAdapter

        val testsList = view.findViewById<RecyclerView>(R.id.student_tests_list)
        testsList.layoutManager = LinearLayoutManager(requireContext())
        testsAdapter = SimpleItemAdapter { item ->
            val test = testsMap[item.id]
            if (test == null) {
                requireContext().toast("Тест не найден")
            } else {
                openTestTypeDialog(test)
            }
        }
        testsList.adapter = testsAdapter

        loadActiveTutor()
        loadResults()
        loadTests()
    }

    override fun onResume() {
        super.onResume()
        loadActiveTutor()
        loadResults()
    }

    private fun loadResults() {
        val studentId = SessionManager(requireContext()).getUserId()
        if (studentId.isNullOrBlank()) {
            requireContext().toast("Не найден идентификатор ученика")
            return
        }

        resultsProgress.show(true)
        lifecycleScope.launch {
            try {
                val results = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext())
                        .getStudentResults(ApiFilters.eq(studentId))
                }
                val items = results.map { result ->
                    val scoreText = result.score?.toString() ?: "в процессе"
                    SimpleItem(
                        id = result.id,
                        title = "Тест ${result.test_id} (${mapTestType(result.type)})",
                        subtitle = "Результат: $scoreText"
                    )
                }
                resultsAdapter.submitList(items)
            } catch (ex: Exception) {
                requireContext().toast("Не удалось загрузить результаты: ${ex.message}")
            } finally {
                resultsProgress.show(false)
            }
        }
    }

    private fun loadTests() {
        testsProgress.show(true)
        lifecycleScope.launch {
            try {
                val tests = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext()).getTestLibrary()
                }
                testsMap = tests.associateBy { it.id.toString() }
                val items = tests.map { test ->
                    SimpleItem(
                        id = test.id.toString(),
                        title = "${test.subject} • ${test.topic}",
                        subtitle = "Тест №${test.id}"
                    )
                }
                testsAdapter.submitList(items)
            } catch (ex: Exception) {
                requireContext().toast("Не удалось загрузить тесты: ${ex.message}")
            } finally {
                testsProgress.show(false)
            }
        }
    }

    private fun loadActiveTutor() {
        val studentId = SessionManager(requireContext()).getUserId()
        if (studentId.isNullOrBlank()) return

        lifecycleScope.launch {
            try {
                val apps = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext()).getApplications(
                        studentIdFilter = ApiFilters.eq(studentId),
                        statusFilter = ApiFilters.eq("accepted")
                    )
                }
                activeTutorId = apps.firstOrNull()?.tutor_id
            } catch (_: Exception) {
                activeTutorId = null
            }
        }
    }

    private fun openTestTypeDialog(test: TestLibrary) {
        val studentId = SessionManager(requireContext()).getUserId()
        val tutorId = activeTutorId
        if (studentId.isNullOrBlank() || tutorId.isNullOrBlank()) {
            requireContext().toast("Нет активного репетитора для назначения теста")
            return
        }

        AlertDialog.Builder(requireContext())
            .setTitle("Выберите тип теста")
            .setItems(arrayOf("Вводный", "Контрольный")) { _, which ->
                val type = if (which == 0) "initial_test" else "control_test"
                openTest(test, studentId, tutorId, type)
            }
            .show()
    }

    private fun openTest(test: TestLibrary, studentId: String, tutorId: String, type: String) {
        val intent = Intent(requireContext(), TestActivity::class.java)
        intent.putExtra(TestActivity.EXTRA_TEST_ID, test.id)
        intent.putExtra(TestActivity.EXTRA_QUESTIONS_JSON, test.questions_json)
        intent.putExtra(TestActivity.EXTRA_STUDENT_ID, studentId)
        intent.putExtra(TestActivity.EXTRA_TUTOR_ID, tutorId)
        intent.putExtra(TestActivity.EXTRA_TEST_TYPE, type)
        startActivity(intent)
    }

    private fun mapTestType(type: String): String {
        return when (type) {
            "initial_test" -> "вводный"
            "control_test" -> "контрольный"
            else -> type
        }
    }
}
