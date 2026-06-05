package com.tutorplatform.app.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.textview.MaterialTextView
import com.tutorplatform.app.R
import com.tutorplatform.app.util.DateUtils

class LessonAdapter(
    private val onClick: ((String) -> Unit)? = null
) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    data class LessonDisplay(
        val lessonId: String,
        val tutorName: String,
        val tutorColor: Int,
        val startDatetime: String,
        val endDatetime: String,
        val status: String
    )

    companion object {
        private const val TYPE_FUTURE_HEADER = 0
        private const val TYPE_PAST_HEADER = 1
        private const val TYPE_LESSON = 2
        private const val TYPE_DIVIDER = 3
    }

    private val items = mutableListOf<Any?>() // String, LessonDisplay, or DividerMarker

    private object DividerMarker

    fun submitList(future: List<LessonDisplay>, past: List<LessonDisplay>) {
        items.clear()
        if (future.isNotEmpty()) {
            items.add("Предстоящие")
            items.addAll(future)
        }
        if (future.isNotEmpty() && past.isNotEmpty()) {
            items.add(DividerMarker)
        }
        if (past.isNotEmpty()) {
            items.add("Прошедшие")
            items.addAll(past)
        }
        notifyDataSetChanged()
    }

    override fun getItemViewType(position: Int): Int {
        val item = items[position]
        return when {
            item is String && item == "Предстоящие" -> TYPE_FUTURE_HEADER
            item is String && item == "Прошедшие" -> TYPE_PAST_HEADER
            item is DividerMarker -> TYPE_DIVIDER
            else -> TYPE_LESSON
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        val inflater = LayoutInflater.from(parent.context)
        return when (viewType) {
            TYPE_FUTURE_HEADER, TYPE_PAST_HEADER -> {
                val v = inflater.inflate(R.layout.item_section_header, parent, false)
                SectionHeaderViewHolder(v)
            }
            TYPE_DIVIDER -> {
                val v = inflater.inflate(R.layout.item_section_divider, parent, false)
                DividerViewHolder(v)
            }
            else -> {
                val v = inflater.inflate(R.layout.item_lesson, parent, false)
                LessonViewHolder(v)
            }
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (holder) {
            is SectionHeaderViewHolder -> {
                holder.text.text = items[position] as String
            }
            is LessonViewHolder -> {
                val lesson = items[position] as LessonDisplay
                holder.date.text = DateUtils.formatDateOnly(lesson.startDatetime)
                holder.time.text = "${DateUtils.formatTimeOnly(lesson.startDatetime)} — ${DateUtils.formatTimeOnly(lesson.endDatetime)}"
                holder.tutor.text = lesson.tutorName
                holder.status.text = mapStatus(lesson.status)
                holder.colorBar.setBackgroundColor(lesson.tutorColor)
                holder.itemView.setOnClickListener { onClick?.invoke(lesson.lessonId) }
            }
        }
    }

    override fun getItemCount(): Int = items.size

    private fun mapStatus(status: String): String = when (status) {
        "planned" -> "Запланирован"
        "completed" -> "Проведен"
        "cancelled" -> "Отменен"
        else -> status
    }

    // ── ViewHolders ──

    class SectionHeaderViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val text: MaterialTextView = view.findViewById(R.id.section_header_text)
    }

    class DividerViewHolder(view: View) : RecyclerView.ViewHolder(view)

    class LessonViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val date: MaterialTextView = view.findViewById(R.id.lesson_date)
        val time: MaterialTextView = view.findViewById(R.id.lesson_time)
        val tutor: MaterialTextView = view.findViewById(R.id.lesson_tutor)
        val status: MaterialTextView = view.findViewById(R.id.lesson_status)
        val colorBar: View = view.findViewById(R.id.lesson_color_bar)
    }
}
