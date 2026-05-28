package com.tutorplatform.app.ui

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.appcompat.app.AppCompatActivity
import com.tutorplatform.app.R
import com.tutorplatform.app.SessionManager
import com.tutorplatform.app.UserRole

class SplashActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        Handler(Looper.getMainLooper()).postDelayed({
            routeNext()
        }, 700)
    }

    private fun routeNext() {
        val session = SessionManager(this)
        val target = if (!session.isLoggedIn()) {
            LoginActivity::class.java
        } else if (session.getRole() == UserRole.TUTOR) {
            TutorMainActivity::class.java
        } else {
            StudentMainActivity::class.java
        }
        startActivity(Intent(this, target))
        finish()
    }
}
