package com.tutorplatform.app

import android.util.Base64
import org.json.JSONObject

object JwtUtils {
    data class ParsedToken(val userId: String?, val roles: List<String>)

    fun parse(token: String): ParsedToken {
        return runCatching {
            val parts = token.split(".")
            if (parts.size < 2) return ParsedToken(null, emptyList())

            val payload = String(Base64.decode(parts[1], Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP))
            val json = JSONObject(payload)
            val realmAccess = json.optJSONObject("realm_access")
            val rolesArray = realmAccess?.optJSONArray("roles")
            val roles = mutableListOf<String>()
            if (rolesArray != null) {
                for (i in 0 until rolesArray.length()) {
                    roles.add(rolesArray.optString(i))
                }
            }
            val userId = when {
                json.has("user_id") -> json.optString("user_id", null)
                json.has("sub") -> json.optString("sub", null)
                else -> null
            }
            ParsedToken(userId, roles)
        }.getOrElse {
            ParsedToken(null, emptyList())
        }
    }
}
