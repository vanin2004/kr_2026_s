package com.tutorplatform.app.model

import java.util.UUID

data class TokenResponse(
    val access_token: String,
    val refresh_token: String?
)

data class TutorProfile(
    val user_id: String,
    val full_name: String,
    val education: String?,
    val specialization: String?,
    val hourly_rate: Int?,
    val experience_years: Int?,
    val rating_overall: Double?,
    val rating_efficiency: Double?,
    val rating_communication: Double?,
    val student_count: Int?
)

data class StudentProfile(
    val user_id: String,
    val full_name: String
)

data class ScheduleSlot(
    val id: Int,
    val tutor_id: String,
    val day_of_week: Int,
    val start_time: String,
    val end_time: String
)

data class ScheduleSlotCreate(
    val tutor_id: String,
    val day_of_week: Int,
    val start_time: String,
    val end_time: String
)

data class Lesson(
    val id: String,
    val student_id: String,
    val tutor_id: String,
    val start_datetime: String,
    val end_datetime: String,
    val status: String,
    val meeting_link: String?
)

data class LessonCreate(
    val student_id: String,
    val tutor_id: String,
    val start_datetime: String,
    val end_datetime: String,
    val status: String = "planned",
    val meeting_link: String? = null
)

data class Application(
    val id: String,
    val student_id: String,
    val tutor_id: String,
    val status: String,
    val created_at: String?
)

data class ApplicationCreate(
    val student_id: String,
    val tutor_id: String,
    val status: String = "pending"
)

data class Chat(
    val id: String,
    val application_id: String,
    val created_at: String?
)

data class Message(
    val id: String,
    val chat_id: String,
    val sender_id: String,
    val text: String,
    val created_at: String?
)

data class MessageCreate(
    val chat_id: String,
    val sender_id: String,
    val text: String
)

data class StudentResult(
    val id: String,
    val student_id: String,
    val tutor_id: String,
    val test_id: Int,
    val type: String,
    val score: Double?,
    val assigned_at: String?,
    val completed_at: String?
)

data class StudentResultCreate(
    val student_id: String,
    val tutor_id: String,
    val test_id: Int,
    val type: String,
    val score: Double?
)

data class TestLibrary(
    val id: Int,
    val subject: String,
    val topic: String,
    val questions_json: String
)

data class Review(
    val id: String,
    val student_id: String,
    val tutor_id: String,
    val lesson_id: String?,
    val communication_score: Int,
    val text: String?,
    val created_at: String?
)

data class ReviewCreate(
    val student_id: String,
    val tutor_id: String,
    val lesson_id: String?,
    val communication_score: Int,
    val text: String?
)

data class SuggestionRequest(
    val subject: String?,
    val max_rate: Int?,
    val min_experience: Int?,
    val weight_efficiency: Double,
    val weight_communication: Double,
    val weight_expertise: Double,
    val weight_responsiveness: Double,
    val weight_tags: Double,
    val desired_tags: List<String>
)

data class TutorSuggestion(
    val user_id: UUID,
    val full_name: String,
    val specialization: String?,
    val hourly_rate: Int?,
    val experience_years: Int?,
    val match_score: Double
)

data class SimpleItem(
    val id: String,
    val title: String,
    val subtitle: String? = null,
    val meta: String? = null
)
