package com.burrownine.game

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.ImageButton
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.burrownine.game.data.GameDatabase
import com.burrownine.game.model.Survivor
import com.burrownine.game.ui.SurvivorAdapter

/**
 * Survivor list. Tap a survivor to move them to the next job.
 * Roof: +1 tap damage. Scrap Dig / Mushroom Farm: +1 progress per manual tap.
 * Survivors only help manual work; machines are what earn while the app is closed.
 */
class SurvivorsActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_BUNKER_NAME = "bunker_name"
        const val RECRUIT_FOOD_COST = 15
    }

    private lateinit var db: GameDatabase
    private lateinit var foodText: TextView
    private lateinit var adapter: SurvivorAdapter
    private var survivors: List<Survivor> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_survivors)
        db = GameDatabase(this)

        // Extra from GameActivity (Module 7).
        val bunkerName = intent.extras?.getString(EXTRA_BUNKER_NAME) ?: getString(R.string.default_bunker_name)
        findViewById<TextView>(R.id.survivorsTitle).text = getString(R.string.survivors_title, bunkerName)
        foodText = findViewById(R.id.survivorsFood)

        adapter = SurvivorAdapter(this, survivors)
        val listView = findViewById<ListView>(R.id.survivorList)
        listView.adapter = adapter
        listView.setOnItemClickListener { _, _, position, _ ->
            val survivor = survivors[position]
            val next = Survivor.JOBS[(Survivor.JOBS.indexOf(survivor.job) + 1) % Survivor.JOBS.size]
            db.updateSurvivorJob(survivor.id, next)
            refresh()
        }

        val nameInput = findViewById<EditText>(R.id.recruitName)
        val recruitButton = findViewById<Button>(R.id.recruitButton)
        recruitButton.text = getString(R.string.recruit_cost, RECRUIT_FOOD_COST)
        recruitButton.setOnClickListener {
            val name = nameInput.text.toString().trim()
            val food = db.getFood()
            when {
                name.isEmpty() -> Toast.makeText(this, R.string.enter_a_name, Toast.LENGTH_SHORT).show()
                food < RECRUIT_FOOD_COST -> Toast.makeText(this, R.string.not_enough_food, Toast.LENGTH_SHORT).show()
                else -> {
                    db.recruitSurvivor(name, Survivor.JOB_DIG, food - RECRUIT_FOOD_COST)
                    nameInput.text.clear()
                    Toast.makeText(this, getString(R.string.recruited, name), Toast.LENGTH_SHORT).show()
                    refresh()
                }
            }
        }

        findViewById<ImageButton>(R.id.survivorsBack).setOnClickListener { finish() }
        refresh()
    }

    private fun refresh() {
        survivors = db.getSurvivors()
        foodText.text = db.getFood().toString()
        adapter.update(survivors)
    }

    override fun onDestroy() {
        db.close()
        super.onDestroy()
    }
}
