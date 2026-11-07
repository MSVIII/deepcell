package com.deepcell.game.ui

import com.deepcell.game.R
import com.deepcell.game.model.Survivor

/** Picture, icon and description for each survivor job (Survivors screen and job picker). */
object Jobs {
    fun figure(job: String): Int = when (job) {
        Survivor.JOB_ROOF -> R.drawable.survivor_guard
        Survivor.JOB_FARM -> R.drawable.survivor_farmer
        Survivor.JOB_COLLECTOR -> R.drawable.survivor_collector
        else -> R.drawable.survivor_digger
    }

    fun icon(job: String): Int = when (job) {
        Survivor.JOB_ROOF -> R.drawable.icon_tab_defense
        Survivor.JOB_FARM -> R.drawable.icon_food
        Survivor.JOB_COLLECTOR -> R.drawable.icon_up_collector
        else -> R.drawable.icon_scrap
    }

    fun effect(job: String): Int = when (job) {
        Survivor.JOB_ROOF -> R.string.job_roof_effect
        Survivor.JOB_FARM -> R.string.job_farm_effect
        Survivor.JOB_COLLECTOR -> R.string.job_collector_effect
        else -> R.string.job_dig_effect
    }
}
