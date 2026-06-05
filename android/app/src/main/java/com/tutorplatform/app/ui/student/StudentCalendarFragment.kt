package com.tutorplatform.app.ui.student

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.CalendarView
import android.widget.ProgressBar
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.tutorplatform.app.R
import com.tutorplatform.app.SessionManager
import com.tutorplatform.app.adapters.LessonAdapter
import com.tutorplatform.app.model.Lesson
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.ui.LessonDetailActivity
import com.tutorplatform.app.util.LessonColorManager
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.ZoneId
import java.time.ZonedDateTime

class StudentCalendarFragment : Fragment(R.layout.fragment_student_calendar) {
    private lateinit var adapter: LessonAdapter
    private lateinit var progress: ProgressBar
    private lateinit var calendarView: CalendarView
    private lateinit var colorManager: LessonColorManager
    private var allLessons = listOf<Lesson>()
    private var tutorNameMap = mapOf<String, String>()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        colorManager = LessonColorManager(requireContext())
        progress = view.findViewById(R.id.student_lessons_progress)
        calendarView = view.findViewById(R.id.student_calendar_view)

        val list = view.findViewById<RecyclerView>(R.id.student_lessons_list)
        list.layoutManager = LinearLayoutManager(requireContext())
        adapter = LessonAdapter { lessonId ->
            val intent = Intent(requireContext(), LessonDetailActivity::class.java)
            intent.putExtra(LessonDetailActivity.EXTRA_LESSON_ID, lessonId)
            startActivity(intent)
        }
        list.adapter = adapter

        calendarView.setOnDateChangeListener { _, year, month, dayOfMonth ->
            filterLessonsByDate(year, month, dayOfMonth)
        }

        loadLessons()
    }

    override fun onResume() {
        super.onResume()
        loadLessons()
    }

    private fun loadLessons() {
        val studentId = SessionManager(requireContext()).getUserId()
        progress.show(true)
        lifecycleScope.launch {
            try {
                val lessons = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext()).getLessons(studentId = studentId)
                }
                allLessons = lessons

                // Загружаем имена преподавателей
                val tutorIds = lessons.map { it.tutor_id }.distinct()
                val names = mutableMapOf<String, String>()
                for (tid in tutorIds) {
                    try {
                        val profile = withContext(Dispatchers.IO) {
                            ApiClient.dataService(requireContext()).getTutorProfile(tid)
                        }
                        names[tid] = profile.full_name
                    } catch (_: Exception) {
                        names[tid] = tid.take(8)
                    }
                }
                tutorNameMap = names

                showLessons(lessons)
            } catch (ex: Exception) {
                requireContext().toast("Не удалось загрузить уроки: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }

    private fun showLessons(lessons: List<Lesson>) {
        val now = ZonedDateTime.now(ZoneId.systemDefault())

        val future = mutableListOf<LessonAdapter.LessonDisplay>()
        val past = mutableListOf<LessonAdapter.LessonDisplay>()

        for (lesson in lessons) {
            val startZdt = try {
                val cleaned = lesson.start_datetime
                    .replace("Z", "")
                    .substringBefore("+")
                    .take(19)
                val dt = java.time.LocalDateTime.parse(cleaned, java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss"))
                dt.atZone(ZoneId.systemDefault())
            } catch (_: Exception) { continue }
            val isFuture = startZdt.isAfter(now)

            val display = LessonAdapter.LessonDisplay(
                lessonId = lesson.id,
                tutorName = formatTutorName(tutorNameMap[lesson.tutor_id] ?: lesson.tutor_id),
                tutorColor = colorManager.getColor(lesson.tutor_id),
                startDatetime = lesson.start_datetime,
                endDatetime = lesson.end_datetime,
                status = lesson.status
            )

            if (isFuture) future.add(display) else past.add(display)
        }

        // будущие — от ближайшего
        future.sortBy { it.startDatetime }
        // прошедшие — от ближайшего прошедшего (сначала свежие)
        past.sortByDescending { it.startDatetime }

        adapter.submitList(future, past)
    }

    private fun filterLessonsByDate(year: Int, month: Int, dayOfMonth: Int) {
        val selectedDate = ZonedDateTime.of(year, month + 1, dayOfMonth, 0, 0, 0, 0, ZoneId.systemDefault())
        val nextDay = selectedDate.plusDays(1)

        val filtered = allLessons.filter { lesson ->
            try {
                val cleaned = lesson.start_datetime
                    .replace("Z", "")
                    .substringBefore("+")
                    .take(19)
                val dt = java.time.LocalDateTime.parse(cleaned, java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss"))
                dt.toLocalDate() == selectedDate.toLocalDate()
            } catch (_: Exception) { false }
        }

        if (filtered.isEmpty()) {
            // показать все
            showLessons(allLessons)
        } else {
            showLessons(filtered)
        }
    }

    private fun formatTutorName(fullName: String): String {
        val parts = fullName.trim().split("\\s+".toRegex())
        if (parts.size < 2) return fullName
        val surname = parts[0]
        val initials = parts.drop(1).joinToString("") { "${it.first()}." }
        return "$surname $initials"
    }
}
