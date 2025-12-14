"""ELM CLI - Command line interface for ELM (Expression Logical Model) operations."""

import json
from pathlib import Path
from typing import Annotated, Any, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from fhirkit.engine.elm import ELMEvaluator, ELMSerializer
from fhirkit.engine.elm.exceptions import ELMError, ELMExecutionError, ELMValidationError

app = typer.Typer(
    name="elm",
    help="ELM (Expression Logical Model) loader and evaluator",
    no_args_is_help=True,
)
console = Console()


def _format_result(value: Any) -> str:
    """Format an ELM result value for display."""
    if value is None:
        return "[dim]null[/dim]"
    if isinstance(value, bool):
        return f"[cyan]{value}[/cyan]"
    if isinstance(value, (int, float)):
        return f"[green]{value}[/green]"
    if isinstance(value, str):
        return f"[yellow]'{value}'[/yellow]"
    if isinstance(value, list):
        if len(value) == 0:
            return "[dim]{}[/dim]"
        items = ", ".join(_format_result(item) for item in value)
        return f"{{ {items} }}"
    if isinstance(value, dict):
        items = ", ".join(f"{k}: {_format_result(v)}" for k, v in value.items())
        return f"{{ {items} }}"
    return str(value)


@app.command()
def load(
    file: Annotated[Path, typer.Argument(help="ELM JSON file to load and validate")],
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show detailed information")] = False,
) -> None:
    """Load and validate an ELM JSON file.

    Examples:
        fhir elm load library.elm.json
        fhir elm load library.elm.json --verbose
    """
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    evaluator = ELMEvaluator()

    try:
        library = evaluator.load_file(file)
    except ELMValidationError as e:
        rprint(f"[red]Validation error:[/red] {e}")
        raise typer.Exit(1)
    except ELMError as e:
        rprint(f"[red]Error loading ELM:[/red] {e}")
        raise typer.Exit(1)

    rprint(f"[green]✓[/green] Successfully loaded: {file}")
    rprint()

    # Show library info
    info = evaluator.get_library_info(library)
    rprint(f"[bold blue]Library:[/bold blue] {info['id']}" + (f" v{info['version']}" if info.get("version") else ""))
    rprint()

    # Show stats
    stats = Table(show_header=False, box=None)
    stats.add_column("Key", style="dim")
    stats.add_column("Value")

    stats.add_row("Definitions", str(len(info.get("definitions", []))))
    stats.add_row("Functions", str(len(info.get("functions", []))))
    stats.add_row("Parameters", str(len(info.get("parameters", []))))
    stats.add_row("Value Sets", str(len(info.get("valueSets", []))))
    stats.add_row("Code Systems", str(len(info.get("codeSystems", []))))
    stats.add_row("Codes", str(len(info.get("codes", []))))

    console.print(stats)

    # Verbose output
    if verbose:
        rprint()

        if info.get("usings"):
            rprint("[bold]Using:[/bold]")
            for using in info["usings"]:
                version_str = f" v{using['version']}" if using.get("version") else ""
                rprint(f"  [magenta]{using['localIdentifier']}[/magenta]{version_str}")

        if info.get("includes"):
            rprint("\n[bold]Includes:[/bold]")
            for include in info["includes"]:
                version_str = f" v{include['version']}" if include.get("version") else ""
                rprint(f"  [magenta]{include['localIdentifier']}[/magenta] ({include['path']}){version_str}")

        if info.get("definitions"):
            rprint("\n[bold]Definitions:[/bold]")
            for name in sorted(info["definitions"]):
                rprint(f"  [cyan]{name}[/cyan]")

        if info.get("functions"):
            rprint("\n[bold]Functions:[/bold]")
            for name in sorted(info["functions"]):
                rprint(f"  [cyan]{name}[/cyan]")

        if info.get("parameters"):
            rprint("\n[bold]Parameters:[/bold]")
            for name in info["parameters"]:
                rprint(f"  [yellow]{name}[/yellow]")

        if info.get("valueSets"):
            rprint("\n[bold]Value Sets:[/bold]")
            for name in info["valueSets"]:
                rprint(f"  [yellow]{name}[/yellow]")


@app.command(name="eval")
def evaluate(
    file: Annotated[Path, typer.Argument(help="ELM JSON file")],
    definition: Annotated[str, typer.Argument(help="Definition name to evaluate")],
    data: Annotated[Optional[Path], typer.Option("--data", "-d", help="JSON data file for context")] = None,
    param: Annotated[Optional[list[str]], typer.Option("--param", "-p", help="Parameter in name=value format")] = None,
) -> None:
    """Evaluate a specific definition from an ELM library.

    Examples:
        fhir elm eval library.elm.json Sum
        fhir elm eval library.elm.json PatientAge --data patient.json
        fhir elm eval library.elm.json Calculate --param Multiplier=10
    """
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    evaluator = ELMEvaluator()

    try:
        evaluator.load_file(file)
    except ELMError as e:
        rprint(f"[red]Error loading ELM:[/red] {e}")
        raise typer.Exit(1)

    # Load data if provided
    resource = None
    if data:
        if not data.exists():
            rprint(f"[red]Error:[/red] Data file not found: {data}")
            raise typer.Exit(1)

        try:
            resource = json.loads(data.read_text())
        except json.JSONDecodeError as e:
            rprint(f"[red]Error parsing JSON:[/red] {e}")
            raise typer.Exit(1)

    # Parse parameters
    parameters: dict[str, Any] = {}
    if param:
        for p in param:
            if "=" not in p:
                rprint(f"[red]Error:[/red] Invalid parameter format: {p} (expected name=value)")
                raise typer.Exit(1)
            name, value = p.split("=", 1)
            # Try to parse as JSON, fall back to string
            try:
                parameters[name] = json.loads(value)
            except json.JSONDecodeError:
                parameters[name] = value

    try:
        result = evaluator.evaluate_definition(
            definition,
            resource=resource,
            parameters=parameters if parameters else None,
        )
        rprint(_format_result(result))

    except ELMExecutionError as e:
        rprint(f"[red]Execution error:[/red] {e}")
        raise typer.Exit(1)
    except ELMError as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def run(
    file: Annotated[Path, typer.Argument(help="ELM JSON file to run")],
    data: Annotated[Optional[Path], typer.Option("--data", "-d", help="JSON data file for context")] = None,
    param: Annotated[Optional[list[str]], typer.Option("--param", "-p", help="Parameter in name=value format")] = None,
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file for results (JSON)")] = None,
    include_private: Annotated[bool, typer.Option("--private", help="Include private definitions")] = False,
) -> None:
    """Run all definitions in an ELM library.

    Examples:
        fhir elm run library.elm.json
        fhir elm run library.elm.json --data patient.json
        fhir elm run library.elm.json --output results.json
    """
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    evaluator = ELMEvaluator()

    try:
        library = evaluator.load_file(file)
    except ELMError as e:
        rprint(f"[red]Error loading ELM:[/red] {e}")
        raise typer.Exit(1)

    # Load data if provided
    resource = None
    if data:
        if not data.exists():
            rprint(f"[red]Error:[/red] Data file not found: {data}")
            raise typer.Exit(1)

        try:
            resource = json.loads(data.read_text())
        except json.JSONDecodeError as e:
            rprint(f"[red]Error parsing JSON:[/red] {e}")
            raise typer.Exit(1)

    # Parse parameters
    parameters: dict[str, Any] = {}
    if param:
        for p in param:
            if "=" not in p:
                rprint(f"[red]Error:[/red] Invalid parameter format: {p} (expected name=value)")
                raise typer.Exit(1)
            name, value = p.split("=", 1)
            try:
                parameters[name] = json.loads(value)
            except json.JSONDecodeError:
                parameters[name] = value

    info = evaluator.get_library_info(library)
    rprint(f"[bold blue]Library:[/bold blue] {info['id']}" + (f" v{info['version']}" if info.get("version") else ""))
    rprint()

    try:
        results = evaluator.evaluate_all_definitions(
            resource=resource,
            parameters=parameters if parameters else None,
            include_private=include_private,
        )

        # Separate errors
        errors = results.pop("_errors", {})

        # Display results
        table = Table(title="Results", show_header=True, header_style="bold")
        table.add_column("Definition", style="cyan")
        table.add_column("Value")

        for name, value in sorted(results.items()):
            table.add_row(name, _format_result(value))

        console.print(table)

        # Show errors if any
        if errors:
            rprint()
            rprint("[red]Errors:[/red]")
            for name, error in errors.items():
                rprint(f"  [red]{name}:[/red] {error}")

        # Write output if requested
        if output:
            json_results = {}
            for name, value in results.items():
                if hasattr(value, "model_dump"):
                    json_results[name] = value.model_dump()
                else:
                    json_results[name] = value

            if errors:
                json_results["_errors"] = errors

            output.write_text(json.dumps(json_results, indent=2, default=str))
            rprint(f"\n[dim]Results written to {output}[/dim]")

    except ELMError as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def show(
    file: Annotated[Path, typer.Argument(help="ELM JSON file to display")],
) -> None:
    """Display an ELM JSON file with syntax highlighting.

    Examples:
        fhir elm show library.elm.json
    """
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    try:
        content = file.read_text()
        # Validate it's valid JSON
        json.loads(content)
        # Pretty print
        formatted = json.dumps(json.loads(content), indent=2)
        syntax = Syntax(formatted, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=str(file), border_style="blue"))
    except json.JSONDecodeError as e:
        rprint(f"[red]Error:[/red] Invalid JSON: {e}")
        raise typer.Exit(1)


@app.command()
def validate(
    files: Annotated[list[Path], typer.Argument(help="ELM JSON files to validate")],
) -> None:
    """Validate one or more ELM JSON files.

    Examples:
        fhir elm validate library.elm.json
        fhir elm validate *.elm.json
    """
    total = len(files)
    passed = 0
    failed = 0

    evaluator = ELMEvaluator()

    for file in files:
        if not file.exists():
            rprint(f"[yellow]⚠[/yellow] File not found: {file}")
            failed += 1
            continue

        is_valid, errors = evaluator.validate(file)

        if not is_valid:
            rprint(f"[red]✗[/red] {file}")
            for error in errors:
                rprint(f"    [red]•[/red] {error}")
            failed += 1
        else:
            rprint(f"[green]✓[/green] {file}")
            passed += 1

    rprint(f"\n[bold]Results:[/bold] {passed}/{total} passed, {failed}/{total} failed")

    if failed > 0:
        raise typer.Exit(1)


@app.command()
def convert(
    file: Annotated[Path, typer.Argument(help="CQL file to convert to ELM")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output ELM JSON file")] = None,
    indent: Annotated[int, typer.Option("--indent", "-i", help="JSON indentation level")] = 2,
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Only output JSON (no status messages)")] = False,
) -> None:
    """Convert a CQL file to ELM JSON.

    Examples:
        fhir elm convert library.cql
        fhir elm convert library.cql -o library.elm.json
        fhir elm convert library.cql --quiet > library.elm.json
    """
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    try:
        source = file.read_text()
        serializer = ELMSerializer()
        elm_json = serializer.serialize_library_json(source, indent=indent)

        if output:
            output.write_text(elm_json)
            if not quiet:
                rprint(f"[green]✓[/green] Converted {file} -> {output}")
        else:
            if quiet:
                # Just print the JSON
                print(elm_json)
            else:
                # Show with syntax highlighting
                syntax = Syntax(elm_json, "json", theme="monokai", line_numbers=True)
                console.print(Panel(syntax, title=f"ELM: {file}", border_style="blue"))

    except Exception as e:
        if quiet:
            print(f"Error: {e}", file=__import__("sys").stderr)
        else:
            rprint(f"[red]Error converting to ELM:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
