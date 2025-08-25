"""
Legacy target functions file - now imports from targets module.
"""

# Import all targets from the new modular structure
from targets import (
    anthropic_torah_qa,
    anthropic_torah_qa_haiku, 
    simple_template_response,
    ituria_like_target,
    TARGET_FUNCTIONS,
    get_target_function,
    list_target_functions
)
