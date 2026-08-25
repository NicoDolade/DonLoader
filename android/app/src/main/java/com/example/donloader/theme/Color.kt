package com.example.donloader.theme

import androidx.compose.runtime.Composable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color

data class DonLoaderPalette(
    val background: Color,
    val surface: Color,
    val surfaceElevated: Color,
    val border: Color,
    val textPrimary: Color,
    val textSecondary: Color,
    val primary: Color,
    val success: Color,
    val amber: Color,
    val error: Color,
    val info: Color,
    val isLight: Boolean,
)

private const val DonLoaderGreenHex = 0xFF079C5E

val DonLoaderDarkPalette = DonLoaderPalette(
    background = Color(0xFF101216),
    surface = Color(0xFF181C22),
    surfaceElevated = Color(0xFF20262F),
    border = Color(0xFF2B333E),
    textPrimary = Color(0xFFF3F5F7),
    textSecondary = Color(0xFF9AA4B2),
    primary = Color(DonLoaderGreenHex),
    success = Color(0xFF43C995),
    amber = Color(0xFFF2B866),
    error = Color(DonLoaderGreenHex),
    info = Color(0xFF7FA8FF),
    isLight = false,
)

private val DonLoaderLightPalette = DonLoaderPalette(
    background = Color(0xFFF4F7F5),
    surface = Color(0xFFFFFFFF),
    surfaceElevated = Color(0xFFE8F1EC),
    border = Color(0xFFC8D8CF),
    textPrimary = Color(0xFF18211C),
    textSecondary = Color(0xFF5D6C63),
    primary = Color(DonLoaderGreenHex),
    success = Color(0xFF087F4C),
    amber = Color(0xFFAD6A00),
    error = Color(DonLoaderGreenHex),
    info = Color(0xFF3167C7),
    isLight = true,
)

private val DonLoaderOceanPalette = DonLoaderPalette(
    background = Color(0xFF0E1720),
    surface = Color(0xFF152431),
    surfaceElevated = Color(0xFF1E3442),
    border = Color(0xFF2D4A5B),
    textPrimary = Color(0xFFEFF7FA),
    textSecondary = Color(0xFF9BB1BD),
    primary = Color(DonLoaderGreenHex),
    success = Color(0xFF43C995),
    amber = Color(0xFFF2B866),
    error = Color(DonLoaderGreenHex),
    info = Color(0xFF7FA8FF),
    isLight = false,
)

private val DonLoaderSlatePalette = DonLoaderPalette(
    background = Color(0xFF17171F),
    surface = Color(0xFF22232D),
    surfaceElevated = Color(0xFF2D303C),
    border = Color(0xFF454856),
    textPrimary = Color(0xFFF4F3F8),
    textSecondary = Color(0xFFB1B0BE),
    primary = Color(DonLoaderGreenHex),
    success = Color(0xFF43C995),
    amber = Color(0xFFF2B866),
    error = Color(DonLoaderGreenHex),
    info = Color(0xFFB6A7FF),
    isLight = false,
)

private val DonLoaderSandPalette = DonLoaderPalette(
    background = Color(0xFFF6F2EB),
    surface = Color(0xFFFFFCF8),
    surfaceElevated = Color(0xFFEFE7DB),
    border = Color(0xFFD8CABA),
    textPrimary = Color(0xFF28251F),
    textSecondary = Color(0xFF756B5E),
    primary = Color(DonLoaderGreenHex),
    success = Color(0xFF187B50),
    amber = Color(0xFFA26700),
    error = Color(DonLoaderGreenHex),
    info = Color(0xFF3A65A8),
    isLight = true,
)

enum class DonLoaderThemeOption(
    val key: String,
    val label: String,
    val palette: DonLoaderPalette,
) {
    DARK("dark", "Oscuro", DonLoaderDarkPalette),
    LIGHT("light", "Claro", DonLoaderLightPalette),
    OCEAN("ocean", "Océano", DonLoaderOceanPalette),
    SLATE("slate", "Pizarra", DonLoaderSlatePalette),
    SAND("sand", "Arena", DonLoaderSandPalette),
    ;

    companion object {
        fun fromKey(key: String?): DonLoaderThemeOption =
            values().firstOrNull { it.key == key } ?: DARK
    }
}

val LocalDonLoaderPalette = staticCompositionLocalOf { DonLoaderDarkPalette }

/* Keep these names for the existing UI while resolving them from the palette. */
val DonLoaderBackground: Color
    @Composable get() = LocalDonLoaderPalette.current.background
val DonLoaderSurface: Color
    @Composable get() = LocalDonLoaderPalette.current.surface
val DonLoaderSurfaceElevated: Color
    @Composable get() = LocalDonLoaderPalette.current.surfaceElevated
val DonLoaderBorder: Color
    @Composable get() = LocalDonLoaderPalette.current.border
val DonLoaderTextPrimary: Color
    @Composable get() = LocalDonLoaderPalette.current.textPrimary
val DonLoaderTextSecondary: Color
    @Composable get() = LocalDonLoaderPalette.current.textSecondary
val DonLoaderCoral: Color
    @Composable get() = LocalDonLoaderPalette.current.primary
val DonLoaderGreen: Color
    @Composable get() = LocalDonLoaderPalette.current.success
val DonLoaderAmber: Color
    @Composable get() = LocalDonLoaderPalette.current.amber
val DonLoaderRed: Color
    @Composable get() = LocalDonLoaderPalette.current.error
val DonLoaderInfo: Color
    @Composable get() = LocalDonLoaderPalette.current.info
