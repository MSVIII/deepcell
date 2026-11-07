package com.burrownine.game.ui

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.Button
import android.widget.TextView
import com.burrownine.game.R
import com.burrownine.game.model.GameState
import com.burrownine.game.model.Upgrade

/**
 * The upgrade list under the floors. [items] is the list for the selected bottom tab
 * (Defense, Supplies or Automation); call [show] to switch tabs.
 */
class UpgradeAdapter(
    private val context: Context,
    private val stateProvider: () -> GameState?,
    private val onBuy: (Upgrade) -> Unit
) : BaseAdapter() {

    private var items: List<Upgrade> = emptyList()

    fun show(newItems: List<Upgrade>) {
        items = newItems
        notifyDataSetChanged()
    }

    override fun getCount(): Int = items.size
    override fun getItem(position: Int): Upgrade = items[position]
    override fun getItemId(position: Int): Long = position.toLong()

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val row = convertView ?: LayoutInflater.from(context).inflate(R.layout.row_upgrade, parent, false)
        val upgrade = items[position]
        val state = stateProvider()
        val level = state?.levelOf(upgrade) ?: 0

        row.findViewById<TextView>(R.id.upgradeName).text =
            context.getString(R.string.upgrade_name_level, upgrade.name, level, upgrade.maxLevel)
        row.findViewById<TextView>(R.id.upgradeDescription).text = upgrade.description

        val button = row.findViewById<Button>(R.id.upgradeBuy)
        if (level >= upgrade.maxLevel) {
            button.text = context.getString(R.string.maxed)
            button.isEnabled = false
        } else {
            val cost = upgrade.costAt(level)
            button.text = context.getString(R.string.buy_cost, cost)
            button.isEnabled = true
            // Dim the button when the player can't afford it; tapping still explains why.
            button.alpha = if (state != null && state.scrap >= cost) 1f else 0.5f
        }
        button.setOnClickListener { onBuy(upgrade) }
        return row
    }
}
