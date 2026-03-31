"""
Faithfulness metric: does the answer stick to what the retrieved context says?
A faithful answer contains no claims that aren't supported by the context.
Uses LLM-as-judge via RAGAS.
"""


class FaithfulnessMetric:
    def score(self, answer: str, context: list[str]) -> float:
        """
        Returns 0.0–1.0. 1.0 = every claim in the answer is supported by context.
        Threshold: settings.eval_threshold_faithfulness (default 0.85).
        """
        raise NotImplementedError
