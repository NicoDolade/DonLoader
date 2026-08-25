package com.example.donloader.ui.main

import com.example.donloader.data.DownloadTask
import com.example.donloader.data.normalizeVideoHeights
import org.junit.Assert.assertEquals
import org.junit.Test

class MainScreenViewModelTest {

    @Test
    fun normalizedHeightsAreUniquePositiveAndDescending() {
        assertEquals(
            listOf(2160, 1080, 720),
            normalizeVideoHeights(listOf(0, 720, 1080, 720, -1, 2160)),
        )
    }

    @Test
    fun downloadTaskKeepsSelectedVideoQuality() {
        val task = DownloadTask(
            id = "test",
            url = "https://example.test/video",
            format = "MP4",
            videoQuality = 720,
        )

        assertEquals(720, task.videoQuality)
    }
}
