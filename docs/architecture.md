# Architecture Overview

This project implements a research-grade, longitudinally-aware AI agent architecture for chronic disease management (targeting T2DM and Hypertension in Mainland China).

## Core Philosophy: Feature-First & Layered Boundaries

Unlike traditional CRUD apps or monolithic LLM loops, we employ a Feature-First layered architecture:
- **Core (`src/chronic_agent/core`)**: Domain contracts, schemas, and the shared `TimelineEngine`.
- **Platform (`src/chronic_agent/platform`)**: Underlying persistence (`db.py`), repositories, settings, and security. No business logic resides here.
- **Features (`src/chronic_agent/features`)**: Vertically sliced functionality blocks. Each block (`companion`, `workflows`, `clinician_digest`, `meals`, `health`, etc.) implements its own orchestration logic over shared repositories.
- **Agent (`src/chronic_agent/agent`)**: Bounded language modeling logic. Ensures LLMs are used as modular calculators, not unstructured master loops.
- **Evaluation (`src/chronic_agent/evaluation`)**: Headless benchmarking modules for offline reproducibility.

## Methodological Centerpieces

### 1. Longitudinal Timeline Engine (`timeline.py`)
A unified abstraction that maps highly heterogeneous chronic care events (meals, symptom logs, blood pressure, medication adherence gaps, follow-ups) into a strictly chronological sequence.
- **Normalization Strategy**: Every event is embedded with `event_category`, `is_anomaly`, `confidence`, and an explicit `provenance` trace pointing back to the raw unstructured log when applicable.
- **Trend Computation**: Performs statistical anomaly detection over configured temporal windows (e.g., trailing 14 days), capturing non-obvious patterns like "recurrent high-sodium meals preceding morning hypertension".

### 2. Evidence-Grounded Clinician Digest (`clinician_digest/service.py`)
Rather than relying on unconstrained LLM text generation, the system explicitly retrieves anomalies via the Timeline Engine and constructs a strict Subjective-Objective-Assessment-Plan (SOAP) structure.
- **Deterministic First, Generative Second**: Objective trends (e.g., avg fasting glucose, gap frequency) are aggregated deterministically.
- **Support Traces (`SupportTraceRepository`)**: Every generated risk flag maintains an immutable pointer (foreign key or logical ID) to the originating timeline event. This forces the agent to provide audit trails for all clinical claims, mitigating hallucination risks.

### 3. State-Machine Driven Workflows (`workflows/service.py`)
Critical system behaviors (e.g., pre-visit digest, medication reconciliation) are executed as deterministic state machines rather than single-shot prompts.
- Ensures mid-execution transparency. If a workflow fails, the step-level `AuditLog` captures exactly where the inference or integration broke.
