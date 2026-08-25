package com.example.donloader.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import com.example.donloader.MainActivity
import com.example.donloader.R
import com.example.donloader.data.DownloadManager
import com.example.donloader.data.DownloadStatus
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.launch

internal fun shouldStopWhenIdle(hasObservedActiveTask: Boolean, activeCount: Int): Boolean {
    return hasObservedActiveTask && activeCount == 0
}

class DownloadService : Service() {

    companion object {
        const val CHANNEL_ID = "donloader_downloads"
        const val NOTIFICATION_ID = 1001

        fun start(context: Context) {
            val intent = Intent(context, DownloadService::class.java)
            ContextCompat.startForegroundService(context, intent)
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, DownloadService::class.java))
        }
    }

    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private var observerJob: Job? = null
    private val downloadManager: DownloadManager by lazy { DownloadManager.get(applicationContext) }

    override fun onCreate() {
        super.onCreate()
        ensureChannel()
        startForegroundCompat(buildNotification(activeCount = 0, percent = 0))
        observeTasks()
    }

    private fun observeTasks() {
        observerJob = serviceScope.launch {
            var hasObservedActiveTask = false
            downloadManager.tasks
                .map { tasks ->
                    val active = tasks.count { isActive(it.status) }
                    val downloading = tasks.filter { it.status == DownloadStatus.DESCARGANDO || it.status == DownloadStatus.CONVIRTIENDO }
                    val percent = if (downloading.isEmpty()) 0 else downloading.map { it.progress }.average().toInt()
                    Triple(tasks.size, active, percent)
                }
                .distinctUntilChanged()
                .collect { (total, active, percent) ->
                    val nm = getSystemService(NotificationManager::class.java)
                    if (active > 0) {
                        hasObservedActiveTask = true
                        nm.notify(NOTIFICATION_ID, buildNotification(active, percent))
                    } else if (shouldStopWhenIdle(hasObservedActiveTask, active)) {
                        stopForegroundCompat()
                        stopSelf()
                    }
                }
        }
    }

    private fun isActive(status: DownloadStatus): Boolean = when (status) {
        DownloadStatus.EN_COLA, DownloadStatus.EXTRAYENDO, DownloadStatus.DESCARGANDO, DownloadStatus.CONVIRTIENDO -> true
        DownloadStatus.COMPLETADO, DownloadStatus.FALLIDO -> false
    }

    private fun ensureChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Descargas de DonLoader",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Notificación persistente que mantiene las descargas activas al minimizar la app"
                setShowBadge(false)
            }
            getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        }
    }

    private fun buildNotification(activeCount: Int, percent: Int): Notification {
        val tapIntent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val pendingFlags = PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        val contentIntent = PendingIntent.getActivity(this, 0, tapIntent, pendingFlags)

        val title = if (activeCount == 1) "1 descarga en curso" else "$activeCount descargas en curso"
        val text = if (percent > 0) "Progreso global: $percent%" else "Preparando descargas..."

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(text)
            .setSmallIcon(R.drawable.ic_status)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setContentIntent(contentIntent)
            .setProgress(100, percent, percent == 0)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
            .build()
    }

    private fun startForegroundCompat(notification: Notification) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun stopForegroundCompat() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            stopForeground(STOP_FOREGROUND_REMOVE)
        } else {
            @Suppress("DEPRECATION")
            stopForeground(true)
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        observerJob?.cancel()
        serviceScope.cancel()
        super.onDestroy()
    }
}
