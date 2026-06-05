package com.tutorplatform.app.ui

import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.activity.enableEdgeToEdge
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import com.tutorplatform.app.R
import com.tutorplatform.app.SessionManager
import com.tutorplatform.app.UserRole

class SplashActivity : AppCompatActivity() {
    companion object {
        private const val TAG = "Splash"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 35) { enableEdgeToEdge() }
        Log.d(TAG, "onCreate: старт приложения")
        setContentView(R.layout.activity_splash)

        Handler(Looper.getMainLooper()).postDelayed({
            routeNext()
        }, 700)
    }

    private fun routeNext() {
        val session = SessionManager(this)
        Log.d(TAG, "routeNext: isLoggedIn=${session.isLoggedIn()}")
        val target = if (!session.isLoggedIn()) {
            Log.i(TAG, "Пользователь не авторизован → LoginActivity")
            LoginActivity::class.java
        } else if (session.getRole() == UserRole.TUTOR) {
            Log.i(TAG, "Роль TUTOR → TutorMainActivity")
            TutorMainActivity::class.java
        } else {
            Log.i(TAG, "Роль STUDENT → StudentMainActivity")
            StudentMainActivity::class.java
        }
        startActivity(Intent(this, target))
        finish()
    }
}
