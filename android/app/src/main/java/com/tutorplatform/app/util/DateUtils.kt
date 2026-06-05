package com.tutorplatform.app.util

import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.util.Locale

object DateUtils {
    private val timeFormatter = DateTimeFormatter.ofPattern("HH:mm", Locale("ru"))
    private val dateTimeFormatter = DateTimeFormatter.ofPattern("d MMM, HH:mm", Locale("ru"))
    private val dateFormatter = DateTimeFormatter.ofPattern("d MMM yyyy", Locale("ru"))
    private val dateOnlyFormatter = DateTimeFormatter.ofPattern("d MMMM", Locale("ru"))

    fun formatDateOnly(iso: String): String {
        return try {
            val instant = Instant.parse(iso)
            instant.atZone(ZoneId.systemDefault()).format(dateOnlyFormatter)
        } catch (e: Exception) {
            try {
                val cleaned = iso.replace("Z", "").substringBefore("+").take(19)
                val dt = java.time.LocalDateTime.parse(cleaned, DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss"))
                dt.format(dateOnlyFormatter)
            } catch (_: Exception) { iso }
        }
    }

    fun formatTimeOnly(iso: String): String {
        return try {
            val instant = Instant.parse(iso)
            instant.atZone(ZoneId.systemDefault()).format(timeFormatter)
        } catch (e: Exception) {
            try {
                val cleaned = iso.replace("Z", "").substringBefore("+").take(19)
                val dt = java.time.LocalDateTime.parse(cleaned, DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss"))
                dt.format(timeFormatter)
            } catch (_: Exception) { iso }
        }
    }

    fun formatDateTime(iso: String): String {
        return try {
            val instant = Instant.parse(iso)
            val zdt = instant.atZone(ZoneId.systemDefault())
            val now = ZonedDateTime.now(ZoneId.systemDefault())

            when {
                zdt.toLocalDate() == now.toLocalDate() ->
                    zdt.format(timeFormatter)                        // 14:30
                zdt.toLocalDate() == now.toLocalDate().minusDays(1) ->
                    "вчера, ${zdt.format(timeFormatter)}"            // вчера, 14:30
                else ->
                    zdt.format(dateTimeFormatter)                     // 15 мар, 14:30
            }
        } catch (e: Exception) {
            // fallback — если Instant.parse не смог
            try {
                val cleaned = iso
                    .replace("Z", "")
                    .substringBefore("+")
                    .substringBefore("-".substringAfter("T"))
                val dt = java.time.LocalDateTime.parse(
                    cleaned.take(19),
                    DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss")
                )
                dt.format(dateTimeFormatter)
            } catch (_: Exception) {
                iso
            }
        }
    }
}
