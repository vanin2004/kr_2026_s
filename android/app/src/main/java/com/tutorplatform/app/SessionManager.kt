package com.tutorplatform.app

import android.content.Context

class SessionManager(context: Context) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun saveSession(accessToken: String, refreshToken: String?, role: UserRole, userId: String?) {
        prefs.edit()
            .putString(KEY_ACCESS_TOKEN, accessToken)
            .putString(KEY_REFRESH_TOKEN, refreshToken)
            .putString(KEY_ROLE, role.name)
            .putString(KEY_USER_ID, userId)
            .apply()
    }

    fun clearSession() {
        prefs.edit().clear().apply()
    }

    fun getAccessToken(): String? = prefs.getString(KEY_ACCESS_TOKEN, null)

    fun getUserId(): String? = prefs.getString(KEY_USER_ID, null)

    fun getRole(): UserRole? {
        val raw = prefs.getString(KEY_ROLE, null) ?: return null
        return runCatching { UserRole.valueOf(raw) }.getOrNull()
    }

    fun isLoggedIn(): Boolean = getAccessToken() != null

    companion object {
        private const val PREFS_NAME = "session"
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_REFRESH_TOKEN = "refresh_token"
        private const val KEY_ROLE = "role"
        private const val KEY_USER_ID = "user_id"
    }
}
