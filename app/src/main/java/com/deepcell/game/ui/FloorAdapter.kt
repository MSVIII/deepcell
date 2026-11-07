package com.deepcell.game.ui

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.animation.AnimationUtils
import android.widget.BaseAdapter
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.ProgressBar
import android.widget.TextView
import com.deepcell.game.R
import com.deepcell.game.model.Floor

/**
 * Shows the underground rooms in a ListView (Module 6). Each row is a cutaway room:
 * floor number in the lift shaft, the rendered room, the survivors working there,
 * the storage chip and a progress bar. Tapping the room works it and collects the storage.
 *
 * Speed: rows keep their views in a [Holder] (no findViewById per bind), and the game calls
 * [refresh] for the numbers that change every second, which updates the visible rows in
 * place instead of re-binding the whole list. [lowDetail] drops the purely decorative
 * animations (lamp flicker, storage pulse, dust/spore bursts) on weak phones.
 *
 * [workersIn] returns how many survivors work in a room, so the row can draw them.
 */
class FloorAdapter(
    private val context: Context,
    private val floors: List<Floor>,
    private val workersIn: (Floor) -> Int,
    private val onAction: (Floor) -> Unit
) : BaseAdapter() {

    companion object {
        private const val MAX_WORKERS_SHOWN = 4
        // Work animation frames are 4:3 with the figure in the middle third.
        private const val WORKER_W_DP = 78
        private const val WORKER_H_DP = 58
        private const val DIG_OVERLAP_DP = -40     // diggers stand close, swinging side by side
        private const val FARM_OVERLAP_DP = -28    // farmers spread along the grow tables
        private const val FX_SIZE_DP = 60
        // Where the tool meets the ground, as a fraction of the frame (from the renders).
        private const val PICK_X = 0.80f
        private const val HAND_X = 0.66f
        // Work zones in the room renders, as a fraction of the room width: the scrap heap
        // (the last digger's pickaxe lands here) and the start of the grow tables.
        private const val HEAP_X = 0.74f
        private const val TABLES_X = 0.36f
    }

    var lowDetail = false

    private val density = context.resources.displayMetrics.density

    /** The row's views, found once when the row is inflated. */
    private class Holder(row: View) {
        val floorNumber: TextView = row.findViewById(R.id.floorNumber)
        val roomName: TextView = row.findViewById(R.id.roomName)
        val roomArt: ImageView = row.findViewById(R.id.roomArt)
        val glow: View = row.findViewById(R.id.roomGlow)
        val yieldText: TextView = row.findViewById(R.id.roomYield)
        val yieldIcon: ImageView = row.findViewById(R.id.roomYieldIcon)
        val bar: ProgressBar = row.findViewById(R.id.floorProgress)
        val storage: View = row.findViewById(R.id.roomStorage)
        val storageIcon: ImageView = row.findViewById(R.id.roomStorageIcon)
        val storageText: TextView = row.findViewById(R.id.roomStorageText)
        val workers: LinearLayout = row.findViewById(R.id.roomWorkers)
        val gear: ImageView = row.findViewById(R.id.roomGear)
        val popup: TextView = row.findViewById(R.id.roomPopup)
        val room: FrameLayout = row.findViewById(R.id.room)
        val fx: FrameLayout = row.findViewById(R.id.roomFx)
        val collector: ImageView = row.findViewById(R.id.roomCollector)
        var art = 0                  // room image shown, so it is only set when it changes
        var position = -1
        var shownStock = -1          // storage text shown, same idea
        var shownCapacity = -1
    }

    override fun getCount(): Int = floors.size
    override fun getItem(position: Int): Floor = floors[position]
    override fun getItemId(position: Int): Long = position.toLong()

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val row = convertView ?: LayoutInflater.from(context).inflate(R.layout.row_floor, parent, false).also {
            it.tag = Holder(it)
        }
        val h = row.tag as Holder
        val floor = floors[position]
        val isScrap = floor.resource == "scrap"

        if (h.position != position) {
            h.position = position
            h.floorNumber.text = context.getString(R.string.floor_number, position + 1)
            h.roomName.text = floor.name
            h.yieldText.text = context.getString(R.string.plus_amount, floor.yieldPerFill)
            val icon = if (isScrap) R.drawable.icon_scrap else R.drawable.icon_food
            h.yieldIcon.setImageResource(icon)
            h.storageIcon.setImageResource(icon)
            h.room.contentDescription = floor.name
            h.room.setOnClickListener {
                if (!lowDetail) showWorkEffect(h, isScrap)
                onAction(floor)
            }
        }
        val art = when {
            !isScrap -> R.drawable.room_farm
            floor.automated -> R.drawable.room_dig_auto   // same room with the Drill Rig in it
            else -> R.drawable.room_dig
        }
        if (h.art != art) {
            h.art = art
            h.roomArt.setImageResource(art)
        }
        // Lamp light breathes; rows start at different points so they don't pulse together.
        // Off in low detail: it repaints the whole room every frame.
        if (lowDetail) {
            h.glow.clearAnimation()
        } else if (h.glow.animation == null) {
            val flicker = AnimationUtils.loadAnimation(context, R.anim.lamp_flicker)
            flicker.startOffset = position * 700L
            h.glow.startAnimation(flicker)
        }

        // Workers: one figure per survivor in this room, each looping its work animation
        // (pickaxe swing or picking mushrooms), started a little apart so they don't swing in step.
        val count = Math.min(workersIn(floor), MAX_WORKERS_SHOWN)
        if (h.workers.childCount != count) {
            h.workers.removeAllViews()
            placeInWorkZone(h.workers, count, isScrap)
            repeat(count) {
                val figure = ImageView(context)
                val params = LinearLayout.LayoutParams((WORKER_W_DP * density).toInt(), (WORKER_H_DP * density).toInt())
                if (it > 0) params.marginStart = ((if (isScrap) DIG_OVERLAP_DP else FARM_OVERLAP_DP) * density).toInt()
                figure.layoutParams = params
                figure.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
                h.workers.addView(figure)
                Fx.loop(figure, if (isScrap) R.drawable.anim_digger_work else R.drawable.anim_farmer_work, it * 170L)
            }
        }

        // Automation: the room art shows the machine; the payout label gets a spinning gear.
        if (floor.automated) {
            h.gear.visibility = View.VISIBLE
            // Only start the animation once, otherwise every refresh restarts it.
            if (h.gear.animation == null) h.gear.startAnimation(AnimationUtils.loadAnimation(context, R.anim.gear_spin))
        } else {
            h.gear.clearAnimation()
            h.gear.visibility = View.GONE
        }
        bindDynamic(h, floor)
        return row
    }

    /**
     * The parts that change every second: progress bar, storage chip, "+N" popup. Only touches
     * a view when its value really changed, so most calls draw nothing.
     */
    private fun bindDynamic(h: Holder, floor: Floor) {
        if (h.bar.max != floor.maxProgress) h.bar.max = floor.maxProgress
        if (h.bar.progress != floor.progress) h.bar.progress = floor.progress

        // Storage chip: amount waiting / capacity. Pulses while there is something to collect.
        if (h.shownStock != floor.stock || h.shownCapacity != floor.capacity) {
            h.shownStock = floor.stock
            h.shownCapacity = floor.capacity
            h.storageText.text = context.getString(R.string.storage_amount, floor.stock, floor.capacity)
            h.storageText.setTextColor(context.getColor(if (floor.isFull) R.color.alarm_red else R.color.text_main))
            h.storage.contentDescription = context.getString(R.string.storage_description, floor.stock, floor.capacity)
        }
        val pulse = floor.stock > 0 && !lowDetail
        if (pulse && h.storage.animation == null) {
            h.storage.startAnimation(AnimationUtils.loadAnimation(context, R.anim.stock_pulse))
        } else if (!pulse && h.storage.animation != null) {
            h.storage.clearAnimation()
        }

        // "+5" popup after the storage is collected.
        if (floor.pendingPopup > 0) {
            h.popup.text = context.getString(R.string.plus_amount, floor.pendingPopup)
            h.popup.visibility = View.VISIBLE
            h.popup.startAnimation(AnimationUtils.loadAnimation(context, R.anim.float_up))
            floor.pendingPopup = 0
        }
    }

    /** Updates the numbers of the rows on screen without re-binding the list. */
    fun refresh(list: ListView) {
        for (i in 0 until list.childCount) {
            val h = list.getChildAt(i).tag as? Holder ?: continue
            if (h.position in floors.indices) bindDynamic(h, floors[h.position])
        }
    }

    /**
     * Draws the Collector in a room row for the current moment of its trip. The game loop calls
     * this every frame (the row may be re-bound at any time, so nothing here relies on a running
     * animation). [phase]: 0 walking in, 1 grabbing, 2 walking out, -1 hidden. [t] is 0..1 of
     * the walk; it is eased (slow start, slow stop) here.
     */
    fun drawCollector(row: View, phase: Int, t: Float) {
        val h = row.tag as? Holder ?: return
        val walker = h.collector
        if (phase < 0) {
            if (walker.visibility != View.GONE) {
                walker.visibility = View.GONE
                walker.tag = null
            }
            return
        }
        val start = -walker.layoutParams.width.toFloat()
        val target = h.storage.left - walker.layoutParams.width * 0.7f
        // Swap the animation only when the phase changes, not every frame.
        val wanted = if (phase == 1) R.drawable.anim_collector_grab else R.drawable.anim_collector_walk
        if (walker.tag != wanted) {
            walker.tag = wanted
            walker.visibility = View.VISIBLE
            if (phase == 1) {
                walker.setImageResource(wanted)
                (walker.drawable as? android.graphics.drawable.AnimationDrawable)?.start()
            } else {
                Fx.loop(walker, wanted)
            }
        }
        val eased = (1 - Math.cos(Math.PI * t.coerceIn(0f, 1f)).toFloat()) / 2   // ease in and out
        when (phase) {
            0 -> { walker.scaleX = 1f; walker.translationX = start + (target - start) * eased }
            1 -> walker.translationX = target
            else -> { walker.scaleX = -1f; walker.translationX = target + (start - target) * eased }
        }
    }

    /** Width the Collector walks in a room, in pixels (for the trip time). */
    fun collectorDistancePx(): Float {
        val shaft = context.resources.getDimensionPixelSize(R.dimen.shaft_width)
        return (context.resources.displayMetrics.widthPixels - shaft) * 0.85f
    }

    /**
     * Shifts the row of workers so they stand in the room's work zone: diggers lined up left of
     * the scrap heap with the last pickaxe landing in it, farmers along the grow tables.
     */
    private fun placeInWorkZone(workers: LinearLayout, count: Int, isScrap: Boolean) {
        val shaft = context.resources.getDimensionPixelSize(R.dimen.shaft_width)
        val roomWidth = context.resources.displayMetrics.widthPixels - shaft
        val frame = WORKER_W_DP * density
        val start = if (isScrap) {
            val step = frame + DIG_OVERLAP_DP * density
            roomWidth * HEAP_X - frame * PICK_X - step * (Math.max(count, 1) - 1)
        } else {
            roomWidth * TABLES_X
        }
        workers.setPadding(Math.max(0f, start).toInt(), 0, 0, 0)
    }

    /** Dust where each pickaxe lands, or spores where each mushroom is picked. */
    private fun showWorkEffect(h: Holder, isScrap: Boolean) {
        val fx = if (isScrap) R.drawable.fx_dust else R.drawable.fx_spores
        val size = (FX_SIZE_DP * density).toInt()
        val workers = h.workers
        if (workers.childCount == 0) {
            // Nobody working here: the player works the zone alone (heap or first table).
            val x = h.room.width * (if (isScrap) HEAP_X else TABLES_X + 0.1f)
            Fx.burst(h.fx, fx, x, workers.bottom - 10 * density, size)
            return
        }
        for (i in 0 until workers.childCount) {
            val figure = workers.getChildAt(i)
            val x = workers.left + figure.left + figure.width * (if (isScrap) PICK_X else HAND_X)
            val y = workers.top + figure.top + figure.height * (if (isScrap) 0.9f else 0.78f)
            Fx.burst(h.fx, fx, x, y, size)
        }
    }
}
