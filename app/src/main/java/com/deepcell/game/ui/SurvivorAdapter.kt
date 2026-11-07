package com.deepcell.game.ui

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.ImageView
import android.widget.TextView
import com.deepcell.game.R
import com.deepcell.game.model.Survivor

/**
 * Rows for the Survivors screen: figure dressed for the job, name, what the job does, and the
 * job chip with a swap icon (tapping the row opens the job picker).
 */
class SurvivorAdapter(
    private val context: Context,
    private var survivors: List<Survivor>
) : BaseAdapter() {

    fun update(newList: List<Survivor>) {
        survivors = newList
        notifyDataSetChanged()
    }

    override fun getCount(): Int = survivors.size
    override fun getItem(position: Int): Survivor = survivors[position]
    override fun getItemId(position: Int): Long = survivors[position].id

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val row = convertView ?: LayoutInflater.from(context).inflate(R.layout.row_survivor, parent, false)
        val survivor = survivors[position]

        row.findViewById<ImageView>(R.id.survivorFigure).setImageResource(Jobs.figure(survivor.job))
        row.findViewById<TextView>(R.id.survivorName).text = survivor.name
        row.findViewById<TextView>(R.id.survivorEffect).setText(Jobs.effect(survivor.job))

        val job = row.findViewById<TextView>(R.id.survivorJob)
        job.text = survivor.job
        val size = (18 * context.resources.displayMetrics.density).toInt()
        val icon = context.getDrawable(Jobs.icon(survivor.job))
        icon?.setBounds(0, 0, size, size)
        val swap = context.getDrawable(R.drawable.ic_swap)
        swap?.setBounds(0, 0, size * 4 / 5, size * 4 / 5)
        job.setCompoundDrawablesRelative(icon, null, swap, null)
        return row
    }
}
