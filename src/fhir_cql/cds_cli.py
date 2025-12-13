"""CDS Hooks CLI commands."""

from pathlib import Path

import typer
import yaml
from rich import print as rprint
from rich.table import Table

app = typer.Typer(
    name="cds",
    help="CDS Hooks server and configuration tools",
    no_args_is_help=True,
)


@app.command("serve")
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8080, "--port", "-p", help="Port to bind to"),
    config: str = typer.Option("cds_services.yaml", "--config", "-c", help="Services config file"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
    cql_path: str = typer.Option("", "--cql-path", help="Base path for CQL library files"),
) -> None:
    """Start the CDS Hooks server.

    Example:
        fhir cds serve --port 8080 --config cds_services.yaml
    """
    import uvicorn

    from fhir_cql.cds_hooks.api.app import create_app
    from fhir_cql.cds_hooks.config.settings import CDSHooksSettings

    settings = CDSHooksSettings(
        host=host,
        port=port,
        services_config_path=config,
        cql_library_path=cql_path,
    )

    app_instance = create_app(settings)

    rprint("[bold green]Starting CDS Hooks server[/bold green]")
    rprint(f"  Host: {host}")
    rprint(f"  Port: {port}")
    rprint(f"  Config: {config}")
    rprint()
    rprint("[bold]Endpoints:[/bold]")
    rprint(f"  Discovery: http://{host}:{port}/cds-services")
    rprint(f"  API Docs:  http://{host}:{port}/docs")
    rprint(f"  Health:    http://{host}:{port}/health")
    rprint()

    uvicorn.run(
        app_instance,
        host=host,
        port=port,
        reload=reload,
    )


@app.command("validate")
def validate(
    config: Path = typer.Argument(..., help="Services config file to validate"),
) -> None:
    """Validate a CDS services configuration file.

    Example:
        fhir cds validate cds_services.yaml
    """
    from fhir_cql.cds_hooks.config.settings import CDSServiceConfig

    if not config.exists():
        rprint(f"[red]Error:[/red] Config file not found: {config}")
        raise typer.Exit(1)

    try:
        with open(config) as f:
            data = yaml.safe_load(f)

        if not data:
            rprint("[yellow]Warning:[/yellow] Config file is empty")
            raise typer.Exit(0)

        services = []
        errors = []

        for i, service_data in enumerate(data.get("services", [])):
            try:
                service = CDSServiceConfig(**service_data)
                services.append(service)
            except Exception as e:
                errors.append(f"Service {i + 1}: {e}")

        if errors:
            rprint("[red]Validation errors:[/red]")
            for error in errors:
                rprint(f"  - {error}")
            raise typer.Exit(1)

        rprint(f"[green]Valid configuration[/green] with {len(services)} service(s):")
        rprint()

        table = Table(title="Configured Services")
        table.add_column("ID", style="cyan")
        table.add_column("Hook", style="magenta")
        table.add_column("Title")
        table.add_column("Status")

        for service in services:
            status = "[green]enabled[/green]" if service.enabled else "[dim]disabled[/dim]"
            table.add_row(service.id, service.hook, service.title, status)

        rprint(table)

    except yaml.YAMLError as e:
        rprint(f"[red]YAML parsing error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Validation error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_services(
    config: str = typer.Option("cds_services.yaml", "--config", "-c", help="Services config file"),
) -> None:
    """List configured CDS services.

    Example:
        fhir cds list --config cds_services.yaml
    """
    config_path = Path(config)
    if not config_path.exists():
        rprint(f"[yellow]Warning:[/yellow] Config file not found: {config}")
        rprint("No services configured.")
        raise typer.Exit(0)

    try:
        with open(config_path) as f:
            data = yaml.safe_load(f)

        if not data or not data.get("services"):
            rprint("No services configured.")
            raise typer.Exit(0)

        from fhir_cql.cds_hooks.config.settings import CDSServiceConfig

        table = Table(title=f"CDS Services from {config}")
        table.add_column("ID", style="cyan")
        table.add_column("Hook", style="magenta")
        table.add_column("Title")
        table.add_column("CQL Library")
        table.add_column("Definitions")

        for service_data in data.get("services", []):
            try:
                service = CDSServiceConfig(**service_data)
                table.add_row(
                    service.id,
                    service.hook,
                    service.title,
                    service.cqlLibrary,
                    str(len(service.evaluateDefinitions)),
                )
            except Exception:
                pass

        rprint(table)

    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("test")
def test_service(
    service_id: str = typer.Argument(..., help="Service ID to test"),
    config: str = typer.Option("cds_services.yaml", "--config", "-c", help="Services config file"),
    patient: Path = typer.Option(None, "--patient", "-p", help="Patient JSON file"),
) -> None:
    """Test a CDS service with sample data.

    Example:
        fhir cds test medication-safety --patient patient.json
    """
    import json
    from uuid import uuid4

    from fhir_cql.cds_hooks.config.settings import CDSHooksSettings
    from fhir_cql.cds_hooks.models.request import CDSRequest
    from fhir_cql.cds_hooks.service.card_builder import CardBuilder
    from fhir_cql.cds_hooks.service.executor import CDSExecutor
    from fhir_cql.cds_hooks.service.registry import ServiceRegistry

    settings = CDSHooksSettings(services_config_path=config)
    registry = ServiceRegistry(settings)

    service = registry.get_service(service_id)
    if not service:
        rprint(f"[red]Error:[/red] Service not found: {service_id}")
        raise typer.Exit(1)

    rprint(f"[bold]Testing service:[/bold] {service.title}")
    rprint(f"  Hook: {service.hook}")
    rprint(f"  CQL Library: {service.cqlLibrary}")
    rprint()

    # Build prefetch from patient file
    prefetch: dict = {}
    if patient and patient.exists():
        with open(patient) as f:
            patient_data = json.load(f)
        prefetch["patient"] = patient_data
        rprint(f"[dim]Loaded patient from {patient}[/dim]")

    # Create mock request
    request = CDSRequest(
        hook=service.hook,
        hookInstance=uuid4(),
        context={"patientId": "test-patient", "userId": "test-user"},
        prefetch=prefetch,
    )

    # Execute
    executor = CDSExecutor(settings)
    try:
        results = executor.execute(service, request)
        rprint()
        rprint("[bold]CQL Results:[/bold]")
        for key, value in results.items():
            if not key.startswith("_"):
                rprint(f"  {key}: {value}")

        # Build cards
        card_builder = CardBuilder()
        response = card_builder.build_response(service, results)

        rprint()
        rprint(f"[bold]Cards generated:[/bold] {len(response.cards)}")
        for card in response.cards:
            indicator_color = {
                "info": "blue",
                "warning": "yellow",
                "critical": "red",
            }.get(card.indicator, "white")
            rprint(f"  [{indicator_color}][{card.indicator.upper()}][/{indicator_color}] {card.summary}")
            if card.detail:
                detail_text = card.detail[:100] + "..." if len(card.detail) > 100 else card.detail
                rprint(f"    [dim]{detail_text}[/dim]")

    except Exception as e:
        rprint(f"[red]Execution error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
