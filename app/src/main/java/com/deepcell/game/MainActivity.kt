package com.deepcell.game

import android.Manifest
import android.app.Dialog
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.media.AudioManager
import android.os.Build
import android.os.Bundle
import android.view.View
import android.view.Window
import android.view.WindowManager
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.deepcell.game.data.GameDatabase
import com.deepcell.game.ui.Notifier
import com.deepcell.game.ui.Quality
import com.deepcell.game.ui.TitleAmbience
import com.deepcell.game.ui.TitleSlideshow

/**
 * Title screen: animated camera shots with drifting dust, the logo, and the menu.
 * Continue loads the save (its card shows the bunker), New Game asks for a bunker name in a
 * dialog, Settings opens the settings screen.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var db: GameDatabase
    private lateinit var continueButton: Button
    private lateinit var saveCard: View
    private lateinit var slideshow: TitleSlideshow
    private lateinit var ambience: TitleAmbience

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        volumeControlStream = AudioManager.STREAM_MUSIC   // volume keys change game sounds

        db = GameDatabase(this)
        continueButton = findViewById(R.id.continueButton)
        saveCard = findViewById(R.id.saveCard)

        continueButton.setOnClickListener { openGame(newGame = false) }
        findViewById<Button>(R.id.newGameButton).setOnClickListener { askBunkerName() }
        findViewById<Button>(R.id.menuSettingsButton).setOnClickListener {
            val intent = Intent(this, SettingsActivity::class.java)
            intent.putExtra(SettingsActivity.EXTRA_FROM_MENU, true)
            db.loadState()?.let {
                intent.putExtra(SettingsActivity.EXTRA_BUNKER_NAME, it.bunkerName)
                intent.putExtra(SettingsActivity.EXTRA_WAVE, it.wave)
            }
            startActivity(intent)
        }

        val low = Quality.lowDetail(this, db.getSetting(GameDatabase.SETTING_DETAIL, Quality.AUTO))
        ambience = TitleAmbience(findViewById(R.id.titleFx), moteCount = if (low) 0 else 22, drones = !low)
        slideshow = TitleSlideshow(
            findViewById(R.id.titleStage),
            findViewById<ImageView>(R.id.titleShot),
            findViewById<ImageView>(R.id.titleShotBlur),
            findViewById(R.id.titleVeil)
            , blurCrossfade = !low
        ) { shot -> ambience.onShot(shot) }

        Notifier.createChannel(this)
        askNotificationPermission()
    }

    override fun onResume() {
        super.onResume()
        // Refresh every time: the save may have been reset in Settings.
        slideshow.start()
        ambience.start()
        val state = db.loadState()
        if (state == null) {
            saveCard.visibility = View.GONE
            continueButton.visibility = View.GONE
        } else {
            saveCard.visibility = View.VISIBLE
            continueButton.visibility = View.VISIBLE
            findViewById<TextView>(R.id.saveName).text = state.bunkerName
            findViewById<TextView>(R.id.saveWave).text = getString(R.string.wave_short, state.wave)
            findViewById<TextView>(R.id.saveScrap).text = state.scrap.toString()
            findViewById<TextView>(R.id.saveFood).text = state.food.toString()
            findViewById<TextView>(R.id.saveCrew).text = db.survivorCount().toString()
        }
    }

    override fun onPause() {
        // Lifecycle (Module 5): no animation work while the screen is hidden.
        slideshow.stop()
        ambience.stop()
        super.onPause()
    }

    /** New Game: a small dialog asks for the bunker name; it warns when a save will be replaced. */
    private fun askBunkerName() {
        val dialog = Dialog(this)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(R.layout.dialog_new_game)
        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        dialog.window?.setLayout(
            (resources.displayMetrics.widthPixels * 0.86f).toInt(), WindowManager.LayoutParams.WRAP_CONTENT
        )
        val saved = db.loadState()
        val warning = dialog.findViewById<TextView>(R.id.newGameWarning)
        if (saved != null) {
            warning.text = getString(R.string.replace_warning, saved.bunkerName, saved.wave)
            warning.visibility = View.VISIBLE
        }
        val name = dialog.findViewById<EditText>(R.id.newGameName)
        val start = {
            val typed = name.text.toString().trim()
            val bunker = if (typed.isEmpty()) getString(R.string.default_bunker_name) else typed
            db.newGame(bunker, GameActivity.BASE_HATCH_HP)
            dialog.dismiss()
            openGame(newGame = true)
        }
        dialog.findViewById<Button>(R.id.newGameStart).setOnClickListener { start() }
        dialog.findViewById<Button>(R.id.newGameCancel).setOnClickListener { dialog.dismiss() }
        name.setOnEditorActionListener { _, _, _ -> start(); true }
        dialog.show()
        name.requestFocus()
        dialog.window?.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_STATE_VISIBLE)
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
