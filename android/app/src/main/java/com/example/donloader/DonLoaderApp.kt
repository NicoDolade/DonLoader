package com.example.donloader

import android.app.Application
import android.util.Log
import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLException
import com.yausername.ffmpeg.FFmpeg
import com.yausername.aria2c.Aria2c

class DonLoaderApp : Application() {
    override fun onCreate() {
        super.onCreate()
        try {
            // Inicializar la librería YoutubeDL nativa y sus dependencias
            YoutubeDL.getInstance().init(this)
            FFmpeg.getInstance().init(this)
            Aria2c.getInstance().init(this)
            Log.d("DonLoaderApp", "Librerías nativas (YoutubeDL, FFmpeg, Aria2c) inicializadas correctamente")
            // La actualización de yt-dlp la dispara el singleton DownloadManager.refreshEngine()
            // en su init, exponiendo el estado via engineStatus para que la UI lo muestre.
        } catch (e: YoutubeDLException) {
            Log.e("DonLoaderApp", "Error al inicializar librerías nativas", e)
        } catch (e: Exception) {
            Log.e("DonLoaderApp", "Error crítico al inicializar la app", e)
        }
    }
}
