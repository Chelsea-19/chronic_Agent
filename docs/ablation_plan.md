# Ablation Plan

To rigorously demonstrate the value of our methodological contributions (the unified timeline, tracing mechanisms, state-machine workflows), we must compare the full-featured system against stripped-down versions ("ablated baselines").

## 1. No-Timeline Baseline
**Hypothesis**: The longitudinal unified timeline significantly improves the detection of chronic-disease related trends (e.g. repeated missed medication combined with high-sodium diet).
**Ablation**: Replace `TimelineEngine.extract_window` with a naive keyword-search extraction directly against the `ChatMessages` table, similar to a standard RAG pipeline.
**Expected Result**: The No-Timeline baseline will struggle to compute robust averages or identify structured temporal patterns (e.g. "missed 3 pills over the last week").

## 2. No-Digest-Logic Baseline
**Hypothesis**: Deterministic computation of Assessment/flags before text generation yields fewer hallucinations than an endpoint that instructs an LLM to "summarize these events".
**Ablation**: Replace the explicit subjective/objective formatting and trend calculations in `ClinicianDigestService` with a single, unbounded LLM prompt: "Read these DB rows and write a clinical digest."
**Expected Result**: The No-Digest-Logic baseline will occasionally fabricate support traces or hallucinate specific average values (calculating averages poorly using an LLM).

## 3. Naive-RAG Chat Baseline (No Workflows)
**Hypothesis**: Pre-visit summaries and specific routines (e.g., daily reviews) require state machine execution (`WorkflowService`) and fail when handled by a generic companion bot loop.
**Ablation**: Exclusively rely on the companion agent to output "Workflow completed" based on system prompts, instead of using the `StateMachineEngine` definition arrays.
**Expected Result**: High failure rate in step consistency; the naive LLM wrapper easily skips required steps (like explicit Reminder creation or Risk tagging) mid-thought.

## Comparison Strategy
Each baseline will be executed against the synthetic dataset generated via `generator.py`. Results should be mapped onto a radar chart spanning: 1) Clinical Safety, 2) Data Completeness, 3) Temporal Reasoning, 4) Traceability.
