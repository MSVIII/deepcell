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
import android.widget.ProgressBar
import android.widget.TextView
import com.deepcell.game.R
import com.deepcell.game.model.Floor

/**
 * Shows the underground rooms in a ListView (Module 6). Each row is a cutaway room:
 * floor number in the lift shaft, the rendered room, the survivors working there,
 * and a progress bar. Tapping the room works it.
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

    override fun getCount(): Int = floors.size
    override fun getItem(position: Int): Floor = floors[position]
    override fun getItemId(position: Int): Long = position.toLong()

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val row = convertView ?: LayoutInflater.from(context).inflate(R.layout.row_floor, parent, false)
        val floor = floors[position]
        val isScrap = floor.resource == "scrap"

        row.findViewById<TextView>(R.id.floorNumber).text = context.getString(R.string.floor_number, position + 1)
        row.findViewById<TextView>(R.id.roomName).text = floor.name
        row.findViewById<ImageView>(R.id.roomArt).setImageResource(
            when {
                !isScrap -> R.drawable.room_farm
                floor.automated -> R.drawable.room_dig_auto   // same room with the Drill Rig in it
                else -> R.drawable.room_dig
            }
        )
        // Lamp light breathes; rows start at different points so they don't pulse together.
        val glow = row.findViewById<View>(R.id.roomGlow)
        if (glow.animation == null) {
            val flicker = AnimationUtils.loadAnimation(context, R.anim.lamp_flicker)
            flicker.startOffset = position * 700L
            glow.startAnimation(flicker)
        }
        row.findViewById<TextView>(R.id.roomYield).text = context.getString(R.string.plus_amount, floor.yieldPerFill)
        row.findViewById<ImageView>(R.id.roomYieldIcon)
            .setImageResource(if (isScrap) R.drawable.icon_scrap else R.drawable.icon_food)

        val bar = row.findViewById<ProgressBar>(R.id.floorProgress)
        bar.max = floor.maxProgress
        bar.progress = floor.progress

        // Workers: one figure per survivor in this room, each looping its work animation
        // (pickaxe swing or picking mushrooms), started a little apart so they don't swing in step.
        val workers = row.findViewById<LinearLayout>(R.id.roomWorkers)
        val count = Math.min(workersIn(floor), MAX_WORKERS_SHOWN)
        val density = context.resources.displayMetrics.density
        if (workers.childCount != count) {
            workers.removeAllViews()
            placeInWorkZone(workers, count, isScrap, density)
            repeat(count) {
                val figure = ImageView(context)
                val params = LinearLayout.LayoutParams((WORKER_W_DP * density).toInt(), (WORKER_H_DP * density).toInt())
                if (it > 0) params.marginStart = ((if (isScrap) DIG_OVERLAP_DP else FARM_OVERLAP_DP) * density).toInt()
                figure.layoutParams = params
                figure.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
                workers.addView(figure)
                Fx.loop(figure, if (isScrap) R.drawable.anim_digger_work else R.drawable.anim_farmer_work, it * 170L)
            }
        }

        // Automation: the room art shows the machine; the payout label gets a spinning gear.
        val gear = row.findViewById<ImageView>(R.id.roomGear)
        if (floor.automated) {
            gear.visibility = View.VISIBLE
            // Only start the animation once, otherwise every refresh restarts it.
            if (gear.animation == null) {
                gear.startAnimation(AnimationUtils.loadAnimation(context, R.anim.gear_spin))
            }
        } else {
            gear.clearAnimation()
            gear.visibility = View.GONE
        }

        // "+5" popup after the bar fills.
        if (floor.pendingPopup > 0) {
            val popup = row.findViewById<TextView>(R.id.roomPopup)
            popup.text = context.getString(R.string.plus_amount, floor.pendingPopup)
            popup.visibility = View.VISIBLE
            popup.startAnimation(AnimationUtils.loadAnimation(context, R.anim.float_up))
            floor.pendingPopup = 0
        }

        val room = row.findViewById<FrameLayout>(R.id.room)
        room.contentDescription = floor.name
        room.setOnClickListener {
            showWorkEffect(row, workers, isScrap, density)
            onAction(floor)
        }
        return row
    }

    /**
     * Shifts the row of workers so they stand in the room's work zone: diggers lined up left of
     * the scrap heap with the last pickaxe landing in it, farmers along the grow tables.
     */
    private fun placeInWorkZone(workers: LinearLayout, count: Int, isScrap: Boolean, density: Float) {
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
    private fun showWorkEffect(row: View, workers: LinearLayout, isScrap: Boolean, density: Float) {
        val layer = row.findViewById<FrameLayout>(R.id.roomFx)
        val fx = if (isScrap) R.drawable.fx_dust else R.drawable.fx_spores
        val size = (FX_SIZE_DP * density).toInt()
        if (workers.childCount == 0) {
            // Nobody working here: the player works the zone alone (heap or first table).
            val x = row.findViewById<View>(R.id.room).width * (if (isScrap) HEAP_X else TABLES_X + 0.1f)
            Fx.burst(layer, fx, x, workers.bottom - 10 * density, size)
            return
        }
        for (i in 0 until workers.childCount) {
            val figure = workers.getChildAt(i)
            val x = workers.left + figure.left + figure.width * (if (isScrap) PICK_X else HAND_X)
            val y = workers.top + figure.top + figure.height * (if (isScrap) 0.9f else 0.78f)
            Fx.burst(layer, fx, x, y, size)
        }
    }
}
