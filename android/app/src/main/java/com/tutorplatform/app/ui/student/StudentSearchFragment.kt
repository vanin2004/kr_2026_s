package com.tutorplatform.app.ui.student

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.ProgressBar
import android.widget.SeekBar
import android.widget.TextView
import androidx.appcompat.widget.AppCompatAutoCompleteTextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.chip.Chip
import com.google.android.material.chip.ChipGroup
import com.tutorplatform.app.R
import com.tutorplatform.app.adapters.SimpleItemAdapter
import com.tutorplatform.app.model.SimpleItem
import com.tutorplatform.app.model.SuggestionRequest
import com.tutorplatform.app.model.SuggestionWeights
import com.tutorplatform.app.model.Subject
import com.tutorplatform.app.model.Tag
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

    // Subject autocomplete
    private lateinit var subjectInput: AppCompatAutoCompleteTextView
    private var subjectMap: Map<String, String> = emptyMap() // name -> id
    private var selectedSubjectId: String? = null

    // Tag chips
    private lateinit var tagChipGroup: ChipGroup
    private lateinit var tagInput: AppCompatAutoCompleteTextView
    private var tagMap: Map<String, String> = emptyMap() // name -> id
    private val selectedTagIds = mutableSetOf<String>()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Subjects
        subjectInput = view.findViewById(R.id.search_subject)
        subjectInput.setOnItemClickListener { _, _, _, _ ->
            selectedSubjectId = subjectMap[subjectInput.text.toString().trim()]
        }
        subjectInput.setOnFocusChangeListener { _, hasFocus ->
            if (hasFocus && subjectInput.adapter?.count ?: 0 > 0) {
                subjectInput.showDropDown()
            }
        }

        // Max rate
        val maxRateInput = view.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.search_max_rate)

        // Min experience
        val minExpInput = view.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.search_min_exp)

        // Tags
        tagChipGroup = view.findViewById(R.id.tag_chip_group)
        tagInput = view.findViewById(R.id.search_tags)
        tagInput.setOnItemClickListener { _, _, _, _ ->
            val name = tagInput.text.toString().trim()
            val id = tagMap[name]
            if (id != null && id !in selectedTagIds) {
                addTagChip(name, id)
                selectedTagIds.add(id)
                tagInput.setText("")
            }
        }
        tagInput.setOnFocusChangeListener { _, hasFocus ->
            if (hasFocus && tagInput.adapter?.count ?: 0 > 0) {
                tagInput.showDropDown()
            }
        }

        // Weights
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
        val searchList = view.findViewById<RecyclerView>(R.id.search_results)
        searchList.layoutManager = LinearLayoutManager(requireContext())
        resultsAdapter = SimpleItemAdapter { item ->
            val intent = Intent(requireContext(), TutorDetailActivity::class.java)
            intent.putExtra(TutorDetailActivity.EXTRA_TUTOR_ID, item.id)
            startActivity(intent)
        }
        searchList.adapter = resultsAdapter

        view.findViewById<Button>(R.id.search_button).setOnClickListener {
            performSearch(
                maxRate = maxRateInput.text?.toString()?.trim()?.toIntOrNull(),
                minExp = minExpInput.text?.toString()?.trim()?.toIntOrNull(),
                wEff = wEfficiency.progress / 100.0,
                wComm = wCommunication.progress / 100.0,
                wExp = wExpertise.progress / 100.0,
                wResp = wResponsiveness.progress / 100.0,
                wTag = wTags.progress / 100.0
            )
        }

        // Load data from server
        loadSubjects()
        loadTags()
    }

    // ─── Load Subjects ────────────────────────────────────────────

    private fun loadSubjects() {
        lifecycleScope.launch {
            try {
                val subjects = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext()).getSubjects()
                }
                subjectMap = subjects.associate { it.name to it.id }
                setupSubjectAdapter(subjects.map { it.name })
            } catch (e: Exception) {
                requireContext().toast("Не удалось загрузить предметы: ${e.message}")
            }
        }
    }

    private fun setupSubjectAdapter(names: List<String>) {
        val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, names)
        subjectInput.setAdapter(adapter)
        subjectInput.threshold = 0
    }

    // ─── Load Tags ────────────────────────────────────────────────

    private fun loadTags() {
        lifecycleScope.launch {
            try {
                val tags = withContext(Dispatchers.IO) {
                    ApiClient.dataService(requireContext()).getTags()
                }
                tagMap = tags.associate { it.name to it.id }
                setupTagAdapter(tags.map { it.name })
            } catch (e: Exception) {
                requireContext().toast("Не удалось загрузить теги: ${e.message}")
            }
        }
    }

    private fun setupTagAdapter(names: List<String>) {
        val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, names)
        tagInput.setAdapter(adapter)
        tagInput.threshold = 0
    }

    private fun addTagChip(name: String, id: String) {
        val chip = Chip(requireContext()).apply {
            text = name
            tag = id
            isCloseIconVisible = true
            setOnCloseIconClickListener {
                tagChipGroup.removeView(this)
                selectedTagIds.remove(tag as String)
            }
        }
        tagChipGroup.addView(chip)
    }

    // ─── Search ───────────────────────────────────────────────────

    private fun performSearch(
        maxRate: Int?,
        minExp: Int?,
        wEff: Double,
        wComm: Double,
        wExp: Double,
        wResp: Double,
        wTag: Double
    ) {
        if (selectedSubjectId == null) {
            requireContext().toast("Выберите предмет из списка")
            return
        }

        val request = SuggestionRequest(
            subject_id = selectedSubjectId!!,
            max_price = maxRate,
            min_experience = minExp,
            required_tag_ids = selectedTagIds.toList().takeIf { it.isNotEmpty() },
            weights = SuggestionWeights(
                k1_effectiveness = wEff,
                k2_communication = wComm,
                k3_expertise = wExp,
                k4_responsiveness = wResp,
                k5_tags = wTag
            )
        )
        fetchSuggestions(request)
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
                        suggestion.hourly_rate?.let { "Ставка $it" },
                        if (suggestion.is_new == true) "Новый" else null
                    ).joinToString(" • ")
                    SimpleItem(
                        id = suggestion.tutor_id,
                        title = suggestion.full_name ?: "Без имени",
                        subtitle = subtitle,
                        meta = "Совпадение ${String.format(Locale.US, "%.2f", suggestion.score)}%"
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
