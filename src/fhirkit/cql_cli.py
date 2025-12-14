"""CQL CLI - Command line interface for CQL parsing, analysis, and evaluation."""

import json
import sys
from pathlib import Path
from typing import Annotated, Any, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

# Add generated directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "generated" / "cql"))

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener
from cqlLexer import cqlLexer
from cqlParser import cqlParser

from fhirkit.engine.cql import CQLEvaluator
from fhirkit.engine.exceptions import CQLError

app = typer.Typer(
    name="cql",
    help="CQL (Clinical Quality Language) parser and analyzer",
    no_args_is_help=True,
)
console = Console()


class CQLErrorListener(ErrorListener):
    """Custom error listener for CQL parsing errors."""

    def __init__(self) -> None:
        self.errors: list[str] = []

    def syntaxError(
        self,
        recognizer: object,
        offendingSymbol: object,
        line: int,
        column: int,
        msg: str,
        e: object,
    ) -> None:
        self.errors.append(f"Line {line}:{column} - {msg}")


def parse_cql(text: str) -> tuple[cqlParser.LibraryContext, list[str]]:
    """Parse CQL text and return parse tree with any errors."""
    input_stream = InputStream(text)
    lexer = cqlLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = cqlParser(token_stream)

    error_listener = CQLErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    tree = parser.library()
    return tree, error_listener.errors


def build_tree(node: object, tree: Tree, parser: cqlParser, depth: int = 0, max_depth: int = 50) -> None:
    """Recursively build a Rich tree from ANTLR parse tree."""
    if depth > max_depth:
        tree.add("[dim]...[/dim]")
        return

    if hasattr(node, "children") and node.children:
        for child in node.children:
            if hasattr(child, "getRuleIndex"):
                rule_name = parser.ruleNames[child.getRuleIndex()]
                branch = tree.add(f"[cyan]{rule_name}[/cyan]")
                build_tree(child, branch, parser, depth + 1, max_depth)
            elif hasattr(child, "getText"):
                text = child.getText()
                if text.strip():
                    tree.add(f"[green]'{text}'[/green]")


@app.command()
def parse(
    file: Annotated[Path, typer.Argument(help="CQL file to parse")],
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Only show errors")] = False,
) -> None:
    """Parse a CQL file and report any syntax errors."""
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    text = file.read_text()
    tree, errors = parse_cql(text)

    if errors:
        rprint(f"[red]Parse errors in {file}:[/red]")
        for error in errors:
            rprint(f"  [red]•[/red] {error}")
        raise typer.Exit(1)

    if not quiet:
        rprint(f"[green]✓[/green] Successfully parsed: {file}")


@app.command()
def ast(
    file: Annotated[Path, typer.Argument(help="CQL file to parse")],
    max_depth: Annotated[int, typer.Option("--depth", "-d", help="Maximum tree depth")] = 50,
) -> None:
    """Display the Abstract Syntax Tree (AST) for a CQL file."""
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    text = file.read_text()
    tree_node, errors = parse_cql(text)

    if errors:
        rprint("[red]Parse errors:[/red]")
        for error in errors:
            rprint(f"  [red]•[/red] {error}")
        raise typer.Exit(1)

    # Build and display tree
    input_stream = InputStream(text)
    lexer = cqlLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = cqlParser(token_stream)

    rich_tree = Tree("[bold blue]library[/bold blue]")
    build_tree(tree_node, rich_tree, parser, max_depth=max_depth)
    rprint(rich_tree)


@app.command()
def tokens(
    file: Annotated[Path, typer.Argument(help="CQL file to tokenize")],
    limit: Annotated[Optional[int], typer.Option("--limit", "-l", help="Limit number of tokens")] = None,
) -> None:
    """Display the token stream for a CQL file."""
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    text = file.read_text()
    input_stream = InputStream(text)
    lexer = cqlLexer(input_stream)

    rprint(f"[bold]Tokens for {file}:[/bold]\n")

    count = 0
    token = lexer.nextToken()
    while token.type != -1:  # EOF
        if limit and count >= limit:
            rprint(f"\n[dim]... (limited to {limit} tokens)[/dim]")
            break

        token_name = lexer.symbolicNames[token.type] if token.type < len(lexer.symbolicNames) else "UNKNOWN"
        rprint(
            f"[cyan]{token_name:20}[/cyan] [green]'{token.text}'[/green] [dim](line {token.line}:{token.column})[/dim]"
        )

        count += 1
        token = lexer.nextToken()

    rprint(f"\n[dim]Total: {count} tokens[/dim]")


@app.command()
def show(
    file: Annotated[Path, typer.Argument(help="CQL file to display")],
) -> None:
    """Display a CQL file with syntax highlighting."""
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    text = file.read_text()
    syntax = Syntax(text, "sql", theme="monokai", line_numbers=True)  # SQL is closest to CQL
    console.print(Panel(syntax, title=str(file), border_style="blue"))


@app.command()
def validate(
    files: Annotated[list[Path], typer.Argument(help="CQL files to validate")],
) -> None:
    """Validate one or more CQL files."""
    total = len(files)
    passed = 0
    failed = 0

    for file in files:
        if not file.exists():
            rprint(f"[yellow]⚠[/yellow] File not found: {file}")
            failed += 1
            continue

        text = file.read_text()
        _, errors = parse_cql(text)

        if errors:
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
def definitions(
    file: Annotated[Path, typer.Argument(help="CQL file to analyze")],
) -> None:
    """List all definitions in a CQL library."""
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    text = file.read_text()
    tree, errors = parse_cql(text)

    if errors:
        rprint("[red]Parse errors:[/red]")
        for error in errors:
            rprint(f"  [red]•[/red] {error}")
        raise typer.Exit(1)

    # Extract definitions
    rprint(f"[bold]Definitions in {file}:[/bold]\n")

    def find_definitions(node: object, indent: int = 0) -> None:
        if hasattr(node, "getRuleIndex"):
            # Get rule name
            input_stream = InputStream(text)
            lexer = cqlLexer(input_stream)
            token_stream = CommonTokenStream(lexer)
            parser = cqlParser(token_stream)
            rule_name = parser.ruleNames[node.getRuleIndex()]

            if rule_name == "libraryDefinition":
                lib_text = node.getText() if hasattr(node, "getText") else ""
                rprint(f"[blue]Library:[/blue] {lib_text[:50]}...")

            elif rule_name == "usingDefinition":
                using_text = node.getText() if hasattr(node, "getText") else ""
                rprint(f"[magenta]Using:[/magenta] {using_text}")

            elif rule_name == "valuesetDefinition":
                vs_text = node.getText() if hasattr(node, "getText") else ""
                rprint(f"[yellow]Valueset:[/yellow] {vs_text[:60]}...")

            elif rule_name == "codesystemDefinition":
                cs_text = node.getText() if hasattr(node, "getText") else ""
                rprint(f"[yellow]Codesystem:[/yellow] {cs_text[:60]}...")

            elif rule_name == "expressionDefinition":
                expr_text = node.getText() if hasattr(node, "getText") else ""
                rprint(f"[green]Define:[/green] {expr_text[:60]}...")

            elif rule_name == "functionDefinition":
                func_text = node.getText() if hasattr(node, "getText") else ""
                rprint(f"[cyan]Function:[/cyan] {func_text[:60]}...")

            elif rule_name == "contextDefinition":
                ctx_text = node.getText() if hasattr(node, "getText") else ""
                rprint(f"[red]Context:[/red] {ctx_text}")

        if hasattr(node, "children") and node.children:
            for child in node.children:
                find_definitions(child, indent + 1)

    find_definitions(tree)


def _format_result(value: Any) -> str:
    """Format a CQL result value for display."""
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


@app.command(name="eval")
def evaluate(
    expression: Annotated[str, typer.Argument(help="CQL expression to evaluate")],
    library: Annotated[Optional[Path], typer.Option("--library", "-l", help="CQL library file for context")] = None,
    data: Annotated[Optional[Path], typer.Option("--data", "-d", help="JSON data file for context")] = None,
) -> None:
    """Evaluate a CQL expression.

    Examples:
        cql eval "1 + 2 * 3"
        cql eval "Sum" --library example.cql
        cql eval "Patient.name" --data patient.json
    """
    evaluator = CQLEvaluator()

    # Load library if provided
    if library:
        if not library.exists():
            rprint(f"[red]Error:[/red] Library file not found: {library}")
            raise typer.Exit(1)

        try:
            source = library.read_text()
            evaluator.compile(source)
        except CQLError as e:
            rprint(f"[red]Error compiling library:[/red] {e}")
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

    try:
        # Try as definition first if library is loaded
        if evaluator.current_library and expression in evaluator.current_library.definitions:
            result = evaluator.evaluate_definition(expression, resource=resource)
        else:
            result = evaluator.evaluate_expression(expression, resource=resource)

        rprint(_format_result(result))

    except CQLError as e:
        rprint(f"[red]Evaluation error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def run(
    file: Annotated[Path, typer.Argument(help="CQL library file to run")],
    definition: Annotated[
        Optional[str], typer.Option("--definition", "-e", help="Specific definition to evaluate")
    ] = None,
    data: Annotated[Optional[Path], typer.Option("--data", "-d", help="JSON data file for context")] = None,
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file for results (JSON)")] = None,
) -> None:
    """Run a CQL library and evaluate definitions.

    Examples:
        cql run library.cql
        cql run library.cql --definition Sum
        cql run library.cql --data patient.json --output results.json
    """
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    evaluator = CQLEvaluator()

    try:
        source = file.read_text()
        lib = evaluator.compile(source)
    except CQLError as e:
        rprint(f"[red]Error compiling library:[/red] {e}")
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

    rprint(f"[bold blue]Library:[/bold blue] {lib.name}" + (f" v{lib.version}" if lib.version else ""))
    rprint()

    try:
        if definition:
            # Evaluate specific definition
            if definition not in lib.definitions:
                rprint(f"[red]Error:[/red] Definition not found: {definition}")
                raise typer.Exit(1)

            result = evaluator.evaluate_definition(definition, resource=resource)
            rprint(f"[bold]{definition}:[/bold] {_format_result(result)}")
            results = {definition: result}
        else:
            # Evaluate all definitions
            results = evaluator.evaluate_all_definitions(resource=resource)

            table = Table(title="Results", show_header=True, header_style="bold")
            table.add_column("Definition", style="cyan")
            table.add_column("Value")

            for name, value in results.items():
                if isinstance(value, Exception):
                    table.add_row(name, f"[red]Error: {value}[/red]")
                else:
                    table.add_row(name, _format_result(value))

            console.print(table)

        # Write output if requested
        if output:
            # Convert results to JSON-serializable format
            json_results = {}
            for name, value in results.items():
                if isinstance(value, Exception):
                    json_results[name] = {"error": str(value)}
                elif hasattr(value, "model_dump"):
                    json_results[name] = value.model_dump()
                else:
                    json_results[name] = value

            output.write_text(json.dumps(json_results, indent=2, default=str))
            rprint(f"\n[dim]Results written to {output}[/dim]")

    except CQLError as e:
        rprint(f"[red]Evaluation error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def check(
    file: Annotated[Path, typer.Argument(help="CQL library file to check")],
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show detailed information")] = False,
) -> None:
    """Check a CQL library for errors and show information.

    Validates syntax, compiles the library, and reports any issues found.

    Examples:
        cql check library.cql
        cql check library.cql --verbose
    """
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    # Step 1: Parse
    text = file.read_text()
    _, parse_errors = parse_cql(text)

    if parse_errors:
        rprint(f"[red]✗[/red] Syntax errors in {file}:")
        for error in parse_errors:
            rprint(f"  [red]•[/red] {error}")
        raise typer.Exit(1)

    rprint("[green]✓[/green] Syntax valid")

    # Step 2: Compile
    evaluator = CQLEvaluator()
    try:
        lib = evaluator.compile(text)
    except CQLError as e:
        rprint(f"[red]✗[/red] Compilation error: {e}")
        raise typer.Exit(1)

    rprint("[green]✓[/green] Compilation successful")

    # Step 3: Show library info
    rprint()
    rprint(f"[bold blue]Library:[/bold blue] {lib.name}" + (f" v{lib.version}" if lib.version else ""))

    # Show stats
    stats = Table(show_header=False, box=None)
    stats.add_column("Key", style="dim")
    stats.add_column("Value")

    stats.add_row("Definitions", str(len(lib.definitions)))
    stats.add_row("Functions", str(len(lib.functions)))
    stats.add_row("Value Sets", str(len(lib.valuesets)))
    stats.add_row("Code Systems", str(len(lib.codesystems)))
    stats.add_row("Codes", str(len(lib.codes)))
    stats.add_row("Parameters", str(len(lib.parameters)))

    console.print(stats)

    # Step 4: Verbose output
    if verbose:
        rprint()

        if lib.definitions:
            rprint("[bold]Definitions:[/bold]")
            for name in sorted(lib.definitions.keys()):
                rprint(f"  [cyan]{name}[/cyan]")

        if lib.functions:
            rprint("\n[bold]Functions:[/bold]")
            for name, func_list in sorted(lib.functions.items()):
                for func in func_list:
                    params = ", ".join(f"{p[0]}: {p[1]}" for p in func.parameters)
                    ret = f" -> {func.return_type}" if func.return_type else ""
                    rprint(f"  [cyan]{name}[/cyan]({params}){ret}")

        if lib.valuesets:
            rprint("\n[bold]Value Sets:[/bold]")
            for name, vs in sorted(lib.valuesets.items()):
                rprint(f"  [yellow]{name}[/yellow]: {vs.id}")

        if lib.codesystems:
            rprint("\n[bold]Code Systems:[/bold]")
            for name, cs in sorted(lib.codesystems.items()):
                rprint(f"  [magenta]{name}[/magenta]: {cs.id}")

    rprint()
    rprint("[green]✓[/green] [bold]All checks passed[/bold]")


@app.command()
def measure(
    file: Annotated[Path, typer.Argument(help="CQL measure file")],
    data: Annotated[Optional[Path], typer.Option("--data", "-d", help="JSON data file (patient or bundle)")] = None,
    patients: Annotated[
        Optional[Path], typer.Option("--patients", "-p", help="Directory with patient JSON files")
    ] = None,
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file for measure report")] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show detailed results")] = False,
) -> None:
    """Evaluate a CQL quality measure against patient data.

    The measure file should define populations like:
    - Initial Population
    - Denominator
    - Numerator
    - etc.

    Examples:
        cql measure measure.cql --data patient.json
        cql measure measure.cql --patients ./patients/
        cql measure measure.cql --data bundle.json --output report.json
    """
    from fhirkit.engine.cql.measure import MeasureEvaluator

    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    # Load patients
    patient_list: list[dict[str, Any]] = []

    if data:
        if not data.exists():
            rprint(f"[red]Error:[/red] Data file not found: {data}")
            raise typer.Exit(1)

        try:
            data_content = json.loads(data.read_text())
            if data_content.get("resourceType") == "Bundle":
                # Extract patients from bundle
                for entry in data_content.get("entry", []):
                    resource = entry.get("resource", {})
                    if resource.get("resourceType") == "Patient":
                        patient_list.append(resource)
            elif data_content.get("resourceType") == "Patient":
                patient_list.append(data_content)
            else:
                rprint("[red]Error:[/red] Data must be a Patient or Bundle resource")
                raise typer.Exit(1)
        except json.JSONDecodeError as e:
            rprint(f"[red]Error parsing JSON:[/red] {e}")
            raise typer.Exit(1)

    if patients:
        if not patients.exists() or not patients.is_dir():
            rprint(f"[red]Error:[/red] Patients directory not found: {patients}")
            raise typer.Exit(1)

        for patient_file in patients.glob("*.json"):
            try:
                patient_data = json.loads(patient_file.read_text())
                if patient_data.get("resourceType") == "Patient":
                    patient_list.append(patient_data)
            except json.JSONDecodeError:
                rprint(f"[yellow]Warning:[/yellow] Skipping invalid JSON: {patient_file}")

    if not patient_list:
        rprint("[yellow]Warning:[/yellow] No patients provided, using empty population")

    # Load and run measure
    try:
        measure_eval = MeasureEvaluator()
        measure_eval.load_measure_file(str(file))

        rprint(f"[bold blue]Measure:[/bold blue] {file.name}")
        rprint(f"[dim]Evaluating {len(patient_list)} patient(s)...[/dim]")
        rprint()

        report = measure_eval.evaluate_population(patient_list)

        # Display results
        for group in report.groups:
            table = Table(title=f"Group: {group.id or 'default'}", show_header=True, header_style="bold")
            table.add_column("Population", style="cyan")
            table.add_column("Count", justify="right")

            for pop_type, pop_count in group.populations.items():
                table.add_row(pop_type, str(pop_count.count))

            if group.measure_score is not None:
                table.add_row("[bold]Score[/bold]", f"[bold]{group.measure_score:.2%}[/bold]")

            console.print(table)

            # Show stratifiers if verbose
            if verbose and group.stratifiers:
                rprint("\n[bold]Stratifiers:[/bold]")
                for strat_name, strat_results in group.stratifiers.items():
                    rprint(f"  [cyan]{strat_name}[/cyan]:")
                    for strat in strat_results:
                        rprint(f"    {strat.value}: {strat.populations}")

        # Write output if requested
        if output:
            # Use the to_fhir() method for proper conversion
            report_dict = report.to_fhir()
            output.write_text(json.dumps(report_dict, indent=2, default=str))
            rprint(f"\n[dim]Report written to {output}[/dim]")

    except CQLError as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def export(
    file: Annotated[Path, typer.Argument(help="CQL file to export to ELM")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output ELM JSON file")] = None,
    indent: Annotated[int, typer.Option("--indent", "-i", help="JSON indentation level")] = 2,
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Only output JSON (no status messages)")] = False,
) -> None:
    """Export a CQL library to ELM JSON format.

    ELM (Expression Logical Model) is the standardized compiled representation
    of CQL that can be executed by any ELM-compatible engine.

    Examples:
        cql export library.cql
        cql export library.cql -o library.elm.json
        cql export library.cql --quiet > library.elm.json
    """
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    try:
        source = file.read_text()
        evaluator = CQLEvaluator()
        elm_json = evaluator.to_elm_json(source, indent=indent)

        if output:
            output.write_text(elm_json)
            if not quiet:
                rprint(f"[green]✓[/green] Exported {file} -> {output}")
        else:
            if quiet:
                # Just print the JSON
                print(elm_json)
            else:
                # Show with syntax highlighting
                syntax = Syntax(elm_json, "json", theme="monokai", line_numbers=True)
                console.print(Panel(syntax, title=f"ELM: {file}", border_style="blue"))

    except CQLError as e:
        if quiet:
            import sys

            print(f"Error: {e}", file=sys.stderr)
        else:
            rprint(f"[red]Error exporting to ELM:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def repl(
    library: Annotated[Optional[Path], typer.Option("--library", "-l", help="CQL library file to load")] = None,
    data: Annotated[Optional[Path], typer.Option("--data", "-d", help="FHIR resource JSON file for context")] = None,
) -> None:
    """Start an interactive CQL REPL.

    The REPL allows you to:
    - Evaluate CQL expressions interactively
    - Load CQL library files
    - Load FHIR data for context
    - View definitions and AST

    Examples:
        fhir cql repl
        fhir cql repl --library mylib.cql
        fhir cql repl --library mylib.cql --data patient.json

    Commands in REPL:
        load <file>     - Load a CQL library
        data <file>     - Load FHIR data for context
        defs            - List loaded definitions
        ast <expr>      - Show AST for expression
        help            - Show help
        quit            - Exit REPL
    """
    from rich.tree import Tree

    rprint("[bold blue]CQL REPL[/bold blue]")
    rprint("Enter CQL expressions to evaluate. Type 'help' for commands.\n")

    evaluator = CQLEvaluator()
    context_data: dict[str, Any] | None = None

    # Load initial library if provided
    if library and library.exists():
        try:
            source = library.read_text()
            lib = evaluator.compile(source)
            rprint(f"[green]✓[/green] Loaded library: {lib.name}")
            if lib.definitions:
                rprint(f"  Definitions: {', '.join(lib.definitions.keys())}")
        except Exception as e:
            rprint(f"[yellow]Warning:[/yellow] Failed to load library: {e}")

    # Load initial data if provided
    if data and data.exists():
        try:
            context_data = json.loads(data.read_text())
            rprint(f"[green]✓[/green] Loaded data: {data}")
            if isinstance(context_data, dict) and "resourceType" in context_data:
                rprint(f"  Resource type: {context_data['resourceType']}")
        except Exception as e:
            rprint(f"[yellow]Warning:[/yellow] Failed to load data: {e}")

    if library or data:
        rprint()

    while True:
        try:
            expr = console.input("[bold green]cql>[/bold green] ")
        except (EOFError, KeyboardInterrupt):
            rprint("\nGoodbye!")
            break

        expr = expr.strip()
        if not expr:
            continue

        if expr.lower() in ("quit", "exit", "q"):
            rprint("Goodbye!")
            break

        if expr.lower() == "help":
            rprint("""[dim]Commands:
  load <file>     Load a CQL library file
  data <file>     Load FHIR data for context
  defs            List loaded definitions
  ast <expr>      Show AST for expression
  eval <name>     Evaluate a definition by name
  clear           Clear loaded library
  help            Show this help
  quit            Exit REPL

Examples:
  1 + 2 * 3                            Evaluate expression
  Today()                              Today's date
  Upper('hello')                       String function
  load mylib.cql                       Load a library
  defs                                 List definitions
  eval MyDefinition                    Evaluate definition[/dim]""")
            continue

        # Load library command
        if expr.lower().startswith("load "):
            lib_path = Path(expr[5:].strip())
            if not lib_path.exists():
                rprint(f"[red]Error:[/red] File not found: {lib_path}")
                continue
            try:
                source = lib_path.read_text()
                lib = evaluator.compile(source)
                rprint(f"[green]✓[/green] Loaded: {lib.name}")
                if lib.definitions:
                    rprint(f"  Definitions: {', '.join(lib.definitions.keys())}")
            except Exception as e:
                rprint(f"[red]Error:[/red] {e}")
            continue

        # Load data command
        if expr.lower().startswith("data "):
            data_path = Path(expr[5:].strip())
            if not data_path.exists():
                rprint(f"[red]Error:[/red] File not found: {data_path}")
                continue
            try:
                context_data = json.loads(data_path.read_text())
                rprint(f"[green]✓[/green] Loaded data: {data_path}")
                if isinstance(context_data, dict) and "resourceType" in context_data:
                    rprint(f"  Resource type: {context_data['resourceType']}")
            except Exception as e:
                rprint(f"[red]Error:[/red] {e}")
            continue

        # List definitions command
        if expr.lower() == "defs":
            current_lib = evaluator.current_library
            if not current_lib:
                rprint("[yellow]No library loaded[/yellow]")
                continue
            if current_lib.definitions:
                rprint(f"[bold]{current_lib.name}[/bold] definitions:")
                for name in current_lib.definitions.keys():
                    rprint(f"  • {name}")
            if current_lib.functions:
                rprint("Functions:")
                for name in current_lib.functions.keys():
                    rprint(f"  • {name}")
            if not current_lib.definitions and not current_lib.functions:
                rprint("[dim]No definitions[/dim]")
            continue

        # Clear library command
        if expr.lower() == "clear":
            evaluator = CQLEvaluator()
            context_data = None
            rprint("[green]✓[/green] Cleared")
            continue

        # Eval definition command
        if expr.lower().startswith("eval "):
            def_name = expr[5:].strip()
            try:
                result = evaluator.evaluate_definition(def_name, resource=context_data)
                rprint(_format_result(result))
            except Exception as e:
                rprint(f"[red]Error:[/red] {e}")
            continue

        # AST command
        if expr.lower().startswith("ast "):
            cql_expr = expr[4:].strip()
            try:
                input_stream = InputStream(cql_expr)
                lexer = cqlLexer(input_stream)
                token_stream = CommonTokenStream(lexer)
                parser = cqlParser(token_stream)
                tree = parser.expression()
                rich_tree = Tree("[bold blue]expression[/bold blue]")
                _build_tree(tree, rich_tree, parser)
                rprint(rich_tree)
            except Exception as e:
                rprint(f"[red]Error:[/red] {e}")
            continue

        # Default: evaluate as expression
        try:
            result = evaluator.evaluate_expression(expr, resource=context_data)
            rprint(_format_result(result))
        except Exception as e:
            rprint(f"[red]Error:[/red] {e}")


def _build_tree(node: Any, rich_tree: "Tree", parser: Any) -> None:
    """Build a Rich tree from a parse tree node."""
    if hasattr(node, "getChildCount"):
        for i in range(node.getChildCount()):
            child = node.getChild(i)
            if hasattr(child, "getText"):
                child_type = type(child).__name__.replace("Context", "")
                text = child.getText()
                if len(text) > 40:
                    text = text[:40] + "..."
                branch = rich_tree.add(f"[cyan]{child_type}[/cyan]: {text}")
                _build_tree(child, branch, parser)


if __name__ == "__main__":
    app()
