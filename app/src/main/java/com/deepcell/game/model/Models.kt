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
    var pendingPopup: Int = 0,
    /** Finished resources waiting in the room's storage. Tap the room or send the Collector. */
    var stock: Int = 0,
    /** Most the storage holds. Work stops while it is full. */
    var capacity: Int = 50
) {
    val isFull: Boolean get() = stock >= capacity

    /** Adds progress and returns how many times the bar filled up. */
    fun addProgress(amount: Int): Int {
        val total = progress + amount
        progress = total % maxProgress
        return total / maxProgress
    }

    /**
     * Work done in this room: fills the bar and puts each full bar's payout into storage.
     * Nothing happens while the storage is full. Returns the amount stored.
     */
    fun work(amount: Int): Int {
        if (isFull || amount <= 0) return 0
        val stored = Math.min(addProgress(amount) * yieldPerFill, capacity - stock)
        stock += stored
        if (isFull) progress = 0
        return stored
    }

    /** Empties the storage and returns what was in it. */
    fun takeStock(): Int {
        val amount = stock
        stock = 0
        return amount
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
    val view: ImageView,
    /** Start point of the flight sway, so enemies don't bob in step. */
    val phase: Float = 0f,
    /** Falling speed; later waves fly faster than the type's base speed. */
    val speedDp: Float = type.speedDp,
    /** HP when it spawned, for the boss health bar. */
    val maxHp: Int = hp
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
        const val JOB_COLLECTOR = "Collector"
        val JOBS = listOf(JOB_ROOF, JOB_DIG, JOB_FARM, JOB_COLLECTOR)

        /** Names for new recruits; one is picked at random, avoiding names already in the bunker. */
        private val NAMES = listOf(
            "Ada", "Bram", "Cass", "Dov", "Edda", "Finn", "Greta", "Hollis", "Ines", "Jory",
            "Kit", "Lio", "Mina", "Nils", "Oona", "Pell", "Quinn", "Rhea", "Sol", "Tamsin",
            "Ulla", "Vik", "Wren", "Yara", "Zed", "Abel", "Brix", "Cora", "Dace", "Elsa",
            "Fenn", "Gil", "Hana", "Ivo", "Juno", "Kade", "Lark", "Moss", "Nell", "Otto",
            "Pia", "Rook", "Sage", "Teo", "Ula", "Vera", "Wade", "Yuri", "Zia", "Bex"
        )

        fun randomName(taken: Collection<String>): String {
            val free = NAMES.filter { it !in taken }
            if (free.isNotEmpty()) return free.random()
            // Every name used: add a number to one.
            var n = 2
            while (true) {
                val name = "${NAMES.random()} $n"
                if (name !in taken) return name
                n++
            }
        }
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
    var digStock: Int = 0,
    var farmStock: Int = 0,
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
