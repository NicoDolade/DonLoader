package com.example.donloader.ui.main

import android.app.Application
import android.content.Context
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.donloader.data.DownloadManager
import com.example.donloader.data.DownloadTask
import com.example.donloader.data.EngineStatus
import com.example.donloader.data.VideoQualityState
import com.example.donloader.service.DownloadService
import com.example.donloader.updater.AppUpdater
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class MainScreenViewModel(application: Application) : AndroidViewModel(application) {

    private val downloadManager = DownloadManager.get(application)
    private val appUpdater = AppUpdater(application)

    val tasks: StateFlow<List<DownloadTask>> = downloadManager.tasks
    val engineStatus: StateFlow<EngineStatus> = downloadManager.engineStatus
    val videoQualityState: StateFlow<VideoQualityState> = downloadManager.videoQualityState
    val updateProgress: StateFlow<Float> = appUpdater.updateProgress

    private val _updateInfo = MutableStateFlow<AppUpdater.UpdateInfo?>(null)
    val updateInfo: StateFlow<AppUpdater.UpdateInfo?> = _updateInfo.asStateFlow()

    private val _selectedFolderUri = MutableStateFlow<String>("")
    val selectedFolderUri: StateFlow<String> = _selectedFolderUri.asStateFlow()

    private val _selectedFolderName = MutableStateFlow<String>("Descargas (Carpeta Interna)")
    val selectedFolderName: StateFlow<String> = _selectedFolderName.asStateFlow()

    init {
        // Cargar carpeta destino previamente guardada de las preferencias
        val prefs = application.getSharedPreferences("donloader_prefs", Context.MODE_PRIVATE)
        val uriStr = prefs.getString("target_folder_uri", "") ?: ""
        val nameStr = prefs.getString("target_folder_name", "Descargas (Carpeta Interna)") ?: "Descargas (Carpeta Interna)"
        
        _selectedFolderUri.value = uriStr
        _selectedFolderName.value = nameStr
        downloadManager.selectedFolderUri = uriStr.ifBlank { null }

        // Arrancar el Foreground Service de descargas (protege las descargas al minimizar la app)
        DownloadService.start(application)

        // Verificar actualizaciones de GitHub al arrancar
        checkForUpdates()
    }

    fun addDownload(url: String, format: String, quality: String, videoQuality: Int? = null) {
        if (url.isNotBlank()) {
            downloadManager.addDownload(url, format, quality, videoQuality)
        }
    }

    fun analyzeVideoQualities(url: String) {
        downloadManager.analyzeVideoQualities(url)
    }

    fun clearCompleted() {
        downloadManager.clearCompleted()
    }

    fun cancelDownload(taskId: String) {
        downloadManager.cancelDownload(taskId)
    }

    fun retryDownload(taskId: String) {
        downloadManager.retryDownload(taskId)
    }

    fun refreshEngine() {
        downloadManager.refreshEngine()
    }

    fun updateSelectedFolder(uri: String, displayName: String) {
        _selectedFolderUri.value = uri
        _selectedFolderName.value = displayName
        downloadManager.selectedFolderUri = uri.ifBlank { null }

        // Guardar en SharedPreferences
        val prefs = getApplication<Application>().getSharedPreferences("donloader_prefs", Context.MODE_PRIVATE)
        prefs.edit().apply {
            putString("target_folder_uri", uri)
            putString("target_folder_name", displayName)
            apply()
        }
    }

    fun checkForUpdates() {
        viewModelScope.launch {
            try {
                // Obtener versión actual de la app
                val packageInfo = getApplication<Application>().packageManager.getPackageInfo(getApplication<Application>().packageName, 0)
                val currentVersion = packageInfo.versionName ?: "1.0.0"
                
                val info = appUpdater.checkUpdates(currentVersion)
                if (info.hasUpdate) {
                    _updateInfo.value = info
                }
            } catch (e: Exception) {
                Log.e("MainViewModel", "Error al chequear actualizaciones", e)
            }
        }
    }

    fun startAppUpdate(downloadUrl: String) {
        viewModelScope.launch {
            appUpdater.downloadAndInstallApk(downloadUrl)
        }
    }

    fun dismissUpdateDialog() {
        _updateInfo.value = null
    }
}
