package com.tutorplatform.app.model

data class TokenResponse(
    val access_token: String,
    val refresh_token: String?
)

data class TutorProfile(
    val user_id: String,
    val full_name: String,
    val photo_url: String?,
    val education: String?,
    val subject_id: String?,
    val hourly_rate: Int?,
    val experience_years: Int?,
    val is_verified: Boolean?,
    val student_count: Int?,
    val rating_efficiency: Double?,
    val rating_communication: Double?,
    val rating_expertise: Double?,
    val rating_responsiveness: Double?,
    val is_new_boost: Boolean?
)

data class StudentProfile(
    val user_id: String,
    val full_name: String?,
    val photo_url: String?,
    val search_weights: Any?
)

data class ScheduleSlot(
    val id: Int,
    val tutor_id: String,
    val day_of_week: Int?,
    val specific_date: String?,
    val start_time: String,
    val end_time: String
)

data class ScheduleSlotCreate(
    val tutor_id: String,
    val day_of_week: Int? = null,
    val specific_date: String? = null,
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
    val meeting_link: String? = null
)

data class Application(
    val id: String,
    val student_id: String,
    val tutor_id: String,
    val status: String,
    val created_at: String?,
    val responded_at: String?
)

data class ApplicationCreate(
    val student_id: String,
    val tutor_id: String
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
    val is_read: Boolean?,
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
    val test_id: String,
    val type: String,
    val score: Double?,
    val assigned_at: String?,
    val completed_at: String?
)

data class StudentResultCreate(
    val student_id: String,
    val tutor_id: String,
    val test_id: String,
    val type: String,
    val score: Double? = null
)

data class TestLibrary(
    val id: String,
    val subject_id: String,
    val topic: String,
    val questions_json: Any?
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

// ─── Suggestions ────────────────────────────────────────────────

data class SuggestionWeights(
    val k1_effectiveness: Double = 0.30,
    val k2_communication: Double = 0.15,
    val k3_expertise: Double = 0.20,
    val k4_responsiveness: Double = 0.15,
    val k5_tags: Double = 0.20
)

data class SuggestionScheduleSlot(
    val day_of_week: Int,
    val start_time: String,
    val end_time: String
)

data class SuggestionRequest(
    val subject_id: String,
    val max_price: Int? = null,
    val min_experience: Int? = null,
    val verified_only: Boolean? = null,
    val schedule_slots: List<SuggestionScheduleSlot>? = null,
    val required_tag_ids: List<String>? = null,
    val weights: SuggestionWeights? = null
)

data class ScoreBreakdown(
    val o1: Double?,
    val o2: Double?,
    val o3: Double?,
    val o4: Double?,
    val o5: Double?
)

data class TutorSuggestion(
    val tutor_id: String,
    val full_name: String?,
    val score: Double,
    val score_breakdown: ScoreBreakdown?,
    val hourly_rate: Int?,
    val is_new: Boolean?
)

data class Subject(
    val id: String,
    val name: String
)

data class Tag(
    val id: String,
    val name: String
)

data class TutorTag(
    val tutor_id: String,
    val tag_id: String
)

// ─── Auth (Register) ───────────────────────────────────────────

data class RegisterRequest(
    val username: String,
    val password: String,
    val full_name: String,
    val role: String,
    val subject_id: String? = null,
    val hourly_rate: Int? = null
)

data class RegisterResponse(
    val user_id: String?,
    val username: String?,
    val role: String?
)

data class SimpleItem(
    val id: String,
    val title: String,
    val subtitle: String? = null,
    val meta: String? = null
)
