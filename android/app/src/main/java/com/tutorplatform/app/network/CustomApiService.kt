package com.tutorplatform.app.network

import com.tutorplatform.app.model.SuggestionRequest
import com.tutorplatform.app.model.TutorSuggestion
import retrofit2.http.Body
import retrofit2.http.POST

interface CustomApiService {
    @POST("api/custom/suggestions")
    suspend fun getSuggestions(@Body request: SuggestionRequest): List<TutorSuggestion>
}
