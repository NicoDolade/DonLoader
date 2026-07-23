package com.example.donloader.data

import android.content.Context
import android.net.Uri
import android.os.Environment
import android.util.Log
import androidx.documentfile.provider.DocumentFile
import com.yausername.youtubedl_android.YoutubeDL
import com.yausername.youtubedl_android.YoutubeDLRequest
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.util.UUID
import java.util.regex.Pattern

class DownloadManager private constructor(private val context: Context) {

    private val _tasks = MutableStateFlow<List<DownloadTask>>(emptyList())
    val tasks: StateFlow<List<DownloadTask>> = _tasks.asStateFlow()

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private val downloadSemaphore = Semaphore(3)

    // URI de la carpeta seleccionada por el usuario (SAF). Si es nulo o vacío, descarga en el almacenamiento privado de la app.
    var selectedFolderUri: String? = null

    companion object {
        @Volatile
        private var INSTANCE: DownloadManager? = null

        fun get(context: Context): DownloadManager {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: DownloadManager(context.applicationContext).also { INSTANCE = it }
            }
        }
    }

    init {
        // Limpiar cualquier residuo de descargas temporales (.part, .temp, etc) en la caché al iniciar
        scope.launch(Dispatchers.IO) {
            try {
                val cacheDir = context.externalCacheDir ?: context.cacheDir
                val tempFolder = File(cacheDir, "downloads")
                if (tempFolder.exists()) {
                    tempFolder.listFiles()?.forEach { file ->
                        file.delete()
                    }
                    Log.d("DownloadManager", "Startup downloads cache cleanup completed")
                }
            } catch (e: Exception) {
                Log.e("DownloadManager", "Error in startup downloads cache cleanup", e)
            }
        }
    }

    fun addDownload(url: String, format: String, quality: String) {
        val taskId = UUID.randomUUID().toString()
        val newTask = DownloadTask(
            id = taskId,
            url = url,
            format = format,
            quality = quality,
            status = DownloadStatus.EN_COLA
        )

        _tasks.value = _tasks.value + newTask

        // Arrancar la corrutina de procesamiento en segundo plano
        scope.launch(Dispatchers.IO) {
            processDownload(taskId)
        }
    }

    fun cancelDownload(taskId: String) {
        try {
            // Cancelar el proceso nativo de yt-dlp
            YoutubeDL.getInstance().destroyProcessById(taskId)
        } catch (e: Exception) {
            Log.e("DownloadManager", "Error al cancelar descarga nativa: $taskId", e)
        }

        updateTask(taskId) {
            it.copy(status = DownloadStatus.FALLIDO, error = "Descarga cancelada por el usuario")
        }
    }

    fun retryDownload(taskId: String) {
        // Re-cola una tarea fallida tras forzar una actualización de yt-dlp.
        // Necesario cuando el fallo fue por HTTP 403 (yt-dlp desactualizado frente a YouTube)
        // o cuando la actualización automática al iniciar la app no llegó a completarse.
        scope.launch(Dispatchers.IO) {
            try {
                val status = YoutubeDL.getInstance().updateYoutubeDL(context, YoutubeDL.UpdateChannel.STABLE)
                Log.d("DownloadManager", "yt-dlp force update status: $status (retry $taskId)")
            } catch (e: Exception) {
                Log.e("DownloadManager", "yt-dlp force update failed on retry $taskId", e)
            }
            updateTask(taskId) {
                it.copy(
                    status = DownloadStatus.EN_COLA,
                    error = null,
                    progress = 0f,
                    speed = "",
                    eta = ""
                )
            }
            processDownload(taskId)
        }
    }

    private suspend fun processDownload(taskId: String) {
        // Esperar en el semáforo para garantizar máximo 3 concurrentes
        downloadSemaphore.withPermit {
            val task = getTask(taskId) ?: return
            if (task.status == DownloadStatus.FALLIDO) return

            updateTask(taskId) { it.copy(status = DownloadStatus.EXTRAYENDO) }

            var tempOutputFile: File? = null
            try {
                // 1. Extraer metadatos para obtener el título del video
                val infoRequest = YoutubeDLRequest(task.url)
                infoRequest.addOption("--no-playlist")
                
                val videoInfo = withContext(Dispatchers.IO) {
                    YoutubeDL.getInstance().getInfo(infoRequest)
                }
                
                val videoTitle = videoInfo.title ?: "video_${System.currentTimeMillis()}"
                val sanitizedTitle = sanitizeFilename(videoTitle)
                val ext = if (task.format == "MP3") "mp3" else if (task.format == "MKV") "mkv" else "mp4"
                val finalFileName = "$sanitizedTitle.$ext"
                val thumbnailUrl = videoInfo.thumbnail

                updateTask(taskId) {
                    it.copy(title = videoTitle, thumbnailUrl = thumbnailUrl, status = DownloadStatus.DESCARGANDO)
                }

                // 2. Definir ruta temporal en caché
                val cacheDir = context.externalCacheDir ?: context.cacheDir
                val tempFolder = File(cacheDir, "downloads")
                if (!tempFolder.exists()) tempFolder.mkdirs()

                // Usamos un nombre único para evitar colisiones en la caché
                val tempFile = File(tempFolder, "${UUID.randomUUID()}.$ext")
                tempOutputFile = tempFile

                // 3. Configurar petición de descarga
                val request = YoutubeDLRequest(task.url)
                request.addOption("--no-playlist")
                request.addOption("--no-mtime")
                
                // Usar acelerador aria2c si está disponible
                request.addOption("--external-downloader", "aria2c")
                request.addOption("--external-downloader-args", "aria2c:-c -j 8 -x 8 -s 8 -k 10M")

                // Configurar opciones de salida
                request.addOption("-o", tempFile.absolutePath)

                if (task.format == "MP3") {
                    request.addOption("-f", "bestaudio/best")
                    request.addOption("--extract-audio")
                    request.addOption("--audio-format", "mp3")
                    val audioQuality = if (task.quality.endsWith("k")) task.quality.removeSuffix("k") else task.quality
                    request.addOption("--audio-quality", audioQuality.ifBlank { "320" })
                } else {
                    request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
                    if (task.format == "MKV") {
                        request.addOption("--merge-output-format", "mkv")
                    } else {
                        request.addOption("--merge-output-format", "mp4")
                    }
                }

                // 4. Ejecutar descarga con monitoreo de progreso
                withContext(Dispatchers.IO) {
                    YoutubeDL.getInstance().execute(request, taskId) { progress, eta, line ->
                        // Parsear velocidad del log de yt-dlp si es posible
                        val speedStr = parseSpeedFromLine(line)
                        val isConverting = line.contains("[ExtractAudio]") || line.contains("[Merger]")
                        
                        updateTask(taskId) { currentTask ->
                            val newSpeed = if (isConverting) "" else if (speedStr.isNotBlank()) speedStr else currentTask.speed
                            val newEta = if (isConverting) "" else if (eta > 0) formatEta(eta) else currentTask.eta
                            val newStatus = if (isConverting) DownloadStatus.CONVIRTIENDO else DownloadStatus.DESCARGANDO

                            currentTask.copy(
                                progress = progress,
                                speed = newSpeed,
                                eta = newEta,
                                status = newStatus
                            )
                        }
                    }
                }

                // Verificar si se canceló en medio del proceso
                if (getTask(taskId)?.status == DownloadStatus.FALLIDO) {
                    return
                }

                // 5. Mover el archivo resultante de la caché al directorio de destino final
                val finalFile = File(tempFile.absolutePath) // A veces yt-dlp cambia la extensión real de forma dinámica
                val resolvedFile = findResultingFile(tempFile) ?: finalFile

                if (resolvedFile.exists() && resolvedFile.length() > 0) {
                    saveFileToDestination(resolvedFile, sanitizedTitle, finalFileName)
                    updateTask(taskId) {
                        it.copy(
                            status = DownloadStatus.COMPLETADO,
                            progress = 100f,
                            speed = "",
                            eta = ""
                        )
                    }
                } else {
                    throw Exception("El archivo descargado no se encuentra o está vacío")
                }

            } catch (e: Exception) {
                // Si la tarea no fue cancelada manualmente
                if (getTask(taskId)?.status != DownloadStatus.FALLIDO) {
                    Log.e("DownloadManager", "Error en la tarea $taskId", e)
                    updateTask(taskId) {
                        it.copy(
                            status = DownloadStatus.FALLIDO,
                            error = cleanErrorMessage(e.localizedMessage)
                        )
                    }
                }
            } finally {
                // Borrar archivos temporales de caché
                try {
                    tempOutputFile?.let {
                        if (it.exists()) it.delete()
                    }
                    // Limpiar posibles archivos temporales creados por el fusionador
                    tempOutputFile?.parentFile?.listFiles()?.forEach { file ->
                        if (file.name.contains(taskId) || file.name.contains(tempOutputFile.nameWithoutExtension)) {
                            file.delete()
                        }
                    }
                } catch (e: Exception) {
                    Log.e("DownloadManager", "Error al limpiar caché", e)
                }
            }
        }
    }

    private fun findResultingFile(baseFile: File): File? {
        if (baseFile.exists()) return baseFile
        
        // Si el archivo no existe con la extensión indicada, buscamos en el mismo directorio
        val parent = baseFile.parentFile ?: return null
        val baseName = baseFile.nameWithoutExtension
        val matchedFiles = parent.listFiles { _, name -> name.startsWith(baseName) }
        return matchedFiles?.firstOrNull()
    }

    private fun saveFileToDestination(sourceFile: File, subfolderName: String, fileName: String) {
        val folderUriStr = selectedFolderUri
        if (!folderUriStr.isNullOrBlank()) {
            // Guardar en la carpeta seleccionada de SAF
            val contextUri = Uri.parse(folderUriStr)
            val parentDoc = DocumentFile.fromTreeUri(context, contextUri)
            if (parentDoc != null && parentDoc.exists()) {
                // Crear subcarpeta con el nombre del video sanitizado
                var targetFolder = parentDoc.findFile(subfolderName)
                if (targetFolder == null || !targetFolder.isDirectory) {
                    targetFolder = parentDoc.createDirectory(subfolderName)
                }

                if (targetFolder != null && targetFolder.exists()) {
                    // Crear el archivo en la subcarpeta
                    var destDoc = targetFolder.findFile(fileName)
                    if (destDoc != null && destDoc.exists()) {
                        destDoc.delete()
                    }
                    destDoc = targetFolder.createFile("*/*", fileName)

                    if (destDoc != null) {
                        context.contentResolver.openOutputStream(destDoc.uri)?.use { outStream ->
                            FileInputStream(sourceFile).use { inStream ->
                                inStream.copyTo(outStream)
                            }
                        }
                        return
                    }
                }
            }
        }

        // Si SAF falla o no está configurado, guardar en descargas privadas de la app en almacenamiento externo
        val defaultDir = context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)
        val targetSubfolder = File(defaultDir, subfolderName)
        if (!targetSubfolder.exists()) targetSubfolder.mkdirs()
        
        val destFile = File(targetSubfolder, fileName)
        if (destFile.exists()) destFile.delete()

        FileInputStream(sourceFile).use { inStream ->
            FileOutputStream(destFile).use { outStream ->
                inStream.copyTo(outStream)
            }
        }
    }

    private fun getTask(taskId: String): DownloadTask? {
        return _tasks.value.firstOrNull { it.id == taskId }
    }

    private fun updateTask(taskId: String, block: (DownloadTask) -> DownloadTask) {
        _tasks.value = _tasks.value.map { task ->
            if (task.id == taskId) block(task) else task
        }
    }

    private fun sanitizeFilename(name: String): String {
        return name.replace(Regex("[\\\\/*?:\"<>|]"), "").trim()
    }

    private fun parseSpeedFromLine(line: String): String {
        // Case-insensitive, optional spaces: e.g. "1.5 MB/s", "142.3 KiB/s", "12.3MiB/s", "450KB/s"
        val pattern = Pattern.compile("([0-9.]+)\\s*([kmgKMG]i?[Bb]/s)", Pattern.CASE_INSENSITIVE)
        val matcher = pattern.matcher(line)
        if (matcher.find()) {
            return matcher.group(0)?.trim() ?: ""
        }
        return ""
    }

    private fun formatEta(seconds: Long): String {
        val h = seconds / 3600
        val m = (seconds % 3600) / 60
        val s = seconds % 60
        return if (h > 0) {
            String.format("%02d:%02d:%02d", h, m, s)
        } else {
            String.format("%02d:%02d", m, s)
        }
    }

    private fun cleanErrorMessage(message: String?): String {
        if (message == null) return "Error desconocido en la descarga"
        
        val lines = message.split("\n")
        val cleanLines = lines.filter { line ->
            val trimmed = line.trim()
            !trimmed.startsWith("WARNING:", ignoreCase = true) &&
            !trimmed.contains("is older than", ignoreCase = true) &&
            !trimmed.contains("update yt-dlp", ignoreCase = true) &&
            !trimmed.contains("many sites will fail", ignoreCase = true)
        }
        
        val result = cleanLines.joinToString("\n").trim()
        return if (result.isEmpty()) message.trim() else result
    }
}
