package com.tutorplatform.app.network

import com.tutorplatform.app.model.RegisterRequest
import com.tutorplatform.app.model.RegisterResponse
import com.tutorplatform.app.model.SuggestionRequest
import com.tutorplatform.app.model.TutorSuggestion
import retrofit2.http.Body
import retrofit2.http.POST

interface CustomApiService {
    @POST("api/custom/auth/register")
    suspend fun register(@Body request: RegisterRequest): RegisterResponse

    @POST("api/custom/suggestions")
    suspend fun getSuggestions(@Body request: SuggestionRequest): List<TutorSuggestion>
}
