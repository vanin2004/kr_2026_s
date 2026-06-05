package com.tutorplatform.app.ui

import android.os.Build
import android.os.Bundle
import android.view.View
import androidx.activity.enableEdgeToEdge
import android.widget.Button
import android.widget.ProgressBar
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.tutorplatform.app.R
import com.tutorplatform.app.model.StudentResultCreate
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import kotlin.math.roundToInt

class TestActivity : AppCompatActivity() {
    private data class Question(
        val text: String,
        val options: List<String>,
        val answerIndex: Int,
        val hint: String?
    )

    private lateinit var progressView: TextView
    private lateinit var questionView: TextView
    private lateinit var hintView: TextView
    private lateinit var optionsGroup: RadioGroup
    private lateinit var optionButtons: List<RadioButton>
    private lateinit var nextButton: Button
    private lateinit var submitProgress: ProgressBar

    private val questions = mutableListOf<Question>()
    private var currentIndex = 0
    private var correctCount = 0

    private var testId: String? = null
    private lateinit var studentId: String
    private lateinit var tutorId: String
    private lateinit var testType: String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 35) { enableEdgeToEdge() }
        setContentView(R.layout.activity_test)

        progressView = findViewById(R.id.test_progress)
        questionView = findViewById(R.id.test_question)
        hintView = findViewById(R.id.test_hint)
        optionsGroup = findViewById(R.id.test_options)
        nextButton = findViewById(R.id.test_next)
        submitProgress = findViewById(R.id.test_submit_progress)

        optionButtons = listOf(
            findViewById(R.id.option_1),
            findViewById(R.id.option_2),
            findViewById(R.id.option_3),
            findViewById(R.id.option_4)
        )

        val rawJson = intent.getStringExtra(EXTRA_QUESTIONS_JSON)
        testId = intent.getStringExtra(EXTRA_TEST_ID)
        studentId = intent.getStringExtra(EXTRA_STUDENT_ID).orEmpty()
        tutorId = intent.getStringExtra(EXTRA_TUTOR_ID).orEmpty()
        testType = intent.getStringExtra(EXTRA_TEST_TYPE).orEmpty()

        if (rawJson.isNullOrBlank() || testId.isNullOrBlank() || studentId.isBlank() || tutorId.isBlank() || testType.isBlank()) {
            toast("Не удалось загрузить тест")
            finish()
            return
        }

        questions.addAll(parseQuestions(rawJson))
        if (questions.isEmpty()) {
            toast("В тесте нет вопросов")
            finish()
            return
        }

        bindQuestion()
        nextButton.setOnClickListener { onNext() }
    }

    private fun bindQuestion() {
        val question = questions[currentIndex]
        progressView.text = "Вопрос ${currentIndex + 1} из ${questions.size}"
        questionView.text = question.text
        if (question.hint.isNullOrBlank()) {
            hintView.visibility = View.GONE
        } else {
            hintView.visibility = View.VISIBLE
            hintView.text = "Подсказка: ${question.hint}"
        }

        optionsGroup.clearCheck()
        optionButtons.forEachIndexed { index, button ->
            val optionText = question.options.getOrNull(index)
            if (optionText.isNullOrBlank()) {
                button.visibility = View.GONE
            } else {
                button.visibility = View.VISIBLE
                button.text = optionText
            }
        }

        nextButton.text = if (currentIndex == questions.lastIndex) "Завершить тест" else "Далее"
    }

    private fun onNext() {
        val selectedId = optionsGroup.checkedRadioButtonId
        if (selectedId == -1) {
            toast("Выберите вариант ответа")
            return
        }
        val selectedIndex = optionButtons.indexOfFirst { it.id == selectedId }
        val correctIndex = questions[currentIndex].answerIndex
        if (correctIndex >= 0 && selectedIndex == correctIndex) {
            correctCount += 1
        }

        if (currentIndex == questions.lastIndex) {
            submitResult()
        } else {
            currentIndex += 1
            bindQuestion()
        }
    }

    private fun submitResult() {
        val score = if (questions.isEmpty()) 0.0 else (correctCount.toDouble() / questions.size) * 100.0
        submitProgress.show(true)
        nextButton.isEnabled = false
        lifecycleScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@TestActivity).createStudentResult(
                        StudentResultCreate(
                            student_id = studentId,
                            tutor_id = tutorId,
                            test_id = testId!!,
                            type = testType,
                            score = score
                        )
                    )
                }
                val rounded = score.roundToInt()
                toast("Тест завершен. Результат: $rounded%")
                finish()
            } catch (ex: Exception) {
                toast("Не удалось сохранить результат: ${ex.message}")
                nextButton.isEnabled = true
            } finally {
                submitProgress.show(false)
            }
        }
    }

    private fun parseQuestions(rawJson: String): List<Question> {
        return runCatching {
            val trimmed = rawJson.trim()
            val questionsArray = if (trimmed.startsWith("[")) {
                JSONArray(trimmed)
            } else {
                val root = JSONObject(trimmed)
                root.optJSONArray("questions") ?: JSONArray()
            }
            val parsed = mutableListOf<Question>()
            for (i in 0 until questionsArray.length()) {
                val obj = questionsArray.optJSONObject(i) ?: continue
                val text = obj.optString("question", obj.optString("text", ""))
                val hint = obj.optString("hint", null)
                val optionsArray = obj.optJSONArray("options") ?: obj.optJSONArray("answers") ?: JSONArray()
                val options = mutableListOf<String>()
                for (j in 0 until optionsArray.length()) {
                    options.add(optionsArray.optString(j))
                }
                val answerIndex = obj.optInt("answer_index", obj.optInt("correct_index", -1))
                if (text.isNotBlank() && options.isNotEmpty()) {
                    parsed.add(Question(text, options, answerIndex, hint))
                }
            }
            parsed
        }.getOrElse { emptyList() }
    }

    companion object {
        const val EXTRA_TEST_ID = "extra_test_id"
        const val EXTRA_QUESTIONS_JSON = "extra_questions_json"
        const val EXTRA_STUDENT_ID = "extra_student_id"
        const val EXTRA_TUTOR_ID = "extra_tutor_id"
        const val EXTRA_TEST_TYPE = "extra_test_type"
    }
}
