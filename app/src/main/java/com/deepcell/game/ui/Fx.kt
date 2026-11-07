package com.deepcell.game.ui

import android.graphics.drawable.AnimationDrawable
import android.widget.FrameLayout
import android.widget.ImageView

/**
 * Plays the rendered flipbooks (Blender frames in an AnimationDrawable).
 *
 * [loop] starts a looping animation already set on an ImageView, e.g. a working survivor.
 * [burst] adds a one-shot effect (explosion, dust, sparks) to a FrameLayout, centred on a
 * point, and removes it when the last frame has played.
 */
object Fx {

    fun loop(view: ImageView, drawableRes: Int, delayMs: Long = 0L) {
        view.setImageResource(drawableRes)
        val anim = view.drawable as? AnimationDrawable ?: return
        // Starting from a post makes sure the view is attached; the delay staggers figures
        // so several workers don't swing in step.
        view.postDelayed({ anim.start() }, delayMs)
    }

    fun burst(layer: FrameLayout, drawableRes: Int, centerX: Float, centerY: Float, sizePx: Int) {
        val view = ImageView(layer.context)
        view.layoutParams = FrameLayout.LayoutParams(sizePx, sizePx)
        view.translationX = centerX - sizePx / 2f
        view.translationY = centerY - sizePx / 2f
        view.importantForAccessibility = ImageView.IMPORTANT_FOR_ACCESSIBILITY_NO
        view.setImageResource(drawableRes)
        layer.addView(view)
        val anim = view.drawable as? AnimationDrawable
        if (anim == null) {
            layer.removeView(view)
            return
        }
        anim.start()
        var total = 0L
        for (i in 0 until anim.numberOfFrames) total += anim.getDuration(i)
        view.postDelayed({ layer.removeView(view) }, total)
    }
}
