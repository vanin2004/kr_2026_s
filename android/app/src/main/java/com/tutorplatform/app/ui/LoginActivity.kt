package com.tutorplatform.app.ui

import android.content.Intent
import android.net.Uri
import android.os.Bundle
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
    private lateinit var emailInput: TextInputEditText
    private lateinit var passwordInput: TextInputEditText
    private lateinit var loginButton: Button
    private lateinit var registerButton: Button
    private lateinit var progress: ProgressBar

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        emailInput = findViewById(R.id.login_email)
        passwordInput = findViewById(R.id.login_password)
        loginButton = findViewById(R.id.login_button)
        registerButton = findViewById(R.id.login_register)
        progress = findViewById(R.id.login_progress)

        loginButton.setOnClickListener { attemptLogin() }
        registerButton.setOnClickListener { openRegistration() }
    }

    private fun attemptLogin() {
        val email = emailInput.text?.toString()?.trim().orEmpty()
        val password = passwordInput.text?.toString()?.trim().orEmpty()

        if (email.isBlank() || password.isBlank()) {
            toast("Введите эл. почту и пароль")
            return
        }

        progress.show(true)
        loginButton.isEnabled = false

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
                val parsed = JwtUtils.parse(token.access_token)
                val role = if (parsed.roles.contains("tutor")) UserRole.TUTOR else UserRole.STUDENT

                SessionManager(this@LoginActivity).saveSession(
                    accessToken = token.access_token,
                    refreshToken = token.refresh_token,
                    role = role,
                    userId = parsed.userId
                )

                val target = if (role == UserRole.TUTOR) TutorMainActivity::class.java else StudentMainActivity::class.java
                startActivity(Intent(this@LoginActivity, target))
                finish()
            } catch (ex: Exception) {
                toast("Не удалось войти: ${ex.message}")
            } finally {
                progress.show(false)
                loginButton.isEnabled = true
            }
        }
    }

    private fun openRegistration() {
        val url = "${AppConfig.KEYCLOAK_BASE_URL}realms/${AppConfig.KEYCLOAK_REALM}/protocol/openid-connect/registrations?client_id=${AppConfig.KEYCLOAK_CLIENT_ID}"
        startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
    }
}
