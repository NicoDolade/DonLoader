package com.example.donloader

import android.app.Application
import android.util.Log
import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLException
import com.yausername.ffmpeg.FFmpeg
import com.yausername.aria2c.Aria2c
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class DonLoaderApp : Application() {
    override fun onCreate() {
        super.onCreate()
        try {
            // Inicializar la librería YoutubeDL nativa y sus dependencias
            YoutubeDL.getInstance().init(this)
            FFmpeg.getInstance().init(this)
            Aria2c.getInstance().init(this)
            Log.d("DonLoaderApp", "Librerías nativas (YoutubeDL, FFmpeg, Aria2c) inicializadas correctamente")
            
            // Actualizar la biblioteca yt-dlp en segundo plano al iniciar
            updateYtDlpAsync()
        } catch (e: YoutubeDLException) {
            Log.e("DonLoaderApp", "Error al inicializar librerías nativas", e)
        } catch (e: Exception) {
            Log.e("DonLoaderApp", "Error crítico al inicializar la app", e)
        }
    }

    private fun updateYtDlpAsync() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                Log.d("DonLoaderApp", "Iniciando actualización automática de yt-dlp...")
                val status = YoutubeDL.getInstance().updateYoutubeDL(this@DonLoaderApp, YoutubeDL.UpdateChannel.STABLE)
                Log.d("DonLoaderApp", "Actualización de yt-dlp finalizada. Estado: $status")
            } catch (e: Exception) {
                Log.e("DonLoaderApp", "Error al actualizar automáticamente yt-dlp", e)
            }
        }
    }
}
