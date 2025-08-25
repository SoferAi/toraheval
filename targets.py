"""
Target functions for LangSmith evaluation.

Each target function represents a different system or approach to evaluate.
All functions should take inputs dict and return outputs dict.
"""
import os
from dotenv import load_dotenv
from langsmith import wrappers
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Initialize clients (can be reused across functions)
anthropic_client = wrappers.wrap_anthropic(Anthropic())


def anthropic_torah_qa(inputs: dict) -> dict:
    """
    Torah Q&A system using Anthropic Claude.
    
    Args:
        inputs: Dict with 'question' key
        
    Returns:
        Dict with 'answer' key
    """
    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        system="You are a Torah scholar assistant. Answer questions about Torah texts and sources accurately, providing specific citations when possible. If asked about Divrei Yoel or other Hasidic texts, try to provide relevant teachings and sources.",
        messages=[
            {
                "role": "user", 
                "content": inputs["question"]
            }
        ],
    )
    
    # Handle different content types
    content = response.content[0]
    if hasattr(content, 'text'):
        return {"answer": content.text.strip()}
    else:
        return {"answer": str(content).strip()}


def anthropic_torah_qa_haiku(inputs: dict) -> dict:
    """
    Torah Q&A system using Anthropic Claude Haiku (faster, cheaper model).
    
    Args:
        inputs: Dict with 'question' key
        
    Returns:
        Dict with 'answer' key
    """
    response = anthropic_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        system="You are a Torah scholar assistant. Answer questions about Torah texts and sources accurately, providing specific citations when possible. If asked about Divrei Yoel or other Hasidic texts, try to provide relevant teachings and sources.",
        messages=[
            {
                "role": "user", 
                "content": inputs["question"]
            }
        ],
    )
    
    # Handle different content types
    content = response.content[0]
    if hasattr(content, 'text'):
        return {"answer": content.text.strip()}
    else:
        return {"answer": str(content).strip()}


def simple_template_response(inputs: dict) -> dict:
    """
    Simple template-based response for baseline comparison.
    
    Args:
        inputs: Dict with 'question' key
        
    Returns:
        Dict with 'answer' key
    """
    question = inputs["question"].lower()
    
    if "divrei yoel" in question or "divrey yoel" in question:
        return {"answer": "This question relates to Divrei Yoel, a collection of Hasidic teachings. I would need to consult the specific text to provide an accurate answer."}
    elif "moses" in question or "moshe" in question:
        return {"answer": "This question concerns Moses (Moshe Rabbenu), the greatest of the prophets and leader of the Jewish people."}
    elif "prayer" in question or "tefillah" in question:
        return {"answer": "This relates to Jewish prayer and spiritual practice. Prayer is a fundamental aspect of Jewish worship."}
    else:
        return {"answer": "This appears to be a Torah-related question that would require careful study of the relevant sources to answer properly."}


# Registry of available target functions
TARGET_FUNCTIONS = {
    "anthropic_sonnet": anthropic_torah_qa,
    "anthropic_haiku": anthropic_torah_qa_haiku,
    "simple_template": simple_template_response,
}


def get_target_function(name: str):
    """Get a target function by name."""
    if name not in TARGET_FUNCTIONS:
        available = ", ".join(TARGET_FUNCTIONS.keys())
        raise ValueError(f"Target function '{name}' not found. Available: {available}")
    return TARGET_FUNCTIONS[name]


def list_target_functions():
    """List all available target functions."""
    return list(TARGET_FUNCTIONS.keys())
