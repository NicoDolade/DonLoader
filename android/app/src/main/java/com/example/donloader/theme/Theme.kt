package com.example.donloader.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

private val DonLoaderColorScheme = darkColorScheme(
  primary = DonLoaderCoral,
  onPrimary = DonLoaderBackground,
  secondary = DonLoaderInfo,
  onSecondary = DonLoaderBackground,
  tertiary = DonLoaderAmber,
  background = DonLoaderBackground,
  onBackground = DonLoaderTextPrimary,
  surface = DonLoaderSurface,
  onSurface = DonLoaderTextPrimary,
  surfaceVariant = DonLoaderSurfaceElevated,
  onSurfaceVariant = DonLoaderTextSecondary,
  outline = DonLoaderBorder,
  error = DonLoaderRed,
  onError = DonLoaderBackground,
)

@Composable
fun DonLoaderTheme(
  darkTheme: Boolean = true,
  dynamicColor: Boolean = false,
  content: @Composable () -> Unit,
) {
  // La identidad es oscura y fija; se mantienen los parámetros para no romper
  // llamadas existentes de la aplicación.
  MaterialTheme(colorScheme = DonLoaderColorScheme, typography = Typography, content = content)
}
