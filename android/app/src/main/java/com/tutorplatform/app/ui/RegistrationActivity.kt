package com.tutorplatform.app.ui

import android.annotation.SuppressLint
import android.content.Intent
import android.graphics.Bitmap
import android.os.Build
import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import android.webkit.CookieManager
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.ProgressBar
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import com.tutorplatform.app.AppConfig
import com.tutorplatform.app.R
import com.tutorplatform.app.util.show

class RegistrationActivity : AppCompatActivity() {
    private lateinit var webView: WebView
    private lateinit var progress: ProgressBar
    private var redirectHandled = false

    companion object {
        const val RESULT_REGISTRATION_OK = 100
        private const val CALLBACK_URL = "tutorapp://callback"
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 35) { enableEdgeToEdge() }
        setContentView(R.layout.activity_registration)

        webView = findViewById(R.id.registration_webview)
        progress = findViewById(R.id.registration_progress)

        clearWebViewSession()

        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: return false
                if (handleCallback(url)) return true
                return false
            }

            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                if (url != null && handleCallback(url)) return
                progress.show(true)
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                progress.show(false)
            }
        }

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack()
                } else {
                    finish()
                }
            }
        })

        webView.loadUrl(buildRegistrationUrl())
    }

    private fun clearWebViewSession() {
        CookieManager.getInstance().removeAllCookies(null)
        CookieManager.getInstance().flush()
        webView.clearCache(true)
        webView.clearHistory()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            android.webkit.WebStorage.getInstance().deleteAllData()
        }
    }

    private fun handleCallback(url: String): Boolean {
        if (redirectHandled) return true
        if (url.startsWith(CALLBACK_URL)) {
            redirectHandled = true
            setResult(RESULT_REGISTRATION_OK)
            finish()
            return true
        }
        return false
    }

    private fun buildRegistrationUrl(): String {
        return "${AppConfig.KEYCLOAK_BASE_URL}realms/${AppConfig.KEYCLOAK_REALM}/protocol/openid-connect/auth" +
            "?client_id=${AppConfig.KEYCLOAK_CLIENT_ID}" +
            "&response_type=code" +
            "&scope=openid" +
            "&redirect_uri=$CALLBACK_URL" +
            "&kc_action=REGISTRATION"
    }


}
