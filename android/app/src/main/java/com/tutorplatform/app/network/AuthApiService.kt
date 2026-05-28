package com.tutorplatform.app.network

import com.tutorplatform.app.model.TokenResponse
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.POST
import retrofit2.http.Path

interface AuthApiService {
    @FormUrlEncoded
    @POST("realms/{realm}/protocol/openid-connect/token")
    suspend fun login(
        @Path("realm") realm: String,
        @Field("client_id") clientId: String,
        @Field("grant_type") grantType: String,
        @Field("username") username: String,
        @Field("password") password: String
    ): TokenResponse
}
