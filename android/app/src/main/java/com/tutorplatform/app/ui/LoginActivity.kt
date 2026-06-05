package com.tutorplatform.app.ui

import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.activity.enableEdgeToEdge
import android.widget.Button
import android.widget.ProgressBar
import com.google.android.material.textfield.TextInputEditText
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.tutorplatform.app.AppConfig
import com.tutorplatform.app.JwtUtils
import com.tutorplatform.app.R
import com.tutorplatform.app.SessionManager
import com.tutorplatform.app.UserRole
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class LoginActivity : AppCompatActivity() {
    companion object {
        private const val TAG = "Login"
        private const val RC_REGISTRATION = 1
    }

    override fun onResume() {
        super.onResume()
        Log.d(TAG, "onResume: восстановление UI после регистрации")
        loginButton.isEnabled = true
        progress.show(false)
    }

    override fun onPause() {
        super.onPause()
        Log.v(TAG, "onPause")
    }

    private lateinit var emailInput: TextInputEditText
    private lateinit var passwordInput: TextInputEditText
    private lateinit var loginButton: Button
    private lateinit var registerButton: Button
    private lateinit var progress: ProgressBar

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 35) { enableEdgeToEdge() }
        Log.d(TAG, "onCreate: инициализация экрана логина")
        setContentView(R.layout.activity_login)

        emailInput = findViewById(R.id.login_email)
        passwordInput = findViewById(R.id.login_password)
        loginButton = findViewById(R.id.login_button)
        registerButton = findViewById(R.id.login_register)
        progress = findViewById(R.id.login_progress)

        loginButton.setOnClickListener { attemptLogin() }
        registerButton.setOnClickListener { openRegistration() }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == RC_REGISTRATION) {
            if (resultCode == RESULT_OK) {
                Log.i(TAG, "Регистрация завершена успешно")
                toast("Регистрация прошла успешно! Теперь войдите в систему.")
            } else {
                Log.d(TAG, "Регистрация отменена пользователем")
            }
        }
    }

    private fun attemptLogin() {
        val email = emailInput.text?.toString()?.trim().orEmpty()
        val password = passwordInput.text?.toString()?.trim().orEmpty()

        Log.d(TAG, "attemptLogin: email=$email")

        if (email.isBlank() || password.isBlank()) {
            Log.w(TAG, "Валидация не пройдена: пустые поля")
            toast("Введите эл. почту и пароль")
            return
        }

        progress.show(true)
        loginButton.isEnabled = false

        Log.i(TAG, "Отправка запроса на логин через Keycloak")

        lifecycleScope.launch {
            try {
                val token = withContext(Dispatchers.IO) {
                    ApiClient.authService().login(
                        realm = AppConfig.KEYCLOAK_REALM,
                        clientId = AppConfig.KEYCLOAK_CLIENT_ID,
                        grantType = "password",
                        username = email,
                        password = password
                    )
                }
                Log.d(TAG, "Token получен: access_token=${token.access_token.take(20)}..., refresh_token=${token.refresh_token?.take(20)}")

                val parsed = JwtUtils.parse(token.access_token)
                val role = if (parsed.roles.contains("tutor")) UserRole.TUTOR else UserRole.STUDENT
                Log.i(TAG, "Пользователь аутентифицирован: userId=${parsed.userId}, role=$role, roles=${parsed.roles}")

                SessionManager(this@LoginActivity).saveSession(
                    accessToken = token.access_token,
                    refreshToken = token.refresh_token,
                    role = role,
                    userId = parsed.userId
                )
                Log.d(TAG, "Сессия сохранена")

                val target = if (role == UserRole.TUTOR) TutorMainActivity::class.java else StudentMainActivity::class.java
                Log.i(TAG, "Переход на ${target.simpleName}")
                startActivity(Intent(this@LoginActivity, target))
                finish()
            } catch (ex: Exception) {
                Log.e(TAG, "Ошибка входа: ${ex::class.simpleName}: ${ex.message}")
                toast("Не удалось войти: ${ex.message}")
            } finally {
                progress.show(false)
                loginButton.isEnabled = true
                Log.v(TAG, "attemptLogin: finally — UI восстановлен")
            }
        }
    }

    private fun openRegistration() {
        Log.d(TAG, "Открытие формы регистрации")
        val intent = Intent(this, RegistrationNewActivity::class.java)
        startActivityForResult(intent, RC_REGISTRATION)
    }
}
