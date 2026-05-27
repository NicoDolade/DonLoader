package com.example.donloader.updater

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.util.Log
import androidx.core.content.FileProvider
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedInputStream
import java.io.File
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URL

class AppUpdater(private val context: Context) {

    private val _updateProgress = MutableStateFlow<Float>(-1f) // -1f = no descargando, 0-100 = progreso
    val updateProgress: StateFlow<Float> = _updateProgress

    data class UpdateInfo(
        val hasUpdate: Boolean,
        val latestVersion: String,
        val downloadUrl: String?
    )

    suspend fun checkUpdates(currentVersion: String): UpdateInfo = withContext(Dispatchers.IO) {
        try {
            val url = URL("https://api.github.com/repos/NicoDolade/DonLoader/releases/latest")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = 10000
            connection.readTimeout = 10000
            connection.setRequestProperty("Accept", "application/vnd.github.v3+json")
            connection.setRequestProperty("User-Agent", "DonLoader-Android-Updater")

            if (connection.responseCode == 200) {
                val responseText = connection.inputStream.bufferedReader().use { it.readText() }
                val json = JSONObject(responseText)
                val latestTag = json.getString("tag_name") // ej. "v1.2.0"

                // Sanitizar versiones para comparar (remover la 'v' inicial si existe)
                val cleanLatest = latestTag.trim().removePrefix("v")
                val cleanCurrent = currentVersion.trim().removePrefix("v")

                if (isNewerVersion(cleanCurrent, cleanLatest)) {
                    // Buscar el archivo APK entre los assets
                    val assetsArray = json.getJSONArray("assets")
                    var downloadUrl: String? = null
                    for (i in 0 until assetsArray.length()) {
                        val asset = assetsArray.getJSONObject(i)
                        val name = asset.getString("name")
                        if (name.endsWith(".apk")) {
                            downloadUrl = asset.getString("browser_download_url")
                            break
                        }
                    }
                    return@withContext UpdateInfo(true, latestTag, downloadUrl)
                }
            }
        } catch (e: Exception) {
            Log.e("AppUpdater", "Error al verificar actualizaciones en GitHub", e)
        }
        return@withContext UpdateInfo(false, currentVersion, null)
    }

    suspend fun downloadAndInstallApk(downloadUrl: String) = withContext(Dispatchers.IO) {
        try {
            _updateProgress.value = 0f
            val url = URL(downloadUrl)
            val connection = url.openConnection() as HttpURLConnection
            connection.connect()

            val fileLength = connection.contentLength
            val cacheFile = File(context.externalCacheDir ?: context.cacheDir, "update.apk")
            if (cacheFile.exists()) cacheFile.delete()

            val input = BufferedInputStream(url.openStream(), 8192)
            val output = FileOutputStream(cacheFile)

            val data = ByteArray(1024)
            var total: Long = 0
            var count: Int
            while (input.read(data).also { count = it } != -1) {
                total += count
                if (fileLength > 0) {
                    _updateProgress.value = (total * 100 / fileLength).toFloat()
                }
                output.write(data, 0, count)
            }

            output.flush()
            output.close()
            input.close()

            _updateProgress.value = 100f
            
            // Iniciar instalación
            withContext(Dispatchers.Main) {
                installApk(cacheFile)
            }
        } catch (e: Exception) {
            Log.e("AppUpdater", "Error al descargar o instalar el APK", e)
            _updateProgress.value = -2f // -2f = error de descarga
        }
    }

    private fun installApk(file: File) {
        if (!file.exists()) return

        val apkUri: Uri = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            FileProvider.getUriForFile(context, "${context.packageName}.provider", file)
        } else {
            Uri.fromFile(file)
        }

        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(apkUri, "application/vnd.android.package-archive")
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }

        try {
            context.startActivity(intent)
        } catch (e: Exception) {
            Log.e("AppUpdater", "Error al ejecutar el intent de instalación", e)
        }
    }

    private fun isNewerVersion(current: String, latest: String): Boolean {
        val currentParts = current.split(".").mapNotNull { it.toIntOrNull() }
        val latestParts = latest.split(".").mapNotNull { it.toIntOrNull() }

        val size = minOf(currentParts.size, latestParts.size)
        for (i in 0 until size) {
            if (latestParts[i] > currentParts[i]) return true
            if (latestParts[i] < currentParts[i]) return false
        }
        return latestParts.size > currentParts.size
    }
}
