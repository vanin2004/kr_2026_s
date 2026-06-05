package com.tutorplatform.app.network

import com.tutorplatform.app.model.Application
import com.tutorplatform.app.model.ApplicationCreate
import com.tutorplatform.app.model.Chat
import com.tutorplatform.app.model.Lesson
import com.tutorplatform.app.model.LessonCreate
import com.tutorplatform.app.model.Message
import com.tutorplatform.app.model.MessageCreate
import com.tutorplatform.app.model.Review
import com.tutorplatform.app.model.ReviewCreate
import com.tutorplatform.app.model.ScheduleSlot
import com.tutorplatform.app.model.ScheduleSlotCreate
import com.tutorplatform.app.model.StudentProfile
import com.tutorplatform.app.model.StudentResult
import com.tutorplatform.app.model.StudentResultCreate
import com.tutorplatform.app.model.Subject
import com.tutorplatform.app.model.Tag
import com.tutorplatform.app.model.TestLibrary
import com.tutorplatform.app.model.TutorProfile
import com.tutorplatform.app.model.TutorTag
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface DataApiService {
    // ─── Tutor Profiles ─────────────────────────────────────────
    @GET("api/custom/tutor_profiles/{user_id}")
    suspend fun getTutorProfile(@Path("user_id") userId: String): TutorProfile

    @PATCH("api/custom/tutor_profiles/{user_id}")
    suspend fun updateTutorProfile(
        @Path("user_id") userId: String,
        @Body patch: Map<String, Any?>
    ): TutorProfile

    // ─── Student Profiles ───────────────────────────────────────
    @GET("api/custom/student_profiles/{user_id}")
    suspend fun getStudentProfile(@Path("user_id") userId: String): StudentProfile

    @PATCH("api/custom/student_profiles/{user_id}")
    suspend fun updateStudentProfile(
        @Path("user_id") userId: String,
        @Body patch: Map<String, Any?>
    ): StudentProfile

    // ─── Schedules ──────────────────────────────────────────────
    @GET("api/custom/schedules")
    suspend fun getSchedules(
        @Query("tutor_id") tutorId: String? = null,
        @Query("limit") limit: Int? = null,
        @Query("offset") offset: Int? = null
    ): List<ScheduleSlot>

    @POST("api/custom/schedules")
    suspend fun addSchedule(@Body slot: ScheduleSlotCreate): ScheduleSlot

    // ─── Lessons ────────────────────────────────────────────────
    @GET("api/custom/lessons")
    suspend fun getLessons(
        @Query("student_id") studentId: String? = null,
        @Query("tutor_id") tutorId: String? = null,
        @Query("limit") limit: Int? = null,
        @Query("offset") offset: Int? = null
    ): List<Lesson>

    @GET("api/custom/lessons/{lesson_id}")
    suspend fun getLesson(@Path("lesson_id") lessonId: String): Lesson

    @POST("api/custom/lessons")
    suspend fun createLesson(@Body request: LessonCreate): Lesson

    @PATCH("api/custom/lessons/{lesson_id}")
    suspend fun updateLesson(
        @Path("lesson_id") lessonId: String,
        @Body patch: Map<String, Any?>
    ): Lesson

    // ─── Applications ───────────────────────────────────────────
    @GET("api/custom/applications")
    suspend fun getApplications(
        @Query("tutor_id") tutorId: String? = null,
        @Query("student_id") studentId: String? = null,
        @Query("limit") limit: Int? = null,
        @Query("offset") offset: Int? = null
    ): List<Application>

    @POST("api/custom/applications")
    suspend fun createApplication(@Body request: ApplicationCreate): Application

    @PATCH("api/custom/applications/{application_id}")
    suspend fun updateApplication(
        @Path("application_id") applicationId: String,
        @Body patch: Map<String, Any?>
    ): Application

    // ─── Chats ──────────────────────────────────────────────────
    @GET("api/custom/chats")
    suspend fun getChats(@Query("application_id") applicationId: String? = null): List<Chat>

    // ─── Messages ───────────────────────────────────────────────
    @GET("api/custom/messages")
    suspend fun getMessages(
        @Query("chat_id") chatId: String,
        @Query("limit") limit: Int? = null,
        @Query("offset") offset: Int? = null
    ): List<Message>

    @POST("api/custom/messages")
    suspend fun sendMessage(@Body request: MessageCreate): Message

    // ─── Student Results ────────────────────────────────────────
    @GET("api/custom/student_results")
    suspend fun getStudentResults(
        @Query("student_id") studentId: String? = null,
        @Query("tutor_id") tutorId: String? = null
    ): List<StudentResult>

    @POST("api/custom/student_results")
    suspend fun createStudentResult(@Body request: StudentResultCreate): StudentResult

    // ─── Test Library ───────────────────────────────────────────
    @GET("api/custom/test_library")
    suspend fun getTestLibrary(@Query("subject_id") subjectId: String? = null): List<TestLibrary>

    // ─── Reviews ────────────────────────────────────────────────
    @GET("api/custom/reviews")
    suspend fun getReviews(
        @Query("tutor_id") tutorId: String? = null,
        @Query("student_id") studentId: String? = null,
        @Query("limit") limit: Int? = null,
        @Query("offset") offset: Int? = null
    ): List<Review>

    @POST("api/custom/reviews")
    suspend fun createReview(@Body request: ReviewCreate): Review

    // ─── Subjects ────────────────────────────────────────────────
    @GET("api/custom/subjects")
    suspend fun getSubjects(
        @Query("limit") limit: Int? = null,
        @Query("offset") offset: Int? = null
    ): List<Subject>

    // ─── Tags ────────────────────────────────────────────────────
    @GET("api/custom/tags")
    suspend fun getTags(
        @Query("limit") limit: Int? = null,
        @Query("offset") offset: Int? = null
    ): List<Tag>

    // ─── Tutor Tags ────────────────────────────────────────────
    @GET("api/custom/tutor_tags")
    suspend fun getTutorTags(
        @Query("tutor_id") tutorId: String? = null
    ): List<TutorTag>
}
