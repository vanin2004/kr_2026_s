package com.tutorplatform.app

import android.content.Context
import android.util.Log

class SessionManager(context: Context) {
    companion object {
        private const val TAG = "Session"
        private const val PREFS_NAME = "session"
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_REFRESH_TOKEN = "refresh_token"
        private const val KEY_ROLE = "role"
        private const val KEY_USER_ID = "user_id"
    }

    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun saveSession(accessToken: String, refreshToken: String?, role: UserRole, userId: String?) {
        Log.i(TAG, "saveSession: userId=$userId, role=$role, token=${accessToken.take(20)}...")
        prefs.edit()
            .putString(KEY_ACCESS_TOKEN, accessToken)
            .putString(KEY_REFRESH_TOKEN, refreshToken)
            .putString(KEY_ROLE, role.name)
            .putString(KEY_USER_ID, userId)
            .apply()
        Log.d(TAG, "saveSession: сессия сохранена в SharedPreferences")
    }

    fun clearSession() {
        Log.w(TAG, "clearSession: очистка сессии")
        prefs.edit().clear().apply()
    }

    fun getAccessToken(): String? {
        val token = prefs.getString(KEY_ACCESS_TOKEN, null)
        Log.v(TAG, "getAccessToken: ${if (token != null) "токен есть (${token.take(20)}...)" else "токена нет"}")
        return token
    }

    fun getUserId(): String? {
        val id = prefs.getString(KEY_USER_ID, null)
        Log.v(TAG, "getUserId: $id")
        return id
    }

    fun getRole(): UserRole? {
        val raw = prefs.getString(KEY_ROLE, null)
        if (raw == null) {
            Log.v(TAG, "getRole: роль не сохранена")
            return null
        }
        val role = runCatching { UserRole.valueOf(raw) }.getOrNull()
        Log.d(TAG, "getRole: $role (raw=$raw)")
        return role
    }

    fun isLoggedIn(): Boolean {
        val loggedIn = getAccessToken() != null
        Log.d(TAG, "isLoggedIn: $loggedIn")
        return loggedIn
    }
}
