import json
import random
from datetime import datetime, timedelta

from chronic_agent.evaluation.schema import DigestEvalSample, MealRiskEvalSample, ParsingEvalSample


class SyntheticDataGenerator:
    """
    Generates synthetic benchmark datasets for Mainland China T2DM/Hypertension scenarios.
    Useful for populating databases prior to running evaluations or A/B testing baselines.
    """

    @staticmethod
    def generate_patient_context(idx: int) -> dict:
        names = ["张三", "李四", "王五", "赵六", "陈七"]
        return {
            "name": f"{random.choice(names)}_{idx}",
            "gender": random.choice(["男", "女"]),
            "age": random.randint(45, 75),
            "diagnosis_summary": "2型糖尿病，高血压三级"
        }

    @staticmethod
    def generate_digest_samples(count: int = 5) -> list[DigestEvalSample]:
        samples = []
        for i in range(count):
            base_date = datetime.utcnow()
            events = []
            sys_bp = []
            
            # Generate 14 days of events
            for days_ago in range(14):
                dt = base_date - timedelta(days=days_ago)
                
                # bp
                sys = random.randint(130, 160)
                dia = random.randint(80, 100)
                sys_bp.append(sys)
                events.append({
                    "type": "blood_pressure",
                    "num1": sys,
                    "num2": dia,
                    "occurred_at": dt.isoformat()
                })
                
                # fg
                if random.random() > 0.5:
                    fg = round(random.uniform(6.0, 9.5), 1)
                    events.append({
                        "type": "fasting_glucose",
                        "num1": fg,
                        "occurred_at": dt.isoformat()
                    })

            avg_sys = sum(sys_bp) / len(sys_bp)
            flags = []
            if avg_sys >= 140:
                flags.append("高血压")

            samples.append(
                DigestEvalSample(
                    id=f"digest_synth_{i}",
                    patient_context=SyntheticDataGenerator.generate_patient_context(i),
                    input_events=events,
                    expected_trend_sys_bp_min=avg_sys - 5,
                    expected_trend_sys_bp_max=avg_sys + 5,
                    expected_flags=flags,
                    must_include_evidence=["bp_trend"]
                )
            )
        return samples

    @staticmethod
    def generate_meal_samples() -> list[MealRiskEvalSample]:
        return [
            MealRiskEvalSample(
                id="meal_1",
                patient_context={"diagnosis_summary": "2型糖尿病"},
                input_text="晚饭喝了全糖奶茶，还吃了两碗米饭",
                expected_tags=["高糖", "高碳水"],
                expected_carbs_category="high",
            ),
            MealRiskEvalSample(
                id="meal_2",
                patient_context={"diagnosis_summary": "高血压"},
                input_text="中午吃了一份很咸的腊肉炒饭，加了腐乳",
                expected_tags=["高钠", "高碳水"],
                forbidden_tags=["健康饮食"],
            ),
            MealRiskEvalSample(
                id="meal_3",
                patient_context={},
                input_text="早上吃了水煮蛋，一杯无糖豆浆，半截玉米",
                expected_tags=["低脂", "健康比例"],
                forbidden_tags=["高糖", "高碳水"],
                expected_carbs_category="medium",
            )
        ]

    @staticmethod
    def generate_parsing_samples() -> list[ParsingEvalSample]:
        return [
            ParsingEvalSample(
                id="parse_1",
                patient_context={},
                input_text="今天早餐后吃了二甲双胍 500mg，感觉还好",
                expected_medications=[{"medicine_name": "二甲双胍", "dose": "500mg"}]
            ),
            ParsingEvalSample(
                id="parse_2",
                patient_context={},
                input_text="早上血压 148/92，有点头晕",
                expected_health_metrics=[{"type": "blood_pressure", "num1": 148.0, "num2": 92.0}],
            )
        ]

    @classmethod
    def export_to_json(cls, filepath: str):
        data = {
            "digest_samples": [s.model_dump() for s in cls.generate_digest_samples()],
            "meal_samples": [s.model_dump() for s in cls.generate_meal_samples()],
            "parsing_samples": [s.model_dump() for s in cls.generate_parsing_samples()],
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        SyntheticDataGenerator.export_to_json(sys.argv[1])
        print(f"Generated synthetic evaluation data -> {sys.argv[1]}")
