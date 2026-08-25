package com.example.donloader.theme

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ThemeTest {

    @Test
    fun knownThemeKeysRestoreTheExpectedOption() {
        assertEquals(DonLoaderThemeOption.OCEAN, DonLoaderThemeOption.fromKey("ocean"))
        assertEquals(DonLoaderThemeOption.DARK, DonLoaderThemeOption.fromKey("missing"))
    }

    @Test
    fun allThemesKeepTheBrandAccent() {
        DonLoaderThemeOption.values().forEach { option ->
            assertTrue(option.palette.primary == DonLoaderDarkPalette.primary)
        }
    }
}
