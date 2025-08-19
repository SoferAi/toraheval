"""
Command-line interface for Sofer.AI TorahEval implementation.
"""

import typer
from rich.console import Console
from typing import Optional

from .implementation import run_evaluation, evaluate, implementation_name
from toraheval.contracts import TorahEvalInput

app = typer.Typer(rich_markup_mode="rich")
console = Console()


@app.command()
def run(
    csv_path: Optional[str] = typer.Option(None, help="Path to CSV file with Torah questions"),
    limit: Optional[int] = typer.Option(None, help="Limit number of questions to evaluate"),
):
    """Run TorahEval evaluation using Sofer.AI implementation."""
    console.print(f"Running TorahEval with {implementation_name()}...", style="bold blue")
    
    try:
        results = run_evaluation(csv_path=csv_path, limit=limit)
        console.print(f"Evaluation completed! Processed {len(results)} questions.", style="bold green")
        
    except Exception as e:
        console.print(f"Error running evaluation: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def test(
    question: str = typer.Option("What is the significance of Shabbat in Jewish practice?", help="Question to test"),
    context: str = typer.Option("", help="Context for the question"),
    question_type: str = typer.Option("general", help="Type of question"),
    language: str = typer.Option("english", help="Language for the question"),
):
    """Test the implementation with a single question."""
    console.print(f"Testing {implementation_name()} with question...", style="bold blue")
    
    try:
        # Create test input
        test_input = TorahEvalInput(
            question=question,
            context=context,
            question_type=question_type,
            language=language
        )
        
        # Get response
        result = evaluate(test_input)
        
        # Display results
        console.print(f"\nQuestion: {question}", style="cyan")
        console.print(f"Answer: {result.answer}", style="white")
        console.print(f"Confidence: {result.confidence}", style="yellow")
        
        if result.reasoning:
            console.print(f"Reasoning: {result.reasoning}", style="dim")
        
        if result.sources_used:
            console.print(f"Sources: {', '.join(result.sources_used)}", style="blue")
            
    except Exception as e:
        console.print(f"Error during test: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def info():
    """Show information about this implementation."""
    console.print(f"Implementation: {implementation_name()}", style="bold cyan")
    console.print("Framework: Braintrust AutoEvals", style="cyan") 
    console.print("Description: Mock implementation of Sofer.AI for TorahEval", style="white")
    console.print()
    console.print("Available commands:", style="bold")
    console.print("  run    - Run full evaluation on dataset")
    console.print("  test   - Test with a single question")
    console.print("  info   - Show this information")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
