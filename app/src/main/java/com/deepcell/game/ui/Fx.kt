package com.deepcell.game.ui

import android.graphics.drawable.AnimationDrawable
import android.view.View
import android.widget.FrameLayout
import android.widget.ImageView

/**
 * Plays the rendered flipbooks (Blender frames in an AnimationDrawable).
 *
 * [loop] starts a looping animation already set on an ImageView, e.g. a working survivor.
 * [burst] adds a one-shot effect (explosion, dust, sparks) to a FrameLayout, centred on a
 * point, and hides it for reuse when the last frame has played.
 */
object Fx {

    fun loop(view: ImageView, drawableRes: Int, delayMs: Long = 0L) {
        view.setImageResource(drawableRes)
        val anim = view.drawable as? AnimationDrawable ?: return
        // Starting from a post makes sure the view is attached; the delay staggers figures
        // so several workers don't swing in step.
        view.postDelayed({ anim.start() }, delayMs)
    }

    /** Tag on an effect view that has finished and can be reused. */
    private const val FREE = "fx_free"

    fun burst(layer: FrameLayout, drawableRes: Int, centerX: Float, centerY: Float, sizePx: Int) {
        // Reuse a finished effect view in this layer before creating a new one: no allocation
        // or layout pass per explosion, which matters when many enemies die at once.
        var view: ImageView? = null
        for (i in 0 until layer.childCount) {
            val child = layer.getChildAt(i)
            if (child.tag == FREE && child is ImageView) { view = child; break }
        }
        if (view == null) {
            view = ImageView(layer.context)
            view.importantForAccessibility = ImageView.IMPORTANT_FOR_ACCESSIBILITY_NO
            layer.addView(view, FrameLayout.LayoutParams(sizePx, sizePx))
        } else if (view.layoutParams.width != sizePx) {
            view.layoutParams = FrameLayout.LayoutParams(sizePx, sizePx)
        }
        view.tag = null
        view.visibility = View.VISIBLE
        view.translationX = centerX - sizePx / 2f
        view.translationY = centerY - sizePx / 2f
        view.setImageResource(drawableRes)
        val anim = view.drawable as? AnimationDrawable
        if (anim == null) {
            view.visibility = View.GONE
            view.tag = FREE
            return
        }
        anim.start()
        var total = 0L
        for (i in 0 until anim.numberOfFrames) total += anim.getDuration(i)
        val done = view
        view.postDelayed({
            done.visibility = View.GONE
            done.setImageDrawable(null)
            done.tag = FREE
        }, total)
    }
}
