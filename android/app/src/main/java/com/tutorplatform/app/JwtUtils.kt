package com.tutorplatform.app

import android.util.Base64
import android.util.Log
import org.json.JSONObject

object JwtUtils {
    private const val TAG = "JwtUtils"

    data class ParsedToken(val userId: String?, val roles: List<String>)

    fun parse(token: String): ParsedToken {
        Log.d(TAG, "parse: разбор JWT-токена (${token.take(20)}...)")
        return runCatching {
            val parts = token.split(".")
            if (parts.size < 2) {
                Log.w(TAG, "parse: токен не содержит payload (всего ${parts.size} частей)")
                return ParsedToken(null, emptyList())
            }

            val payload = String(Base64.decode(parts[1], Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP))
            val json = JSONObject(payload)
            Log.v(TAG, "parse: payload декодирован: $payload")

            val realmAccess = json.optJSONObject("realm_access")
            val rolesArray = realmAccess?.optJSONArray("roles")
            val roles = mutableListOf<String>()
            if (rolesArray != null) {
                for (i in 0 until rolesArray.length()) {
                    roles.add(rolesArray.optString(i))
                }
            }
            Log.d(TAG, "parse: найдено ролей: ${roles.size} — $roles")

            val userId = when {
                json.has("user_id") -> json.optString("user_id", null)
                json.has("sub") -> json.optString("sub", null)
                else -> null
            }
            Log.d(TAG, "parse: userId=$userId")

            ParsedToken(userId, roles)
        }.getOrElse { ex ->
            Log.e(TAG, "parse: ошибка разбора токена: ${ex::class.simpleName}: ${ex.message}")
            ParsedToken(null, emptyList())
        }
    }
}
