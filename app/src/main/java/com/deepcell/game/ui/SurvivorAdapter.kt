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

/** Rows for the Survivors screen: figure dressed for the job, name, and job chip. */
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

        val figure = when (survivor.job) {
            Survivor.JOB_ROOF -> R.drawable.ic_survivor_guard
            Survivor.JOB_FARM -> R.drawable.ic_survivor_farmer
            else -> R.drawable.ic_survivor_digger
        }
        val jobIcon = when (survivor.job) {
            Survivor.JOB_ROOF -> R.drawable.ic_tab_defense
            Survivor.JOB_FARM -> R.drawable.ic_food
            else -> R.drawable.ic_scrap
        }
        row.findViewById<ImageView>(R.id.survivorFigure).setImageResource(figure)
        row.findViewById<TextView>(R.id.survivorName).text = survivor.name

        val job = row.findViewById<TextView>(R.id.survivorJob)
        job.text = survivor.job
        val icon = context.getDrawable(jobIcon)
        val size = (18 * context.resources.displayMetrics.density).toInt()
        icon?.setBounds(0, 0, size, size)
        job.setCompoundDrawablesRelative(icon, null, null, null)
        return row
    }
}
