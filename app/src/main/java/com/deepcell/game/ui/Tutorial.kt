package com.deepcell.game.ui

import android.app.Activity
import android.view.Gravity
import android.view.View
import android.view.animation.AnimationUtils
import android.widget.Button
import android.widget.FrameLayout
import android.widget.TextView
import com.deepcell.game.R
import com.deepcell.game.data.GameDatabase

/**
 * The first-game tutorial: a card with one instruction and an arrow pointing at the thing to
 * tap. Offered when a new game starts (MainActivity). The step is saved in settings, so it
 * carries on across the Game and Survivors screens and after the app is closed.
 *
 * Steps that wait for the player to do something (shoot, dig, recruit) move on when the game
 * calls [complete] with that step; explanation steps have a "Got it" button.
 *
 * Each screen creates one with the overlay from view_tutorial.xml and calls [show] with a
 * function that says which view each step points at on that screen (null: not this screen).
 */
class Tutorial(
    private val activity: Activity,
    private val db: GameDatabase,
    private val target: (Int) -> View?
) {

    companion object {
        const val OFF = 0
        const val SHOOT = 1        // tap drones
        const val DIG = 2          // tap Scrap Dig, collect the storage
        const val RECRUIT = 3      // open Survivors, recruit
        const val JOBS = 4         // (Survivors screen) jobs explained
        const val STORAGE = 5      // workers fill storage; tap or Collector
        const val UPGRADES = 6     // spend scrap; repair the hatch
        private const val LAST = UPGRADES

        /** Steps that are explained with a "Got it" button instead of waiting for an action. */
        private val EXPLAIN = setOf(JOBS, STORAGE, UPGRADES)
        /** Steps about the whole sky: no arrow, the card says where to look. */
        private val NO_ARROW = setOf(SHOOT)

        private val TEXT = mapOf(
            SHOOT to R.string.tutorial_shoot,
            DIG to R.string.tutorial_dig,
            RECRUIT to R.string.tutorial_recruit,
            JOBS to R.string.tutorial_jobs,
            STORAGE to R.string.tutorial_storage,
            UPGRADES to R.string.tutorial_upgrades
        )
    }

    private val layer: FrameLayout = activity.findViewById(R.id.tutorialLayer)
    private val arrow: View = activity.findViewById(R.id.tutorialArrow)
    private val card: View = activity.findViewById(R.id.tutorialCard)
    private val text: TextView = activity.findViewById(R.id.tutorialText)
    private val next: Button = activity.findViewById(R.id.tutorialNext)

    val step: Int get() = db.getSetting(GameDatabase.SETTING_TUTORIAL, "0").toIntOrNull() ?: OFF
    val active: Boolean get() = step != OFF

    init {
        activity.findViewById<Button>(R.id.tutorialSkip).setOnClickListener { finish() }
        next.setOnClickListener { complete(step) }
    }

    /** Shows the current step if it belongs to this screen; hides the overlay otherwise. */
    fun show() {
        val s = step
        val view = if (s == OFF) null else target(s)
        if (view == null) {
            hide()
            return
        }
        text.setText(TEXT[s] ?: return)
        next.visibility = if (s in EXPLAIN) View.VISIBLE else View.GONE
        layer.visibility = View.VISIBLE
        // Wait for layout so the target has its size and position.
        layer.post { point(view) }
    }

    /** The player did what [doneStep] asked: go to the next step. Ignored for other steps. */
    fun complete(doneStep: Int) {
        if (step != doneStep || doneStep == OFF) return
        val nextStep = if (doneStep >= LAST) OFF else doneStep + 1
        db.setSetting(GameDatabase.SETTING_TUTORIAL, nextStep.toString())
        show()
    }

    fun finish() {
        db.setSetting(GameDatabase.SETTING_TUTORIAL, OFF.toString())
        hide()
    }

    private fun hide() {
        arrow.clearAnimation()
        layer.visibility = View.GONE
    }

    /**
     * Puts the arrow next to [view], pointing at it. The card sits low on the screen, over the
     * bedrock under the rooms (above the tab bar), so the sky stays clear during the waves; for
     * a target at the very bottom (a tab, the recruit button) it sits just above the arrow.
     */
    private fun point(view: View) {
        if (layer.visibility != View.VISIBLE) return
        val origin = IntArray(2).also { layer.getLocationInWindow(it) }
        val at = IntArray(2).also { view.getLocationInWindow(it) }
        val x = at[0] - origin[0] + view.width / 2f
        val top = (at[1] - origin[1]).toFloat()
        val bottom = top + view.height
        val inUpperQuarter = (top + bottom) / 2 < layer.height * 0.25f
        arrow.translationX = (x - arrow.width / 2f).coerceIn(0f, (layer.width - arrow.width).toFloat())
        if (inUpperQuarter) {
            arrow.rotation = 180f                       // below the target, pointing up
            arrow.translationY = bottom + 4
        } else {
            arrow.rotation = 0f                         // above the target, pointing down
            arrow.translationY = top - arrow.height - 4
        }
        val params = card.layoutParams as FrameLayout.LayoutParams
        params.gravity = Gravity.BOTTOM
        val tabBar = (activity.resources.displayMetrics.density * 84).toInt()
        // If the card would cover the target, lift it above the arrow.
        val cardTop = layer.height - tabBar - card.height
        val covered = bottom > cardTop - 8
        params.bottomMargin = if (covered) (layer.height - top).toInt() + arrow.height + 8 else tabBar
        card.layoutParams = params
        if (step in NO_ARROW) {
            arrow.clearAnimation()
            arrow.visibility = View.INVISIBLE
        } else {
            arrow.visibility = View.VISIBLE
            if (arrow.animation == null) arrow.startAnimation(AnimationUtils.loadAnimation(activity, R.anim.tutorial_bob))
        }
    }
}
