# Limitations and Safety Notes

As a research-grade prototype addressing chronic diseases (T2DM & Hypertension), this system introduces boundaries and systemic limitations. It is NOT built for direct, fully autonomous patient clinical intervention without human oversight loops.

## 1. Strict Exclusion of Independent Diagnosis
- The Agent operates purely as a `Clinician-Facing Digest Generator` and `Companion`.
- It is NOT permitted to declare new primary diagnoses or directly modify medication dosages via active commands. The `StateMachineEngine` executes summaries, but medication adherence relies solely on reflecting prescribed input records, not prescribing.

## 2. Safety Layer & Uncertainty Disclaimer
- Automatic digests include an explicit bounding statement: *"本摘要由系统自动基于患者日常数据抽取生成，仅代表记录区间内的数值规律，未涵盖患者所有线下诊疗记录。不构成独立医疗决策方案..."*
- Extracted anomaly events (`is_anomaly = True` in `TimelineEngine`) are treated as *indicators for clinical review*, NOT emergencies activating local EMS protocols. Critical acute states (e.g. Sudden intense chest pain) must be handled by external rules-based triage, outside the RAG boundary.

## 3. Methodological Limitations
- **Data Completeness**: If a patient provides incomplete input (no meals recorded for 3 days), the generated average metrics (e.g., Sodium intake) will misrepresent true risk. The `ClinicianDigestService` partially guards against this by explicitly listing `count` numbers next to extracted averages.
- **Language Boundaries**: The model's evaluation targets localized Chinese terminology (e.g. translating "二甲双胍" to Metformin mechanisms). Performance outside of typical T2DM/Hypertension Mainland language structures (e.g. deeply regional dialects) has not been benchmarked.
- **Information Retrieval**: Complex reasoning spanning multiple months (e.g., a one-year sliding timeline) can overwhelm prompt windows; hence the `TimelineEngine` strictly handles quantitative aggregations inside Python space, relying on LLMs mostly for structured phrasing and simple parsing.
