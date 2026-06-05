package com.tutorplatform.app.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.tutorplatform.app.R
import com.tutorplatform.app.model.Application

class ApplicationAdapter(
    private val onAccept: (Application) -> Unit,
    private val onReject: (Application) -> Unit
) : RecyclerView.Adapter<ApplicationAdapter.ViewHolder>() {

    private val items = mutableListOf<Application>()
    private var studentNames: Map<String, String> = emptyMap()

    fun setStudentNames(names: Map<String, String>) {
        studentNames = names
    }

    fun submitList(newItems: List<Application>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_application, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        val studentName = studentNames[item.student_id] ?: "Ученик"
        holder.title.text = studentName
        holder.subtitle.text = item.created_at ?: "-"
        holder.status.text = "Статус: ${mapStatus(item.status)}"
        holder.accept.setOnClickListener { onAccept(item) }
        holder.reject.setOnClickListener { onReject(item) }
    }

    override fun getItemCount(): Int = items.size

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val title: TextView = view.findViewById(R.id.application_title)
        val subtitle: TextView = view.findViewById(R.id.application_subtitle)
        val status: TextView = view.findViewById(R.id.application_status)
        val accept: Button = view.findViewById(R.id.application_accept)
        val reject: Button = view.findViewById(R.id.application_reject)
    }

    private fun mapStatus(status: String): String {
        return when (status) {
            "pending" -> "ожидает"
            "accepted" -> "принята"
            "rejected" -> "отклонена"
            else -> status
        }
    }
}
