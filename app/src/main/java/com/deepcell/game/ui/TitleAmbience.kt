package com.deepcell.game.ui

import android.graphics.PorterDuff
import android.view.View
import android.view.animation.AccelerateInterpolator
import android.view.animation.DecelerateInterpolator
import android.view.animation.LinearInterpolator
import android.widget.FrameLayout
import android.widget.ImageView
import com.deepcell.game.R
import kotlin.random.Random

/**
 * The moving layer over the title shots: dust motes drifting through the light, and on the
 * surface shot a couple of drones crossing the sky. Each mote fades in while it slows down
 * (ease-out), then speeds up as it fades away (ease-in), and starts again somewhere else.
 */
class TitleAmbience(
    private val layer: FrameLayout,
    private val moteCount: Int = 22,
    private val drones: Boolean = true
) {

    private val motes = ArrayList<ImageView>()
    private val droneViews = ArrayList<ImageView>()
    private var running = false
    private val density = layer.resources.displayMetrics.density

    // Warm lamp dust in the rooms, cool ash outside.
    private var tint = WARM

    fun start() {
        if (running) return
        running = true
        layer.post {
            if (!running) return@post
            repeat(moteCount) { drift(newMote(), Random.nextLong(0, 4000)) }
        }
    }

    fun stop() {
        running = false
        for (v in motes + droneViews) v.animate().cancel()
        layer.removeAllViews()
        motes.clear()
        droneViews.clear()
    }

    /** Shot index from TitleSlideshow: 0 surface, 1 dig, 2 farm. */
    fun onShot(index: Int) {
        tint = if (index == 0) COOL else WARM
        for (m in motes) m.setColorFilter(tint, PorterDuff.Mode.MULTIPLY)
        if (index == 0 && drones) launchDrones() else clearDrones()
    }

    private fun newMote(): ImageView {
        val v = ImageView(layer.context)
        val size = ((3 + Random.nextFloat() * 7) * density).toInt()
        v.layoutParams = FrameLayout.LayoutParams(size, size)
        v.setImageResource(R.drawable.fx_mote)
        v.setColorFilter(tint, PorterDuff.Mode.MULTIPLY)
        v.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
        v.alpha = 0f
        layer.addView(v)
        motes.add(v)
        return v
    }

    private fun drift(v: ImageView, delay: Long = 0L) {
        if (!running || layer.width == 0) return
        val x = Random.nextFloat() * layer.width
        val y = Random.nextFloat() * layer.height
        val dx = (Random.nextFloat() * 60 - 30) * density
        val dy = -(20 + Random.nextFloat() * 60) * density      // dust rises in warm air
        val half = (2500 + Random.nextLong(0, 3000))
        val peak = 0.35f + Random.nextFloat() * 0.55f
        v.translationX = x
        v.translationY = y
        v.alpha = 0f
        v.animate().translationX(x + dx).translationY(y + dy).alpha(peak)
            .setStartDelay(delay).setDuration(half).setInterpolator(DecelerateInterpolator())
            .withEndAction {
                v.animate().translationX(x + dx * 2).translationY(y + dy * 2).alpha(0f)
                    .setStartDelay(0).setDuration(half).setInterpolator(AccelerateInterpolator())
                    .withEndAction { drift(v) }.start()
            }.start()
    }

    /** Two drones cross the upper sky at different heights and speeds. */
    private fun launchDrones() {
        clearDrones()
        val kinds = listOf(R.drawable.anim_scout to 34, R.drawable.anim_bomber to 44)
        kinds.forEachIndexed { i, (res, sizeDp) ->
            val size = (sizeDp * density).toInt()
            val v = ImageView(layer.context)
            v.layoutParams = FrameLayout.LayoutParams(size, size)
            v.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
            layer.addView(v)
            droneViews.add(v)
            Fx.loop(v, res)
            val leftToRight = i == 0
            val fromX = if (leftToRight) -size.toFloat() else layer.width.toFloat()
            val toX = if (leftToRight) layer.width.toFloat() else -size.toFloat()
            val y = layer.height * (0.30f + i * 0.08f)
            v.translationX = fromX
            v.translationY = y
            v.scaleX = if (leftToRight) 1f else -1f
            v.animate().translationX(toX).translationY(y + 30 * density)
                .setStartDelay(400L + i * 1500L).setDuration(6500L + i * 1500L)
                .setInterpolator(LinearInterpolator())                 // steady flight
                .start()
        }
    }

    private fun clearDrones() {
        for (d in droneViews) {
            d.animate().cancel()
            layer.removeView(d)
        }
        droneViews.clear()
    }

    companion object {
        private const val WARM = 0xFFFFC27A.toInt()
        private const val COOL = 0xFFB9C4D6.toInt()
    }
}
