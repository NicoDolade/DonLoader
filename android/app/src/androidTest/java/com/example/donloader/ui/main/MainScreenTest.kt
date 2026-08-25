package com.example.donloader.ui.main

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import com.example.donloader.data.VideoQualityState
import com.example.donloader.theme.DonLoaderTheme
import org.junit.Rule
import org.junit.Test

class MainScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun videoQualityPickerShowsAnalyzedHeights() {
        composeTestRule.setContent {
            DonLoaderTheme {
                VideoQualityPicker(
                    state = VideoQualityState.Ready("https://example.test/video", listOf(1080, 720, 480)),
                    selectedQuality = 720,
                    onQualitySelected = {},
                    onAnalyze = {},
                    analyzeEnabled = true,
                )
            }
        }

        composeTestRule.onNodeWithText("720p").assertIsDisplayed()
        composeTestRule.onNodeWithText("3 calidades disponibles · la mayor se selecciona por defecto").assertIsDisplayed()
    }

    @Test
    fun videoQualityPickerSupportsUnknownHeight() {
        composeTestRule.setContent {
            DonLoaderTheme {
                VideoQualityPicker(
                    state = VideoQualityState.Ready("https://example.test/video", emptyList()),
                    selectedQuality = null,
                    onQualitySelected = {},
                    onAnalyze = {},
                    analyzeEnabled = true,
                )
            }
        }

        composeTestRule.onNodeWithText("Mejor disponible").assertIsDisplayed()
    }
}
