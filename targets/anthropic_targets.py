"""Anthropic-based Torah Q&A targets."""

from anthropic import Anthropic
from dotenv import load_dotenv
from langsmith import wrappers

SYSTEM_PROMPT = """
You are a Torah scholar assistant.
Answer questions about Torah texts and sources accurately, providing specific citations
when possible.
If asked about Divrei Yoel or other Hasidic texts, try to provide relevant teachings
and sources.
"""
# Load environment variables
load_dotenv()

# Initialize clients
anthropic_client = wrappers.wrap_anthropic(Anthropic())


def anthropic_torah_qa(inputs: dict) -> dict:
    """Torah Q&A system using Anthropic Claude.

    Args:
        inputs: Dict with 'question' key

    Returns:
        Dict with 'answer' key

    """
    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": inputs["question"]}],
    )

    # Handle different content types
    content = response.content[0]
    if hasattr(content, "text"):
        return {"answer": content.text.strip()}
    else:
        return {"answer": str(content).strip()}


def anthropic_torah_qa_haiku(inputs: dict) -> dict:
    """Torah Q&A system using Anthropic Claude Haiku (faster, cheaper model).

    Args:
        inputs: Dict with 'question' key

    Returns:
        Dict with 'answer' key

    """
    response = anthropic_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": inputs["question"]}],
    )

    # Handle different content types
    content = response.content[0]
    if hasattr(content, "text"):
        return {"answer": content.text.strip()}
    else:
        return {"answer": str(content).strip()}
