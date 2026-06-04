package com.tutorplatform.app.ui

import android.annotation.SuppressLint
import android.graphics.Bitmap
import android.os.Bundle
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

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_registration)

        webView = findViewById(R.id.registration_webview)
        progress = findViewById(R.id.registration_progress)

        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                return false
            }

            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
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

    private fun buildRegistrationUrl(): String {
        return "${AppConfig.KEYCLOAK_BASE_URL}realms/${AppConfig.KEYCLOAK_REALM}/protocol/openid-connect/registrations?client_id=${AppConfig.KEYCLOAK_CLIENT_ID}"
    }
}
