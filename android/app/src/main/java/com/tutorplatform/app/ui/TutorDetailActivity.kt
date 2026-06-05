package com.tutorplatform.app.ui

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import android.os.Build
import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import android.widget.Button
import android.widget.ProgressBar
import android.widget.TextView
import com.google.android.material.button.MaterialButton
import java.util.Calendar
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
import com.tutorplatform.app.model.TutorProfile
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class TutorDetailActivity : AppCompatActivity() {
    private var subjectNameMap: Map<String, String> = emptyMap()
    private var tagNameMap: Map<String, String> = emptyMap()
    private val dayNames = listOf("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 35) { enableEdgeToEdge() }
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

        val dateBtn = findViewById<MaterialButton>(R.id.tutor_detail_date_btn)
        val startBtn = findViewById<MaterialButton>(R.id.tutor_detail_start_btn)
        val endBtn = findViewById<MaterialButton>(R.id.tutor_detail_end_btn)
        val bookButton = findViewById<Button>(R.id.tutor_detail_book)

        // views для метрик
        val ratingEff = findViewById<TextView>(R.id.tutor_detail_rating_eff)
        val ratingComm = findViewById<TextView>(R.id.tutor_detail_rating_comm)
        val ratingExp = findViewById<TextView>(R.id.tutor_detail_rating_exp)
        val ratingResp = findViewById<TextView>(R.id.tutor_detail_rating_resp)
        val educationView = findViewById<TextView>(R.id.tutor_detail_education)
        val studentsView = findViewById<TextView>(R.id.tutor_detail_students)
        val verifiedView = findViewById<TextView>(R.id.tutor_detail_verified)
        val newBadge = findViewById<TextView>(R.id.tutor_detail_new_badge)

        var selectedDate: String? = null
        var selectedStart: String? = null
        var selectedEnd: String? = null

        dateBtn.setOnClickListener {
            val now = Calendar.getInstance()
            DatePickerDialog(
                this,
                { _, year, month, dayOfMonth ->
                    val date = "%04d-%02d-%02d".format(year, month + 1, dayOfMonth)
                    selectedDate = date
                    dateBtn.text = date
                },
                now.get(Calendar.YEAR),
                now.get(Calendar.MONTH),
                now.get(Calendar.DAY_OF_MONTH)
            ).show()
        }

        startBtn.setOnClickListener {
            val now = Calendar.getInstance()
            TimePickerDialog(
                this,
                { _, hour, minute ->
                    val time = "%02d:%02d".format(hour, minute)
                    selectedStart = time
                    startBtn.text = time
                },
                now.get(Calendar.HOUR_OF_DAY),
                now.get(Calendar.MINUTE),
                true
            ).show()
        }

        endBtn.setOnClickListener {
            val now = Calendar.getInstance()
            TimePickerDialog(
                this,
                { _, hour, minute ->
                    val time = "%02d:%02d".format(hour, minute)
                    selectedEnd = time
                    endBtn.text = time
                },
                now.get(Calendar.HOUR_OF_DAY),
                now.get(Calendar.MINUTE),
                true
            ).show()
        }

        // Загружаем справочники (предметы + теги) параллельно
        lifecycleScope.launch {
            val subjects = withContext(Dispatchers.IO) {
                ApiClient.dataService(this@TutorDetailActivity).getSubjects(limit = 100)
            }
            subjectNameMap = subjects.associate { it.id to it.name }

            val tags = withContext(Dispatchers.IO) {
                ApiClient.dataService(this@TutorDetailActivity).getTags(limit = 100)
            }
            tagNameMap = tags.associate { it.id to it.name }

            loadTutor(
                tutorId, nameView, subtitleView, ratingView,
                ratingEff, ratingComm, ratingExp, ratingResp,
                educationView, studentsView, verifiedView, newBadge,
                tagsView
            )
        }

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
            val date = selectedDate
            val start = selectedStart
            val end = selectedEnd
            if (date.isNullOrBlank() || start.isNullOrBlank() || end.isNullOrBlank()) {
                toast("Выберите дату и время")
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

        loadSchedules(tutorId, scheduleAdapter)
        loadReviews(tutorId, reviewsAdapter)
    }

    private fun loadTutor(
        tutorId: String,
        nameView: TextView,
        subtitleView: TextView,
        ratingView: TextView,
        ratingEff: TextView,
        ratingComm: TextView,
        ratingExp: TextView,
        ratingResp: TextView,
        educationView: TextView,
        studentsView: TextView,
        verifiedView: TextView,
        newBadge: TextView,
        tagsView: TextView
    ) {
        lifecycleScope.launch {
            try {
                val profile = withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@TutorDetailActivity)
                        .getTutorProfile(tutorId)
                }

                // имя
                nameView.text = profile.full_name

                // подзаголовок: предмет • ставка • опыт
                val subjectLabel = profile.subject_id?.let { id ->
                    "Предмет ${subjectNameMap[id] ?: id}"
                }
                subtitleView.text = listOfNotNull(
                    subjectLabel,
                    profile.hourly_rate?.let { "Ставка $it ₽" },
                    profile.experience_years?.let { "Опыт $it лет" },
                    profile.student_count?.let { "Учеников: $it" }
                ).joinToString(" • ")

                // средний рейтинг
                val ratings = listOfNotNull(
                    profile.rating_efficiency,
                    profile.rating_communication,
                    profile.rating_expertise,
                    profile.rating_responsiveness
                )
                val avg = if (ratings.isNotEmpty()) ratings.average() else 0.0
                ratingView.text = "Средний рейтинг: ${"%.0f%%".format(avg * 100)}"

                // детальные рейтинги
                ratingEff.text = "Эффективность: ${formatRating(profile.rating_efficiency)}"
                ratingComm.text = "Общение: ${formatRating(profile.rating_communication)}"
                ratingExp.text = "Экспертиза: ${formatRating(profile.rating_expertise)}"
                ratingResp.text = "Отзывчивость: ${formatRating(profile.rating_responsiveness)}"

                // образование
                if (!profile.education.isNullOrBlank()) {
                    educationView.text = "🎓 ${profile.education}"
                    educationView.visibility = android.view.View.VISIBLE
                }

                // ученики
                studentsView.text = profile.student_count?.let { "👨‍🎓 Учеников: $it" } ?: "👨‍🎓 Учеников: 0"

                // верификация
                if (profile.is_verified == true) {
                    verifiedView.text = "✅ Верифицирован"
                    verifiedView.visibility = android.view.View.VISIBLE
                }

                // новичок
                if (profile.is_new_boost == true) {
                    newBadge.text = "⭐ Новый репетитор (повышение в поиске)"
                    newBadge.visibility = android.view.View.VISIBLE
                }

                // теги
                loadTutorTags(tutorId, tagsView)

            } catch (ex: Exception) {
                toast("Не удалось загрузить данные: ${ex.message}")
            }
        }
    }

    private suspend fun loadTutorTags(tutorId: String, tagsView: TextView) {
        try {
            val tutorTags = withContext(Dispatchers.IO) {
                ApiClient.dataService(this@TutorDetailActivity).getTutorTags(tutorId)
            }
            if (tutorTags.isNotEmpty()) {
                val tagNames = tutorTags.mapNotNull { tt ->
                    tagNameMap[tt.tag_id]
                }
                if (tagNames.isNotEmpty()) {
                    tagsView.text = "🏷️ Теги: ${tagNames.joinToString(", ")}"
                    tagsView.visibility = android.view.View.VISIBLE
                }
            }
        } catch (_: Exception) {
            // игнорируем ошибку загрузки тегов
        }
    }

    private fun formatRating(value: Double?): String {
        return if (value != null) "%.0f%%".format(value * 100) else "—"
    }

    private fun loadSchedules(tutorId: String, adapter: SimpleItemAdapter) {
        lifecycleScope.launch {
            try {
                val slots = withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@TutorDetailActivity)
                        .getSchedules(tutorId)
                }
                val items = slots.map { slot ->
                    SimpleItem(
                        id = slot.id.toString(),
                        title = dayNames.getOrElse(slot.day_of_week?.minus(1) ?: -1) { "День ${slot.day_of_week}" },
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
                        .getReviews(tutorId)
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
