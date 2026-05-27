package com.example.donloader

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import com.example.donloader.theme.DonLoaderTheme
import com.example.donloader.updater.AppUpdater

class MainActivity : ComponentActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    enableEdgeToEdge()

    // Limpiar caché de actualizaciones antiguas al iniciar
    try {
        AppUpdater(this).clearUpdateCache()
    } catch (e: Exception) {
        // Ignorar errores de limpieza
    }

    // Ocultar la barra de notificaciones y la barra de navegación de forma inmersiva transitoria
    val windowInsetsController = WindowCompat.getInsetsController(window, window.decorView)
    windowInsetsController.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
    windowInsetsController.hide(WindowInsetsCompat.Type.systemBars())

    setContent {
      DonLoaderTheme { Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) { MainNavigation() } }
    }
  }
}
