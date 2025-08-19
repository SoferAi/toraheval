"""
Sofer.AI implementation for TorahEval using AutoEvals framework.
"""

from typing import List
from toraheval.contracts import TorahEvalInput, TorahEvalOutput
from toraheval.runner import run_torah_eval

IMPLEMENTATION_NAME = "sofer-ai"


def implementation_name() -> str:
    return IMPLEMENTATION_NAME


def evaluate(input_data: TorahEvalInput) -> TorahEvalOutput:
    """
    Evaluate using Sofer.AI (mock implementation).
    
    In the future, this would integrate with the actual Sofer.AI API.
    For now, this demonstrates how the torahbench CLI can work with
    the inspect_ai-based evaluation framework.
    """
    try:
        # Mock response based on the question
        if "shabbat" in input_data.question.lower():
            answer = "Shabbat is a weekly day of rest and spiritual renewal in Jewish practice, observed from Friday evening to Saturday evening. It commemorates God's rest after the six days of creation and represents a fundamental pillar of Jewish life, providing time for prayer, family, and reflection while abstaining from work."
        else:
            answer = f"This is a mock response to the question: {input_data.question}. In a real implementation, this would be answered by the Sofer.AI model using Torah knowledge and sources."
        
        return TorahEvalOutput(
            answer=answer,
            confidence=0.8,  # Mock confidence
            reasoning="Generated using mock Sofer.AI implementation",
            sources_used=input_data.sources,
            language=input_data.language,
            metadata={"implementation": "sofer-ai-mock", "version": "0.1.0"}
        )
            
    except Exception as e:
        return TorahEvalOutput(
            answer=f"Error during evaluation: {str(e)}",
            confidence=0.0,
            reasoning=f"Exception occurred: {str(e)}",
            sources_used=input_data.sources,
            language=input_data.language,
            metadata={"error": str(e)}
        )


def evaluate_batch(inputs: List[TorahEvalInput]) -> List[TorahEvalOutput]:
    """
    Evaluate a batch of inputs.
    """
    return [evaluate(i) for i in inputs]


def run_evaluation(csv_path: str = None, limit: int = None):
    """
    Run TorahEval evaluation using AutoEvals framework.
    
    This is the main entry point that integrates with the AutoEvals framework
    to evaluate the Sofer.AI implementation.
    """
    results = run_torah_eval(
        implementation_func=evaluate,
        csv_path=csv_path,
        limit=limit
    )
    
    # Print results summary
    from toraheval.runner import TorahEvalRunner
    runner = TorahEvalRunner()
    runner.print_results_summary(results)
    
    return results
