"""FHIR Server CLI commands."""

import json
from pathlib import Path
from typing import Any

import typer
from rich import print as rprint
from rich.table import Table

from fhir_cql.server.generator import (
    AllergyIntoleranceGenerator,
    AppointmentGenerator,
    CarePlanGenerator,
    CareTeamGenerator,
    ClaimGenerator,
    CodeSystemGenerator,
    ConditionGenerator,
    CoverageGenerator,
    DeviceGenerator,
    DiagnosticReportGenerator,
    DocumentReferenceGenerator,
    EncounterGenerator,
    ExplanationOfBenefitGenerator,
    GoalGenerator,
    GroupGenerator,
    ImmunizationGenerator,
    LibraryGenerator,
    LocationGenerator,
    MeasureGenerator,
    MeasureReportGenerator,
    MedicationGenerator,
    MedicationRequestGenerator,
    ObservationGenerator,
    OrganizationGenerator,
    PatientGenerator,
    PractitionerGenerator,
    PractitionerRoleGenerator,
    ProcedureGenerator,
    RelatedPersonGenerator,
    ScheduleGenerator,
    ServiceRequestGenerator,
    SlotGenerator,
    TaskGenerator,
    ValueSetGenerator,
)

app = typer.Typer(
    name="server",
    help="FHIR R4 server utilities (generate, load, stats, info). Use 'fhir serve' to start the server.",
    no_args_is_help=True,
)

# Mapping of resource types to generator classes
GENERATORS: dict[str, type] = {
    # Administrative
    "Patient": PatientGenerator,
    "Practitioner": PractitionerGenerator,
    "PractitionerRole": PractitionerRoleGenerator,
    "Organization": OrganizationGenerator,
    "Location": LocationGenerator,
    "RelatedPerson": RelatedPersonGenerator,
    # Clinical
    "Encounter": EncounterGenerator,
    "Condition": ConditionGenerator,
    "Observation": ObservationGenerator,
    "Procedure": ProcedureGenerator,
    "DiagnosticReport": DiagnosticReportGenerator,
    "AllergyIntolerance": AllergyIntoleranceGenerator,
    "Immunization": ImmunizationGenerator,
    # Medications
    "Medication": MedicationGenerator,
    "MedicationRequest": MedicationRequestGenerator,
    # Care Management
    "CarePlan": CarePlanGenerator,
    "CareTeam": CareTeamGenerator,
    "Goal": GoalGenerator,
    "Task": TaskGenerator,
    # Scheduling
    "Appointment": AppointmentGenerator,
    "Schedule": ScheduleGenerator,
    "Slot": SlotGenerator,
    # Financial
    "Coverage": CoverageGenerator,
    "Claim": ClaimGenerator,
    "ExplanationOfBenefit": ExplanationOfBenefitGenerator,
    # Devices
    "Device": DeviceGenerator,
    # Documents
    "ServiceRequest": ServiceRequestGenerator,
    "DocumentReference": DocumentReferenceGenerator,
    # Quality Measures
    "Measure": MeasureGenerator,
    "MeasureReport": MeasureReportGenerator,
    "Library": LibraryGenerator,
    # Terminology
    "ValueSet": ValueSetGenerator,
    "CodeSystem": CodeSystemGenerator,
    # Groups
    "Group": GroupGenerator,
}


@app.command("generate")
def generate(
    output: Path = typer.Argument(..., help="Output JSON file path"),
    patients: int = typer.Option(10, "--patients", "-n", help="Number of patients to generate"),
    seed: int = typer.Option(None, "--seed", "-s", help="Random seed for reproducible data"),
    format: str = typer.Option("bundle", "--format", "-f", help="Output format: bundle, ndjson, or files"),
    pretty: bool = typer.Option(True, "--pretty/--no-pretty", help="Pretty-print JSON output"),
) -> None:
    """Generate synthetic FHIR data to a file.

    Examples:
        # Generate 100 patients as a bundle
        fhir server generate ./data.json --patients 100

        # Generate with reproducible seed
        fhir server generate ./data.json --patients 50 --seed 42

        # Generate as NDJSON (one resource per line)
        fhir server generate ./data.ndjson --patients 100 --format ndjson
    """
    import uuid

    from fhir_cql.server.generator import PatientRecordGenerator

    rprint(f"[bold]Generating {patients} patient(s)...[/bold]")
    if seed:
        rprint(f"  Random seed: {seed}")

    generator = PatientRecordGenerator(seed=seed)
    resources = generator.generate_population(patients)

    rprint(f"  Generated {len(resources)} total resources")

    # Count by type
    by_type: dict[str, int] = {}
    for r in resources:
        rt = r.get("resourceType", "Unknown")
        by_type[rt] = by_type.get(rt, 0) + 1

    table = Table(title="Generated Resources")
    table.add_column("Resource Type", style="cyan")
    table.add_column("Count", justify="right")
    for rt, count in sorted(by_type.items()):
        table.add_row(rt, str(count))
    rprint(table)

    # Write output
    if format == "bundle":
        bundle = {
            "resourceType": "Bundle",
            "id": str(uuid.uuid4()),
            "type": "collection",
            "total": len(resources),
            "entry": [{"fullUrl": f"urn:uuid:{r.get('id', uuid.uuid4())}", "resource": r} for r in resources],
        }
        with open(output, "w") as f:
            json.dump(bundle, f, indent=2 if pretty else None)
        rprint(f"[green]Written to {output}[/green] (Bundle format)")

    elif format == "ndjson":
        with open(output, "w") as f:
            for r in resources:
                f.write(json.dumps(r) + "\n")
        rprint(f"[green]Written to {output}[/green] (NDJSON format)")

    elif format == "files":
        # Create directory structure
        output_dir = output.parent / output.stem
        output_dir.mkdir(parents=True, exist_ok=True)

        for r in resources:
            rt = r.get("resourceType", "Unknown")
            rid = r.get("id", str(uuid.uuid4()))
            type_dir = output_dir / rt
            type_dir.mkdir(exist_ok=True)
            file_path = type_dir / f"{rid}.json"
            with open(file_path, "w") as f:
                json.dump(r, f, indent=2 if pretty else None)

        rprint(f"[green]Written to {output_dir}/[/green] (individual files)")

    else:
        rprint(f"[red]Unknown format: {format}[/red]")
        raise typer.Exit(1)


@app.command("generate-resource")
def generate_resource(
    resource_type: str = typer.Argument(None, help="Resource type to generate (e.g., Patient, Observation)"),
    output: Path = typer.Argument(None, help="Output JSON file path"),
    count: int = typer.Option(1, "--count", "-n", help="Number of resources to generate"),
    seed: int = typer.Option(None, "--seed", "-s", help="Random seed for reproducible data"),
    format: str = typer.Option("bundle", "--format", "-f", help="Output format: bundle, ndjson, or json"),
    pretty: bool = typer.Option(True, "--pretty/--no-pretty", help="Pretty-print JSON output"),
    list_types: bool = typer.Option(False, "--list", "-l", help="List available resource types"),
    patient_ref: str = typer.Option(None, "--patient-ref", help="Patient reference (e.g., Patient/123)"),
    practitioner_ref: str = typer.Option(None, "--practitioner-ref", help="Practitioner reference"),
    organization_ref: str = typer.Option(None, "--organization-ref", help="Organization reference"),
    encounter_ref: str = typer.Option(None, "--encounter-ref", help="Encounter reference"),
    hierarchy_depth: int = typer.Option(None, "--hierarchy-depth", help="For Location: generate hierarchy (1-6)"),
    load: bool = typer.Option(False, "--load", help="Load generated resources to FHIR server"),
    url: str = typer.Option("http://localhost:8080", "--url", "-u", help="FHIR server URL (used with --load)"),
) -> None:
    """Generate individual FHIR resources of a specific type.

    Examples:
        # List available resource types
        fhir server generate-resource --list

        # Generate 10 patients
        fhir server generate-resource Patient ./patients.json -n 10

        # Generate observations for a patient
        fhir server generate-resource Observation ./obs.json -n 5 --patient-ref Patient/123

        # Generate location hierarchy (Site → Building → Wing → Ward)
        fhir server generate-resource Location ./locations.json --hierarchy-depth 4

        # Generate with reproducible seed
        fhir server generate-resource Condition ./conditions.json -n 20 --seed 42

        # Generate and load to server in one step
        fhir server generate-resource Patient ./patients.json -n 10 --load --url http://localhost:8080
    """
    # Handle --list option
    if list_types:
        rprint("[bold]Available Resource Types:[/bold]")
        table = Table()
        table.add_column("Resource Type", style="cyan")
        table.add_column("Generator Class")
        for rt, gen_class in sorted(GENERATORS.items()):
            table.add_row(rt, gen_class.__name__)
        rprint(table)
        return

    # Validate arguments
    if not resource_type:
        rprint("[red]Error:[/red] Resource type is required. Use --list to see available types.")
        raise typer.Exit(1)

    if not output:
        rprint("[red]Error:[/red] Output file path is required.")
        raise typer.Exit(1)

    if resource_type not in GENERATORS:
        rprint(f"[red]Error:[/red] Unknown resource type '{resource_type}'")
        rprint("Use --list to see available types.")
        raise typer.Exit(1)

    # Get generator class and instantiate
    generator_class = GENERATORS[resource_type]
    generator = generator_class(seed=seed)

    rprint(f"[bold]Generating {resource_type} resource(s)...[/bold]")
    if seed:
        rprint(f"  Random seed: {seed}")

    resources: list[dict[str, Any]] = []

    # Special handling for Location hierarchy
    if resource_type == "Location" and hierarchy_depth:
        rprint(f"  Generating location hierarchy with depth {hierarchy_depth}")
        resources = generator.generate_hierarchy(
            managing_organization_ref=organization_ref,
            depth=hierarchy_depth,
        )
    else:
        # Build kwargs for generate method based on resource type
        kwargs: dict[str, Any] = {}

        # Add references if provided
        if patient_ref:
            kwargs["patient_ref"] = patient_ref
        if practitioner_ref:
            kwargs["practitioner_ref"] = practitioner_ref
        if organization_ref and resource_type == "Location":
            kwargs["managing_organization_ref"] = organization_ref
        elif organization_ref:
            kwargs["organization_ref"] = organization_ref
        if encounter_ref:
            kwargs["encounter_ref"] = encounter_ref

        # Generate resources
        for _ in range(count):
            resource = generator.generate(**kwargs)
            resources.append(resource)

    rprint(f"  Generated {len(resources)} resource(s)")

    # Write output using same logic as generate command
    _write_resources(resources, output, format, pretty)

    # Optionally load to server
    if load:
        _load_resources_to_server(resources, url)


def _load_resources_to_server(resources: list[dict[str, Any]], url: str) -> None:
    """Load resources to a FHIR server via batch transaction."""
    import uuid

    import httpx

    rprint(f"\n[bold]Loading {len(resources)} resource(s) to {url}...[/bold]")

    # Create batch bundle
    batch_bundle = {
        "resourceType": "Bundle",
        "id": str(uuid.uuid4()),
        "type": "batch",
        "entry": [
            {
                "resource": r,
                "request": {
                    "method": "POST",
                    "url": r.get("resourceType", ""),
                },
            }
            for r in resources
        ],
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                url,
                json=batch_bundle,
                headers={"Content-Type": "application/fhir+json"},
            )

        if response.status_code in (200, 201):
            result = response.json()
            success = sum(
                1 for e in result.get("entry", []) if e.get("response", {}).get("status", "").startswith("20")
            )
            rprint(f"[green]Loaded successfully:[/green] {success}/{len(resources)} resources created")
        else:
            rprint(f"[red]Load failed:[/red] {response.status_code}")
            rprint(response.text[:500])
            raise typer.Exit(1)

    except httpx.RequestError as e:
        rprint(f"[red]Connection error:[/red] {e}")
        raise typer.Exit(1)


def _write_resources(
    resources: list[dict[str, Any]],
    output: Path,
    format: str,
    pretty: bool,
) -> None:
    """Write resources to file in specified format."""
    import uuid

    if format == "bundle":
        bundle = {
            "resourceType": "Bundle",
            "id": str(uuid.uuid4()),
            "type": "collection",
            "total": len(resources),
            "entry": [{"fullUrl": f"urn:uuid:{r.get('id', uuid.uuid4())}", "resource": r} for r in resources],
        }
        with open(output, "w") as f:
            json.dump(bundle, f, indent=2 if pretty else None)
        rprint(f"[green]Written to {output}[/green] (Bundle format)")

    elif format == "ndjson":
        with open(output, "w") as f:
            for r in resources:
                f.write(json.dumps(r) + "\n")
        rprint(f"[green]Written to {output}[/green] (NDJSON format)")

    elif format == "json":
        # Single resource or array
        data = resources[0] if len(resources) == 1 else resources
        with open(output, "w") as f:
            json.dump(data, f, indent=2 if pretty else None)
        rprint(f"[green]Written to {output}[/green] (JSON format)")

    else:
        rprint(f"[red]Unknown format: {format}[/red]")
        raise typer.Exit(1)


@app.command("load")
def load(
    input_file: Path = typer.Argument(..., help="FHIR JSON file to load (Bundle or single resource)"),
    url: str = typer.Option("http://localhost:8080", "--url", "-u", help="FHIR server base URL"),
    batch: bool = typer.Option(True, "--batch/--no-batch", help="Use batch transaction for loading"),
) -> None:
    """Load FHIR resources from a file into a running server.

    Examples:
        # Load a bundle into the server
        fhir server load ./data.json

        # Load to a specific server
        fhir server load ./data.json --url http://fhir.example.com

        # Load resources individually (no batch)
        fhir server load ./data.json --no-batch
    """
    import uuid

    import httpx

    if not input_file.exists():
        rprint(f"[red]Error:[/red] File not found: {input_file}")
        raise typer.Exit(1)

    # Load the file
    with open(input_file) as f:
        data = json.load(f)

    # Extract resources
    resources: list[dict] = []
    if data.get("resourceType") == "Bundle":
        for entry in data.get("entry", []):
            if "resource" in entry:
                resources.append(entry["resource"])
    else:
        resources.append(data)

    rprint(f"[bold]Loading {len(resources)} resource(s) to {url}[/bold]")

    if batch and len(resources) > 1:
        # Create batch bundle
        batch_bundle = {
            "resourceType": "Bundle",
            "id": str(uuid.uuid4()),
            "type": "batch",
            "entry": [
                {
                    "resource": r,
                    "request": {
                        "method": "POST",
                        "url": r.get("resourceType", ""),
                    },
                }
                for r in resources
            ],
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    url,
                    json=batch_bundle,
                    headers={"Content-Type": "application/fhir+json"},
                )

            if response.status_code in (200, 201):
                result = response.json()
                success = sum(
                    1 for e in result.get("entry", []) if e.get("response", {}).get("status", "").startswith("20")
                )
                rprint(f"[green]Batch complete:[/green] {success}/{len(resources)} resources created")
            else:
                rprint(f"[red]Batch failed:[/red] {response.status_code}")
                rprint(response.text[:500])
                raise typer.Exit(1)

        except httpx.RequestError as e:
            rprint(f"[red]Connection error:[/red] {e}")
            raise typer.Exit(1)

    else:
        # Load individually
        success = 0
        errors = 0

        with httpx.Client(timeout=30.0) as client:
            for r in resources:
                resource_type = r.get("resourceType")
                if not resource_type:
                    errors += 1
                    continue

                try:
                    response = client.post(
                        f"{url}/{resource_type}",
                        json=r,
                        headers={"Content-Type": "application/fhir+json"},
                    )

                    if response.status_code in (200, 201):
                        success += 1
                    else:
                        errors += 1
                        rprint(f"[yellow]Failed {resource_type}:[/yellow] {response.status_code}")

                except httpx.RequestError as e:
                    errors += 1
                    rprint(f"[red]Error loading {resource_type}:[/red] {e}")

        rprint(f"[green]Complete:[/green] {success} success, {errors} errors")


@app.command("stats")
def stats(
    url: str = typer.Option("http://localhost:8080", "--url", "-u", help="FHIR server base URL"),
) -> None:
    """Show statistics for a running FHIR server.

    Example:
        fhir server stats --url http://localhost:8080
    """
    import httpx

    resource_types = [
        "Patient",
        "Practitioner",
        "Organization",
        "Encounter",
        "Condition",
        "Observation",
        "MedicationRequest",
        "Procedure",
        "ValueSet",
        "CodeSystem",
        "Library",
    ]

    rprint("[bold]FHIR Server Statistics[/bold]")
    rprint(f"URL: {url}")
    rprint()

    table = Table(title="Resource Counts")
    table.add_column("Resource Type", style="cyan")
    table.add_column("Count", justify="right")

    total = 0
    try:
        with httpx.Client(timeout=10.0) as client:
            for rt in resource_types:
                try:
                    response = client.get(
                        f"{url}/{rt}",
                        params={"_count": 0, "_total": "accurate"},
                        headers={"Accept": "application/fhir+json"},
                    )
                    if response.status_code == 200:
                        data = response.json()
                        count = data.get("total", 0)
                        if count > 0:
                            table.add_row(rt, str(count))
                            total += count
                except Exception:
                    pass

        table.add_row("─" * 20, "─" * 8)
        table.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]")
        rprint(table)

    except httpx.RequestError as e:
        rprint(f"[red]Connection error:[/red] {e}")
        raise typer.Exit(1)


@app.command("info")
def info(
    url: str = typer.Option("http://localhost:8080", "--url", "-u", help="FHIR server base URL"),
) -> None:
    """Show server capability statement information.

    Example:
        fhir server info --url http://localhost:8080
    """
    import httpx

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{url}/metadata",
                headers={"Accept": "application/fhir+json"},
            )

        if response.status_code != 200:
            rprint(f"[red]Error:[/red] Server returned {response.status_code}")
            raise typer.Exit(1)

        capability = response.json()

        rprint("[bold]FHIR Server Information[/bold]")
        rprint()
        rprint(f"  Name:         {capability.get('name', 'Unknown')}")
        rprint(f"  Publisher:    {capability.get('publisher', 'Unknown')}")
        rprint(f"  FHIR Version: {capability.get('fhirVersion', 'Unknown')}")
        rprint(f"  Status:       {capability.get('status', 'Unknown')}")
        rprint()

        # Show supported resources
        rest = capability.get("rest", [{}])[0]
        resources = rest.get("resource", [])

        if resources:
            table = Table(title="Supported Resources")
            table.add_column("Type", style="cyan")
            table.add_column("Interactions")
            table.add_column("Search Params")

            for r in resources:
                interactions = ", ".join(i.get("code", "") for i in r.get("interaction", []))
                search_params = len(r.get("searchParam", []))
                table.add_row(r.get("type", ""), interactions[:40], str(search_params))

            rprint(table)

    except httpx.RequestError as e:
        rprint(f"[red]Connection error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
