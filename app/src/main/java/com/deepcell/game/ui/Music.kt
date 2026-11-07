package com.deepcell.game.ui

import android.content.Context
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.os.Handler
import android.os.Looper

/**
 * Background music: one looping MediaPlayer at a time. [play] fades the current track out and
 * the new one in, so switching from the gameplay loop to the boss loop doesn't cut. The tracks
 * are composed in tools/audio/gen_music.py (res/raw/music_*.ogg).
 *
 * Lifecycle: call [play] in onResume, [pause] in onPause, [release] in onDestroy.
 * [enabled] follows the Music switch in Settings.
 */
class Music(private val context: Context) {

    companion object {
        /** Music sits under the sound effects. */
        private const val VOLUME = 0.55f
        private const val FADE_MS = 900L
        private const val STEP_MS = 50L
    }

    var enabled = true
        set(value) {
            field = value
            if (!value) stopNow()
        }

    private var player: MediaPlayer? = null
    private var track = 0
    private var level = 0f            // current volume, 0..VOLUME
    private val handler = Handler(Looper.getMainLooper())
    private var fade: Runnable? = null

    /** Plays [res] (looping). Does nothing if it is already playing. */
    fun play(res: Int) {
        if (!enabled) return
        val current = player
        if (current != null && track == res) {
            if (!current.isPlaying) current.start()
            fadeTo(VOLUME, null)
            return
        }
        if (current == null) {
            start(res)
        } else {
            // Fade the old track out, then start the new one.
            fadeTo(0f) { stopNow(); start(res) }
        }
    }

    fun pause() {
        cancelFade()
        player?.pause()
    }

    fun release() {
        stopNow()
    }

    private fun start(res: Int) {
        val mp = MediaPlayer.create(
            context, res,
            AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_GAME)
                .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                .build(),
            0
        ) ?: return
        mp.isLooping = true
        level = 0f
        mp.setVolume(0f, 0f)
        mp.start()
        player = mp
        track = res
        fadeTo(VOLUME, null)
    }

    private fun stopNow() {
        cancelFade()
        player?.release()
        player = null
        track = 0
    }

    /** Moves the volume to [target] in small steps over FADE_MS, then runs [then]. */
    private fun fadeTo(target: Float, then: (() -> Unit)?) {
        cancelFade()
        val step = VOLUME * STEP_MS / FADE_MS
        val r = object : Runnable {
            override fun run() {
                val mp = player ?: return
                level = if (level < target) Math.min(target, level + step) else Math.max(target, level - step)
                mp.setVolume(level, level)
                if (level == target) {
                    fade = null
                    then?.invoke()
                } else {
                    handler.postDelayed(this, STEP_MS)
                }
            }
        }
        fade = r
        handler.post(r)
    }

    private fun cancelFade() {
        fade?.let { handler.removeCallbacks(it) }
        fade = null
    }
}
