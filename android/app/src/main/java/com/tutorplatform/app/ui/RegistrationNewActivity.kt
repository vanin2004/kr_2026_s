package com.tutorplatform.app.ui

import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.activity.enableEdgeToEdge
import android.widget.ArrayAdapter
import android.widget.AutoCompleteTextView
import android.widget.LinearLayout
import android.widget.ProgressBar
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.google.android.material.button.MaterialButton
import com.google.android.material.button.MaterialButtonToggleGroup
import com.google.android.material.textfield.TextInputEditText
import com.tutorplatform.app.R
import com.tutorplatform.app.model.RegisterRequest
import com.tutorplatform.app.model.Subject
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class RegistrationNewActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "RegisterNew"
    }

    private lateinit var usernameInput: TextInputEditText
    private lateinit var passwordInput: TextInputEditText
    private lateinit var fullNameInput: TextInputEditText
    private lateinit var roleGroup: MaterialButtonToggleGroup
    private lateinit var tutorFields: LinearLayout
    private lateinit var subjectInput: AutoCompleteTextView
    private lateinit var hourlyRateInput: TextInputEditText
    private lateinit var registerButton: MaterialButton
    private lateinit var backToLoginButton: MaterialButton
    private lateinit var progress: ProgressBar

    private val subjects = mutableListOf<Subject>()
    private var selectedSubject: Subject? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 35) { enableEdgeToEdge() }
        Log.d(TAG, "onCreate: инициализация формы регистрации")
        setContentView(R.layout.activity_registration_new)

        usernameInput = findViewById(R.id.register_username)
        passwordInput = findViewById(R.id.register_password)
        fullNameInput = findViewById(R.id.register_full_name)
        roleGroup = findViewById(R.id.register_role_group)
        tutorFields = findViewById(R.id.tutor_fields_container)
        subjectInput = findViewById(R.id.register_subject)
        hourlyRateInput = findViewById(R.id.register_hourly_rate)
        registerButton = findViewById(R.id.register_button)
        backToLoginButton = findViewById(R.id.register_back_to_login)
        progress = findViewById(R.id.register_progress)
        Log.v(TAG, "onCreate: все View найдены")

        roleGroup.addOnButtonCheckedListener { _, checkedId, isChecked ->
            if (isChecked) {
                val isTutor = checkedId == R.id.radio_tutor
                Log.d(TAG, "Роль изменена: ${if (isTutor) "tutor" else "student"}")
                tutorFields.visibility = if (isTutor) android.view.View.VISIBLE else android.view.View.GONE
            }
        }

        registerButton.setOnClickListener {
            Log.i(TAG, "Нажата кнопка «Зарегистрироваться»")
            attemptRegister()
        }
        backToLoginButton.setOnClickListener {
            Log.d(TAG, "Нажата кнопка «Назад к логину»")
            finish()
        }

        // Load subjects for the dropdown
        loadSubjects()
    }

    private fun loadSubjects() {
        Log.d(TAG, "loadSubjects: загрузка списка предметов")
        lifecycleScope.launch {
            try {
                val result = withContext(Dispatchers.IO) {
                    ApiClient.dataService(this@RegistrationNewActivity).getSubjects(limit = 100)
                }
                subjects.clear()
                subjects.addAll(result)
                Log.i(TAG, "loadSubjects: загружено ${subjects.size} предметов")

                val names = subjects.map { it.name }.toTypedArray()
                val adapter = ArrayAdapter(
                    this@RegistrationNewActivity,
                    android.R.layout.simple_dropdown_item_1line,
                    names
                )
                subjectInput.setAdapter(adapter)
                subjectInput.setOnItemClickListener { _, _, position, _ ->
                    selectedSubject = subjects[position]
                    Log.d(TAG, "Выбран предмет: ${selectedSubject?.name} (${selectedSubject?.id})")
                }
            } catch (ex: Exception) {
                Log.w(TAG, "loadSubjects: не удалось загрузить предметы — ${ex::class.simpleName}: ${ex.message}")
                toast("Не удалось загрузить список предметов")
            }
        }
    }

    private fun attemptRegister() {
        val username = usernameInput.text?.toString()?.trim().orEmpty()
        val password = passwordInput.text?.toString()?.trim().orEmpty()
        val fullName = fullNameInput.text?.toString()?.trim().orEmpty()

        Log.d(TAG, "attemptRegister: username=$username, fullName=$fullName")

        if (username.isBlank() || password.isBlank() || fullName.isBlank()) {
            Log.w(TAG, "Валидация не пройдена: есть пустые поля")
            toast("Заполните все обязательные поля")
            return
        }

        if (password.length < 4) {
            Log.w(TAG, "Валидация не пройдена: короткий пароль (${password.length} символов)")
            toast("Пароль должен быть не менее 4 символов")
            return
        }

        val isTutor = roleGroup.checkedButtonId == R.id.radio_tutor
        val role = if (isTutor) "tutor" else "student"
        Log.d(TAG, "Роль: $role")

        var subjectId: String? = null
        var hourlyRate: Int? = null

        if (isTutor) {
            subjectId = selectedSubject?.id
            if (subjectId == null) {
                val typedText = subjectInput.text?.toString()?.trim().orEmpty()
                Log.v(TAG, "subjectId не выбран из списка, введён текст: $typedText")
                if (typedText.isBlank()) {
                    Log.w(TAG, "Валидация: не выбран предмет")
                    toast("Выберите предмет")
                    return
                }
                val match = subjects.find { it.name.equals(typedText, ignoreCase = true) }
                if (match != null) {
                    subjectId = match.id
                    Log.d(TAG, "Предмет найден по тексту: ${match.name} (${match.id})")
                } else {
                    Log.w(TAG, "Валидация: предмет не найден в списке: $typedText")
                    toast("Выберите предмет из списка")
                    return
                }
            }

            val rateText = hourlyRateInput.text?.toString()?.trim().orEmpty()
            if (rateText.isBlank()) {
                Log.w(TAG, "Валидация: не указана ставка")
                toast("Укажите ставку")
                return
            }
            hourlyRate = rateText.toIntOrNull()
            if (hourlyRate == null || hourlyRate <= 0) {
                Log.w(TAG, "Валидация: некорректная ставка $rateText")
                toast("Укажите корректную ставку")
                return
            }
            Log.d(TAG, "Ставка: $hourlyRate ₽/час")
        }

        progress.show(true)
        registerButton.isEnabled = false

        Log.i(TAG, "Отправка запроса на регистрацию: role=$role, username=$username")

        lifecycleScope.launch {
            try {
                val request = RegisterRequest(
                    username = username,
                    password = password,
                    full_name = fullName,
                    role = role,
                    subject_id = subjectId,
                    hourly_rate = hourlyRate
                )
                Log.v(TAG, "RegisterRequest: $request")

                val response = withContext(Dispatchers.IO) {
                    ApiClient.customService(this@RegistrationNewActivity).register(request)
                }
                Log.i(TAG, "Регистрация успешна: user_id=${response.user_id}, username=${response.username}")

                toast("Регистрация прошла успешно! Теперь войдите в систему.")
                setResult(RESULT_OK)
                finish()
            } catch (ex: Exception) {
                Log.e(TAG, "Ошибка регистрации: ${ex::class.simpleName}: ${ex.message}")
                val message = ex.message?.let { msg ->
                    when {
                        msg.contains("409") -> "Имя пользователя уже занято"
                        msg.contains("422") -> "Проверьте правильность заполнения полей"
                        msg.contains("502") -> "Сервис регистрации временно недоступен. Проверьте, запущен ли Keycloak"
                        msg.contains("Unable to resolve host") -> "Сервер недоступен. Проверьте подключение"
                        msg.contains("timeout") -> "Сервер не отвечает. Попробуйте позже"
                        else -> "Ошибка регистрации: ${ex.message}"
                    }
                } ?: "Ошибка регистрации"
                toast(message)
            } finally {
                progress.show(false)
                registerButton.isEnabled = true
                Log.v(TAG, "attemptRegister: finally — UI восстановлен")
            }
        }
    }
}
