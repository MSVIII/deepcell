package com.deepcell.game

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.CheckBox
import android.widget.ImageButton
import android.widget.Spinner
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import android.widget.Switch
import com.deepcell.game.data.GameDatabase

/** Sound switch, difficulty Spinner, reset save, Share (implicit ACTION_SEND) and Main menu. */
class SettingsActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_BUNKER_NAME = "bunker_name"
        const val EXTRA_WAVE = "wave"
    }

    private lateinit var db: GameDatabase

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)
        db = GameDatabase(this)

        // Sound: GameActivity reads this on resume and mutes its sound effects (ui/Sfx).
        val soundSwitch = findViewById<Switch>(R.id.soundSwitch)
        soundSwitch.isChecked = db.getSetting(GameDatabase.SETTING_SOUND, "true") == "true"
        soundSwitch.setOnCheckedChangeListener { _, isChecked ->
            db.setSetting(GameDatabase.SETTING_SOUND, isChecked.toString())
        }

        // Difficulty: index into R.array.difficulty_names. GameActivity scales enemy HP with it.
        val spinner = findViewById<Spinner>(R.id.difficultySpinner)
        val adapter = ArrayAdapter.createFromResource(
            this, R.array.difficulty_names, android.R.layout.simple_spinner_item
        )
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        spinner.adapter = adapter
        spinner.setSelection(db.getSetting(GameDatabase.SETTING_DIFFICULTY, "1").toInt())
        spinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                db.setSetting(GameDatabase.SETTING_DIFFICULTY, position.toString())
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        // Reset save: the CheckBox must be ticked first so it can't happen by accident.
        val confirm = findViewById<CheckBox>(R.id.resetConfirm)
        val resetButton = findViewById<Button>(R.id.resetButton)
        resetButton.isEnabled = false
        confirm.setOnCheckedChangeListener { _, isChecked -> resetButton.isEnabled = isChecked }
        resetButton.setOnClickListener {
            db.resetSave()
            Toast.makeText(this, R.string.save_deleted, Toast.LENGTH_SHORT).show()
            // Back to the title screen; CLEAR_TOP closes the game screen underneath.
            val intent = Intent(this, MainActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
            startActivity(intent)
            finish()
        }

        // Share: implicit Intent, the system lets the player pick an app (Module 7).
        val extras = intent.extras
        val bunkerName = extras?.getString(EXTRA_BUNKER_NAME) ?: getString(R.string.default_bunker_name)
        val wave = extras?.getInt(EXTRA_WAVE, 1) ?: 1
        findViewById<Button>(R.id.shareButton).setOnClickListener {
            val send = Intent(Intent.ACTION_SEND)
            send.type = "text/plain"
            send.putExtra(Intent.EXTRA_TEXT, getString(R.string.share_text, bunkerName, wave))
            startActivity(Intent.createChooser(send, getString(R.string.share)))
        }

        // Main menu: back to the title screen. The game already saved in its onPause when this
        // screen opened; CLEAR_TOP closes the game screen underneath (explicit Intent, Module 7).
        findViewById<Button>(R.id.mainMenuButton).setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
            startActivity(intent)
            finish()
        }

        findViewById<ImageButton>(R.id.settingsBack).setOnClickListener { finish() }
    }

    override fun onDestroy() {
        db.close()
        super.onDestroy()
    }
}
