"""
Target functions for LangSmith evaluation.

Each target function represents a different system or approach to evaluate.
All functions should take inputs dict and return outputs dict.
"""

from .anthropic_targets import anthropic_torah_qa, anthropic_torah_qa_haiku
from .simple_target import simple_template_response
from .ituria_target import ituria_like_target

# Registry of available target functions
TARGET_FUNCTIONS = {
    "anthropic_sonnet": anthropic_torah_qa,
    "anthropic_haiku": anthropic_torah_qa_haiku,
    "simple_template": simple_template_response,
    "ituria_agent": ituria_like_target,
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

__all__ = [
    'anthropic_torah_qa',
    'anthropic_torah_qa_haiku', 
    'simple_template_response',
    'ituria_like_target',
    'TARGET_FUNCTIONS',
    'get_target_function',
    'list_target_functions'
]
