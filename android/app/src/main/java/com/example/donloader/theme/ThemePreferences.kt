package com.example.donloader.theme

import android.content.Context
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class DonLoaderThemeStore private constructor(context: Context) {

    private val preferences = context.applicationContext.getSharedPreferences(
        "donloader_prefs",
        Context.MODE_PRIVATE,
    )
    private val _theme = MutableStateFlow(
        DonLoaderThemeOption.fromKey(preferences.getString(THEME_KEY, null)),
    )

    val theme: StateFlow<DonLoaderThemeOption> = _theme.asStateFlow()

    fun setTheme(theme: DonLoaderThemeOption) {
        if (_theme.value == theme) return
        _theme.value = theme
        preferences.edit().putString(THEME_KEY, theme.key).apply()
    }

    companion object {
        private const val THEME_KEY = "theme_key"

        @Volatile
        private var instance: DonLoaderThemeStore? = null

        fun get(context: Context): DonLoaderThemeStore =
            instance ?: synchronized(this) {
                instance ?: DonLoaderThemeStore(context).also { instance = it }
            }
    }
}
