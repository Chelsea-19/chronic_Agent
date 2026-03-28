# Module Map

**Project Root**: `D:\DD\chronic_agent_super`

## Top-Level
- `README.md`: Project summary, setup instructions, and evaluation entry points.
- `requirements.txt`: Python package dependencies.
- `run_api.sh` / `run_worker.sh`: Execution scripts.

## `apps/`
- `api/app/routers.py`: FastAPI endpoints. Kept thin. Relies entirely on `features/` services.
- `workers/run.py`: Background job executor. Modified to handle system beats and async workflows.

## `src/chronic_agent/`

### 1. `core/` (Domain Logic & Architectures)
- `contracts.py`: Pydantic definitions bridging API and business logic.
- `timeline.py`: The `TimelineEngine` implementation. Normalizes unstructured records (Meals, Health, Chat) into chronologically sorted, anomaly-tagged objects (`UnifiedEvent`).

### 2. `platform/` (Infrastructure Layer)
- `db.py`: SQLAlchemy ORM mapping. Includes `PatientProfile`, `HealthEvent`, `AuditLog`, `SupportTrace`, etc.
- `repositories.py`: Data-access layer abstracts DB calls from features. Includes `DigestRepository`, `ReportRepository`, `TimelineRepository`, `WorkflowRepository`.
- `settings.py`: Configuration and environment parsers.

### 3. `features/` (Bounded Context Services)
- `clinician_digest/service.py`: Employs `TimelineEngine` to generate SOAP-structured reports with embedded evidence/provenance metadata.
- `workflows/service.py`: A full State Machine Engine (`StateMachineEngine`) mapping workflow steps to functional behaviors along with `AuditLog` checkpoints.
- `health/`, `medications/`, `meals/`, `reminders/`, `companion/`: Vertical slices connecting domain behaviors with `platform` repos.

### 4. `evaluation/` (Research & Benchmarking)
- `schema.py`: Definition of performance measures (`EvalSample`, `EvalResult`, `DigestEvalSample`).
- `generator.py`: Generates synthetic ground-truth data targeted at Mainland China T2DM datasets for testing baseline pipelines.
- `runner.py`: Executes tests, returning precision/recall statistics.

### 5. `docs/`
Contains architectural documents, methodology ablation strategies, and safety boundaries necessary for publication.
