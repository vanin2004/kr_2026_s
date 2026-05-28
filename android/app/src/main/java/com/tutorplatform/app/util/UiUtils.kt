package com.tutorplatform.app.util

import android.content.Context
import android.view.View
import android.widget.Toast

fun View.show(visible: Boolean) {
    visibility = if (visible) View.VISIBLE else View.GONE
}

fun Context.toast(message: String) {
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}
