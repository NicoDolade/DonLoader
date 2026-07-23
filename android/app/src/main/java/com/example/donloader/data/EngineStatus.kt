package com.example.donloader.data

sealed class EngineStatus {
    /** Estado inicial / sin chequeos hechos. */
    object Unknown : EngineStatus()

    /** Actualización de yt-dlp en curso (incluye descarga del binario). */
    data class Updating(val message: String = "Actualizando motor yt-dlp...") : EngineStatus()

    /** yt-dlp está al día y listo para usar. */
    object UpToDate : EngineStatus()

    /** La última actualización falló (sin red, rate-limit de GitHub, etc.). */
    data class Failed(val message: String) : EngineStatus()
}