package com.tutorplatform.app.ui

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.tutorplatform.app.R
import com.tutorplatform.app.SessionManager
import com.tutorplatform.app.model.ApplicationCreate
import com.tutorplatform.app.model.LessonCreate
import com.tutorplatform.app.adapters.SimpleItemAdapter
import com.tutorplatform.app.model.SimpleItem
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.util.ApiFilters
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class TutorDetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_tutor_detail)

        val tutorId = intent.getStringExtra(EXTRA_TUTOR_ID)
        if (tutorId.isNullOrBlank()) {
            toast("Не найден идентификатор репетитора")
            finish()
            return
        }

        val nameView = findViewById<TextView>(R.id.tutor_detail_name)
        val subtitleView = findViewById<TextView>(R.id.tutor_detail_subtitle)
        val ratingView = findViewById<TextView>(R.id.tutor_detail_rating)
        val tagsView = findViewById<TextView>(R.id.tutor_detail_tags)
        val applyButton = findViewById<Button>(R.id.tutor_detail_apply)
        val progress = findViewById<ProgressBar>(R.id.tutor_detail_progress)

        val scheduleList = findViewById<RecyclerView>(R.id.tutor_detail_schedule_list)
        val scheduleAdapter = SimpleItemAdapter()
        scheduleList.layoutManager = LinearLayoutManager(this)
        scheduleList.adapter = scheduleAdapter

        val reviewsList = findViewById<RecyclerView>(R.id.tutor_detail_reviews_list)
        val reviewsAdapter = SimpleItemAdapter()
        reviewsList.layoutManager = LinearLayoutManager(this)
        reviewsList.adapter = reviewsAdapter

        val dateInput = findViewById<EditText>(R.id.tutor_detail_date)
        val startInput = findViewById<EditText>(R.id.tutor_detail_start)
        val endInput = findViewById<EditText>(R.id.tutor_detail_end)
        val bookButton = findViewById<Button>(R.id.tutor_detail_book)

        loadTutor(tutorId, nameView, subtitleView, ratingView)

        applyButton.setOnClickListener {
            val studentId = SessionManager(this).getUserId()
            if (studentId.isNullOrBlank()) {
                toast("Не найден идентификатор ученика")
                return@setOnClickListener
            }
            progress.show(true)
            lifecycleScope.launch {
                try {
                    withContext(Dispatchers.IO) {
                        ApiClient.dataService(this@TutorDetailActivity).createApplication(
                            ApplicationCreate(student_id = studentId, tutor_id = tutorId)
                        )
                    }
                    toast("Заявка отправлена")
                } catch (ex: Exception) {
                    toast("Не удалось отправить заявку: ${ex.message}")
                } finally {
                    progress.show(false)
                }
            }
        }

        bookButton.setOnClickListener {
            val studentId = SessionManager(this).getUserId()
            if (studentId.isNullOrBlank()) {
                toast("Не найден идентификатор ученика")
                return@setOnClickListener
            }
            val date = dateInput.text.toString().trim()
            val start = startInput.text.toString().trim()
            val end = endInput.text.toString().trim()
            if (date.isBlank() || start.isBlank() || end.isBlank()) {
                toast("Заполните дату и время")
                return@setOnClickListener
            }
            val startDateTime = "${date}T${start}:00"
            val endDateTime = "${date}T${end}:00"
            progress.show(true)
            lifecycleScope.launch {
                try {
                    withContext(Dispatchers.IO) {
                        ApiClient.dataService(this@TutorDetailActivity).createLesson(
                            LessonCreate(
                                student_id = studentId,
                                tutor_id = tutorId,
                                start_datetime = startDateTime,
                                end_datetime = endDateTime
                            )
                        )
                    }
                    toast("Урок забронирован")
                } catch (ex: Exception) {
                    toast("Не удалось забронировать урок: ${ex.message}")
                } finally {
                    progress.show(false)
                }
            }
        }

        tagsView.text = "Теги: данные будут доступны позже"

        loadSchedules(tutorId, scheduleAdapter)
        loadReviews(tutorId, reviewsAdapter)
    }

    private fun loadTutor(
        tutorId: String,
        nameView: TextView,
        subtitleView: TextView,
        ratingView: TextView
    ) {
        lifecycleScope.launch {
            try {
                val profiles = withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@TutorDetailActivity)
                        .getTutorProfiles(ApiFilters.eq(tutorId))
                }
                val profile = profiles.firstOrNull()
                if (profile != null) {
                    nameView.text = profile.full_name
                    subtitleView.text = listOfNotNull(
                        profile.specialization,
                        profile.hourly_rate?.let { "Ставка $it" },
                        profile.experience_years?.let { "Опыт $it" }
                    ).joinToString(" • ")
                    ratingView.text = "Рейтинг: ${profile.rating_overall ?: 0.0}"
                }
            } catch (ex: Exception) {
                toast("Не удалось загрузить данные: ${ex.message}")
            }
        }
    }

    private fun loadSchedules(tutorId: String, adapter: SimpleItemAdapter) {
        lifecycleScope.launch {
            try {
                val slots = withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@TutorDetailActivity)
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
                toast("Не удалось загрузить расписание: ${ex.message}")
            }
        }
    }

    private fun loadReviews(tutorId: String, adapter: SimpleItemAdapter) {
        lifecycleScope.launch {
            try {
                val reviews = withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@TutorDetailActivity)
                        .getReviews(ApiFilters.eq(tutorId))
                }
                val items = reviews.map { review ->
                    SimpleItem(
                        id = review.id,
                        title = "Оценка: ${review.communication_score}/5",
                        subtitle = review.text ?: "Без комментария"
                    )
                }
                adapter.submitList(items)
            } catch (ex: Exception) {
                toast("Не удалось загрузить отзывы: ${ex.message}")
            }
        }
    }

    companion object {
        const val EXTRA_TUTOR_ID = "extra_tutor_id"
    }
}
