package com.example.donloader.service

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class DownloadServiceTest {

    @Test
    fun emptyQueueBeforeAnyDownloadDoesNotStopService() {
        assertFalse(shouldStopWhenIdle(hasObservedActiveTask = false, activeCount = 0))
    }

    @Test
    fun serviceStopsAfterAnActiveQueueBecomesIdle() {
        assertTrue(shouldStopWhenIdle(hasObservedActiveTask = true, activeCount = 0))
    }

    @Test
    fun activeQueueKeepsServiceRunning() {
        assertFalse(shouldStopWhenIdle(hasObservedActiveTask = true, activeCount = 1))
    }
}
