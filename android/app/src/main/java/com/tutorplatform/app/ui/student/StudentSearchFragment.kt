package com.tutorplatform.app.ui.student

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.SeekBar
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.tutorplatform.app.R
import com.tutorplatform.app.adapters.SimpleItemAdapter
import com.tutorplatform.app.model.SimpleItem
import com.tutorplatform.app.model.SuggestionRequest
import com.tutorplatform.app.network.ApiClient
import com.tutorplatform.app.ui.TutorDetailActivity
import com.tutorplatform.app.util.show
import com.tutorplatform.app.util.toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.util.Locale

class StudentSearchFragment : Fragment(R.layout.fragment_student_search) {
    private lateinit var resultsAdapter: SimpleItemAdapter
    private lateinit var progress: ProgressBar

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val subjectInput = view.findViewById<EditText>(R.id.search_subject)
        val maxRateInput = view.findViewById<EditText>(R.id.search_max_rate)
        val minExpInput = view.findViewById<EditText>(R.id.search_min_exp)
        val tagsInput = view.findViewById<EditText>(R.id.search_tags)

        val wEfficiency = view.findViewById<SeekBar>(R.id.weight_efficiency)
        val wCommunication = view.findViewById<SeekBar>(R.id.weight_communication)
        val wExpertise = view.findViewById<SeekBar>(R.id.weight_expertise)
        val wResponsiveness = view.findViewById<SeekBar>(R.id.weight_responsiveness)
        val wTags = view.findViewById<SeekBar>(R.id.weight_tags)

        val vEfficiency = view.findViewById<TextView>(R.id.weight_efficiency_value)
        val vCommunication = view.findViewById<TextView>(R.id.weight_communication_value)
        val vExpertise = view.findViewById<TextView>(R.id.weight_expertise_value)
        val vResponsiveness = view.findViewById<TextView>(R.id.weight_responsiveness_value)
        val vTags = view.findViewById<TextView>(R.id.weight_tags_value)

        bindWeight(wEfficiency, vEfficiency, 0.30)
        bindWeight(wCommunication, vCommunication, 0.15)
        bindWeight(wExpertise, vExpertise, 0.20)
        bindWeight(wResponsiveness, vResponsiveness, 0.15)
        bindWeight(wTags, vTags, 0.20)

        progress = view.findViewById(R.id.search_progress)
        val list = view.findViewById<RecyclerView>(R.id.search_results)
        list.layoutManager = LinearLayoutManager(requireContext())
        resultsAdapter = SimpleItemAdapter { item ->
            val intent = Intent(requireContext(), TutorDetailActivity::class.java)
            intent.putExtra(TutorDetailActivity.EXTRA_TUTOR_ID, item.id)
            startActivity(intent)
        }
        list.adapter = resultsAdapter

        view.findViewById<Button>(R.id.search_button).setOnClickListener {
            val subject = subjectInput.text.toString().trim().ifBlank { null }
            val maxRate = maxRateInput.text.toString().trim().toIntOrNull()
            val minExp = minExpInput.text.toString().trim().toIntOrNull()
            val desiredTags = tagsInput.text.toString()
                .split(",")
                .map { it.trim() }
                .filter { it.isNotBlank() }

            val request = SuggestionRequest(
                subject = subject,
                max_rate = maxRate,
                min_experience = minExp,
                weight_efficiency = wEfficiency.progress / 100.0,
                weight_communication = wCommunication.progress / 100.0,
                weight_expertise = wExpertise.progress / 100.0,
                weight_responsiveness = wResponsiveness.progress / 100.0,
                weight_tags = wTags.progress / 100.0,
                desired_tags = desiredTags
            )
            fetchSuggestions(request)
        }
    }

    private fun fetchSuggestions(request: SuggestionRequest) {
        progress.show(true)
        lifecycleScope.launch {
            try {
                val suggestions = withContext(Dispatchers.IO) {
                    ApiClient.customService(requireContext()).getSuggestions(request)
                }
                val items = suggestions.map { suggestion ->
                    val subtitle = listOfNotNull(
                        suggestion.specialization,
                        suggestion.hourly_rate?.let { "Ставка $it" },
                        suggestion.experience_years?.let { "Опыт $it" }
                    ).joinToString(" • ")
                    SimpleItem(
                        id = suggestion.user_id.toString(),
                        title = suggestion.full_name,
                        subtitle = subtitle,
                        meta = "Совпадение ${String.format(Locale.US, "%.2f", suggestion.match_score)}%"
                    )
                }
                resultsAdapter.submitList(items)
            } catch (ex: Exception) {
                requireContext().toast("Не удалось выполнить поиск: ${ex.message}")
            } finally {
                progress.show(false)
            }
        }
    }

    private fun bindWeight(seekBar: SeekBar, valueView: TextView, defaultValue: Double) {
        val initial = (defaultValue * 100).toInt()
        seekBar.progress = initial
        valueView.text = String.format(Locale.US, "%.2f", defaultValue)
        seekBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar, progress: Int, fromUser: Boolean) {
                valueView.text = String.format(Locale.US, "%.2f", progress / 100.0)
            }
            override fun onStartTrackingTouch(seekBar: SeekBar) = Unit
            override fun onStopTrackingTouch(seekBar: SeekBar) = Unit
        })
    }
}
