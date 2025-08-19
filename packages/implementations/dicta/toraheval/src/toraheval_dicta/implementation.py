"""
Very thin stub for the (future) Dicta integration.
Implements a few helper functions that ToraBench can import.
"""

from typing import List
from toraheval.contracts import TorahEvalInput, TorahEvalOutput

IMPLEMENTATION_NAME = "dicta"


def implementation_name() -> str:
    return IMPLEMENTATION_NAME


def evaluate(input_data: TorahEvalInput) -> TorahEvalOutput:
    """
    Return a deterministic dummy answer. Replace this later with
    a real API call once Dicta is available.
    """
    return TorahEvalOutput(
        answer=f'[DICTA stub] Answer to: "{input_data.question}"',
        confidence=1.0,
        reasoning="Stubbed – API not wired yet.",
        sources_used=input_data.sources,
        language=input_data.language,
        metadata={"note": "stub-implementation", "specializes_in": "hebrew_aramaic"}
    )


def evaluate_batch(inputs: List[TorahEvalInput]) -> List[TorahEvalOutput]:
    return [evaluate(i) for i in inputs]
