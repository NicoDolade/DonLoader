package com.example.donloader

import android.app.Application
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Build
import android.util.Log
import com.example.donloader.updater.AppUpdater
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

        // Registrar receptor para limpiar el APK de actualización inmediatamente después
        // de que el sistema complete la instalación. En ese momento el PackageInstaller
        // ya liberó el lock sobre update.apk y se puede borrar sin reintentos.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(
                postUpdateCleanupReceiver,
                IntentFilter(Intent.ACTION_MY_PACKAGE_REPLACED),
                RECEIVER_NOT_EXPORTED
            )
        } else {
            @Suppress("UnspecifiedRegisterReceiverFlag")
            registerReceiver(postUpdateCleanupReceiver, IntentFilter(Intent.ACTION_MY_PACKAGE_REPLACED))
        }
    }

    private val postUpdateCleanupReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            if (intent.action == Intent.ACTION_MY_PACKAGE_REPLACED) {
                Log.d("DonLoaderApp", "ACTION_MY_PACKAGE_REPLACED received, cleaning leftover update APK")
                try {
                    AppUpdater(context).clearUpdateCache()
                } catch (e: Exception) {
                    Log.e("DonLoaderApp", "Post-update cleanup failed", e)
                }
            }
        }
    }
}
