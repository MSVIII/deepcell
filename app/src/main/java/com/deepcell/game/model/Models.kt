package com.deepcell.game.model

import android.widget.ImageView

// Plain Kotlin data classes (Module 3). Every game object lives here so
// groupmates can find them in one place.

/** One row of assets/upgrades.json. type is "defense", "supplies" or "automation". */
data class Upgrade(
    val id: String,
    val name: String,
    val type: String,
    val description: String,
    val baseCost: Int,
    val costGrowth: Double,
    val maxLevel: Int
) {
    /** Scrap price of the next level when the current level is [level]. */
    fun costAt(level: Int): Int = Math.round(baseCost * Math.pow(costGrowth, level.toDouble())).toInt()
}

/**
 * An underground room. Tapping (or a machine) adds progress; a full bar pays out
 * [yieldPerFill] of [resource] ("scrap" or "food") and empties again.
 */
data class Floor(
    val id: String,
    val name: String,
    val resource: String,
    val maxProgress: Int,
    val yieldPerFill: Int,
    var progress: Int = 0,
    var automated: Boolean = false,
    /** Amount the room just paid out; the adapter shows it as a "+5" popup, then sets it back to 0. */
    var pendingPopup: Int = 0
) {
    /** Adds progress and returns how many times the bar filled up. */
    fun addProgress(amount: Int): Int {
        val total = progress + amount
        progress = total % maxProgress
        return total / maxProgress
    }
}

/** One enemy kind from assets/waves.json ("scout", "shrike", "bomber", "boss"). */
data class EnemyType(
    val id: String,
    val name: String,
    val hp: Int,
    val speedDp: Float,
    val damage: Int,
    val reward: Int,
    val sizeDp: Int
)

/**
 * A live enemy in the sky. [view] is the ImageView the Handler loop moves down.
 * It drifts from [startX] towards [targetX] (above the bunker) as it falls.
 */
data class Enemy(
    val type: EnemyType,
    var hp: Int,
    var y: Float,
    val startX: Float,
    val targetX: Float,
    val view: ImageView
)

/** One wave from assets/waves.json, already expanded to a spawn queue of type ids. */
data class Wave(
    val spawnMs: Long,
    val enemyIds: List<String>
)

/** A bunker resident. job is one of [Survivor.JOBS]. */
data class Survivor(
    val id: Long,
    val name: String,
    var job: String
) {
    companion object {
        const val JOB_ROOF = "Roof"
        const val JOB_DIG = "Scrap Dig"
        const val JOB_FARM = "Mushroom Farm"
        val JOBS = listOf(JOB_ROOF, JOB_DIG, JOB_FARM)
    }
}

/** Everything that is saved to SQLite. Loaded in onResume, saved in onPause. */
data class GameState(
    var bunkerName: String,
    var scrap: Int,
    var food: Int,
    var wave: Int,
    var hatchHp: Int,
    var digProgress: Int,
    var farmProgress: Int,
    var lastPlayed: Long,
    /** Level of every defense/supplies upgrade, by upgrade id. */
    val upgradeLevels: MutableMap<String, Int> = mutableMapOf(),
    /** Level of every automation machine, by upgrade id. Level 0 means not owned. */
    val automationLevels: MutableMap<String, Int> = mutableMapOf()
) {
    fun levelOf(upgrade: Upgrade): Int =
        if (upgrade.type == TYPE_AUTOMATION) automationLevels[upgrade.id] ?: 0
        else upgradeLevels[upgrade.id] ?: 0

    fun setLevel(upgrade: Upgrade, level: Int) {
        if (upgrade.type == TYPE_AUTOMATION) automationLevels[upgrade.id] = level
        else upgradeLevels[upgrade.id] = level
    }

    /** Level by id, looking in both maps. */
    fun level(id: String): Int = upgradeLevels[id] ?: automationLevels[id] ?: 0

    companion object {
        const val TYPE_DEFENSE = "defense"
        const val TYPE_SUPPLIES = "supplies"
        const val TYPE_AUTOMATION = "automation"
    }
}
