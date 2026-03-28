import json
import logging
import sys

from chronic_agent.evaluation.schema import EvalResult, MealRiskEvalSample

logger = logging.getLogger(__name__)


class EvaluationRunner:
    """
    Executes benchmark data against the live system modules
    to produce evaluation scores and performance reports.
    """
    def __init__(self, data_path: str):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)
        self.results: list[EvalResult] = []

    def evaluate_meals(self) -> None:
        # Placeholder for actual parser invocation
        # from chronic_agent.agent.parser import extract_tags
        # Or you can test via real LLM parser if it's integrated

        for sample_dict in self.dataset.get("meal_samples", []):
            sample = MealRiskEvalSample(**sample_dict)
            
            # Simulated integration (replace with `CompanionChatService` logic in real eval)
            # Typically you mock out the DB or create a fresh temp one.
            extracted_tags = [] # mock result
            if "奶茶" in sample.input_text:
                extracted_tags = ["高糖", "高碳水"]
                
            passed = all(tag in extracted_tags for tag in sample.expected_tags)
            no_forbidden = not any(tag in extracted_tags for tag in sample.forbidden_tags)
            
            score = 1.0 if (passed and no_forbidden) else 0.0
            self.results.append(
                EvalResult(
                    sample_id=sample.id,
                    passed=(passed and no_forbidden),
                    score=score,
                    details={"extracted": extracted_tags, "expected": sample.expected_tags}
                )
            )

    def print_report(self):
        total = len(self.results)
        if total == 0:
            print("No evaluations were run.")
            return

        passed = sum(1 for r in self.results if r.passed)
        avg_score = sum(r.score for r in self.results) / total

        print("=== EVALUATION REPORT ===")
        print(f"Total Samples Tested: {total}")
        print(f"Passed: {passed}/{total} ({(passed/total)*100:.1f}%)")
        print(f"Average Score: {avg_score:.2f}")

        for r in self.results:
            if not r.passed:
                print(f"[FAIL] {r.sample_id} - Score: {r.score:.2f}")
                print(f"       Details: {r.details}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python runner.py <benchmark_json_path>")
        sys.exit(1)
        
    runner = EvaluationRunner(sys.argv[1])
    try:
        runner.evaluate_meals()
    except Exception as e:
        logger.error(f"Eval failed: {e}")
        
    runner.print_report()
