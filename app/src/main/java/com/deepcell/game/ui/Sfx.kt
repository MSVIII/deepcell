package com.deepcell.game.ui

import android.content.Context
import android.media.AudioAttributes
import android.media.SoundPool
import com.deepcell.game.R

/**
 * Short sound effects through SoundPool. The sounds are synthesised by tools/audio/gen_sfx.py
 * and stored in res/raw. Create one per screen in onCreate and call [release] in onDestroy.
 * [enabled] follows the Sound switch in Settings. Loudness is balanced in the files
 * (gen_sfx.py); explosions are turned down here because they stack up when many drones die.
 */
class Sfx(context: Context) {

    enum class Sound(val res: Int, val volume: Float) {
        DIG(R.raw.sfx_dig, 1f),
        HARVEST(R.raw.sfx_harvest, 1f),
        SHOT(R.raw.sfx_shot, 1f),
        TURRET(R.raw.sfx_turret, 1f),
        HIT(R.raw.sfx_hit, 1f),
        EXPLODE(R.raw.sfx_explode, 0.4f),     // plays for every kill: kept well under the rest
        IMPACT(R.raw.sfx_impact, 0.6f),
        REPAIR(R.raw.sfx_repair, 1f),
        BUY(R.raw.sfx_buy, 1f),
        WAVE(R.raw.sfx_wave, 1f),
        ALARM(R.raw.sfx_alarm, 1f),
        TAP(R.raw.sfx_tap, 1f),
        COLLECT(R.raw.sfx_collect, 1f)
    }

    var enabled = true

    private val pool: SoundPool = SoundPool.Builder()
        .setMaxStreams(8)
        .setAudioAttributes(
            AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_GAME)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .build()
        )
        .build()

    private val ids = HashMap<Sound, Int>()

    init {
        for (s in Sound.values()) ids[s] = pool.load(context, s.res, 1)
    }

    fun play(sound: Sound, rate: Float = 1f) {
        if (!enabled) return
        val id = ids[sound] ?: return
        pool.play(id, sound.volume, sound.volume, 1, 0, rate)
    }

    fun release() {
        pool.release()
    }
}
