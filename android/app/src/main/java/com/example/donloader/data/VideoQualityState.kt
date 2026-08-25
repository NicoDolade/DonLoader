package com.example.donloader.data

/** Estado del análisis de resoluciones de video para la URL actual. */
sealed class VideoQualityState {
    object Idle : VideoQualityState()

    data class Loading(val url: String) : VideoQualityState()

    /** Una lista vacía significa que el sitio no informó alturas: usar mejor disponible. */
    data class Ready(val url: String, val heights: List<Int>) : VideoQualityState()

    data class Error(val url: String, val message: String) : VideoQualityState()
}
