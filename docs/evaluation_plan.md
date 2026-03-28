# Evaluation Plan

For the resulting publication, we propose a rigorous evaluation schema that quantifies the effectiveness of our longitudinal extraction, risk determination, and generated digests.

## Core Evaluation Targets
We assess performance along three main axes:
1. **Extraction Fidelity (n=300 synthetic inputs)**: Parsing multi-modal, unstructured logs into exact parameters (Medications, Bloops Pressure, Glucose, Meals).
   - Metrics: Precision, Recall, F1 for Named Entities and Parameter Values.
2. **Clinical Reasoning (n=200 longitudinal windows)**: Determining clinically-sound risk flags (e.g. Adherence Gaps vs. Unhealthy Diet vs. Somatic Symptoms).
   - Metrics: Diagnostic Odds Ratio, Sensitivity, Specificity comparing the Agent's flags to synthetically generated ground-truth or human Clinician labels.
3. **Digest Quality & Traceability (n=50 pre-visit summaries)**: Evaluating the summary structure, correctness, and its traceability back to unstructured daily events.
   - Metrics: Evaluator-In-The-Loop (LLM-as-a-judge or human panel) assigning Likert scores (1-5) on:
     - Completeness of the objective data sum.
     - Clinical relevance of the assessment plan flags.
     - Accuracy of the provenance mapping (`SupportTrace` alignment to original `.raw_text`).

## Setup Execution
Run `python src/chronic_agent/evaluation/runner.py <benchmark_json>` against the dataset produced by `generator.py`. This script iterates through `EvalSample` contracts and scores each module independently.

## Data Schema & Localization
- Ensure the datasets heavily rely on local Chinese syntax and meal patterns ("全糖奶茶", "二甲双胍", "头晕").
- The evaluation must penalize hallucinations (False Positives in extraction) stricter than False Negatives, reflecting the high-stakes clinical standard.
