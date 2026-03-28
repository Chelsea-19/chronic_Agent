from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class EvalSample(BaseModel):
    id: str
    patient_context: dict[str, Any]
    input_text: str | None = None
    input_events: list[dict[str, Any]] = []


class DigestEvalSample(EvalSample):
    """
    Schema for evaluating clinician digest generation.
    """
    expected_flags: list[str] = []
    expected_action_items: list[str] = []
    expected_trend_sys_bp_min: float | None = None
    expected_trend_sys_bp_max: float | None = None
    must_include_evidence: list[str] = []


class MealRiskEvalSample(EvalSample):
    """
    Schema for evaluating meal parsing and risk tagging.
    """
    expected_tags: list[str] = []
    forbidden_tags: list[str] = []
    expected_carbs_category: str | None = None


class ParsingEvalSample(EvalSample):
    """
    Schema for testing Chinese clinical entity parsing.
    """
    expected_medications: list[dict[str, Any]] = []
    expected_health_metrics: list[dict[str, Any]] = []


class EvalResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    sample_id: str
    passed: bool
    score: float
    details: dict[str, Any]
    baseline_used: str | None = None
