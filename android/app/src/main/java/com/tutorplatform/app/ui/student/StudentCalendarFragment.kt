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
import com.tutorplatform.app.adapters.SimpleItemAdapter
import com.tutorplatform.app.model.SimpleItem
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.ui.LessonDetailActivity
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class StudentCalendarFragment : Fragment(R.layout.fragment_student_calendar) {
    private lateinit var adapter: SimpleItemAdapter
    private lateinit var progress: ProgressBar

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        progress = view.findViewById(R.id.student_lessons_progress)
        val list = view.findViewById<RecyclerView>(R.id.student_lessons_list)
        list.layoutManager = LinearLayoutManager(requireContext())
        adapter = SimpleItemAdapter { item ->
            val intent = Intent(requireContext(), LessonDetailActivity::class.java)
            intent.putExtra(LessonDetailActivity.EXTRA_LESSON_ID, item.id)
            startActivity(intent)
        }
        list.adapter = adapter

        loadLessons()
    }

    override fun onResume() {
        super.onResume()
        loadLessons()
    }

    private fun loadLessons() {
        progress.show(true)
        lifecycleScope.launch {
            try {
                val lessons = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext()).getLessons()
                }
                val items = lessons.map { lesson ->
                    SimpleItem(
                        id = lesson.id,
                        title = "Урок ${lesson.id.take(8)}",
                        subtitle = "${lesson.start_datetime} • ${mapStatus(lesson.status)}"
                    )
                }
                adapter.submitList(items)
            } catch (ex: Exception) {
                requireContext().toast("Не удалось загрузить уроки: ${ex.message}")
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
