# RFC: TorahEval - Simplified Evaluation Framework

## Abstract

TorahEval is a simplified, locally-running evaluation framework built on DeepEval that enables standardized testing of different implementations against Torah-related datasets. The system provides a clean CLI interface for running evaluations with pluggable datasets and implementations.

## Goals

1. **Simplicity**: Replace the current complex TorahBench architecture with a straightforward evaluation system
2. **Modularity**: Allow different implementations (Dicta, Sofer.AI, etc.) to be tested against the same datasets
3. **Local Execution**: Run entirely locally using DeepEval without cloud dependencies
4. **Standardization**: Provide consistent interfaces for datasets and implementations

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        TorahEval CLI                            │
│                 toraheval --dataset X --implementation Y        │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      │
              ┌───────▼────────┐
              │  Core Engine   │
              │   (DeepEval)   │
              └───────┬────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
    ┌────▼─────┐              ┌────▼──────┐
    │ Dataset  │              │Implementation│
    │ Loader   │              │   Driver    │
    └────┬─────┘              └────┬──────┘
         │                         │
    ┌────▼─────┐              ┌────▼──────┐
    │ Goldens  │              │ evaluate() │
    │ (CSV/JSON)│             │ function   │
    └──────────┘              └───────────┘
```

### Component Flow

```
User Command:
toraheval --dataset torah_basics --implementation dicta

Flow:
┌─────────┐    ┌──────────────┐    ┌─────────────────┐    ┌─────────────┐
│   CLI   │───▶│ Load Dataset │───▶│ Load Implementation│───▶│ Run DeepEval│
└─────────┘    └──────────────┘    └─────────────────┘    └─────────────┘
                       │                       │                    │
                ┌──────▼──────┐       ┌────────▼────────┐   ┌───────▼───────┐
                │ torah_basics│       │ dicta_evaluate()│   │ Results Report│
                │ goldens.csv │       │    function     │   │  (local only) │
                └─────────────┘       └─────────────────┘   └───────────────┘
```

## Directory Structure

```
toraheval/
├── src/
│   └── toraheval/
│       ├── cli.py                 # Main CLI entry point
│       ├── core/
│       │   ├── engine.py          # DeepEval orchestration
│       │   ├── dataset.py         # Dataset loading logic
│       │   └── implementation.py  # Implementation interface
│       ├── datasets/
│       │   ├── torah_basics/
│       │   │   ├── __init__.py
│       │   │   └── goldens.csv    # Question/expected_output pairs
│       │   └── torah_advanced/
│       │       ├── __init__.py
│       │       └── goldens.csv
│       └── implementations/
│           ├── dicta/
│           │   ├── __init__.py
│           │   └── driver.py      # Dicta-specific evaluate()
│           └── sofer_ai/
│               ├── __init__.py
│               └── driver.py      # Sofer.AI-specific evaluate()
└── pyproject.toml
```

## CLI Interface

### Primary Command

```bash
toraheval --dataset <dataset_name> --implementation <implementation_name> [options]
```

### Examples

```bash
# Run Dicta implementation against torah_basics dataset
toraheval --dataset torah_basics --implementation dicta

# Run with specific options
toraheval --dataset torah_basics --implementation dicta --limit 10 --output results.json

# List available datasets
toraheval --list-datasets

# List available implementations
toraheval --list-implementations

# Get info about a specific combination
toraheval --info --dataset torah_basics --implementation dicta
```

### Options

- `--dataset`: Dataset name (required)
- `--implementation`: Implementation name (required)
- `--limit`: Limit number of test cases
- `--output`: Output file for results
- `--list-datasets`: List all available datasets
- `--list-implementations`: List all available implementations
- `--info`: Show information about dataset/implementation combination
- `--verbose`: Enable verbose logging

## Dataset Specification

### Dataset Structure

Each dataset is a directory containing:

1. `__init__.py` - Dataset metadata and configuration
2. `goldens.csv` - The actual test data

### CSV Format

```csv
input,expected_output
"What is the first word of the Torah?","בראשית"
"How many books are in the Torah?","5"
"Who wrote the Torah according to tradition?","Moses"
```

### Dataset Metadata (`__init__.py`)

```python
from toraheval.core.dataset import Dataset

dataset = Dataset(
    name="torah_basics",
    description="Basic questions about the Torah",
    source="goldens.csv",
    size=100,
    tags=["basic", "torah", "fundamentals"]
)
```

## Implementation Specification

### Implementation Interface

Each implementation must provide an `evaluate()` function:

```python
from typing import Dict, Any

def evaluate(input_text: str) -> str:
    """
    Evaluate a single input and return the response.
    
    Args:
        input_text: The question/prompt to evaluate
        
    Returns:
        The implementation's response as a string
    """
    pass
```

### Implementation Structure (`driver.py`)

```python
from toraheval.core.implementation import Implementation

class DictaImplementation(Implementation):
    name = "dicta"
    description = "Dicta's Torah knowledge implementation"
    
    def evaluate(self, input_text: str) -> str:
        # Implementation-specific logic here
        # Could call APIs, use local models, etc.
        return response
        
    def setup(self) -> None:
        # Any initialization needed
        pass
        
    def teardown(self) -> None:
        # Any cleanup needed
        pass

# Export the implementation
implementation = DictaImplementation()
```

## Core Engine

### DeepEval Integration

The core engine orchestrates DeepEval to run evaluations:

```python
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset, Golden
from deepeval.metrics import ExactMatchMetric

def run_evaluation(dataset_name: str, implementation_name: str) -> Dict[str, Any]:
    # Load dataset
    dataset = load_dataset(dataset_name)
    
    # Load implementation
    implementation = load_implementation(implementation_name)
    
    # Create DeepEval goldens
    goldens = []
    for row in dataset.data:
        golden = Golden(
            input=row['input'],
            expected_output=row['expected_output']
        )
        goldens.append(golden)
    
    # Create evaluation dataset
    eval_dataset = EvaluationDataset(goldens=goldens)
    
    # Run evaluation
    results = []
    for golden in goldens:
        actual_output = implementation.evaluate(golden.input)
        
        test_case = LLMTestCase(
            input=golden.input,
            actual_output=actual_output,
            expected_output=golden.expected_output
        )
        
        # Use exact match for now, can add more sophisticated metrics later
        metric = ExactMatchMetric()
        result = assert_test(test_case, [metric])
        results.append(result)
    
    return aggregate_results(results)
```

## Migration from Current System

### Phase 1: Core Framework
1. Create simplified CLI interface
2. Implement dataset loading from CSV
3. Create basic implementation interface
4. Set up DeepEval integration

### Phase 2: Dataset Migration
1. Convert existing TorahBench datasets to CSV format
2. Migrate TorahEval datasets
3. Create unified dataset registry

### Phase 3: Implementation Migration
1. Simplify existing Dicta implementation
2. Simplify existing Sofer.AI implementation
3. Remove complex orchestration layers

### Deprecation Path
- Keep current `torahbench` CLI for compatibility
- Introduce new `toraheval` CLI alongside
- Gradually migrate users to simplified interface
- Remove old system in future version

## Benefits

1. **Reduced Complexity**: Single CLI command vs current multi-step process
2. **Better Developer Experience**: Clear interfaces for datasets and implementations
3. **Local-First**: No cloud dependencies, all evaluation runs locally
4. **Extensible**: Easy to add new datasets and implementations
5. **Standard Metrics**: Built on DeepEval's proven evaluation framework

## Future Enhancements

1. **Advanced Metrics**: Beyond exact match (semantic similarity, custom evaluators)
2. **Parallel Execution**: Run multiple implementations simultaneously
3. **Benchmarking**: Compare implementations side-by-side
4. **Custom Evaluators**: Allow domain-specific evaluation logic
5. **Result Visualization**: Generate charts and reports
6. **Configuration Files**: Support YAML/JSON configs for complex setups

## Implementation Timeline

- **Week 1**: Core framework and CLI
- **Week 2**: Dataset loading and basic implementation interface
- **Week 3**: DeepEval integration and first working evaluation
- **Week 4**: Migration of existing datasets and implementations
- **Week 5**: Testing, documentation, and polish

---

*This RFC replaces the current complex TorahBench architecture with a streamlined, locally-running evaluation system focused on simplicity and developer productivity.*
