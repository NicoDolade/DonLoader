package com.example.donloader

import android.app.Application
import android.util.Log
import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLException

class DonLoaderApp : Application() {
    override fun onCreate() {
        super.onCreate()
        try {
            // Inicializar la librería YoutubeDL nativa
            YoutubeDL.getInstance().init(this)
            Log.d("DonLoaderApp", "YoutubeDL inicializado correctamente")
        } catch (e: YoutubeDLException) {
            Log.e("DonLoaderApp", "Error al inicializar YoutubeDL", e)
        } catch (e: Exception) {
            Log.e("DonLoaderApp", "Error crítico al inicializar la app", e)
        }
    }
}
