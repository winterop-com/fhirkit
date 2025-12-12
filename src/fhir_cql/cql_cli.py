"""CQL CLI - Command line interface for CQL parsing and analysis."""

import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree

# Add generated directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "generated" / "cql"))

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener
from cqlLexer import cqlLexer
from cqlParser import cqlParser

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


if __name__ == "__main__":
    app()
