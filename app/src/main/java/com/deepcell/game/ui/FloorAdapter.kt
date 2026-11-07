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

        // Workers: one figure per survivor in this room.
        val workers = row.findViewById<LinearLayout>(R.id.roomWorkers)
        val count = Math.min(workersIn(floor), MAX_WORKERS_SHOWN)
        if (workers.childCount != count) {
            workers.removeAllViews()
            val density = context.resources.displayMetrics.density
            repeat(count) {
                val figure = ImageView(context)
                figure.setImageResource(if (isScrap) R.drawable.survivor_digger else R.drawable.survivor_farmer)
                val params = LinearLayout.LayoutParams((26 * density).toInt(), (39 * density).toInt())
                params.marginEnd = (2 * density).toInt()
                figure.layoutParams = params
                workers.addView(figure)
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
            workers.startAnimation(AnimationUtils.loadAnimation(context, R.anim.work_bob))
            onAction(floor)
        }
        return row
    }
}
