"""TorahBench command-line interface."""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from .discovery import TorahBenchDiscovery

app = typer.Typer(rich_markup_mode="rich")
console = Console()


@app.command()
def list_evaluations():
    """List all available evaluation packages."""
    discovery = TorahBenchDiscovery()
    evaluations = discovery.discover_evaluations()
    
    if not evaluations:
        console.print("No evaluation packages found.", style="yellow")
        return
    
    table = Table(title="Available Evaluations")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Description", style="white")
    
    for eval_info in evaluations:
        table.add_row(eval_info.name, eval_info.version, eval_info.description)
    
    console.print(table)


@app.command()
def list_implementations(evaluation: Optional[str] = None):
    """List all available implementation packages."""
    discovery = TorahBenchDiscovery()
    implementations = discovery.discover_implementations(evaluation)
    
    if not implementations:
        filter_msg = f" for evaluation '{evaluation}'" if evaluation else ""
        console.print(f"No implementation packages found{filter_msg}.", style="yellow")
        return
    
    table = Table(title="Available Implementations")
    table.add_column("Service", style="cyan")
    table.add_column("Evaluation", style="blue")
    table.add_column("Version", style="green")
    table.add_column("Description", style="white")
    
    for impl_info in implementations:
        table.add_row(
            impl_info.name,
            impl_info.evaluation,
            impl_info.version,
            impl_info.description
        )
    
    console.print(table)


@app.command()
def info(
    evaluation: str = typer.Argument(..., help="Evaluation name (e.g., toraheval)"),
    implementation: str = typer.Argument(..., help="Implementation name (e.g., sofer-ai)"),
):
    """Show information about how to run a specific evaluation-implementation pair."""
    discovery = TorahBenchDiscovery()
    
    impl_info = discovery.find_implementation(evaluation, implementation)
    if not impl_info:
        console.print(
            f"Implementation '{implementation}' not found for evaluation '{evaluation}'",
            style="red"
        )
        return
    
    console.print(f"Evaluation: {evaluation}", style="cyan")
    console.print(f"Implementation: {implementation}", style="cyan")
    console.print(f"Description: {impl_info.description}", style="white")
    console.print()
    console.print("To run this evaluation:", style="bold")
    console.print(f"  cd {impl_info.path} && uv run {evaluation}-{implementation} run", style="green")
    console.print()
    console.print("To see implementation-specific options:", style="bold")
    console.print(f"  cd {impl_info.path} && uv run {evaluation}-{implementation} --help", style="green")
    console.print(f"  cd {impl_info.path} && uv run {evaluation}-{implementation} info", style="green")


@app.command()
def run(
    evaluation: str = typer.Argument(..., help="Evaluation to run (e.g., toraheval)"),
    implementation: str = typer.Argument(..., help="Implementation to use (e.g., sofer-ai)"),
    csv_path: Optional[str] = typer.Option(None, help="Path to CSV file with questions"),
    limit: Optional[int] = typer.Option(None, help="Limit number of questions to evaluate"),
    question: Optional[str] = typer.Option(None, help="Single question to test (overrides dataset)"),
    context: Optional[str] = typer.Option("", help="Context for single question"),
    question_type: Optional[str] = typer.Option("general", help="Type of single question"),
    language: Optional[str] = typer.Option("english", help="Language for single question"),
):
    """Run an evaluation with an implementation using AutoEvals framework."""
    discovery = TorahBenchDiscovery()
    
    # Check if implementation exists
    impl_info = discovery.find_implementation(evaluation, implementation)
    if not impl_info:
        console.print(
            f"Implementation '{implementation}' not found for evaluation '{evaluation}'",
            style="red"
        )
        return
    
    try:
        console.print(f"Running {evaluation} with {implementation} using AutoEvals...", style="bold blue")
        
        # Load the implementation module 
        impl_module = discovery.load_implementation_module(evaluation, implementation)
        
        if question:
            # Single question mode
            from toraheval.contracts import TorahEvalInput
            test_input = TorahEvalInput(
                question=question,
                context=context,
                question_type=question_type,
                language=language
            )
            
            console.print(f"Question: {test_input.question}")
            console.print(f"Implementation: {impl_module.implementation_name()}")
            console.print()
            
            # Run single evaluation
            result = impl_module.evaluate(test_input)
            
            console.print("Result:", style="bold green")
            console.print(f"Answer: {result.answer}")
            console.print(f"Confidence: {result.confidence}")
            if result.reasoning:
                console.print(f"Reasoning: {result.reasoning}")
            if result.sources_used:
                console.print(f"Sources: {', '.join(result.sources_used)}")
            console.print()
        else:
            # Full evaluation mode using AutoEvals
            if hasattr(impl_module, 'run_evaluation'):
                console.print("Running full evaluation with AutoEvals framework...")
                results = impl_module.run_evaluation(csv_path=csv_path, limit=limit)
                console.print(f"Evaluation completed! Processed {len(results)} questions.", style="bold green")
            else:
                console.print(
                    f"Implementation does not support AutoEvals framework. Please use --question for single tests.",
                    style="yellow"
                )
        
    except Exception as e:
        console.print(f"Error running evaluation: {e}", style="red")
        # Print more details for debugging
        import traceback
        console.print(f"Details: {traceback.format_exc()}", style="dim")


def main() -> None:
    """Main entry point for TorahBench CLI."""
    app()


if __name__ == "__main__":
    main()
