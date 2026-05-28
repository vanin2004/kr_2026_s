package com.tutorplatform.app.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.tutorplatform.app.R
import com.tutorplatform.app.model.SimpleItem

class SimpleItemAdapter(
    private val onClick: ((SimpleItem) -> Unit)? = null
) : RecyclerView.Adapter<SimpleItemAdapter.ViewHolder>() {

    private val items = mutableListOf<SimpleItem>()

    fun submitList(newItems: List<SimpleItem>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_simple, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        holder.title.text = item.title
        holder.subtitle.text = item.subtitle ?: ""
        holder.subtitle.visibility = if (item.subtitle.isNullOrBlank()) View.GONE else View.VISIBLE
        holder.meta.text = item.meta ?: ""
        holder.meta.visibility = if (item.meta.isNullOrBlank()) View.GONE else View.VISIBLE
        holder.itemView.setOnClickListener { onClick?.invoke(item) }
    }

    override fun getItemCount(): Int = items.size

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val title: TextView = view.findViewById(R.id.item_title)
        val subtitle: TextView = view.findViewById(R.id.item_subtitle)
        val meta: TextView = view.findViewById(R.id.item_meta)
    }
}
