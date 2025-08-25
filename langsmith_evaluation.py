import json
import sys
from dotenv import load_dotenv
from langsmith import Client
from targets import get_target_function, list_target_functions
from evaluators import get_evaluators, list_evaluators

# Load environment variables from .env file
load_dotenv()

# Initialize LangSmith client
client = Client()

# Load existing dataset
with open('Q1-dataset.json', 'r', encoding='utf-8') as f:
    dataset_examples = json.load(f)

# Create or get dataset in LangSmith
try:
    dataset = client.create_dataset(
        dataset_name="Torah Evaluation Dataset", 
        description="A dataset for evaluating Torah-related Q&A responses."
    )
    # Add examples to the dataset
    client.create_examples(dataset_id=dataset.id, examples=dataset_examples)
    print(f"Created new dataset with ID: {dataset.id}")
except Exception as e:
    print(f"Dataset might already exist: {e}")
    # If dataset exists, try to find it
    datasets = client.list_datasets()
    dataset = next((d for d in datasets if d.name == "Torah Evaluation Dataset"), None)
    if not dataset:
        raise Exception("Could not create or find dataset")

# Evaluators are now imported from evaluators.py

# Run the evaluation
if __name__ == "__main__":
    # Parse command line arguments
    target_name = "anthropic_sonnet"
    evaluator_names = None
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            print("Available target functions:")
            for name in list_target_functions():
                print(f"  - {name}")
            print("\nAvailable evaluators:")
            for name in list_evaluators():
                print(f"  - {name}")
            sys.exit(0)
        else:
            target_name = sys.argv[1]
            # Optional: specify evaluators as second argument (comma-separated)
            if len(sys.argv) > 2:
                evaluator_names = sys.argv[2].split(',')
    
    try:
        target_function = get_target_function(target_name)
        print(f"Using target function: {target_name}")
    except ValueError as e:
        print(f"Error: {e}")
        print("Use 'python langsmith_evaluation.py list' to see available functions")
        sys.exit(1)
    
    try:
        evaluators = get_evaluators(evaluator_names)
        if evaluator_names:
            print(f"Using evaluators: {', '.join(evaluator_names)}")
        else:
            print(f"Using all evaluators: {', '.join(list_evaluators())}")
    except ValueError as e:
        print(f"Error: {e}")
        print("Use 'python langsmith_evaluation.py list' to see available evaluators")
        sys.exit(1)
    
    print("Starting evaluation...")
    
    experiment_results = client.evaluate(
        target_function,
        data="Torah Evaluation Dataset",
        evaluators=evaluators,
        experiment_prefix=f"torah-eval-{target_name}",
    )
    
    print(f"Evaluation complete! Results: {experiment_results}")
    print("Check the LangSmith UI for detailed results.")
