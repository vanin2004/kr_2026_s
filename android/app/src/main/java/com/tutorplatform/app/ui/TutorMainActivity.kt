package com.tutorplatform.app.ui

import android.os.Build
import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.tutorplatform.app.R
import com.tutorplatform.app.ui.tutor.TutorDashboardFragment
import com.tutorplatform.app.ui.tutor.TutorProfileFragment
import com.tutorplatform.app.ui.tutor.TutorRequestsFragment
import com.tutorplatform.app.ui.tutor.TutorScheduleFragment
import com.tutorplatform.app.ui.tutor.TutorStudentsFragment

class TutorMainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 35) { enableEdgeToEdge() }
        setContentView(R.layout.activity_tutor_main)

        val nav = findViewById<BottomNavigationView>(R.id.tutor_bottom_nav)
        nav.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_tutor_dashboard -> showFragment(TutorDashboardFragment())
                R.id.nav_tutor_schedule -> showFragment(TutorScheduleFragment())
                R.id.nav_tutor_requests -> showFragment(TutorRequestsFragment())
                R.id.nav_tutor_students -> showFragment(TutorStudentsFragment())
                R.id.nav_tutor_profile -> showFragment(TutorProfileFragment())
            }
            true
        }

        if (savedInstanceState == null) {
            nav.selectedItemId = R.id.nav_tutor_dashboard
        }
    }

    private fun showFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.tutor_container, fragment)
            .commit()
    }
}
