package com.tutorplatform.app.ui

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.tutorplatform.app.R
import com.tutorplatform.app.ui.student.StudentCalendarFragment
import com.tutorplatform.app.ui.student.StudentChatsFragment
import com.tutorplatform.app.ui.student.StudentProfileFragment
import com.tutorplatform.app.ui.student.StudentProgressFragment
import com.tutorplatform.app.ui.student.StudentSearchFragment

class StudentMainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_student_main)

        val nav = findViewById<BottomNavigationView>(R.id.student_bottom_nav)
        nav.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_student_search -> showFragment(StudentSearchFragment())
                R.id.nav_student_chats -> showFragment(StudentChatsFragment())
                R.id.nav_student_calendar -> showFragment(StudentCalendarFragment())
                R.id.nav_student_progress -> showFragment(StudentProgressFragment())
                R.id.nav_student_profile -> showFragment(StudentProfileFragment())
            }
            true
        }

        if (savedInstanceState == null) {
            nav.selectedItemId = R.id.nav_student_search
        }
    }

    private fun showFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.student_container, fragment)
            .commit()
    }
}
