# Torah Evaluation with LangSmith

This project provides a LangSmith evaluation setup for Torah Q&A systems using various AI models.

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Create `.env` file with your API keys:
```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Usage

### List available target functions and evaluators:
```bash
uv run langsmith_evaluation.py list
```

### Run evaluation with specific target function:
```bash
uv run langsmith_evaluation.py anthropic_sonnet
uv run langsmith_evaluation.py anthropic_haiku
uv run langsmith_evaluation.py simple_template
uv run langsmith_evaluation.py ituria_agent
```

### Run evaluation with specific evaluators:
```bash
# Use only correctness and helpfulness evaluators
uv run langsmith_evaluation.py anthropic_sonnet correctness,helpfulness

# Use only Torah-specific evaluators
uv run langsmith_evaluation.py anthropic_sonnet torah_citations,hebrew_handling
```

### Run evaluation with default (anthropic_sonnet, all evaluators):
```bash
uv run langsmith_evaluation.py
```

## Target Functions

The evaluation system supports multiple target functions defined in the `targets/` directory:

- **anthropic_sonnet**: Uses Claude 3.5 Sonnet (high quality)
- **anthropic_haiku**: Uses Claude 3 Haiku (faster, cheaper)  
- **simple_template**: Template-based baseline responses
- **ituria_agent**: Comprehensive search using MCP Jewish Library server

## Evaluators

The system includes several evaluators to comprehensively assess Torah Q&A responses:

### Standard Evaluators:
- **correctness**: Compares output against reference answer (requires ground truth)
- **helpfulness**: Measures how well the response addresses the input question

### Custom Torah-Specific Evaluators:
- **torah_citations**: Checks if responses include proper source citations and follow scholarly conventions
- **hebrew_handling**: Evaluates correct interpretation of Hebrew/Aramaic text and Jewish concepts
- **depth_analysis**: Assesses the depth and sophistication of Torah analysis

## Adding New Target Functions

To add a new target function:

1. Create a new Python file in the `targets/` directory (e.g., `my_target.py`)
2. Implement a function that takes `inputs: dict` and returns `outputs: dict`
3. Import it in `targets/__init__.py`
4. Add it to the `TARGET_FUNCTIONS` registry

Example in `targets/my_target.py`:
```python
def my_new_target(inputs: dict) -> dict:
    # Your implementation here
    return {"answer": "Some response"}
```

Then in `targets/__init__.py`:
```python
from .my_target import my_new_target

TARGET_FUNCTIONS = {
    # ... existing targets
    "my_target": my_new_target,
}
```

## Adding New Evaluators

To add a custom evaluator:

1. Open `evaluators.py` 
2. Create a new evaluator function
3. Add it to the `EVALUATOR_FUNCTIONS` registry

Example:
```python
def my_custom_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    # Your evaluation logic here
    return {"key": "my_metric", "score": True, "comment": "Good response"}

# Add to registry  
EVALUATOR_FUNCTIONS["my_metric"] = my_custom_evaluator
```

## Dataset

The evaluation uses `Q1-dataset.json` which contains Hebrew Torah scholarship questions and reference answers.

## Results

After running an evaluation, you'll get a link to view results in the LangSmith UI where you can compare different target functions' performance.
