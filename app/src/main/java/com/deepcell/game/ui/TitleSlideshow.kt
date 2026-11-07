package com.deepcell.game.ui

import android.os.Handler
import android.os.Looper
import android.view.View
import android.view.animation.AlphaAnimation
import android.view.animation.Animation
import android.view.animation.AnimationSet
import android.view.animation.AccelerateDecelerateInterpolator
import android.view.animation.ScaleAnimation
import android.view.animation.TranslateAnimation
import android.widget.ImageView
import com.deepcell.game.R

/**
 * Title screen background: several camera shots of the bunker, each slowly panning, with a
 * blurred crossfade between them. Built from a Handler (Module 6) and tween animations
 * (Module 4); the blurred frames are pre-rendered images, so it works on every Android version.
 *
 * [stage] holds [sharp] and [blur]; the pan moves the whole stage. [veil] is a black view that
 * dips during the switch so the change of shot is hidden.
 */
class TitleSlideshow(
    private val stage: View,
    private val sharp: ImageView,
    private val blur: ImageView,
    private val veil: View,
    /** False in low detail: shots cut through the dark veil only, without the blurred copy. */
    private val blurCrossfade: Boolean = true,
    /** Called with the shot index (0 surface, 1 dig, 2 farm) each time a shot starts. */
    private val onShot: (Int) -> Unit = {}
) {
    private class Shot(val image: Int, val blurred: Int, val pan: FloatArray)

    // pan = fromScale, toScale, fromX, toX, fromY, toY (translation as a fraction of the size)
    private val shots = listOf(
        // Small moves only: the shots are rendered at screen size, so big zooms would soften them.
        Shot(R.drawable.title_surface, R.drawable.title_surface_blur, floatArrayOf(1.02f, 1.06f, -0.01f, 0.01f, 0.008f, -0.008f)),
        Shot(R.drawable.title_dig, R.drawable.title_dig_blur, floatArrayOf(1.06f, 1.02f, 0.012f, -0.01f, 0f, 0f)),
        Shot(R.drawable.title_farm, R.drawable.title_farm_blur, floatArrayOf(1.02f, 1.06f, 0f, 0f, 0.01f, -0.01f))
    )

    private val handler = Handler(Looper.getMainLooper())
    private var index = 0
    private var running = false

    private val nextShot = Runnable { showShot(index + 1, fromBlur = true) }
    private val blurOut = Runnable {
        if (blurCrossfade) fade(blur, 0f, 1f, BLUR_MS)
        fade(veil, 0f, if (blurCrossfade) VEIL_ALPHA else 1f, BLUR_MS)
    }

    fun start() {
        if (running) return
        running = true
        showShot(index, fromBlur = false)
    }

    fun stop() {
        running = false
        handler.removeCallbacks(nextShot)
        handler.removeCallbacks(blurOut)
        stage.clearAnimation()
        blur.clearAnimation()
        veil.clearAnimation()
    }

    private fun showShot(i: Int, fromBlur: Boolean) {
        if (!running) return
        index = i % shots.size
        val shot = shots[index]
        sharp.setImageResource(shot.image)
        if (blurCrossfade) blur.setImageResource(shot.blurred)
        stage.startAnimation(pan(shot.pan))
        onShot(index)
        if (fromBlur) {
            // Arrive blurred and dimmed, then sharpen.
            if (blurCrossfade) fade(blur, 1f, 0f, BLUR_MS)
            fade(veil, VEIL_ALPHA, 0f, BLUR_MS)
        } else {
            blur.visibility = View.INVISIBLE
            veil.visibility = View.INVISIBLE
        }
        handler.postDelayed(blurOut, SHOT_MS - BLUR_MS)
        handler.postDelayed(nextShot, SHOT_MS)
    }

    private fun pan(p: FloatArray): Animation {
        val set = AnimationSet(true)
        set.addAnimation(ScaleAnimation(p[0], p[1], p[0], p[1],
            Animation.RELATIVE_TO_SELF, 0.5f, Animation.RELATIVE_TO_SELF, 0.5f))
        set.addAnimation(TranslateAnimation(
            Animation.RELATIVE_TO_SELF, p[2], Animation.RELATIVE_TO_SELF, p[3],
            Animation.RELATIVE_TO_SELF, p[4], Animation.RELATIVE_TO_SELF, p[5]))
        set.duration = SHOT_MS + BLUR_MS
        set.interpolator = AccelerateDecelerateInterpolator()   // camera eases in and out of each pan
        set.fillAfter = true
        return set
    }

    private fun fade(view: View, from: Float, to: Float, ms: Long) {
        view.visibility = View.VISIBLE
        val a = AlphaAnimation(from, to)
        a.duration = ms
        a.fillAfter = true
        view.startAnimation(a)
    }

    companion object {
        private const val SHOT_MS = 6500L
        private const val BLUR_MS = 650L
        private const val VEIL_ALPHA = 0.5f
    }
}
