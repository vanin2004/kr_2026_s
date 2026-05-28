package com.tutorplatform.app.ui.tutor

import android.os.Bundle
import android.view.View
import android.content.Intent
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.tutorplatform.app.R
import com.tutorplatform.app.SessionManager
import com.tutorplatform.app.adapters.SimpleItemAdapter
import com.tutorplatform.app.model.ScheduleSlotCreate
import com.tutorplatform.app.model.SimpleItem
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.ui.LessonDetailActivity
import com.tutorplatform.app.util.ApiFilters
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class TutorScheduleFragment : Fragment(R.layout.fragment_tutor_schedule) {
    private lateinit var adapter: SimpleItemAdapter
    private lateinit var lessonsAdapter: SimpleItemAdapter
    private lateinit var progress: ProgressBar
    private lateinit var lessonsProgress: ProgressBar

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        progress = view.findViewById(R.id.schedule_progress)
        lessonsProgress = view.findViewById(R.id.tutor_lessons_progress)
        val list = view.findViewById<RecyclerView>(R.id.schedule_list)
        list.layoutManager = LinearLayoutManager(requireContext())
        adapter = SimpleItemAdapter()
        list.adapter = adapter

        val lessonsList = view.findViewById<RecyclerView>(R.id.tutor_lessons_list)
        lessonsList.layoutManager = LinearLayoutManager(requireContext())
        lessonsAdapter = SimpleItemAdapter { item ->
            val intent = Intent(requireContext(), LessonDetailActivity::class.java)
            intent.putExtra(LessonDetailActivity.EXTRA_LESSON_ID, item.id)
            startActivity(intent)
        }
        lessonsList.adapter = lessonsAdapter

        val dayInput = view.findViewById<EditText>(R.id.schedule_day)
        val startInput = view.findViewById<EditText>(R.id.schedule_start)
        val endInput = view.findViewById<EditText>(R.id.schedule_end)
        view.findViewById<Button>(R.id.schedule_add).setOnClickListener {
            val tutorId = SessionManager(requireContext()).getUserId()
            if (tutorId.isNullOrBlank()) {
                requireContext().toast("Не найден идентификатор репетитора")
                return@setOnClickListener
            }
            val day = dayInput.text.toString().toIntOrNull()
            val start = startInput.text.toString().trim()
            val end = endInput.text.toString().trim()
            if (day == null || start.isBlank() || end.isBlank()) {
                requireContext().toast("Заполните все поля")
                return@setOnClickListener
            }
            addSlot(tutorId, day, start, end)
        }

        loadSchedules()
        loadLessons()
    }

    override fun onResume() {
        super.onResume()
        loadLessons()
    }

    private fun loadSchedules() {
        val tutorId = SessionManager(requireContext()).getUserId()
        if (tutorId.isNullOrBlank()) {
            requireContext().toast("Не найден идентификатор репетитора")
            return
        }

        progress.show(true)
        lifecycleScope.launch {
            try {
                val slots = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext())
                        .getSchedules(ApiFilters.eq(tutorId))
                }
                val items = slots.map { slot ->
                    SimpleItem(
                        id = slot.id.toString(),
                        title = "День ${slot.day_of_week}",
                        subtitle = "${slot.start_time} - ${slot.end_time}"
                    )
                }
                adapter.submitList(items)
            } catch (ex: Exception) {
                requireContext().toast("Не удалось загрузить расписание: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }

    private fun loadLessons() {
        lessonsProgress.show(true)
        lifecycleScope.launch {
            try {
                val lessons = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext()).getLessons()
                }
                val items = lessons.filter { it.status == "planned" }.map { lesson ->
                    SimpleItem(
                        id = lesson.id,
                        title = "Урок ${lesson.id.take(8)}",
                        subtitle = "${lesson.start_datetime} • ${mapStatus(lesson.status)}"
                    )
                }
                lessonsAdapter.submitList(items)
            } catch (ex: Exception) {
                requireContext().toast("Не удалось загрузить уроки: ${ex.message}")
            } finally {
                lessonsProgress.show(false)
            }
        }
    }

    private fun addSlot(tutorId: String, day: Int, start: String, end: String) {
        progress.show(true)
        lifecycleScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext()).addSchedule(
                        ScheduleSlotCreate(
                            tutor_id = tutorId,
                            day_of_week = day,
                            start_time = start,
                            end_time = end
                        )
                    )
                }
                loadSchedules()
                loadLessons()
            } catch (ex: Exception) {
                requireContext().toast("Не удалось добавить слот: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }

    private fun mapStatus(status: String): String {
        return when (status) {
            "planned" -> "Запланирован"
            "completed" -> "Проведен"
            "cancelled" -> "Отменен"
            else -> status
        }
    }
}
