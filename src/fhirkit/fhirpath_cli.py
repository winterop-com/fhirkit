"""FHIRPath CLI - Command line interface for FHIRPath parsing and analysis."""

import json
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree

# Add generated directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "generated" / "fhirpath"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "generated"))

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener
from fhirpathLexer import fhirpathLexer
from fhirpathParser import fhirpathParser

app = typer.Typer(
    name="fhirpath",
    help="FHIRPath expression parser and analyzer",
    no_args_is_help=True,
)
console = Console()


class FHIRPathErrorListener(ErrorListener):
    """Custom error listener for FHIRPath parsing errors."""

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


def parse_fhirpath(text: str) -> tuple[fhirpathParser.ExpressionContext, list[str]]:
    """Parse FHIRPath expression and return parse tree with any errors."""
    input_stream = InputStream(text)
    lexer = fhirpathLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = fhirpathParser(token_stream)

    error_listener = FHIRPathErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    tree = parser.expression()
    return tree, error_listener.errors


def build_tree(node: object, tree: Tree, parser: fhirpathParser, depth: int = 0, max_depth: int = 50) -> None:
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
    expression: Annotated[str, typer.Argument(help="FHIRPath expression to parse")],
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Only show errors")] = False,
) -> None:
    """Parse a FHIRPath expression and report any syntax errors."""
    tree, errors = parse_fhirpath(expression)

    if errors:
        rprint("[red]Parse errors:[/red]")
        for error in errors:
            rprint(f"  [red]•[/red] {error}")
        raise typer.Exit(1)

    if not quiet:
        rprint("[green]✓[/green] Valid FHIRPath expression")


@app.command()
def ast(
    expression: Annotated[str, typer.Argument(help="FHIRPath expression to parse")],
    max_depth: Annotated[int, typer.Option("--depth", "-d", help="Maximum tree depth")] = 50,
) -> None:
    """Display the Abstract Syntax Tree (AST) for a FHIRPath expression."""
    tree_node, errors = parse_fhirpath(expression)

    if errors:
        rprint("[red]Parse errors:[/red]")
        for error in errors:
            rprint(f"  [red]•[/red] {error}")
        raise typer.Exit(1)

    # Build and display tree
    input_stream = InputStream(expression)
    lexer = fhirpathLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = fhirpathParser(token_stream)

    rich_tree = Tree("[bold blue]expression[/bold blue]")
    build_tree(tree_node, rich_tree, parser, max_depth=max_depth)
    rprint(rich_tree)


@app.command()
def tokens(
    expression: Annotated[str, typer.Argument(help="FHIRPath expression to tokenize")],
) -> None:
    """Display the token stream for a FHIRPath expression."""
    input_stream = InputStream(expression)
    lexer = fhirpathLexer(input_stream)

    rprint("[bold]Tokens:[/bold]\n")

    count = 0
    token = lexer.nextToken()
    while token.type != -1:  # EOF
        token_name = lexer.symbolicNames[token.type] if token.type < len(lexer.symbolicNames) else "UNKNOWN"
        rprint(f"[cyan]{token_name:20}[/cyan] [green]'{token.text}'[/green] [dim](col {token.column})[/dim]")

        count += 1
        token = lexer.nextToken()

    rprint(f"\n[dim]Total: {count} tokens[/dim]")


@app.command("parse-file")
def parse_file(
    file: Annotated[Path, typer.Argument(help="File containing FHIRPath expressions (one per line)")],
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Only show errors")] = False,
) -> None:
    """Parse a file containing FHIRPath expressions (one per line)."""
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    lines = file.read_text().strip().split("\n")
    total = 0
    passed = 0
    failed = 0

    for i, line in enumerate(lines, 1):
        # Skip empty lines and comments
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("#"):
            continue

        total += 1
        _, errors = parse_fhirpath(line)

        if errors:
            rprint(f"[red]✗[/red] Line {i}: {line[:50]}...")
            for error in errors:
                rprint(f"    [red]•[/red] {error}")
            failed += 1
        else:
            if not quiet:
                rprint(f"[green]✓[/green] Line {i}: {line[:50]}{'...' if len(line) > 50 else ''}")
            passed += 1

    rprint(f"\n[bold]Results:[/bold] {passed}/{total} passed, {failed}/{total} failed")

    if failed > 0:
        raise typer.Exit(1)


@app.command()
def repl() -> None:
    """Start an interactive FHIRPath REPL."""
    rprint("[bold blue]FHIRPath REPL[/bold blue]")
    rprint("Enter FHIRPath expressions to parse. Type 'quit' or 'exit' to quit.\n")

    while True:
        try:
            expr = console.input("[bold green]fhirpath>[/bold green] ")
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
            rprint("[dim]Commands: ast <expr>, tokens <expr>, quit[/dim]")
            continue

        # Check for subcommands
        if expr.lower().startswith("ast "):
            tree_node, errors = parse_fhirpath(expr[4:])
            if errors:
                for error in errors:
                    rprint(f"  [red]•[/red] {error}")
            else:
                input_stream = InputStream(expr[4:])
                lexer = fhirpathLexer(input_stream)
                token_stream = CommonTokenStream(lexer)
                parser = fhirpathParser(token_stream)
                rich_tree = Tree("[bold blue]expression[/bold blue]")
                build_tree(tree_node, rich_tree, parser)
                rprint(rich_tree)
            continue

        if expr.lower().startswith("tokens "):
            input_stream = InputStream(expr[7:])
            lexer = fhirpathLexer(input_stream)
            token = lexer.nextToken()
            while token.type != -1:
                token_name = lexer.symbolicNames[token.type] if token.type < len(lexer.symbolicNames) else "UNKNOWN"
                rprint(f"[cyan]{token_name}[/cyan]: [green]'{token.text}'[/green]")
                token = lexer.nextToken()
            continue

        # Default: just parse
        tree, errors = parse_fhirpath(expr)
        if errors:
            for error in errors:
                rprint(f"  [red]•[/red] {error}")
        else:
            rprint("[green]✓[/green] Valid")


@app.command()
def show(
    file: Annotated[Path, typer.Argument(help="FHIRPath file to display")],
) -> None:
    """Display a FHIRPath file with syntax highlighting."""
    if not file.exists():
        rprint(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    text = file.read_text()
    syntax = Syntax(text, "javascript", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=str(file), border_style="blue"))


@app.command()
def eval(
    expression: Annotated[str, typer.Argument(help="FHIRPath expression to evaluate")],
    resource: Annotated[Path | None, typer.Option("--resource", "-r", help="Path to FHIR JSON resource file")] = None,
    json_input: Annotated[str | None, typer.Option("--json", "-j", help="Inline JSON resource")] = None,
    output_json: Annotated[bool, typer.Option("--json-output", help="Output result as JSON")] = False,
) -> None:
    """Evaluate a FHIRPath expression against a FHIR resource."""
    from fhirkit.engine.exceptions import FHIRPathError
    from fhirkit.engine.fhirpath import FHIRPathEvaluator

    # Load resource
    fhir_resource = None
    if resource:
        if not resource.exists():
            rprint(f"[red]Error:[/red] Resource file not found: {resource}")
            raise typer.Exit(1)
        try:
            fhir_resource = json.loads(resource.read_text())
        except json.JSONDecodeError as e:
            rprint(f"[red]Error:[/red] Invalid JSON in resource file: {e}")
            raise typer.Exit(1)
    elif json_input:
        try:
            fhir_resource = json.loads(json_input)
        except json.JSONDecodeError as e:
            rprint(f"[red]Error:[/red] Invalid JSON input: {e}")
            raise typer.Exit(1)

    # Evaluate expression
    try:
        evaluator = FHIRPathEvaluator()
        result = evaluator.evaluate(expression, fhir_resource)

        if output_json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if not result:
                rprint("[dim]Empty result ([])[/dim]")
            elif len(result) == 1:
                rprint(f"[green]{result[0]!r}[/green]")
            else:
                rprint("[bold]Results:[/bold]")
                for i, item in enumerate(result):
                    rprint(f"  [{i}] [green]{item!r}[/green]")

    except FHIRPathError as e:
        rprint(f"[red]FHIRPath Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("eval-file")
def eval_file(
    expressions_file: Annotated[Path, typer.Argument(help="File containing FHIRPath expressions")],
    resource: Annotated[Path | None, typer.Option("--resource", "-r", help="Path to FHIR JSON resource file")] = None,
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Only show errors")] = False,
) -> None:
    """Evaluate FHIRPath expressions from a file against a FHIR resource."""
    from fhirkit.engine.exceptions import FHIRPathError
    from fhirkit.engine.fhirpath import FHIRPathEvaluator

    if not expressions_file.exists():
        rprint(f"[red]Error:[/red] File not found: {expressions_file}")
        raise typer.Exit(1)

    # Load resource
    fhir_resource = None
    if resource:
        if not resource.exists():
            rprint(f"[red]Error:[/red] Resource file not found: {resource}")
            raise typer.Exit(1)
        fhir_resource = json.loads(resource.read_text())

    evaluator = FHIRPathEvaluator()
    lines = expressions_file.read_text().strip().split("\n")
    total = 0
    passed = 0
    failed = 0

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("#"):
            continue

        total += 1
        try:
            result = evaluator.evaluate(line, fhir_resource)
            if not quiet:
                result_str = repr(result[0]) if len(result) == 1 else repr(result)
                if len(result_str) > 50:
                    result_str = result_str[:47] + "..."
                rprint(f"[green]✓[/green] {line[:40]:40} => [cyan]{result_str}[/cyan]")
            passed += 1
        except FHIRPathError as e:
            rprint(f"[red]✗[/red] Line {i}: {line}")
            rprint(f"    [red]•[/red] {e}")
            failed += 1

    rprint(f"\n[bold]Results:[/bold] {passed}/{total} passed, {failed}/{total} failed")

    if failed > 0:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
