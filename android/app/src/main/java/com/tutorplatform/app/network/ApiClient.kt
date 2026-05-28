package com.tutorplatform.app.network

import android.content.Context
import com.tutorplatform.app.AppConfig
import com.tutorplatform.app.SessionManager
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    private var authRetrofit: Retrofit? = null
    private var apiRetrofit: Retrofit? = null

    fun authService(): AuthApiService {
        val retrofit = authRetrofit ?: buildAuthRetrofit().also { authRetrofit = it }
        return retrofit.create(AuthApiService::class.java)
    }

    fun dataService(context: Context): DataApiService {
        val retrofit = apiRetrofit ?: buildApiRetrofit(context.applicationContext).also { apiRetrofit = it }
        return retrofit.create(DataApiService::class.java)
    }

    fun customService(context: Context): CustomApiService {
        val retrofit = apiRetrofit ?: buildApiRetrofit(context.applicationContext).also { apiRetrofit = it }
        return retrofit.create(CustomApiService::class.java)
    }

    private fun buildAuthRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl(AppConfig.KEYCLOAK_BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .client(buildBaseClient())
            .build()
    }

    private fun buildApiRetrofit(context: Context): Retrofit {
        return Retrofit.Builder()
            .baseUrl(AppConfig.API_BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .client(buildAuthedClient(context))
            .build()
    }

    private fun buildBaseClient(): OkHttpClient {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        }
        return OkHttpClient.Builder()
            .addInterceptor(logging)
            .build()
    }

    private fun buildAuthedClient(context: Context): OkHttpClient {
        val sessionManager = SessionManager(context)
        val authInterceptor = Interceptor { chain ->
            val token = sessionManager.getAccessToken()
            val request = if (token.isNullOrBlank()) {
                chain.request()
            } else {
                chain.request().newBuilder()
                    .addHeader("Authorization", "Bearer $token")
                    .build()
            }
            chain.proceed(request)
        }
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        }
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(logging)
            .build()
    }
}
