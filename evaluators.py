"""Custom evaluators for Torah scholarship evaluation."""

from openevals.llm import create_llm_as_judge
from openevals.prompts import RAG_HELPFULNESS_PROMPT

# Specific source-finding correctness prompt
SOURCE_CORRECTNESS_PROMPT = """
You are evaluating whether the response contains the exact source that is expected.

QUESTION:
{inputs}

RESPONSE:
{outputs}

EXPECTED SOURCE (from reference answer):
{reference_outputs}

Please evaluate ONLY whether the response contains the exact source that appears in the expected answer.

Look for the specific book name, section, and reference details that match the expected source.
Look also on the content of the response to see if it comes from the expected source.

Provide a score of true/false:
- true: The response contains the exact source from the expected answer, even if additional context is present, some text is missing, or the format is slightly different
- false: The response does not contain the exact source, or contains a different/incorrect source

LOOK VERY CAREFULLY at the reference source and the actual response, some times the citing is little different due to a different splitting or different editions, and you will have to make the decision if it is the same source.

SCORE: [true/false]
COMMENT: [Brief explanation of whether the exact source was found or not]
"""  # noqa: E501


def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    """Return correctness evaluator result.

    Evaluator checks if the target function's output contains the exact
    source reference from the expected answer - a simple yes/no evaluation.
    """
    evaluator = create_llm_as_judge(
        prompt=SOURCE_CORRECTNESS_PROMPT,
        model="anthropic:claude-sonnet-4-20250514",
        feedback_key="correctness",
    )
    eval_result = evaluator(
        inputs=inputs, outputs=outputs, reference_outputs=reference_outputs
    )
    return eval_result


def helpfulness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    """Return helpfulness evaluator result.

    Evaluator that checks how well the output addresses the input question.
    Does not require reference outputs.
    """
    evaluator = create_llm_as_judge(
        prompt=RAG_HELPFULNESS_PROMPT,
        model="anthropic:claude-sonnet-4-20250514",
        feedback_key="helpfulness",
    )
    eval_result = evaluator(
        inputs=inputs,
        outputs=outputs,
    )
    return eval_result


# Custom Torah-specific evaluator
TORAH_CITATION_PROMPT = """
You are evaluating whether a Torah scholarship answer properly cites sources and follows
scholarly conventions.

INPUT:
{inputs}

OUTPUT:
{outputs}

Please evaluate the output on the following criteria:
1. Does it cite specific sources when making claims?
2. Does it use proper Hebrew/Aramaic terminology?
3. Does it demonstrate knowledge of Torah scholarship conventions?
4. Are the citations accurate and properly formatted?

Provide a score of true/false and a brief explanation.

SCORE: [true/false]
COMMENT: [Your explanation here]
"""


def torah_citation_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    """Return citation evaluator result.

    Custom evaluator that checks if Torah responses include proper citations
    and follow scholarly conventions.
    """
    evaluator = create_llm_as_judge(
        prompt=TORAH_CITATION_PROMPT,
        model="anthropic:claude-sonnet-4-20250514",
        feedback_key="torah_citations",
    )
    eval_result = evaluator(
        inputs=inputs,
        outputs=outputs,
    )
    return eval_result


# Custom Hebrew/Jewish text handling evaluator
HEBREW_HANDLING_PROMPT = """
You are evaluating whether a response properly handles Hebrew text and
Jewish religious concepts.

INPUT:
{inputs}

OUTPUT:
{outputs}

Please evaluate the output on the following criteria:
1. Does it correctly interpret Hebrew/Aramaic text when present?
2. Does it show understanding of Jewish religious concepts?
3. Does it handle transliteration appropriately?
4. Does it respect the religious context of the material?

Provide a score of true/false and a brief explanation.

SCORE: [true/false]
COMMENT: [Your explanation here]
"""


def hebrew_handling_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    """Return hebrew evaluator result.

    Custom evaluator that checks if responses properly handle Hebrew text
    and Jewish religious concepts.
    """
    evaluator = create_llm_as_judge(
        prompt=HEBREW_HANDLING_PROMPT,
        model="anthropic:claude-sonnet-4-20250514",
        feedback_key="hebrew_handling",
    )
    eval_result = evaluator(
        inputs=inputs,
        outputs=outputs,
    )
    return eval_result


# Custom depth of analysis evaluator
DEPTH_ANALYSIS_PROMPT = """
You are evaluating the depth and sophistication of Torah scholarship analysis.

INPUT:
{inputs}

OUTPUT:
{outputs}

Please evaluate the output on the following criteria:
1. Does it provide deep, nuanced analysis rather than surface-level answers?
2. Does it consider multiple perspectives or interpretations?
3. Does it demonstrate knowledge of commentaries and secondary sources?
4. Does it show awareness of the broader context and implications?

Provide a score of true/false and a brief explanation.

SCORE: [true/false]
COMMENT: [Your explanation here]
"""


def depth_analysis_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    """Return depth analysis evaluator result.

    Custom evaluator that checks the depth and sophistication of Torah analysis.
    """
    evaluator = create_llm_as_judge(
        prompt=DEPTH_ANALYSIS_PROMPT,
        model="anthropic:claude-sonnet-4-20250514",
        feedback_key="depth_analysis",
    )
    eval_result = evaluator(
        inputs=inputs,
        outputs=outputs,
    )
    return eval_result


# Registry of available evaluators
EVALUATOR_FUNCTIONS = {
    "correctness": correctness_evaluator,
    "helpfulness": helpfulness_evaluator,
    "torah_citations": torah_citation_evaluator,
    "hebrew_handling": hebrew_handling_evaluator,
    "depth_analysis": depth_analysis_evaluator,
}


def get_evaluators(names=None):
    """Get evaluator functions by names.

    Args:
        names: List of evaluator names, or None for all evaluators

    Returns:
        List of evaluator functions

    """
    if names is None:
        return list(EVALUATOR_FUNCTIONS.values())

    evaluators = []
    for name in names:
        if name not in EVALUATOR_FUNCTIONS:
            available = ", ".join(EVALUATOR_FUNCTIONS.keys())
            raise ValueError(f"Evaluator '{name}' not found. Available: {available}")
        evaluators.append(EVALUATOR_FUNCTIONS[name])

    return evaluators


def list_evaluators():
    """List all available evaluator names."""
    return list(EVALUATOR_FUNCTIONS.keys())
