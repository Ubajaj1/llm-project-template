"""
Eval runner: run the full evaluation suite and fail CI below threshold.
Set this up before you ship — retrofitting evals after the fact is painful.
"""
from dataclasses import dataclass
from pathlib import Path
import json
from core.config import settings


@dataclass
class EvalResult:
    faithfulness: float
    relevancy: float
    passed: bool


class EvalRunner:
    def __init__(self, dataset_path: Path) -> None:
        self.dataset_path = dataset_path

    def load_dataset(self) -> list[dict]:
        """Load a JSONL file of {question, ground_truth, context} records."""
        with open(self.dataset_path) as f:
            return [json.loads(line) for line in f if line.strip()]

    def run(self) -> EvalResult:
        """Run all metrics, return scores, raise if below threshold and eval_fail_ci=true."""
        raise NotImplementedError

    def _check_thresholds(self, result: EvalResult) -> None:
        if not settings.eval_fail_ci:
            return
        if result.faithfulness < settings.eval_threshold_faithfulness:
            raise ValueError(f"Faithfulness {result.faithfulness} below threshold")
        if result.relevancy < settings.eval_threshold_relevancy:
            raise ValueError(f"Relevancy {result.relevancy} below threshold")
