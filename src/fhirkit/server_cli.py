"""FHIR Server CLI commands."""

import json
from pathlib import Path
from typing import Any

import typer
from rich import print as rprint
from rich.table import Table

from fhirkit.server.generator import (
    AdverseEventGenerator,
    AllergyIntoleranceGenerator,
    AppointmentGenerator,
    AuditEventGenerator,
    CarePlanGenerator,
    CareTeamGenerator,
    ClaimGenerator,
    ClinicalImpressionGenerator,
    CodeSystemGenerator,
    CommunicationGenerator,
    CompositionGenerator,
    ConceptMapGenerator,
    ConditionGenerator,
    ConsentGenerator,
    CoverageGenerator,
    DetectedIssueGenerator,
    DeviceGenerator,
    DiagnosticReportGenerator,
    DocumentReferenceGenerator,
    EncounterGenerator,
    ExplanationOfBenefitGenerator,
    FamilyMemberHistoryGenerator,
    FlagGenerator,
    GoalGenerator,
    GroupGenerator,
    HealthcareServiceGenerator,
    ImmunizationGenerator,
    LibraryGenerator,
    LocationGenerator,
    MeasureGenerator,
    MeasureReportGenerator,
    MediaGenerator,
    MedicationAdministrationGenerator,
    MedicationDispenseGenerator,
    MedicationGenerator,
    MedicationRequestGenerator,
    MedicationStatementGenerator,
    NutritionOrderGenerator,
    ObservationGenerator,
    OrganizationGenerator,
    PatientGenerator,
    PractitionerGenerator,
    PractitionerRoleGenerator,
    ProcedureGenerator,
    ProvenanceGenerator,
    QuestionnaireGenerator,
    QuestionnaireResponseGenerator,
    RelatedPersonGenerator,
    RiskAssessmentGenerator,
    ScheduleGenerator,
    ServiceRequestGenerator,
    SlotGenerator,
    SpecimenGenerator,
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
    "ClinicalImpression": ClinicalImpressionGenerator,
    "FamilyMemberHistory": FamilyMemberHistoryGenerator,
    # Medications
    "Medication": MedicationGenerator,
    "MedicationRequest": MedicationRequestGenerator,
    "MedicationAdministration": MedicationAdministrationGenerator,
    "MedicationStatement": MedicationStatementGenerator,
    "MedicationDispense": MedicationDispenseGenerator,
    # Care Management
    "CarePlan": CarePlanGenerator,
    "CareTeam": CareTeamGenerator,
    "Goal": GoalGenerator,
    "Task": TaskGenerator,
    # Scheduling
    "Appointment": AppointmentGenerator,
    "Schedule": ScheduleGenerator,
    "Slot": SlotGenerator,
    "HealthcareService": HealthcareServiceGenerator,
    # Financial
    "Coverage": CoverageGenerator,
    "Claim": ClaimGenerator,
    "ExplanationOfBenefit": ExplanationOfBenefitGenerator,
    # Devices
    "Device": DeviceGenerator,
    # Documents
    "ServiceRequest": ServiceRequestGenerator,
    "DocumentReference": DocumentReferenceGenerator,
    "Media": MediaGenerator,
    # Quality Measures
    "Measure": MeasureGenerator,
    "MeasureReport": MeasureReportGenerator,
    "Library": LibraryGenerator,
    # Terminology
    "ValueSet": ValueSetGenerator,
    "CodeSystem": CodeSystemGenerator,
    "ConceptMap": ConceptMapGenerator,
    # Documents (Clinical)
    "Composition": CompositionGenerator,
    # Groups
    "Group": GroupGenerator,
    # Forms & Consent
    "Questionnaire": QuestionnaireGenerator,
    "QuestionnaireResponse": QuestionnaireResponseGenerator,
    "Consent": ConsentGenerator,
    # Communication & Alerts
    "Communication": CommunicationGenerator,
    "Flag": FlagGenerator,
    # Diagnostics
    "Specimen": SpecimenGenerator,
    # Orders
    "NutritionOrder": NutritionOrderGenerator,
    # Clinical Decision Support
    "RiskAssessment": RiskAssessmentGenerator,
    "DetectedIssue": DetectedIssueGenerator,
    # Safety
    "AdverseEvent": AdverseEventGenerator,
    # Infrastructure
    "Provenance": ProvenanceGenerator,
    "AuditEvent": AuditEventGenerator,
}


@app.command("generate")
def generate(
    resource_type: str = typer.Argument(None, help="Resource type to generate (e.g., Patient, Observation)"),
    output: Path = typer.Argument(None, help="Output JSON file path (stdout if not specified)"),
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
    """Generate FHIR resources of a specific type.

    Examples:
        # List available resource types
        fhir server generate --list

        # Generate 10 patients to stdout
        fhir server generate Patient -n 10

        # Generate and pipe to jq
        fhir server generate Patient -n 3 | jq '.entry[0].resource'

        # Generate 10 patients to file
        fhir server generate Patient ./patients.json -n 10

        # Generate observations for a patient
        fhir server generate Observation ./obs.json -n 5 --patient-ref Patient/123

        # Generate location hierarchy (Site → Building → Wing → Ward)
        fhir server generate Location ./locations.json --hierarchy-depth 4

        # Generate with reproducible seed
        fhir server generate Condition ./conditions.json -n 20 --seed 42

        # Generate and load to server in one step
        fhir server generate Patient ./patients.json -n 10 --load --url http://localhost:8080
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

    if resource_type not in GENERATORS:
        rprint(f"[red]Error:[/red] Unknown resource type '{resource_type}'")
        rprint("Use --list to see available types.")
        raise typer.Exit(1)

    # Get generator class and instantiate
    generator_class = GENERATORS[resource_type]
    generator = generator_class(seed=seed)

    # Only print status messages when writing to file (not stdout)
    if output:
        rprint(f"[bold]Generating {resource_type} resource(s)...[/bold]")
        if seed:
            rprint(f"  Random seed: {seed}")

    resources: list[dict[str, Any]] = []

    # Special handling for Location hierarchy
    if resource_type == "Location" and hierarchy_depth:
        if output:
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

    if output:
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
    output: Path | None,
    format: str,
    pretty: bool,
) -> None:
    """Write resources to file or stdout in specified format."""
    import uuid

    if format == "bundle":
        bundle = {
            "resourceType": "Bundle",
            "id": str(uuid.uuid4()),
            "type": "collection",
            "total": len(resources),
            "entry": [{"fullUrl": f"urn:uuid:{r.get('id', uuid.uuid4())}", "resource": r} for r in resources],
        }
        if output is None:
            print(json.dumps(bundle, indent=2 if pretty else None))
        else:
            with open(output, "w") as f:
                json.dump(bundle, f, indent=2 if pretty else None)
            rprint(f"[green]Written to {output}[/green] (Bundle format)")

    elif format == "ndjson":
        if output is None:
            for r in resources:
                print(json.dumps(r))
        else:
            with open(output, "w") as f:
                for r in resources:
                    f.write(json.dumps(r) + "\n")
            rprint(f"[green]Written to {output}[/green] (NDJSON format)")

    elif format == "json":
        # Single resource or array
        data = resources[0] if len(resources) == 1 else resources
        if output is None:
            print(json.dumps(data, indent=2 if pretty else None))
        else:
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


@app.command("populate")
def populate(
    url: str = typer.Option("http://localhost:8080", "--url", "-u", help="FHIR server URL"),
    seed: int | None = typer.Option(None, "--seed", "-s", help="Random seed for reproducible data"),
    patients: int = typer.Option(3, "--patients", "-n", help="Number of patients to generate"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Generate but don't load to server"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Save generated resources to file"),
) -> None:
    """Populate a FHIR server with linked example resources of all types.

    Creates a complete dataset with:
    - Administrative resources (organizations, practitioners, locations)
    - Multiple patients with linked clinical data
    - Care management resources (care teams, care plans, goals)
    - Financial resources (coverage, claims)
    - Quality measures with linked reports

    Examples:
        # Populate local server with defaults (3 patients)
        fhir server populate

        # Populate with more patients
        fhir server populate --patients 10

        # Dry run - generate but don't load
        fhir server populate --dry-run --output ./population.json

        # Reproducible data
        fhir server populate --seed 42 --patients 5
    """
    from faker import Faker

    rprint("[bold]Generating linked FHIR resources...[/bold]")
    if seed:
        rprint(f"  Random seed: {seed}")

    # Initialize Faker with seed
    faker = Faker()
    if seed is not None:
        Faker.seed(seed)
        faker.seed_instance(seed)

    resources: list[dict[str, Any]] = []

    # Track created resources for linking
    created: dict[str, list[dict[str, Any]]] = {}

    def track(resource: dict[str, Any]) -> dict[str, Any]:
        """Track a resource and return it."""
        rt = resource.get("resourceType", "Unknown")
        if rt not in created:
            created[rt] = []
        created[rt].append(resource)
        resources.append(resource)
        return resource

    def ref(resource: dict[str, Any]) -> str:
        """Get reference string for a resource."""
        return f"{resource['resourceType']}/{resource['id']}"

    # ============================================================
    # TIER 1: Foundation (no dependencies)
    # ============================================================
    rprint("  [cyan]Tier 1:[/cyan] Foundation resources")

    # Organizations (hospital + insurance company)
    org_gen = OrganizationGenerator(faker, seed)
    hospital_org = track(org_gen.generate(name="General Hospital"))
    insurance_org = track(org_gen.generate(name="Blue Cross Insurance"))

    # Location hierarchy
    loc_gen = LocationGenerator(faker, seed)
    locations = loc_gen.generate_hierarchy(
        managing_organization_ref=ref(hospital_org),
        depth=4,  # Site → Building → Wing → Room
    )
    for loc in locations:
        track(loc)
    clinic_location = locations[-1] if locations else None

    # Practitioners
    prac_gen = PractitionerGenerator(faker, seed)
    practitioners = [track(prac_gen.generate()) for _ in range(3)]

    # Terminology resources
    vs_gen = ValueSetGenerator(faker, seed)
    cs_gen = CodeSystemGenerator(faker, seed)
    cm_gen = ConceptMapGenerator(faker, seed)
    track(vs_gen.generate())
    track(cs_gen.generate())
    # Generate all pre-defined ConceptMaps (SNOMED→ICD-10, LOINC→Local, RxNorm→NDC)
    for concept_map in cm_gen.generate_all_templates():
        track(concept_map)

    # Questionnaires (standalone forms)
    quest_gen = QuestionnaireGenerator(faker, seed)
    questionnaires = [
        track(quest_gen.generate(template="phq-9")),
        track(quest_gen.generate(template="gad-7")),
    ]

    # ============================================================
    # TIER 2: Administrative (depend on Tier 1)
    # ============================================================
    rprint("  [cyan]Tier 2:[/cyan] Administrative resources")

    # PractitionerRoles
    pr_gen = PractitionerRoleGenerator(faker, seed)
    for prac in practitioners:
        track(
            pr_gen.generate(
                practitioner_ref=ref(prac),
                organization_ref=ref(hospital_org),
                location_ref=ref(clinic_location) if clinic_location else None,
            )
        )

    # Devices
    dev_gen = DeviceGenerator(faker, seed)
    track(dev_gen.generate())

    # ============================================================
    # TIER 3: Scheduling (depend on Tier 1, 2)
    # ============================================================
    rprint("  [cyan]Tier 3:[/cyan] Scheduling resources")

    # Schedule
    sched_gen = ScheduleGenerator(faker, seed)
    schedule = track(
        sched_gen.generate(
            practitioner_ref=ref(practitioners[0]),
            location_ref=ref(clinic_location) if clinic_location else None,
        )
    )

    # Slots
    slot_gen = SlotGenerator(faker, seed)
    slots = [track(slot_gen.generate(schedule_ref=ref(schedule))) for _ in range(3)]

    # HealthcareService
    healthcare_svc_gen = HealthcareServiceGenerator(faker, seed)
    track(
        healthcare_svc_gen.generate(
            organization_ref=ref(hospital_org),
            location_ref=ref(clinic_location) if clinic_location else None,
        )
    )

    # ============================================================
    # Generate per-patient resources
    # ============================================================
    pat_gen = PatientGenerator(faker, seed)
    rel_gen = RelatedPersonGenerator(faker, seed)
    enc_gen = EncounterGenerator(faker, seed)
    cond_gen = ConditionGenerator(faker, seed)
    obs_gen = ObservationGenerator(faker, seed)
    allergy_gen = AllergyIntoleranceGenerator(faker, seed)
    imm_gen = ImmunizationGenerator(faker, seed)
    care_team_gen = CareTeamGenerator(faker, seed)
    care_plan_gen = CarePlanGenerator(faker, seed)
    goal_gen = GoalGenerator(faker, seed)
    task_gen = TaskGenerator(faker, seed)
    med_gen = MedicationGenerator(faker, seed)
    med_req_gen = MedicationRequestGenerator(faker, seed)
    med_admin_gen = MedicationAdministrationGenerator(faker, seed)
    med_stmt_gen = MedicationStatementGenerator(faker, seed)
    proc_gen = ProcedureGenerator(faker, seed)
    svc_req_gen = ServiceRequestGenerator(faker, seed)
    diag_gen = DiagnosticReportGenerator(faker, seed)
    doc_gen = DocumentReferenceGenerator(faker, seed)
    comp_gen = CompositionGenerator(faker, seed)
    appt_gen = AppointmentGenerator(faker, seed)
    cov_gen = CoverageGenerator(faker, seed)
    claim_gen = ClaimGenerator(faker, seed)
    eob_gen = ExplanationOfBenefitGenerator(faker, seed)
    consent_gen = ConsentGenerator(faker, seed)
    quest_resp_gen = QuestionnaireResponseGenerator(faker, seed)
    comm_gen = CommunicationGenerator(faker, seed)
    flag_gen = FlagGenerator(faker, seed)
    specimen_gen = SpecimenGenerator(faker, seed)
    family_hist_gen = FamilyMemberHistoryGenerator(faker, seed)
    clin_imp_gen = ClinicalImpressionGenerator(faker, seed)
    nutr_order_gen = NutritionOrderGenerator(faker, seed)
    med_disp_gen = MedicationDispenseGenerator(faker, seed)
    media_gen = MediaGenerator(faker, seed)
    risk_assess_gen = RiskAssessmentGenerator(faker, seed)
    detected_issue_gen = DetectedIssueGenerator(faker, seed)
    adverse_event_gen = AdverseEventGenerator(faker, seed)
    provenance_gen = ProvenanceGenerator(faker, seed)
    audit_event_gen = AuditEventGenerator(faker, seed)

    patient_refs: list[str] = []

    for i in range(patients):
        rprint(f"  [cyan]Patient {i + 1}/{patients}:[/cyan] Generating clinical data")

        # Patient
        patient = track(
            pat_gen.generate(
                practitioner_ref=ref(practitioners[0]),
                organization_ref=ref(hospital_org),
            )
        )
        patient_ref = ref(patient)
        patient_refs.append(patient_ref)

        # RelatedPerson
        track(rel_gen.generate(patient_ref=patient_ref))

        # Consent (privacy consent for patient)
        track(
            consent_gen.generate(
                patient_ref=patient_ref,
                organization_ref=ref(hospital_org),
                scope="patient-privacy",
            )
        )

        # ============================================================
        # TIER 4: Clinical Core
        # ============================================================

        # Encounters
        encounters = []
        for _ in range(faker.random_int(1, 3)):
            enc = track(
                enc_gen.generate(
                    patient_ref=patient_ref,
                    practitioner_ref=ref(faker.random_element(practitioners)),
                    organization_ref=ref(hospital_org),
                )
            )
            encounters.append(enc)

        # Per-encounter resources
        conditions_for_patient = []
        observations_for_patient = []

        for enc in encounters:
            enc_ref = ref(enc)

            # Conditions
            for _ in range(faker.random_int(1, 2)):
                cond = track(
                    cond_gen.generate(
                        patient_ref=patient_ref,
                        encounter_ref=enc_ref,
                    )
                )
                conditions_for_patient.append(cond)

            # Observations
            for _ in range(faker.random_int(2, 4)):
                obs = track(
                    obs_gen.generate(
                        patient_ref=patient_ref,
                        encounter_ref=enc_ref,
                    )
                )
                observations_for_patient.append(obs)

        # AllergyIntolerance
        track(
            allergy_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=ref(encounters[0]) if encounters else None,
                recorder_ref=ref(practitioners[0]),
            )
        )

        # Immunization
        track(
            imm_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=ref(encounters[0]) if encounters else None,
                performer_ref=ref(practitioners[0]),
            )
        )

        # ============================================================
        # TIER 5: Care Management
        # ============================================================

        # CareTeam
        track(
            care_team_gen.generate(
                patient_ref=patient_ref,
                practitioner_refs=[ref(p) for p in practitioners[:2]],
                encounter_ref=ref(encounters[0]) if encounters else None,
            )
        )

        # CarePlan (linked to conditions)
        track(
            care_plan_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=ref(encounters[0]) if encounters else None,
                author_ref=ref(practitioners[0]),
                condition_refs=[ref(c) for c in conditions_for_patient[:2]],
            )
        )

        # Goal
        track(goal_gen.generate(patient_ref=patient_ref))

        # Task
        track(
            task_gen.generate(
                patient_ref=patient_ref,
                owner_ref=ref(practitioners[0]),
            )
        )

        # QuestionnaireResponses (completed forms)
        for quest in questionnaires:
            track(
                quest_resp_gen.generate(
                    questionnaire_ref=f"Questionnaire/{quest['id']}",
                    questionnaire_template=quest.get("name", "").replace("_", "-"),
                    patient_ref=patient_ref,
                    encounter_ref=ref(encounters[0]) if encounters else None,
                    author_ref=patient_ref,
                )
            )

        # ============================================================
        # TIER 6: Treatment
        # ============================================================

        # Medication
        track(med_gen.generate())

        # MedicationRequest
        med_request = track(
            med_req_gen.generate(
                patient_ref=patient_ref,
                practitioner_ref=ref(practitioners[0]),
                encounter_ref=ref(encounters[0]) if encounters else None,
            )
        )

        # MedicationAdministration (record of med being given)
        track(
            med_admin_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=ref(encounters[0]) if encounters else None,
                practitioner_ref=ref(practitioners[0]),
                medication_request_ref=ref(med_request),
            )
        )

        # MedicationStatement (what patient reports taking)
        track(
            med_stmt_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=ref(encounters[0]) if encounters else None,
                medication_request_ref=ref(med_request),
            )
        )

        # MedicationDispense (pharmacy dispensing)
        track(
            med_disp_gen.generate(
                patient_ref=patient_ref,
                practitioner_ref=ref(practitioners[0]),
                medication_request_ref=ref(med_request),
                location_ref=ref(clinic_location) if clinic_location else None,
            )
        )

        # Procedure
        track(
            proc_gen.generate(
                patient_ref=patient_ref,
                practitioner_ref=ref(practitioners[0]),
                encounter_ref=ref(encounters[0]) if encounters else None,
            )
        )

        # ServiceRequest
        service_request = track(
            svc_req_gen.generate(
                patient_ref=patient_ref,
                requester_ref=ref(practitioners[0]),
                encounter_ref=ref(encounters[0]) if encounters else None,
            )
        )

        # Specimen (linked to service request)
        track(
            specimen_gen.generate(
                patient_ref=patient_ref,
                collector_ref=ref(practitioners[0]),
                service_request_ref=ref(service_request),
            )
        )

        # DiagnosticReport (linked to observations)
        track(
            diag_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=ref(encounters[0]) if encounters else None,
                performer_ref=ref(practitioners[0]),
                result_refs=[ref(o) for o in observations_for_patient[:3]],
            )
        )

        # DocumentReference
        track(doc_gen.generate(patient_ref=patient_ref))

        # Composition (clinical document structure)
        track(
            comp_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=ref(encounters[0]) if encounters else None,
                author_ref=ref(practitioners[0]),
                custodian_ref=ref(hospital_org),
                section_refs={
                    "11450-4": [ref(c) for c in conditions_for_patient],  # Problem list
                    "8716-3": [ref(o) for o in observations_for_patient[:3]],  # Vital signs
                },
            )
        )

        # Appointment (linked to slot)
        track(
            appt_gen.generate(
                patient_ref=patient_ref,
                practitioner_ref=ref(practitioners[0]),
                location_ref=ref(clinic_location) if clinic_location else None,
                slot_ref=ref(slots[i % len(slots)]) if slots else None,
            )
        )

        # ============================================================
        # TIER 6.5: Additional Clinical Resources
        # ============================================================

        # Flag (safety alerts)
        track(
            flag_gen.generate(
                patient_ref=patient_ref,
                author_ref=ref(practitioners[0]),
                encounter_ref=ref(encounters[0]) if encounters else None,
            )
        )

        # Communication (patient/provider messages)
        track(
            comm_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=ref(encounters[0]) if encounters else None,
                sender_ref=ref(practitioners[0]),
                recipient_ref=patient_ref,
            )
        )

        # FamilyMemberHistory
        for _ in range(faker.random_int(1, 3)):
            track(family_hist_gen.generate(patient_ref=patient_ref))

        # ClinicalImpression (linked to encounter and conditions)
        track(
            clin_imp_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=ref(encounters[0]) if encounters else None,
                assessor_ref=ref(practitioners[0]),
                condition_ref=ref(conditions_for_patient[0]) if conditions_for_patient else None,
            )
        )

        # NutritionOrder (diet orders)
        track(
            nutr_order_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=ref(encounters[0]) if encounters else None,
                orderer_ref=ref(practitioners[0]),
            )
        )

        # Media (clinical images/attachments)
        track(
            media_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=ref(encounters[0]) if encounters else None,
                operator_ref=ref(practitioners[0]),
            )
        )

        # RiskAssessment (clinical risk scoring)
        track(
            risk_assess_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=ref(encounters[0]) if encounters else None,
                performer_ref=ref(practitioners[0]),
                condition_ref=ref(conditions_for_patient[0]) if conditions_for_patient else None,
            )
        )

        # DetectedIssue (CDS alerts)
        track(
            detected_issue_gen.generate(
                patient_ref=patient_ref,
                author_ref=ref(practitioners[0]),
            )
        )

        # AdverseEvent (patient safety events) - only 20% of patients
        if faker.boolean(chance_of_getting_true=20):
            track(
                adverse_event_gen.generate(
                    patient_ref=patient_ref,
                    encounter_ref=ref(encounters[0]) if encounters else None,
                    practitioner_ref=ref(practitioners[0]),
                    location_ref=ref(clinic_location) if clinic_location else None,
                )
            )

        # Provenance (resource audit trail)
        track(
            provenance_gen.generate(
                target_ref=patient_ref,
                agent_ref=ref(practitioners[0]),
                organization_ref=ref(hospital_org),
            )
        )

        # AuditEvent (security logging)
        track(
            audit_event_gen.generate(
                agent_ref=ref(practitioners[0]),
                patient_ref=patient_ref,
            )
        )

        # ============================================================
        # TIER 7: Financial
        # ============================================================

        # Coverage
        coverage = track(
            cov_gen.generate(
                patient_ref=patient_ref,
                payor_ref=ref(insurance_org),
            )
        )

        # Claim
        claim = track(
            claim_gen.generate(
                patient_ref=patient_ref,
                provider_ref=ref(practitioners[0]),
                insurer_ref=ref(insurance_org),
                coverage_ref=ref(coverage),
            )
        )

        # ExplanationOfBenefit
        track(
            eob_gen.generate(
                patient_ref=patient_ref,
                provider_ref=ref(practitioners[0]),
                insurer_ref=ref(insurance_org),
                coverage_ref=ref(coverage),
                claim_ref=ref(claim),
            )
        )

    # ============================================================
    # TIER 8: Quality Measures
    # ============================================================
    rprint("  [cyan]Tier 8:[/cyan] Quality Measures")

    # Group (with patient members)
    grp_gen = GroupGenerator(faker, seed)
    track(
        grp_gen.generate(
            name="Diabetes Patient Cohort",
            group_type="person",
            actual=True,
            member_refs=patient_refs,
            managing_entity_ref=ref(hospital_org),
        )
    )

    # Library
    lib_gen = LibraryGenerator(faker, seed)
    library = track(
        lib_gen.generate(
            name="DiabetesMeasuresLibrary",
            include_cql=True,
        )
    )

    # Measure (linked to library)
    measure_gen = MeasureGenerator(faker, seed)
    measure = track(
        measure_gen.generate(
            name="DiabetesHbA1cControl",
            title="Diabetes: HbA1c Poor Control",
            library_ref=f"Library/{library['id']}",
        )
    )

    # MeasureReport (one per patient + summary)
    mr_gen = MeasureReportGenerator(faker, seed)

    # Individual reports
    for patient_ref in patient_refs:
        track(
            mr_gen.generate(
                measure_ref=f"Measure/{measure['id']}",
                patient_ref=patient_ref,
                reporter_ref=ref(hospital_org),
                report_type="individual",
            )
        )

    # Summary report
    track(
        mr_gen.generate(
            measure_ref=f"Measure/{measure['id']}",
            reporter_ref=ref(hospital_org),
            report_type="summary",
        )
    )

    # ============================================================
    # Summary
    # ============================================================
    rprint(f"\n[bold]Generated {len(resources)} total resources[/bold]")

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
    table.add_row("─" * 20, "─" * 8)
    table.add_row("[bold]Total[/bold]", f"[bold]{len(resources)}[/bold]")
    rprint(table)

    # Save to file if requested
    if output:
        _write_resources(resources, output, "bundle", True)

    # Load to server unless dry run
    if not dry_run:
        _load_resources_to_server(resources, url)
    else:
        rprint("[yellow]Dry run - resources not loaded to server[/yellow]")


if __name__ == "__main__":
    app()
