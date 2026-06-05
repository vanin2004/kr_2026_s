package com.tutorplatform.app.adapters

import android.content.Context
import android.util.TypedValue
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.card.MaterialCardView
import com.google.android.material.textview.MaterialTextView
import com.tutorplatform.app.R
import com.tutorplatform.app.model.Message
import com.tutorplatform.app.util.DateUtils

class MessageAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {
    private val items = mutableListOf<Message>()
    private var myUserId: String = ""
    private var otherUserId: String = ""
    private var otherUserName: String = ""
    private var bubbleMaxWidth = 0

    companion object {
        private const val TYPE_MY = 0
        private const val TYPE_OTHER = 1
        private const val BUBBLE_WIDTH_RATIO = 0.85f
    }

    fun setParticipants(myUserId: String, otherUserId: String, otherUserName: String) {
        this.myUserId = myUserId
        this.otherUserId = otherUserId
        this.otherUserName = otherUserName
    }

    fun submitList(newItems: List<Message>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    override fun getItemViewType(position: Int): Int {
        return if (items[position].sender_id == myUserId) TYPE_MY else TYPE_OTHER
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_message, parent, false)
        // вычисляем 85% ширины экрана один раз
        if (bubbleMaxWidth == 0) {
            val displayMetrics = parent.context.resources.displayMetrics
            bubbleMaxWidth = (displayMetrics.widthPixels * BUBBLE_WIDTH_RATIO).toInt()
        }
        return MessageViewHolder(view, bubbleMaxWidth)
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val vh = holder as MessageViewHolder
        val item = items[position]
        val context = vh.itemView.context
        val isMyMessage = item.sender_id == myUserId

        // --- текст ---
        vh.message.text = item.text

        // --- мета (время + имя для чужих) ---
        val formattedTime = if (item.created_at != null) {
            DateUtils.formatDateTime(item.created_at)
        } else {
            ""
        }
        val metaParts = mutableListOf<String>()
        if (!isMyMessage && otherUserName.isNotBlank()) {
            metaParts.add(otherUserName)
        }
        if (formattedTime.isNotBlank()) {
            metaParts.add(formattedTime)
        }
        vh.meta.text = metaParts.joinToString(" • ")

        // --- прижатие к краю ---
        val flLp = vh.bubble.layoutParams as FrameLayout.LayoutParams
        flLp.gravity = if (isMyMessage) Gravity.END else Gravity.START
        vh.bubble.layoutParams = flLp

        // --- цвета из темы ---
        if (isMyMessage) {
            val bg = resolveThemeColor(context, R.attr.chatMyBubbleColor)
            val fg = resolveThemeColor(context, R.attr.chatMyBubbleTextColor)
            vh.bubble.setCardBackgroundColor(bg)
            vh.message.setTextColor(fg)
            vh.meta.setTextColor(fg)
        } else {
            val bg = resolveThemeColor(context, R.attr.chatOtherBubbleColor)
            val fg = resolveThemeColor(context, R.attr.chatOtherBubbleTextColor)
            vh.bubble.setCardBackgroundColor(bg)
            vh.message.setTextColor(fg)
            vh.meta.setTextColor(fg)
        }
    }

    override fun getItemCount(): Int = items.size

    private fun resolveThemeColor(context: Context, attrRes: Int): Int {
        val tv = TypedValue()
        if (context.theme.resolveAttribute(attrRes, tv, true)) {
            return if (tv.type == TypedValue.TYPE_INT_COLOR_ARGB8 ||
                       tv.type == TypedValue.TYPE_INT_COLOR_RGB4) {
                tv.data
            } else if (tv.type == TypedValue.TYPE_REFERENCE) {
                context.resources.getColor(tv.resourceId, context.theme)
            } else {
                0
            }
        }
        return 0
    }

    class MessageViewHolder(view: View, maxWidth: Int) : RecyclerView.ViewHolder(view) {
        val bubble: MaterialCardView = view.findViewById(R.id.message_bubble)
        val message: MaterialTextView = view.findViewById(R.id.message_text)
        val meta: MaterialTextView = view.findViewById(R.id.message_meta)

        init {
            message.setMaxWidth(maxWidth)
        }
    }
}
