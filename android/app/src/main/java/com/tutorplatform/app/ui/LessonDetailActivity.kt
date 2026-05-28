package com.tutorplatform.app.ui

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.tutorplatform.app.R
import com.tutorplatform.app.SessionManager
import com.tutorplatform.app.model.Lesson
import com.tutorplatform.app.model.ReviewCreate
import com.tutorplatform.app.UserRole
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.util.ApiFilters
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class LessonDetailActivity : AppCompatActivity() {
    private lateinit var lessonId: String
    private lateinit var titleView: TextView
    private lateinit var timeView: TextView
    private lateinit var statusView: TextView
    private lateinit var linkInput: EditText
    private lateinit var progress: ProgressBar
    private lateinit var reviewBlock: View
    private lateinit var reviewScore: EditText
    private lateinit var reviewText: EditText
    private lateinit var reviewButton: Button
    private var currentLesson: Lesson? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_lesson_detail)

        lessonId = intent.getStringExtra(EXTRA_LESSON_ID).orEmpty()
        if (lessonId.isBlank()) {
            toast("Не найден идентификатор урока")
            finish()
            return
        }

        titleView = findViewById(R.id.lesson_title)
        timeView = findViewById(R.id.lesson_time)
        statusView = findViewById(R.id.lesson_status)
        linkInput = findViewById(R.id.lesson_link)
        progress = findViewById(R.id.lesson_progress)
        reviewBlock = findViewById(R.id.lesson_review_block)
        reviewScore = findViewById(R.id.lesson_review_score)
        reviewText = findViewById(R.id.lesson_review_text)
        reviewButton = findViewById(R.id.lesson_review_send)

        findViewById<Button>(R.id.lesson_save_link).setOnClickListener {
            updateLesson(mapOf("meeting_link" to linkInput.text.toString().trim()))
        }
        findViewById<Button>(R.id.lesson_mark_done).setOnClickListener {
            updateLesson(mapOf("status" to "completed"))
        }
        findViewById<Button>(R.id.lesson_cancel).setOnClickListener {
            updateLesson(mapOf("status" to "cancelled"))
        }

        reviewButton.setOnClickListener { sendReview() }

        val role = SessionManager(this).getRole()
        reviewBlock.visibility = if (role == UserRole.STUDENT) View.VISIBLE else View.GONE

        loadLesson()
    }

    private fun loadLesson() {
        progress.show(true)
        lifecycleScope.launch {
            try {
                val lessons = withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@LessonDetailActivity)
                        .getLessons(ApiFilters.eq(lessonId))
                }
                val lesson = lessons.firstOrNull()
                if (lesson != null) bindLesson(lesson)
            } catch (ex: Exception) {
                toast("Не удалось загрузить урок: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }

    private fun bindLesson(lesson: Lesson) {
        currentLesson = lesson
        titleView.text = "Урок ${lesson.id.take(8)}"
        timeView.text = "Время: ${lesson.start_datetime} - ${lesson.end_datetime}"
        statusView.text = "Статус: ${mapStatus(lesson.status)}"
        linkInput.setText(lesson.meeting_link ?: "")
        val role = SessionManager(this).getRole()
        reviewBlock.visibility = if (role == UserRole.STUDENT && lesson.status == "completed") {
            View.VISIBLE
        } else {
            View.GONE
        }
    }

    private fun updateLesson(patch: Map<String, Any?>) {
        progress.show(true)
        lifecycleScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@LessonDetailActivity)
                        .updateLesson(ApiFilters.eq(lessonId), patch)
                }
                loadLesson()
            } catch (ex: Exception) {
                toast("Не удалось обновить урок: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }

    private fun sendReview() {
        val lesson = currentLesson
        val studentId = SessionManager(this).getUserId()
        if (lesson == null || studentId.isNullOrBlank()) {
            toast("Нет данных для отзыва")
            return
        }
        val score = reviewScore.text.toString().trim().toIntOrNull()
        if (score == null || score !in 1..5) {
            toast("Введите оценку от 1 до 5")
            return
        }
        progress.show(true)
        lifecycleScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@LessonDetailActivity).createReview(
                        ReviewCreate(
                            student_id = studentId,
                            tutor_id = lesson.tutor_id,
                            lesson_id = lesson.id,
                            communication_score = score,
                            text = reviewText.text.toString().trim().ifBlank { null }
                        )
                    )
                }
                toast("Отзыв отправлен")
            } catch (ex: Exception) {
                toast("Не удалось отправить отзыв: ${ex.message}")
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

    companion object {
        const val EXTRA_LESSON_ID = "extra_lesson_id"
    }
}
