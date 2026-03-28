# China Chronic Care Agent Platform

This repository constitutes a publication-grade, localized artificial intelligence platform specifically designed for longitudinal chronic disease management (encompassing Type 2 Diabetes and Hypertension) within the context of Mainland China.

## Table of Contents
- [Architecture & Design Philosophy](#architecture--design-philosophy)
- [Key Research Features](#key-research-features)
- [Project Layout & Modules](#project-layout--modules)
- [Installation & Deployment](#installation--deployment)
- [Evaluation Modules](#evaluation-modules)
- [Additional Documentation](#additional-documentation)

## Architecture & Design Philosophy
This system is strictly structured along a vertical feature-first ideology mapping clinical requirements directly to Python namespaces. Crucially, the system moves away from typical RAG architectures; it computes a strictly chronological `TimelineEngine` capable of aggregating disparate event signals (from arbitrary textual meal entries, to precise blood pressure integer readings). State machine configurations control workflow boundaries, significantly curbing LLM hallucination and unpredictability. See deeper rationale inside `docs/architecture.md`.

## Key Research Features
- **Deterministic-first Longitudinal Timeline Engine**: Reduces reasoning burden on generation backends by strictly compiling arrays of anomalies (and standard deviations) computationally in Python, explicitly tracing quantitative trends over weeks/months.
- **Clinician Digest (Support Traces)**: Automatically translates the raw timeline logs into an auditor-ready SOAP structure. Employs `SupportTrace` entities; every critical claim maps to the raw entry's origin point.
- **Guardrailed Workflow Service**: Essential clinical activities like "Daily Reviews" or "Pre-visit Summaries" are bounded by explicit deterministic state machines and execution checkpoints within an active Worker loop.

## Project Layout & Modules
```text
.
├── apps/               # Entrypoints: fastAPI routers and background worker scripts
├── docs/               # Research materials (Architecture, Safety, Ablation, Evaluation Plans)
├── exports/            # Report generation storage (.pdf, .docx, .html)
├── src/chronic_agent/
│   ├── core/           # Contracts, timeline definitions, and domain schema mapping
│   ├── platform/       # Orchestration underlying DB access and SQL repository interactions
│   ├── features/       # Companion/Chat, Meals, Medications, Summaries, Reports, Workflows
│   ├── agent/          # Bound Language Model interactions
│   └── evaluation/     # Reproducibility artifacts: synthetic generators, schemas, runner scripts
```
For a deeper granular summary, refer to `docs/module_map.md`.

## Installation & Deployment

### Quickstart Example
```bash
# 1. Initialize environment
python -m venv .venv
# On Windows: .venv\Scripts\activate. On Unix: source .venv/bin/activate
pip install -r requirements.txt

# 2. Database (SQLite auto-initializes)
export PYTHONPATH="$(pwd)/src:$(pwd)" # On Windows: $env:PYTHONPATH="$(pwd)/src;$(pwd)"

# 3. Start API Service
uvicorn apps.api.app.main:app --reload

# 4. Start Background Worker (Separate terminal)
export PYTHONPATH="$(pwd)/src:$(pwd)"
python -m apps.workers.run
```

## Evaluation Modules
Our integration provides extensive testing boundaries. Researchers may generate 300+ synthetic patient interactions using Chinese cultural contexts mimicking exact T2DM + Hypertension profiles.
```bash
# Populates JSON test data 
python src/chronic_agent/evaluation/generator.py benchmark_data.json

# Evaluates current logic implementations against ground-truth parameters
python src/chronic_agent/evaluation/runner.py benchmark_data.json
```

## Additional Documentation
Please meticulously review our research notes mapping our boundaries, schemas, and ablation methodologies prior to any manuscript preparation:
- [Evaluation Plan](docs/evaluation_plan.md)
- [Ablation Plan](docs/ablation_plan.md) 
- [Contribution Summary](docs/contribution_summary.md)
- [Limitations & Safety Notes](docs/limitations_safety.md)
