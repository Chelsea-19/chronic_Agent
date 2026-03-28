# Paper-Oriented Contribution Summary

This repository realizes a publication-grade, localized AI medical agent system designed specifically for self-management and clinical reporting in Mainland China, focusing on prevalent chronic conditions like Type 2 Diabetes (T2DM) and Hypertension. 

The transition from a prototype logic to a research-grade environment is backed by three distinct scientific contributions suitable for conference paper framing (e.g., AMIA, CHIL, MICCAI, or top-tier NLP/Clinical informatics venues):

## 1. The Unified Longitudinal Timeline Framework
Current LLM agents handle historical context via rudimentary RAG or sliding memory windows, losing chronological fidelity and missing long-term quantitative trends necessary for chronic care. We introduced the `TimelineEngine`, an explicit abstraction that normalizes heterogeneous signals (chat, meals, symptoms, medication gaps) onto a structured mathematical timeline. This enables rigorous algorithmic detection of anomalies (e.g., linking specific dietary high-sugar behaviors to glycemic spikes) before passing any data to generative LLMs, ensuring higher accuracy and drastically reduced hallucinations.

## 2. Evidence-Grounded, Traceable Clinician Digest
Pre-visit summarization is often prone to fabrication in LLMs. We introduced an explicit `SupportTrace` architecture. Every risk flag, trend calculation, and diagnostic assertion outputted by the `ClinicianDigestService` must securely map to a specific primary event entry (with confidence, timestamp, and source text provenances). Generating the digest follows a strict deterministic-to-generative pathway, resulting in a safe, auditor-ready SOAP-formatted summary that clinicians can trust without querying the raw patient conversational history.

## 3. State-Machine Guardrailed Medical Workflows
Replacing a "single-prompt" logic pattern, we implemented robust, observable deterministic state machines (`StateMachineEngine` and `AuditLog`). This ensures multi-step clinical behaviors like Medication Reconciliation or Daily Review are executed with guaranteed transactional consistency. It enables granular evaluation: researchers can pinpoint exact pipeline failures within the workflow definitions, solving the black-box nature of current autonomous agents.

These features establish a robust, defensible infrastructure combining deterministic clinical safety boundaries with the fluent ingestion and reasoning capabilities of modern LLMs.
