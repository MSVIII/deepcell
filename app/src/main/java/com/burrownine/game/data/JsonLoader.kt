package com.burrownine.game.data

import android.content.Context
import com.burrownine.game.model.EnemyType
import com.burrownine.game.model.Upgrade
import com.burrownine.game.model.Wave
import org.json.JSONArray
import org.json.JSONObject

/**
 * Reads the balance files in assets/ with JSONObject and JSONArray (Module 10).
 * To rebalance the game, change the JSON files, not this code.
 */
object JsonLoader {

    private fun readAsset(context: Context, fileName: String): String =
        context.assets.open(fileName).bufferedReader().use { it.readText() }

    fun loadUpgrades(context: Context): List<Upgrade> {
        val root = JSONObject(readAsset(context, "upgrades.json"))
        val array: JSONArray = root.getJSONArray("upgrades")
        val result = ArrayList<Upgrade>()
        for (i in 0 until array.length()) {
            val o = array.getJSONObject(i)
            result.add(
                Upgrade(
                    id = o.getString("id"),
                    name = o.getString("name"),
                    type = o.getString("type"),
                    description = o.getString("description"),
                    baseCost = o.getInt("baseCost"),
                    costGrowth = o.getDouble("costGrowth"),
                    maxLevel = o.getInt("maxLevel")
                )
            )
        }
        return result
    }

    /** Parsed waves.json: enemy kinds, the 10-wave cycle, and the HP scaling per cycle. */
    class WaveData(
        val enemyTypes: Map<String, EnemyType>,
        val waves: List<Wave>,
        val hpScalePerCycle: Double
    )

    fun loadWaves(context: Context): WaveData {
        val root = JSONObject(readAsset(context, "waves.json"))

        val types = HashMap<String, EnemyType>()
        val typeArray = root.getJSONArray("enemyTypes")
        for (i in 0 until typeArray.length()) {
            val o = typeArray.getJSONObject(i)
            val type = EnemyType(
                id = o.getString("id"),
                name = o.getString("name"),
                hp = o.getInt("hp"),
                speedDp = o.getDouble("speedDp").toFloat(),
                damage = o.getInt("damage"),
                reward = o.getInt("reward"),
                sizeDp = o.getInt("sizeDp")
            )
            types[type.id] = type
        }

        val waves = ArrayList<Wave>()
        val waveArray = root.getJSONArray("waves")
        for (i in 0 until waveArray.length()) {
            val o = waveArray.getJSONObject(i)
            val ids = ArrayList<String>()
            val groups = o.getJSONArray("enemies")
            for (g in 0 until groups.length()) {
                val group = groups.getJSONObject(g)
                repeat(group.getInt("count")) { ids.add(group.getString("type")) }
            }
            waves.add(Wave(o.getLong("spawnMs"), ids))
        }
        return WaveData(types, waves, root.getDouble("hpScalePerCycle"))
    }
}
