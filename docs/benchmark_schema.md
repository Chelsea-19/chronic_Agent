# Benchmark Schema Description

To compare different iterations of the chronic care agent (e.g. comparing Naive RAG vs `TimelineEngine`, or pure LLM vs Deterministic Digest generation), we have engineered evaluation schemas defined in `src/chronic_agent/evaluation/schema.py`.

The datasets produced by the synthetic system (`generator.py`) adhere strictly to these models:

## `EvalSample` (Base)
Requires:
- `id`: unique test identifier.
- `patient_context`: relevant patient data (`age`, `diagnosis_summary`, etc.).
- `input_text` / `input_events`: Unstructured data the model must ingest.

## 1. `MealRiskEvalSample`
Evaluates Dietary parsing and semantic risk tagging under Chinese culture settings.
- `expected_tags`: e.g., `["高糖", "高碳水"]`
- `forbidden_tags`: Any outputs mapping to these denote hallucination or reasoning failure.
- `expected_carbs_category`: Enforces quantitative estimation capacity.

## 2. `DigestEvalSample`
Evaluates the capability of producing a Clinician Digest. Instead of exact string matching, we evaluate using extraction rules and bounding boxes.
- `expected_trend_sys_bp_min` & `expected_trend_sys_bp_max`: The generated output MUST explicitly extract a quantitative moving average within this bracket.
- `expected_action_items` & `expected_flags`: The Plan/Assessment portion of the SOAP note MUST suggest these specific intervention goals based on the Timeline history.
- `must_include_evidence`: Enforces that `SupportTrace` repositories link specific timeline entries to high-level clinical claims, heavily penalizing fabricated trends.

## 3. `ParsingEvalSample`
Quantifies entity-level precision.
- Tests translation of inputs like "早餐后吃了二甲双胍 500mg，感觉还好" into expected JSON payloads: `[{"medicine_name": "二甲双胍", "dose": "500mg"}]`.

## Output Formats
Results are collected into an `EvalResult` schema indicating the model baseline used, a binary `passed` condition, a continuous `score` (0.0 to 1.0), and dict-based `details` for logging systematic failures.
