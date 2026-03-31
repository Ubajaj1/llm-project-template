"""
Run the full eval suite locally.
Usage: python scripts/run_evals.py --dataset evals/datasets/golden.jsonl
"""
import argparse
from pathlib import Path
from evals import EvalRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run evaluation suite")
    parser.add_argument("--dataset", type=Path, default=Path("evals/datasets/golden.jsonl"))
    args = parser.parse_args()

    runner = EvalRunner(dataset_path=args.dataset)
    result = runner.run()

    print(f"Faithfulness: {result.faithfulness:.2f}")
    print(f"Relevancy:    {result.relevancy:.2f}")
    print(f"Result:       {'PASS' if result.passed else 'FAIL'}")


if __name__ == "__main__":
    main()
