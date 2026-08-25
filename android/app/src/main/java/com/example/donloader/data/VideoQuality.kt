package com.example.donloader.data

/** Normaliza alturas reales para presentarlas sin audio-only, ceros ni duplicados. */
fun normalizeVideoHeights(heights: Iterable<Int>): List<Int> =
    heights.filter { it > 0 }.distinct().sortedDescending()
