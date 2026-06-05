package com.tutorplatform.app.network

import android.content.Context
import android.util.Log
import com.tutorplatform.app.AppConfig
import com.tutorplatform.app.SessionManager
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    private const val TAG = "ApiClient"

    private var authRetrofit: Retrofit? = null
    private var apiRetrofit: Retrofit? = null

    fun authService(): AuthApiService {
        Log.d(TAG, "authService: создание AuthApiService (base=${AppConfig.KEYCLOAK_BASE_URL})")
        val retrofit = authRetrofit ?: buildAuthRetrofit().also {
            authRetrofit = it
            Log.i(TAG, "authService: новый Retrofit создан")
        }
        return retrofit.create(AuthApiService::class.java)
    }

    fun dataService(context: Context): DataApiService {
        Log.v(TAG, "dataService: запрос DataApiService")
        val retrofit = apiRetrofit ?: buildApiRetrofit(context.applicationContext).also {
            apiRetrofit = it
            Log.i(TAG, "dataService: новый Retrofit создан (base=${AppConfig.API_BASE_URL})")
        }
        return retrofit.create(DataApiService::class.java)
    }

    fun customService(context: Context): CustomApiService {
        Log.v(TAG, "customService: запрос CustomApiService")
        val retrofit = apiRetrofit ?: buildApiRetrofit(context.applicationContext).also {
            apiRetrofit = it
            Log.i(TAG, "customService: новый Retrofit создан (base=${AppConfig.API_BASE_URL})")
        }
        return retrofit.create(CustomApiService::class.java)
    }

    private fun buildAuthRetrofit(): Retrofit {
        Log.d(TAG, "buildAuthRetrofit: baseUrl=${AppConfig.KEYCLOAK_BASE_URL}")
        return Retrofit.Builder()
            .baseUrl(AppConfig.KEYCLOAK_BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .client(buildBaseClient())
            .build()
    }

    private fun buildApiRetrofit(context: Context): Retrofit {
        Log.d(TAG, "buildApiRetrofit: baseUrl=${AppConfig.API_BASE_URL}")
        return Retrofit.Builder()
            .baseUrl(AppConfig.API_BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .client(buildAuthedClient(context))
            .build()
    }

    private fun buildBaseClient(): OkHttpClient {
        val logging = HttpLoggingInterceptor { msg -> Log.d(TAG, "[HTTP] $msg") }.apply {
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
            if (token.isNullOrBlank()) {
                Log.d(TAG, "Auth-Interceptor: токена нет, запрос без авторизации")
                chain.proceed(chain.request())
            } else {
                Log.d(TAG, "Auth-Interceptor: добавлен Bearer-токен (${token.take(20)}...)")
                val request = chain.request().newBuilder()
                    .addHeader("Authorization", "Bearer $token")
                    .build()
                chain.proceed(request)
            }
        }
        val logging = HttpLoggingInterceptor { msg -> Log.d(TAG, "[HTTP] $msg") }.apply {
            level = HttpLoggingInterceptor.Level.HEADERS
        }
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(logging)
            .build()
    }
}
