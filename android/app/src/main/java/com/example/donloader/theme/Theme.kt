package com.example.donloader.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider

private fun donLoaderColorScheme(palette: DonLoaderPalette) =
    if (palette.isLight) {
        lightColorScheme(
            primary = palette.primary,
            onPrimary = palette.background,
            secondary = palette.info,
            onSecondary = palette.background,
            tertiary = palette.amber,
            background = palette.background,
            onBackground = palette.textPrimary,
            surface = palette.surface,
            onSurface = palette.textPrimary,
            surfaceVariant = palette.surfaceElevated,
            onSurfaceVariant = palette.textSecondary,
            outline = palette.border,
            error = palette.error,
            onError = palette.background,
        )
    } else {
        darkColorScheme(
            primary = palette.primary,
            onPrimary = palette.background,
            secondary = palette.info,
            onSecondary = palette.background,
            tertiary = palette.amber,
            background = palette.background,
            onBackground = palette.textPrimary,
            surface = palette.surface,
            onSurface = palette.textPrimary,
            surfaceVariant = palette.surfaceElevated,
            onSurfaceVariant = palette.textSecondary,
            outline = palette.border,
            error = palette.error,
            onError = palette.background,
        )
    }

@Composable
fun DonLoaderTheme(
    theme: DonLoaderThemeOption = DonLoaderThemeOption.DARK,
    darkTheme: Boolean = true,
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit,
) {
    val effectiveTheme = if (theme == DonLoaderThemeOption.DARK && !darkTheme) {
        DonLoaderThemeOption.LIGHT
    } else {
        theme
    }
    val palette = effectiveTheme.palette

    CompositionLocalProvider(LocalDonLoaderPalette provides palette) {
        MaterialTheme(
            colorScheme = donLoaderColorScheme(palette),
            typography = Typography,
            content = content,
        )
    }
}
