package com.example.donloader.data

data class DownloadTask(
    val id: String,
    val url: String,
    val title: String = "",
    val status: DownloadStatus = DownloadStatus.EN_COLA,
    val progress: Float = 0f,
    val speed: String = "",
    val eta: String = "",
    val format: String = "MP4",
    val quality: String = "",
    val thumbnailUrl: String? = null,
    val error: String? = null
) {
    val displayTitle: String
        get() = title.ifBlank { url }
}
