package com.tutorplatform.app.util

import android.content.Context
import androidx.core.graphics.ColorUtils

class LessonColorManager(context: Context) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    companion object {
        private const val PREFS_NAME = "lesson_tutor_colors"
        private const val KEY_PREFIX = "tutor_color_"

        // 12 хорошо различимых Material-цветов
        private val PALETTE = intArrayOf(
            0xFFE53935.toInt(), // red 600
            0xFF1E88E5.toInt(), // blue 600
            0xFF43A047.toInt(), // green 600
            0xFFFB8C00.toInt(), // orange 600
            0xFF8E24AA.toInt(), // purple 600
            0xFF00ACC1.toInt(), // cyan 600
            0xFF3949AB.toInt(), // indigo 600
            0xFFD81B60.toInt(), // pink 600
            0xFF6D4C41.toInt(), // brown 600
            0xFF546E7A.toInt(), // blue-grey 600
            0xFFFDD835.toInt(), // yellow 600
            0xFF00897B.toInt(), // teal 600
        )
    }

    fun getColor(tutorId: String): Int {
        val key = KEY_PREFIX + tutorId
        val stored = prefs.getInt(key, -1)
        if (stored != -1) return stored

        val used = getUsedColors()
        val color = pickColor(used)
        prefs.edit().putInt(key, color).apply()
        return color
    }

    private fun getUsedColors(): Set<Int> {
        return prefs.all
            .filterKeys { it.startsWith(KEY_PREFIX) }
            .values
            .filterIsInstance<Int>()
            .toSet()
    }

    private fun pickColor(used: Set<Int>): Int {
        for (c in PALETTE) {
            if (c !in used) return c
        }
        // если все цвета заняты — берём первый с небольшим сдвигом
        return PALETTE[used.size % PALETTE.size]
    }
}
