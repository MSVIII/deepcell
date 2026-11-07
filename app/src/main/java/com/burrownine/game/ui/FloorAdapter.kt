package com.burrownine.game.ui

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.animation.AnimationUtils
import android.widget.BaseAdapter
import android.widget.Button
import android.widget.ImageView
import android.widget.ProgressBar
import android.widget.TextView
import com.burrownine.game.R
import com.burrownine.game.model.Floor

/**
 * Shows the underground floors in a ListView (Module 6). Each row has a manual
 * button and a ProgressBar. Automated rooms show a spinning gear (res/anim/gear_spin.xml).
 */
class FloorAdapter(
    private val context: Context,
    private val floors: List<Floor>,
    private val onAction: (Floor) -> Unit
) : BaseAdapter() {

    override fun getCount(): Int = floors.size
    override fun getItem(position: Int): Floor = floors[position]
    override fun getItemId(position: Int): Long = position.toLong()

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val row = convertView ?: LayoutInflater.from(context).inflate(R.layout.row_floor, parent, false)
        val floor = floors[position]

        val icon = row.findViewById<ImageView>(R.id.floorIcon)
        val gear = row.findViewById<ImageView>(R.id.floorGear)
        val name = row.findViewById<TextView>(R.id.floorName)
        val status = row.findViewById<TextView>(R.id.floorStatus)
        val bar = row.findViewById<ProgressBar>(R.id.floorProgress)
        val button = row.findViewById<Button>(R.id.floorButton)

        icon.setImageResource(if (floor.resource == "scrap") R.drawable.ic_scrap else R.drawable.ic_mushroom)
        name.text = floor.name
        val resourceName = context.getString(if (floor.resource == "scrap") R.string.scrap else R.string.food)
        status.text = context.getString(
            R.string.floor_status, floor.progress, floor.maxProgress, floor.yieldPerFill, resourceName
        )
        bar.max = floor.maxProgress
        bar.progress = floor.progress
        button.text = floor.actionLabel
        button.setOnClickListener { onAction(floor) }

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
        return row
    }
}
