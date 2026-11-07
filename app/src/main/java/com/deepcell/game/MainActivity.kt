package com.deepcell.game

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.deepcell.game.data.GameDatabase
import com.deepcell.game.ui.Notifier
import com.deepcell.game.ui.TitleSlideshow

/** Title screen: animated camera shots, bunker name, Play (new game) and Continue (load save). */
class MainActivity : AppCompatActivity() {

    private lateinit var db: GameDatabase
    private lateinit var nameInput: EditText
    private lateinit var continueButton: Button
    private lateinit var saveSummary: TextView
    private lateinit var slideshow: TitleSlideshow

    /** Play replaces an existing save only after a second tap. */
    private var replaceConfirmed = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        db = GameDatabase(this)
        nameInput = findViewById(R.id.bunkerNameInput)
        continueButton = findViewById(R.id.continueButton)
        saveSummary = findViewById(R.id.saveSummary)

        findViewById<Button>(R.id.playButton).setOnClickListener { onPlay() }
        continueButton.setOnClickListener { openGame(newGame = false) }

        slideshow = TitleSlideshow(
            findViewById(R.id.titleStage),
            findViewById<ImageView>(R.id.titleShot),
            findViewById<ImageView>(R.id.titleShotBlur),
            findViewById(R.id.titleVeil)
        )

        Notifier.createChannel(this)
        askNotificationPermission()
    }

    override fun onResume() {
        super.onResume()
        // Refresh every time: the save may have been reset in Settings.
        replaceConfirmed = false
        slideshow.start()
        val state = db.loadState()
        continueButton.isEnabled = state != null
        saveSummary.text = if (state != null) {
            getString(R.string.save_summary, state.bunkerName, state.wave)
        } else {
            ""
        }
    }

    override fun onPause() {
        // Lifecycle (Module 5): no animation work while the screen is hidden.
        slideshow.stop()
        super.onPause()
    }

    private fun onPlay() {
        if (db.hasSave() && !replaceConfirmed) {
            replaceConfirmed = true
            Toast.makeText(this, R.string.tap_again_to_replace, Toast.LENGTH_LONG).show()
            return
        }
        val typed = nameInput.text.toString().trim()
        val name = if (typed.isEmpty()) getString(R.string.default_bunker_name) else typed
        db.newGame(name, GameActivity.BASE_HATCH_HP)
        openGame(newGame = true)
    }

    /** Explicit Intent with extras (Module 7). GameActivity reads them with intent.extras. */
    private fun openGame(newGame: Boolean) {
        val intent = Intent(this, GameActivity::class.java)
        intent.putExtra(GameActivity.EXTRA_NEW_GAME, newGame)
        db.loadState()?.let { intent.putExtra(GameActivity.EXTRA_BUNKER_NAME, it.bunkerName) }
        startActivity(intent)
    }

    /** Android 13+ asks the player before an app may post notifications. */
    private fun askNotificationPermission() {
        if (Build.VERSION.SDK_INT >= 33 &&
            ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
            != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1)
        }
    }

    override fun onDestroy() {
        db.close()
        super.onDestroy()
    }
}
