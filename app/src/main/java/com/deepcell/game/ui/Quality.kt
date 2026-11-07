package com.deepcell.game.ui

import android.app.ActivityManager
import android.content.Context

/**
 * Detail level. "Auto" picks Low on weak phones (Android's low-RAM flag, a small app memory
 * budget, or four cores or fewer). Low drops decoration that costs frame time: lamp flicker,
 * storage pulse, dust and spore bursts, title dust and drones, the title's blur crossfade,
 * and runs the game loop at 20 updates a second instead of 30.
 */
object Quality {
    const val AUTO = "auto"
    const val HIGH = "high"
    const val LOW = "low"

    /** Order of R.array.detail_names. */
    val VALUES = listOf(AUTO, HIGH, LOW)

    fun isWeakDevice(context: Context): Boolean {
        val am = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        return am.isLowRamDevice || am.memoryClass <= 128 || Runtime.getRuntime().availableProcessors() <= 4
    }

    fun lowDetail(context: Context, setting: String): Boolean = when (setting) {
        LOW -> true
        HIGH -> false
        else -> isWeakDevice(context)
    }
}
