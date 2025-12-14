"""Unified FHIR CLI - Command line interface for FHIRPath, CQL, ELM, CDS Hooks, Terminology, and FHIR Server."""

import typer
from rich import print as rprint

from fhir_cql.cds_cli import app as cds_app
from fhir_cql.cql_cli import app as cql_app
from fhir_cql.elm_cli import app as elm_app
from fhir_cql.fhirpath_cli import app as fhirpath_app
from fhir_cql.server_cli import app as server_app
from fhir_cql.terminology_cli import app as terminology_app

app = typer.Typer(
    name="fhir",
    help="FHIR tooling: FHIRPath, CQL, ELM, CDS Hooks, Terminology Service, and FHIR Server",
    no_args_is_help=True,
)

# Add subcommands
app.add_typer(cql_app, name="cql", help="CQL parser, evaluator, and quality measures")
app.add_typer(elm_app, name="elm", help="ELM (Expression Logical Model) loader and evaluator")
app.add_typer(fhirpath_app, name="fhirpath", help="FHIRPath expression parser and evaluator")
app.add_typer(cds_app, name="cds", help="CDS Hooks server and configuration tools")
app.add_typer(terminology_app, name="terminology", help="FHIR Terminology Service")
app.add_typer(server_app, name="server", help="FHIR R4 server utilities (generate, load, stats)")


@app.command("serve")
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8080, "--port", "-p", help="Port to bind to"),
    patients: int = typer.Option(0, "--patients", "-n", help="Number of synthetic patients to generate"),
    seed: int = typer.Option(None, "--seed", "-s", help="Random seed for reproducible data"),
    preload_cql: str = typer.Option(None, "--preload-cql", help="Directory of CQL files to preload"),
    preload_valuesets: str = typer.Option(
        None, "--preload-valuesets", help="Directory of ValueSet/CodeSystem JSON files"
    ),
    preload_data: str = typer.Option(None, "--preload-data", help="FHIR Bundle JSON file to preload"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload for development"),
    log_level: str = typer.Option("INFO", "--log-level", "-l", help="Logging level"),
) -> None:
    """Start the FHIR R4 server.

    Examples:
        # Start with 100 synthetic patients
        fhir serve --patients 100

        # With reproducible data
        fhir serve --patients 50 --seed 42

        # Preload CQL libraries and ValueSets
        fhir serve --preload-cql ./cql --preload-valuesets ./valuesets

        # Load existing FHIR data
        fhir serve --preload-data ./patients.json
    """
    import uvicorn

    from fhir_cql.server.api.app import create_app
    from fhir_cql.server.config.settings import FHIRServerSettings
    from fhir_cql.server.preload import load_cql_directory, load_fhir_directory, load_single_file
    from fhir_cql.server.storage.fhir_store import FHIRStore

    settings = FHIRServerSettings(
        host=host,
        port=port,
        patients=patients,
        seed=seed,
        preload_cql=preload_cql,
        preload_valuesets=preload_valuesets,
        log_level=log_level.upper(),
    )

    # Create store and preload data
    store = FHIRStore()

    # Preload CQL libraries
    if preload_cql:
        rprint(f"[dim]Loading CQL libraries from {preload_cql}...[/dim]")
        libraries = load_cql_directory(preload_cql)
        for lib in libraries:
            store.create(lib)
        rprint(f"  Loaded {len(libraries)} CQL libraries")

    # Preload ValueSets and CodeSystems
    if preload_valuesets:
        rprint(f"[dim]Loading terminology from {preload_valuesets}...[/dim]")
        resources_by_type = load_fhir_directory(preload_valuesets)
        total = 0
        for resource_type, resources in resources_by_type.items():
            for resource in resources:
                store.create(resource)
                total += 1
        rprint(f"  Loaded {total} terminology resources")

    # Preload FHIR data file
    if preload_data:
        rprint(f"[dim]Loading FHIR data from {preload_data}...[/dim]")
        resources = load_single_file(preload_data)
        for resource in resources:
            store.create(resource)
        rprint(f"  Loaded {len(resources)} resources")

    app_instance = create_app(settings=settings, store=store)

    rprint()
    rprint("[bold green]Starting FHIR R4 Server[/bold green]")
    rprint(f"  Host: {host}")
    rprint(f"  Port: {port}")
    if patients > 0:
        rprint(f"  Synthetic patients: {patients}")
        if seed:
            rprint(f"  Random seed: {seed}")
    api_base = settings.api_base_path
    rprint()
    rprint("[bold]Endpoints:[/bold]")
    rprint(f"  Web UI:       http://{host}:{port}/")
    rprint(f"  FHIR API:     http://{host}:{port}{api_base}")
    rprint(f"  Metadata:     http://{host}:{port}{api_base}/metadata")
    rprint(f"  API Docs:     http://{host}:{port}{api_base}/docs")
    rprint()
    rprint("[bold]Example requests:[/bold]")
    rprint(f"  GET  http://{host}:{port}{api_base}/Patient")
    rprint(f"  GET  http://{host}:{port}{api_base}/Patient/{{id}}")
    rprint(f"  POST http://{host}:{port}{api_base}/Patient")
    rprint()

    uvicorn.run(
        app_instance,
        host=host,
        port=port,
        reload=reload,
        log_level=log_level.lower(),
    )


if __name__ == "__main__":
    app()
