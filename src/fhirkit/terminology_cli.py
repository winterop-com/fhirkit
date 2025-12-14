"""Terminology Service CLI.

Provides commands for running and managing the terminology service.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .terminology import (
    InMemoryTerminologyService,
    MemberOfRequest,
    ValidateCodeRequest,
)

app = typer.Typer(
    name="terminology",
    help="FHIR Terminology Service commands",
    no_args_is_help=True,
)

console = Console()


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8080, "--port", "-p", help="Port to listen on"),
    valueset_dir: Optional[Path] = typer.Option(
        None, "--valuesets", "-v", help="Directory containing ValueSet JSON files"
    ),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload for development"),
) -> None:
    """Start the terminology service.

    Examples:
        # Start with default settings
        fhir terminology serve

        # Start on specific port with value sets
        fhir terminology serve --port 9000 --valuesets ./valuesets
    """
    import uvicorn

    from .terminology.api import create_app

    console.print("[bold green]Starting Terminology Service[/bold green]")
    console.print(f"  Host: {host}")
    console.print(f"  Port: {port}")

    if valueset_dir:
        console.print(f"  ValueSet directory: {valueset_dir}")

    console.print(f"\n  API docs: http://{host}:{port}/docs")
    console.print(f"  Health check: http://{host}:{port}/health")
    console.print()

    app = create_app(value_set_directory=valueset_dir)
    uvicorn.run(app, host=host, port=port, reload=reload)


@app.command()
def validate(
    code: str = typer.Argument(..., help="Code to validate"),
    system: str = typer.Option(..., "--system", "-s", help="Code system URL"),
    valueset: str = typer.Option(..., "--valueset", "-v", help="ValueSet URL"),
    valueset_dir: Optional[Path] = typer.Option(None, "--dir", "-d", help="Directory containing ValueSet JSON files"),
) -> None:
    """Validate a code against a value set.

    Examples:
        fhir terminology validate final -s http://hl7.org/fhir/observation-status \\
            -v http://hl7.org/fhir/ValueSet/observation-status \\
            -d ./valuesets
    """
    service = InMemoryTerminologyService()

    if valueset_dir and valueset_dir.exists():
        count = service.load_value_sets_from_directory(valueset_dir)
        console.print(f"Loaded {count} value sets from {valueset_dir}")

    request = ValidateCodeRequest(
        url=valueset,
        code=code,
        system=system,
    )

    result = service.validate_code(request)

    if result.result:
        console.print(f"[green]✓ Valid[/green]: {code} is in {valueset}")
        if result.display:
            console.print(f"  Display: {result.display}")
    else:
        console.print(f"[red]✗ Invalid[/red]: {code} is not in {valueset}")
        if result.message:
            console.print(f"  Message: {result.message}")


@app.command()
def member_of(
    code: str = typer.Argument(..., help="Code to check"),
    system: str = typer.Option(..., "--system", "-s", help="Code system URL"),
    valueset: str = typer.Option(..., "--valueset", "-v", help="ValueSet URL"),
    valueset_dir: Optional[Path] = typer.Option(None, "--dir", "-d", help="Directory containing ValueSet JSON files"),
) -> None:
    """Check if a code is a member of a value set.

    Examples:
        fhir terminology member-of final -s http://hl7.org/fhir/observation-status \\
            -v http://hl7.org/fhir/ValueSet/observation-status \\
            -d ./valuesets
    """
    service = InMemoryTerminologyService()

    if valueset_dir and valueset_dir.exists():
        count = service.load_value_sets_from_directory(valueset_dir)
        console.print(f"Loaded {count} value sets from {valueset_dir}")

    request = MemberOfRequest(
        code=code,
        system=system,
        valueSetUrl=valueset,
    )

    result = service.member_of(request)

    if result.result:
        console.print(f"[green]✓ Member[/green]: {code} is in {valueset}")
    else:
        console.print(f"[red]✗ Not a member[/red]: {code} is not in {valueset}")


@app.command()
def list_valuesets(
    valueset_dir: Path = typer.Argument(..., help="Directory containing ValueSet JSON files"),
) -> None:
    """List value sets in a directory.

    Examples:
        fhir terminology list-valuesets ./valuesets
    """
    service = InMemoryTerminologyService()
    count = service.load_value_sets_from_directory(valueset_dir)

    if count == 0:
        console.print("[yellow]No value sets found[/yellow]")
        return

    table = Table(title=f"Value Sets ({count} loaded)")
    table.add_column("URL", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Name", style="white")
    table.add_column("Codes", style="magenta", justify="right")

    seen_urls: set[str] = set()
    for url, vs in service._value_sets.items():
        # Avoid duplicates from version-indexed entries
        if "|" in url:
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)

        # Count codes
        code_count = 0
        if vs.expansion and vs.expansion.contains:
            code_count = len(vs.expansion.contains)
        elif vs.compose:
            for include in vs.compose.include:
                code_count += len(include.concept)

        table.add_row(
            vs.url or url,
            vs.version or "-",
            vs.name or vs.title or "-",
            str(code_count),
        )

    console.print(table)


if __name__ == "__main__":
    app()
