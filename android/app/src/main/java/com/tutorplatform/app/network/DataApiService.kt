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
import com.tutorplatform.app.model.TestLibrary
import com.tutorplatform.app.model.TutorProfile
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Query

interface DataApiService {
    @GET("api/data/tutor_profiles")
    suspend fun getTutorProfiles(@Query("user_id") userIdFilter: String? = null): List<TutorProfile>

    @PATCH("api/data/tutor_profiles")
    suspend fun updateTutorProfile(
        @Query("user_id") userIdFilter: String,
        @Body patch: Map<String, Any?>
    ): List<TutorProfile>

    @GET("api/data/student_profiles")
    suspend fun getStudentProfiles(@Query("user_id") userIdFilter: String? = null): List<StudentProfile>

    @PATCH("api/data/student_profiles")
    suspend fun updateStudentProfile(
        @Query("user_id") userIdFilter: String,
        @Body patch: Map<String, Any?>
    ): List<StudentProfile>

    @GET("api/data/schedules")
    suspend fun getSchedules(@Query("tutor_id") tutorIdFilter: String? = null): List<ScheduleSlot>

    @POST("api/data/schedules")
    suspend fun addSchedule(@Body slot: ScheduleSlotCreate): ScheduleSlot

    @GET("api/data/lessons")
    suspend fun getLessons(@Query("id") idFilter: String? = null): List<Lesson>

    @POST("api/data/lessons")
    suspend fun createLesson(@Body request: LessonCreate): Lesson

    @PATCH("api/data/lessons")
    suspend fun updateLesson(@Query("id") idFilter: String, @Body patch: Map<String, Any?>): List<Lesson>

    @GET("api/data/applications")
    suspend fun getApplications(
        @Query("tutor_id") tutorIdFilter: String? = null,
        @Query("student_id") studentIdFilter: String? = null,
        @Query("status") statusFilter: String? = null
    ): List<Application>

    @POST("api/data/applications")
    suspend fun createApplication(@Body request: ApplicationCreate): Application

    @PATCH("api/data/applications")
    suspend fun updateApplication(@Query("id") idFilter: String, @Body patch: Map<String, Any?>): List<Application>

    @GET("api/data/chats")
    suspend fun getChats(@Query("application_id") applicationIdFilter: String? = null): List<Chat>

    @GET("api/data/messages")
    suspend fun getMessages(
        @Query("chat_id") chatIdFilter: String,
        @Query("order") order: String = "created_at.asc"
    ): List<Message>

    @POST("api/data/messages")
    suspend fun sendMessage(@Body request: MessageCreate): Message

    @GET("api/data/student_results")
    suspend fun getStudentResults(@Query("student_id") studentIdFilter: String? = null): List<StudentResult>

    @POST("api/data/student_results")
    suspend fun createStudentResult(@Body request: StudentResultCreate): StudentResult

    @GET("api/data/test_library")
    suspend fun getTestLibrary(): List<TestLibrary>

    @GET("api/data/reviews")
    suspend fun getReviews(@Query("tutor_id") tutorIdFilter: String? = null): List<Review>

    @POST("api/data/reviews")
    suspend fun createReview(@Body request: ReviewCreate): Review
}
