"""FastAPI application factory for FHIR server."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..config.settings import FHIRServerSettings
from ..generator import PatientRecordGenerator
from ..storage.fhir_store import FHIRStore
from .routes import create_router
from .ui_routes import create_ui_router

logger = logging.getLogger(__name__)

# Template and static directories
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
STATIC_DIR = Path(__file__).parent.parent / "static"


def create_app(
    settings: FHIRServerSettings | None = None,
    store: FHIRStore | None = None,
) -> FastAPI:
    """Create and configure the FHIR server FastAPI application.

    Args:
        settings: Server settings (uses defaults if None)
        store: FHIR data store (creates new if None)

    Returns:
        Configured FastAPI application
    """
    if settings is None:
        settings = FHIRServerSettings()

    if store is None:
        store = FHIRStore()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan handler."""
        # Startup
        logger.info("Starting FHIR server...")

        # Generate synthetic data if requested
        if settings.patients > 0:
            logger.info(f"Generating {settings.patients} synthetic patients...")
            generator = PatientRecordGenerator(seed=settings.seed)
            resources = generator.generate_population(settings.patients)

            for resource in resources:
                store.create(resource)

            logger.info(f"Generated {len(resources)} resources for {settings.patients} patients")

        # Store references in app state
        app.state.store = store
        app.state.settings = settings

        yield

        # Shutdown
        logger.info("Shutting down FHIR server...")

    # Determine docs URLs based on settings (docs at root, not under FHIR base path)
    api_base = settings.api_base_path.rstrip("/")
    docs_url = "/docs" if settings.enable_docs else None
    redoc_url = "/redoc" if settings.enable_docs else None
    openapi_url = "/openapi.json" if settings.enable_docs else None

    app = FastAPI(
        title=settings.server_name,
        description="FHIR R4 REST Server with synthetic data generation and Web UI",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )

    # Add CORS middleware
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Create and include FHIR API router at /baseR4
    base_url = f"http://{settings.host}:{settings.port}{api_base}"
    fhir_router = create_router(store=store, base_url=base_url)
    app.include_router(fhir_router, prefix=api_base)

    # CDS Hooks endpoints (per HL7 CDS Hooks specification)
    # NOTE: Must be defined BEFORE UI router to avoid being caught by /{resource_type}
    @app.get("/cds-services", tags=["CDS Hooks"])
    async def cds_services_discovery() -> dict[str, Any]:
        """CDS Hooks discovery endpoint.

        Returns the list of CDS services available on this server.
        """
        return {
            "services": [
                {
                    "hook": "patient-view",
                    "title": "Patient Summary",
                    "description": "Provides a summary of patient data when viewing a patient record",
                    "id": "patient-summary",
                    "prefetch": {
                        "patient": "Patient/{{context.patientId}}",
                        "conditions": "Condition?patient={{context.patientId}}&clinical-status=active",
                        "medications": "MedicationRequest?patient={{context.patientId}}&status=active",
                    },
                },
                {
                    "hook": "order-select",
                    "title": "Drug Interaction Check",
                    "description": "Checks for potential drug interactions when selecting medications",
                    "id": "drug-interaction-check",
                    "prefetch": {
                        "patient": "Patient/{{context.patientId}}",
                        "medications": "MedicationRequest?patient={{context.patientId}}&status=active",
                    },
                },
            ]
        }

    @app.post("/cds-services/{service_id}", tags=["CDS Hooks"])
    async def cds_services_invoke(service_id: str, request: Request) -> dict[str, Any]:
        """Invoke a CDS Hook service.

        Args:
            service_id: The ID of the CDS service to invoke
            request: The CDS Hooks request containing hook context and prefetch data
        """
        from datetime import date

        body = await request.json()
        context = body.get("context", {})
        prefetch = body.get("prefetch", {})

        # Get patient ID from context
        patient_id = context.get("patientId", "")

        cards = []

        if service_id == "patient-summary":
            # Try to get patient from prefetch, otherwise fetch from store
            patient = prefetch.get("patient", {})
            if not patient and patient_id:
                patient = store.read("Patient", patient_id) or {}

            # Extract patient info
            patient_name = "Unknown"
            if patient.get("name"):
                name = patient["name"][0] if patient["name"] else {}
                given = " ".join(name.get("given", []))
                family = name.get("family", "")
                patient_name = f"{given} {family}".strip() or "Unknown"

            # Calculate age
            age_str = ""
            if patient.get("birthDate"):
                try:
                    birth = date.fromisoformat(patient["birthDate"])
                    today = date.today()
                    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
                    age_str = f", {age}yo"
                except (ValueError, TypeError):
                    pass

            gender = patient.get("gender", "")
            gender_str = f" {gender.upper()[0]}" if gender else ""

            # Fetch conditions and medications from store
            conditions, _ = store.search("Condition", {"patient": f"Patient/{patient_id}"}, _count=10)
            medications, _ = store.search("MedicationRequest", {"patient": f"Patient/{patient_id}"}, _count=10)

            # Build detail
            detail_parts = [f"**Patient:** {patient_name}{age_str}{gender_str}"]

            if conditions:
                cond_names = []
                for c in conditions[:5]:
                    code = c.get("code", {})
                    text = code.get("text") or (
                        code.get("coding", [{}])[0].get("display") if code.get("coding") else None
                    )
                    if text:
                        cond_names.append(text)
                if cond_names:
                    detail_parts.append(f"\n**Active Conditions:** {', '.join(cond_names)}")

            if medications:
                med_names = []
                for m in medications[:5]:
                    med = m.get("medicationCodeableConcept", {})
                    text = med.get("text") or (med.get("coding", [{}])[0].get("display") if med.get("coding") else None)
                    if text:
                        med_names.append(text)
                if med_names:
                    detail_parts.append(f"\n**Active Medications:** {', '.join(med_names)}")

            if len(detail_parts) == 1:
                detail_parts.append("\nNo active conditions or medications on file.")

            cards.append(
                {
                    "uuid": "patient-summary-card",
                    "summary": f"Patient Summary: {patient_name}{age_str}{gender_str}",
                    "indicator": "info",
                    "detail": "\n".join(detail_parts),
                    "source": {
                        "label": "FHIR CQL Server",
                        "url": f"http://{settings.host}:{settings.port}",
                    },
                }
            )

        elif service_id == "drug-interaction-check":
            # Known drug interactions (simplified)
            INTERACTIONS = {
                ("warfarin", "aspirin"): {
                    "severity": "warning",
                    "message": "Increased bleeding risk when combining Warfarin with Aspirin",
                },
                ("warfarin", "ibuprofen"): {
                    "severity": "critical",
                    "message": "NSAIDs significantly increase bleeding risk with Warfarin",
                },
                ("metformin", "contrast"): {
                    "severity": "warning",
                    "message": "Hold Metformin before contrast procedures (lactic acidosis risk)",
                },
                ("lisinopril", "potassium"): {
                    "severity": "warning",
                    "message": "ACE inhibitors + potassium supplements may cause hyperkalemia",
                },
                ("simvastatin", "amiodarone"): {
                    "severity": "warning",
                    "message": "Increased risk of myopathy/rhabdomyolysis",
                },
                ("atorvastatin", "gemfibrozil"): {
                    "severity": "warning",
                    "message": "Increased risk of myopathy with statin + fibrate combination",
                },
                ("prednisone", "ibuprofen"): {
                    "severity": "warning",
                    "message": "Increased GI bleeding risk with corticosteroid + NSAID",
                },
                ("glipizide", "fluconazole"): {
                    "severity": "warning",
                    "message": "Fluconazole may increase hypoglycemic effect of sulfonylureas",
                },
            }

            # Get the medication being ordered from draftOrders
            draft_orders = context.get("draftOrders", {})
            new_med_name = ""
            if draft_orders.get("entry"):
                for entry in draft_orders["entry"]:
                    res = entry.get("resource", {})
                    if res.get("resourceType") == "MedicationRequest":
                        med_concept = res.get("medicationCodeableConcept", {})
                        new_med_name = med_concept.get("text", "").lower()
                        break

            # Get patient's current medications
            current_meds = []
            if patient_id:
                medications, _ = store.search("MedicationRequest", {"patient": f"Patient/{patient_id}"}, _count=20)
                for m in medications:
                    med = m.get("medicationCodeableConcept", {})
                    med_name = med.get("text") or (
                        med.get("coding", [{}])[0].get("display") if med.get("coding") else ""
                    )
                    if med_name:
                        current_meds.append(med_name.lower())

            # Check for interactions
            interactions_found = []
            if new_med_name:
                new_med_key = new_med_name.split()[0].lower()  # First word (drug name)
                for current in current_meds:
                    current_key = current.split()[0].lower()
                    # Check both orderings
                    pair1 = (new_med_key, current_key)
                    pair2 = (current_key, new_med_key)
                    if pair1 in INTERACTIONS:
                        interactions_found.append((current, INTERACTIONS[pair1]))
                    elif pair2 in INTERACTIONS:
                        interactions_found.append((current, INTERACTIONS[pair2]))

            if interactions_found:
                # Return warning cards for each interaction
                for current_med, interaction in interactions_found:
                    cards.append(
                        {
                            "uuid": f"interaction-{current_med[:10]}",
                            "summary": f"⚠️ Drug Interaction: {new_med_name.title()} + {current_med.title()}",
                            "indicator": interaction["severity"],
                            "detail": interaction["message"],
                            "source": {"label": "Drug Interaction Database"},
                        }
                    )
            else:
                # Show what was checked
                detail = f"Checked **{new_med_name.title() if new_med_name else 'selected medication'}** against "
                if current_meds:
                    detail += (
                        f"{len(current_meds)} current medication(s): {', '.join(m.title() for m in current_meds[:5])}"
                    )
                    if len(current_meds) > 5:
                        detail += f" (+{len(current_meds) - 5} more)"
                else:
                    detail += "no current medications on file"

                cards.append(
                    {
                        "uuid": "drug-check-card",
                        "summary": "✓ No drug interactions detected",
                        "indicator": "info",
                        "detail": detail,
                        "source": {"label": "Drug Interaction Database"},
                    }
                )

        else:
            return {"cards": [], "systemActions": []}

        return {"cards": cards, "systemActions": []}

    # Setup Web UI if enabled
    if settings.enable_ui:
        # Setup Jinja2 templates
        templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

        # Mount static files if directory exists
        if STATIC_DIR.exists():
            app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

        # Create and include UI router
        ui_router = create_ui_router(
            templates=templates,
            store=store,
            settings=settings,
        )

        # Mount UI at root or specified path
        ui_prefix = settings.ui_mount_path if settings.ui_mount_path else ""
        app.include_router(ui_router, prefix=ui_prefix)

        logger.info(f"Web UI enabled at {ui_prefix or '/'}")

    # API info endpoint (always at /api-info for discoverability)
    @app.get("/api-info", tags=["Info"])
    async def api_info() -> dict[str, Any]:
        """API information endpoint."""
        return {
            "name": settings.server_name,
            "fhirVersion": "4.0.1",
            "status": "running",
            "endpoints": {
                "fhir_api": api_base,
                "metadata": f"{api_base}/metadata",
                "docs": docs_url,
                "ui": settings.ui_mount_path or "/" if settings.enable_ui else None,
                "cds_hooks": "/cds-services",
            },
        }

    return app


def run_server(
    settings: FHIRServerSettings | None = None,
    store: FHIRStore | None = None,
) -> None:
    """Run the FHIR server with uvicorn.

    Args:
        settings: Server settings
        store: Optional pre-configured store
    """
    import uvicorn

    if settings is None:
        settings = FHIRServerSettings()

    app = create_app(settings=settings, store=store)

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
