package com.tutorplatform.app.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.tutorplatform.app.R
import com.tutorplatform.app.model.Message

class MessageAdapter : RecyclerView.Adapter<MessageAdapter.ViewHolder>() {
    private val items = mutableListOf<Message>()

    fun submitList(newItems: List<Message>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_message, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        holder.message.text = item.text
        val meta = listOfNotNull(item.sender_id, item.created_at).joinToString(" • ")
        holder.meta.text = if (meta.isBlank()) "сообщение" else meta
    }

    override fun getItemCount(): Int = items.size

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val message: TextView = view.findViewById(R.id.message_text)
        val meta: TextView = view.findViewById(R.id.message_meta)
    }
}
