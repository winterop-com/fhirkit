"""FHIR REST API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import JSONResponse

from ..models.responses import (
    Bundle,
    BundleEntry,
    BundleEntryRequest,
    BundleLink,
    CapabilityStatement,
    OperationOutcome,
    OperationOutcomeIssue,
)
from ..storage.fhir_store import FHIRStore

# FHIR content type
FHIR_JSON = "application/fhir+json"

# Supported resource types
SUPPORTED_TYPES = [
    # Administrative
    "Patient",
    "Practitioner",
    "PractitionerRole",
    "Organization",
    "Location",
    "RelatedPerson",
    # Clinical
    "Encounter",
    "Condition",
    "Observation",
    "Procedure",
    "DiagnosticReport",
    "AllergyIntolerance",
    "Immunization",
    # Medications
    "Medication",
    "MedicationRequest",
    # Care Management
    "CarePlan",
    "CareTeam",
    "Goal",
    "Task",
    # Scheduling
    "Appointment",
    "Schedule",
    "Slot",
    # Financial
    "Coverage",
    "Claim",
    "ExplanationOfBenefit",
    # Devices
    "Device",
    # Documents & Binary
    "ServiceRequest",
    "DocumentReference",
    "Binary",
    # Quality Measures
    "Measure",
    "MeasureReport",
    "Library",
    # Terminology
    "ValueSet",
    "CodeSystem",
    "ConceptMap",
    # Documents (Clinical)
    "Composition",
    # Forms
    "Questionnaire",
    "QuestionnaireResponse",
    # Groups
    "Group",
]

# Summary elements per resource type (per FHIR spec)
SUMMARY_ELEMENTS: dict[str, list[str]] = {
    # Administrative
    "Patient": ["identifier", "active", "name", "telecom", "gender", "birthDate", "address"],
    "Practitioner": ["identifier", "active", "name", "telecom", "address"],
    "PractitionerRole": ["identifier", "active", "practitioner", "organization", "code", "specialty"],
    "Organization": ["identifier", "active", "name", "type", "telecom", "address"],
    "Location": ["identifier", "status", "name", "type", "telecom", "address"],
    "RelatedPerson": ["identifier", "active", "patient", "relationship", "name"],
    # Clinical
    "Encounter": ["identifier", "status", "class", "type", "subject", "period"],
    "Condition": ["identifier", "clinicalStatus", "verificationStatus", "code", "subject", "onsetDateTime"],
    "Observation": ["identifier", "status", "category", "code", "subject", "effectiveDateTime", "valueQuantity"],
    "Procedure": ["identifier", "status", "code", "subject", "performedDateTime", "performedPeriod"],
    "DiagnosticReport": ["identifier", "status", "category", "code", "subject", "effectiveDateTime", "issued"],
    "AllergyIntolerance": ["identifier", "clinicalStatus", "verificationStatus", "code", "patient", "onsetDateTime"],
    "Immunization": ["identifier", "status", "vaccineCode", "patient", "occurrenceDateTime"],
    # Medications
    "Medication": ["identifier", "code", "status"],
    "MedicationRequest": ["identifier", "status", "intent", "medicationCodeableConcept", "subject", "authoredOn"],
    # Care Management
    "CarePlan": ["identifier", "status", "intent", "category", "subject", "period"],
    "CareTeam": ["identifier", "status", "name", "subject", "period"],
    "Goal": ["identifier", "lifecycleStatus", "category", "description", "subject"],
    "Task": ["identifier", "status", "intent", "code", "focus", "for", "authoredOn"],
    # Scheduling
    "Appointment": ["identifier", "status", "serviceType", "start", "end", "participant"],
    "Schedule": ["identifier", "active", "serviceType", "actor", "planningHorizon"],
    "Slot": ["identifier", "status", "schedule", "start", "end"],
    # Financial
    "Coverage": ["identifier", "status", "type", "beneficiary", "payor", "period"],
    "Claim": ["identifier", "status", "type", "use", "patient", "created"],
    "ExplanationOfBenefit": ["identifier", "status", "type", "use", "patient", "created", "outcome"],
    # Devices
    "Device": ["identifier", "status", "type", "patient", "manufacturer", "serialNumber"],
    # Documents
    "ServiceRequest": ["identifier", "status", "intent", "code", "subject", "authoredOn"],
    "DocumentReference": ["identifier", "status", "type", "subject", "date", "author"],
    # Quality Measures
    "Measure": ["identifier", "url", "name", "status", "title", "date"],
    "MeasureReport": ["identifier", "status", "type", "measure", "subject", "date"],
    "Library": ["identifier", "url", "name", "status", "title", "date"],
    # Terminology
    "ValueSet": ["identifier", "url", "name", "status", "title"],
    "CodeSystem": ["identifier", "url", "name", "status", "title"],
    "ConceptMap": ["identifier", "url", "name", "status", "title", "sourceUri", "targetUri"],
    # Documents (Clinical)
    "Composition": ["identifier", "status", "type", "subject", "date", "author", "title"],
    # Forms
    "Questionnaire": ["identifier", "url", "name", "status", "title", "date", "publisher"],
    "QuestionnaireResponse": ["identifier", "status", "questionnaire", "subject", "authored", "author"],
    # Groups
    "Group": ["identifier", "active", "type", "actual", "name", "quantity"],
}


def filter_elements(resource: dict[str, Any], elements: list[str]) -> dict[str, Any]:
    """Filter resource to only include specified elements.

    Always includes: resourceType, id, meta (per FHIR spec).

    Args:
        resource: The FHIR resource to filter
        elements: List of element names to include

    Returns:
        Filtered resource with only specified elements
    """
    result: dict[str, Any] = {
        "resourceType": resource.get("resourceType"),
    }
    if "id" in resource:
        result["id"] = resource["id"]
    if "meta" in resource:
        result["meta"] = resource["meta"]

    for element in elements:
        if element in resource:
            result[element] = resource[element]

    return result


def filter_summary(resource: dict[str, Any], summary_type: str) -> dict[str, Any]:
    """Filter resource based on _summary type.

    Args:
        resource: The FHIR resource to filter
        summary_type: Summary type (true, text, data, false)

    Returns:
        Filtered resource based on summary type
    """
    if summary_type == "false":
        return resource

    resource_type = resource.get("resourceType", "")

    if summary_type == "true":
        elements = SUMMARY_ELEMENTS.get(resource_type, [])
        return filter_elements(resource, elements)

    if summary_type == "text":
        result: dict[str, Any] = {
            "resourceType": resource.get("resourceType"),
        }
        if "id" in resource:
            result["id"] = resource["id"]
        if "meta" in resource:
            result["meta"] = resource["meta"]
        if "text" in resource:
            result["text"] = resource["text"]
        return result

    if summary_type == "data":
        result = dict(resource)
        result.pop("text", None)
        return result

    return resource


def create_router(store: FHIRStore, base_url: str = "") -> APIRouter:
    """Create FHIR API router.

    Args:
        store: The FHIR data store
        base_url: Base URL for the server

    Returns:
        Configured APIRouter
    """
    router = APIRouter()

    def get_base_url(request: Request) -> str:
        """Get base URL from request or config."""
        if base_url:
            return base_url.rstrip("/")
        return str(request.base_url).rstrip("/")

    # =========================================================================
    # Capability Statement (metadata)
    # =========================================================================

    @router.get("/metadata", tags=["Capability"])
    async def get_metadata(request: Request) -> Response:
        """Return the CapabilityStatement for this server.

        This endpoint describes the server's capabilities including:
        - Supported resource types
        - Supported interactions (read, search, create, update, delete)
        - Supported search parameters
        - Server information
        """
        capability = CapabilityStatement.default(base_url=get_base_url(request))
        return JSONResponse(
            content=capability.model_dump(exclude_none=True),
            media_type=FHIR_JSON,
        )

    @router.get("/.well-known/smart-configuration", tags=["Capability"])
    async def get_smart_config(request: Request) -> Response:
        """Return SMART on FHIR configuration.

        Basic SMART configuration for discovery.
        """
        config = {
            "issuer": get_base_url(request),
            "authorization_endpoint": f"{get_base_url(request)}/auth/authorize",
            "token_endpoint": f"{get_base_url(request)}/auth/token",
            "capabilities": [
                "launch-standalone",
                "client-public",
                "client-confidential-symmetric",
                "context-standalone-patient",
                "permission-offline",
                "permission-patient",
            ],
        }
        return JSONResponse(content=config, media_type="application/json")

    # =========================================================================
    # Schema Endpoints (for UI form generation)
    # =========================================================================

    @router.get("/schema", tags=["Schema"])
    async def list_schemas() -> Response:
        """List all available resource schemas.

        Returns a list of resource types that have JSON Schema definitions.
        """
        from ..models import RESOURCE_MODELS

        return JSONResponse(
            content={
                "schemas": list(RESOURCE_MODELS.keys()),
                "count": len(RESOURCE_MODELS),
            },
            media_type="application/json",
        )

    @router.get("/schema/{resource_type}", tags=["Schema"])
    async def get_schema(resource_type: str) -> Response:
        """Get JSON Schema for a resource type.

        Returns the Pydantic-generated JSON Schema for form generation.
        """
        from ..models import get_resource_schema

        schema = get_resource_schema(resource_type)
        if schema is None:
            # Return a minimal schema for unsupported types
            schema = {
                "type": "object",
                "properties": {
                    "resourceType": {"type": "string", "const": resource_type},
                    "id": {"type": "string"},
                },
                "required": ["resourceType"],
            }

        return JSONResponse(content=schema, media_type="application/json")

    # =========================================================================
    # FHIRPath and CQL Evaluation Operations
    # =========================================================================

    @router.post("/$fhirpath", tags=["Operations"])
    async def evaluate_fhirpath(request: Request) -> Response:
        """Evaluate a FHIRPath expression against a FHIR resource.

        Request body:
        {
            "expression": "Patient.name.given",
            "resource": { ... }  // FHIR resource JSON
            // OR
            "resourceType": "Patient",
            "resourceId": "123"  // Load from store
        }

        Returns:
        {
            "success": true,
            "result": [...],
            "executionTime": "5ms"
        }
        """
        import time

        from fhirkit.engine.fhirpath import FHIRPathEvaluator

        try:
            body = await request.json()
        except Exception:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Invalid JSON in request body"},
            )

        expression = body.get("expression")
        if not expression:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Missing 'expression' field"},
            )

        # Get resource from body or load from store
        resource = body.get("resource")
        if not resource:
            resource_type = body.get("resourceType")
            resource_id = body.get("resourceId")
            if resource_type and resource_id:
                resource = store.read(resource_type, resource_id)
                if not resource:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": False,
                            "error": f"Resource {resource_type}/{resource_id} not found",
                        },
                    )
            else:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "error": "Missing 'resource' or 'resourceType'/'resourceId'",
                    },
                )

        start_time = time.perf_counter()
        try:
            evaluator = FHIRPathEvaluator()
            result = evaluator.evaluate(expression, resource)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            return JSONResponse(
                content={
                    "success": True,
                    "result": result,
                    "executionTime": f"{elapsed_ms:.1f}ms",
                }
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": str(e),
                    "executionTime": f"{elapsed_ms:.1f}ms",
                },
            )

    @router.post("/$cql", tags=["Operations"])
    async def evaluate_cql(request: Request) -> Response:
        """Evaluate CQL code or a Library resource.

        Request body:
        {
            "code": "define X: 1 + 1",  // Inline CQL code
            // OR
            "library": "Library/123",   // Reference to Library resource
            "definitions": ["X", "Y"],  // Optional: specific definitions to evaluate
            "subject": "Patient/456"    // Optional: patient context
        }

        Returns:
        {
            "success": true,
            "results": {
                "X": 2,
                "Y": [...]
            },
            "executionTime": "10ms"
        }
        """
        import base64
        import time

        from fhirkit.engine.cql import CQLEvaluator

        try:
            body = await request.json()
        except Exception:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Invalid JSON in request body"},
            )

        code = body.get("code")
        library_ref = body.get("library")
        definitions = body.get("definitions")  # Optional list of definitions to evaluate
        subject_ref = body.get("subject")  # Optional patient context

        if not code and not library_ref:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Missing 'code' or 'library' field"},
            )

        # If library reference provided, load CQL from Library resource
        if library_ref and not code:
            # Parse reference like "Library/123" or just "123"
            if "/" in library_ref:
                _, library_id = library_ref.split("/", 1)
            else:
                library_id = library_ref

            library_resource = store.read("Library", library_id)
            if not library_resource:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": f"Library {library_id} not found"},
                )

            # Extract CQL from Library content
            content_list = library_resource.get("content", [])
            for content in content_list:
                content_type = content.get("contentType", "")
                if "cql" in content_type.lower():
                    data = content.get("data")
                    if data:
                        code = base64.b64decode(data).decode("utf-8")
                        break

            if not code:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "No CQL content found in Library"},
                )

        # Load subject resource if provided
        subject_resource = None
        if subject_ref:
            if "/" in subject_ref:
                subj_type, subj_id = subject_ref.split("/", 1)
            else:
                subj_type, subj_id = "Patient", subject_ref
            subject_resource = store.read(subj_type, subj_id)

        start_time = time.perf_counter()
        try:
            evaluator = CQLEvaluator(data_source=store)
            library = evaluator.compile(code)

            # Determine which definitions to evaluate
            defs_to_eval = definitions if definitions else list(library.definitions.keys())

            results = {}
            for def_name in defs_to_eval:
                if def_name in library.definitions:
                    try:
                        result = evaluator.evaluate_definition(
                            def_name,
                            resource=subject_resource,
                            library=library,
                        )
                        # Convert result to JSON-serializable format
                        results[def_name] = _serialize_cql_result(result)
                    except Exception as e:
                        results[def_name] = {"error": str(e)}

            elapsed_ms = (time.perf_counter() - start_time) * 1000

            return JSONResponse(
                content={
                    "success": True,
                    "results": results,
                    "definitions": list(library.definitions.keys()),
                    "executionTime": f"{elapsed_ms:.1f}ms",
                }
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": str(e),
                    "executionTime": f"{elapsed_ms:.1f}ms",
                },
            )

    def _serialize_cql_result(value: Any) -> Any:
        """Convert CQL result to JSON-serializable format."""
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, list):
            return [_serialize_cql_result(v) for v in value]
        if isinstance(value, dict):
            return {k: _serialize_cql_result(v) for k, v in value.items()}
        # For custom types, try to get dict representation
        if hasattr(value, "__dict__"):
            return _serialize_cql_result(vars(value))
        return str(value)

    # =========================================================================
    # CQL Examples API
    # =========================================================================

    @router.get("/cql/examples", tags=["CQL"])
    async def list_cql_examples() -> Response:
        """List all available CQL examples.

        Returns the manifest with all example metadata.
        """
        from fhirkit.server.cql_examples import load_manifest

        manifest = load_manifest()
        return JSONResponse(content=manifest)

    @router.get("/cql/examples/{example_id}", tags=["CQL"])
    async def get_cql_example(example_id: str) -> Response:
        """Get a specific CQL example by ID.

        Returns the example with its CQL code loaded.
        """
        from fhirkit.server.cql_examples import load_example

        example = load_example(example_id)
        if example is None:
            return JSONResponse(
                status_code=404,
                content={"error": f"Example '{example_id}' not found"},
            )
        return JSONResponse(content=example)

    # =========================================================================
    # Bulk Data Export Operations
    # =========================================================================

    @router.get("/$export", tags=["Bulk Data"])
    async def system_export(
        request: Request,
        _type: str | None = Query(default=None, alias="_type"),
        _since: str | None = Query(default=None, alias="_since"),
    ) -> Response:
        """Initiate system-level bulk data export.

        Exports all resources from the server.

        Headers required:
        - Accept: application/fhir+ndjson
        - Prefer: respond-async

        Parameters:
            _type: Comma-separated list of resource types to export
            _since: Only export resources updated after this datetime

        Returns:
            202 Accepted with Content-Location header for status polling
        """
        from .bulk import ALL_EXPORT_TYPES, create_export_job, run_export

        # Validate headers
        prefer = request.headers.get("Prefer", "")
        if "respond-async" not in prefer:
            outcome = OperationOutcome.error(
                "Bulk export requires 'Prefer: respond-async' header",
                code="required",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Parse resource types
        resource_types = _type.split(",") if _type else ALL_EXPORT_TYPES

        # Parse since datetime
        since = None
        if _since:
            try:
                from datetime import datetime

                since = datetime.fromisoformat(_since.replace("Z", "+00:00"))
            except ValueError:
                outcome = OperationOutcome.error(
                    f"Invalid _since datetime: {_since}",
                    code="invalid",
                )
                return JSONResponse(
                    content=outcome.model_dump(exclude_none=True),
                    status_code=400,
                    media_type=FHIR_JSON,
                )

        # Create and start export job
        job = create_export_job(resource_types, patient_ids=None, since=since)
        # Run export immediately for in-memory store (fast)
        await run_export(job, store)

        return Response(
            status_code=202,
            headers={
                "Content-Location": f"{get_base_url(request)}/bulk-status/{job.id}",
            },
        )

    @router.get("/Patient/$export", tags=["Bulk Data"])
    async def patient_export(
        request: Request,
        _type: str | None = Query(default=None, alias="_type"),
        _since: str | None = Query(default=None, alias="_since"),
    ) -> Response:
        """Initiate patient-level bulk data export.

        Exports Patient resources and related clinical data.

        Headers required:
        - Accept: application/fhir+ndjson
        - Prefer: respond-async

        Parameters:
            _type: Comma-separated list of resource types to export
            _since: Only export resources updated after this datetime

        Returns:
            202 Accepted with Content-Location header for status polling
        """
        from .bulk import PATIENT_EXPORT_TYPES, create_export_job, run_export

        # Validate headers
        prefer = request.headers.get("Prefer", "")
        if "respond-async" not in prefer:
            outcome = OperationOutcome.error(
                "Bulk export requires 'Prefer: respond-async' header",
                code="required",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Parse resource types
        resource_types = _type.split(",") if _type else PATIENT_EXPORT_TYPES

        # Parse since datetime
        since = None
        if _since:
            try:
                from datetime import datetime

                since = datetime.fromisoformat(_since.replace("Z", "+00:00"))
            except ValueError:
                outcome = OperationOutcome.error(
                    f"Invalid _since datetime: {_since}",
                    code="invalid",
                )
                return JSONResponse(
                    content=outcome.model_dump(exclude_none=True),
                    status_code=400,
                    media_type=FHIR_JSON,
                )

        # Create and start export job
        job = create_export_job(resource_types, patient_ids=None, since=since)
        # Run export immediately for in-memory store (fast)
        await run_export(job, store)

        return Response(
            status_code=202,
            headers={
                "Content-Location": f"{get_base_url(request)}/bulk-status/{job.id}",
            },
        )

    @router.get("/Group/{group_id}/$export", tags=["Bulk Data"])
    async def group_export(
        request: Request,
        group_id: str,
        _type: str | None = Query(default=None, alias="_type"),
        _since: str | None = Query(default=None, alias="_since"),
    ) -> Response:
        """Initiate group-level bulk data export.

        Exports resources for all patients in the specified Group.

        Headers required:
        - Accept: application/fhir+ndjson
        - Prefer: respond-async

        Parameters:
            group_id: The Group resource ID
            _type: Comma-separated list of resource types to export
            _since: Only export resources updated after this datetime

        Returns:
            202 Accepted with Content-Location header for status polling
        """
        from .bulk import PATIENT_EXPORT_TYPES, create_export_job, run_export

        # Validate headers
        prefer = request.headers.get("Prefer", "")
        if "respond-async" not in prefer:
            outcome = OperationOutcome.error(
                "Bulk export requires 'Prefer: respond-async' header",
                code="required",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Get the Group and extract patient IDs
        group = store.read("Group", group_id)
        if not group:
            outcome = OperationOutcome.not_found("Group", group_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        patient_ids = []
        for member in group.get("member", []):
            ref = member.get("entity", {}).get("reference", "")
            if ref.startswith("Patient/"):
                patient_ids.append(ref.split("/")[1])

        if not patient_ids:
            outcome = OperationOutcome.error(
                f"Group/{group_id} has no Patient members",
                code="not-found",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=422,
                media_type=FHIR_JSON,
            )

        # Parse resource types
        resource_types = _type.split(",") if _type else PATIENT_EXPORT_TYPES

        # Parse since datetime
        since = None
        if _since:
            try:
                from datetime import datetime

                since = datetime.fromisoformat(_since.replace("Z", "+00:00"))
            except ValueError:
                outcome = OperationOutcome.error(
                    f"Invalid _since datetime: {_since}",
                    code="invalid",
                )
                return JSONResponse(
                    content=outcome.model_dump(exclude_none=True),
                    status_code=400,
                    media_type=FHIR_JSON,
                )

        # Create and start export job
        job = create_export_job(resource_types, patient_ids=patient_ids, since=since)
        # Run export immediately for in-memory store (fast)
        await run_export(job, store)

        return Response(
            status_code=202,
            headers={
                "Content-Location": f"{get_base_url(request)}/bulk-status/{job.id}",
            },
        )

    @router.get("/bulk-status/{job_id}", tags=["Bulk Data"])
    async def export_status(
        request: Request,
        job_id: str,
    ) -> Response:
        """Check the status of a bulk export job.

        Returns:
            - 202 Accepted if in progress (with X-Progress header)
            - 200 OK with output manifest if complete
            - 500 Error if job failed
        """
        from .bulk import get_export_job

        job = get_export_job(job_id)
        if not job:
            outcome = OperationOutcome.error(
                f"Export job {job_id} not found",
                code="not-found",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        if job.status == "error":
            outcome = OperationOutcome.error(
                f"Export job failed: {job.error}",
                code="exception",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=500,
                media_type=FHIR_JSON,
            )

        if job.status in ("accepted", "in-progress"):
            return Response(
                status_code=202,
                headers={
                    "X-Progress": f"{job.progress}%",
                    "Retry-After": "1",
                },
            )

        # Job is complete - return manifest
        base = get_base_url(request)
        output = []
        for resource_type, resources in job.output_files.items():
            if resources:
                output.append(
                    {
                        "type": resource_type,
                        "url": f"{base}/bulk-output/{job.id}/{resource_type}.ndjson",
                        "count": len(resources),
                    }
                )

        manifest = {
            "transactionTime": job.request_time.isoformat() + "Z",
            "request": f"{base}/$export",
            "requiresAccessToken": False,
            "output": output,
            "error": [],
        }

        return JSONResponse(
            content=manifest,
            media_type="application/json",
        )

    @router.get("/bulk-output/{job_id}/{filename}", tags=["Bulk Data"])
    async def export_output(
        request: Request,
        job_id: str,
        filename: str,
    ) -> Response:
        """Download bulk export output file.

        Returns NDJSON formatted data for the specified resource type.

        Parameters:
            job_id: The export job ID
            filename: The output file name (e.g., "Patient.ndjson")
        """
        from .bulk import get_export_job, resources_to_ndjson

        job = get_export_job(job_id)
        if not job:
            outcome = OperationOutcome.error(
                f"Export job {job_id} not found",
                code="not-found",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        if job.status != "complete":
            outcome = OperationOutcome.error(
                "Export job is not yet complete",
                code="transient",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Extract resource type from filename
        if not filename.endswith(".ndjson"):
            outcome = OperationOutcome.error(
                "Invalid filename format. Expected {type}.ndjson",
                code="invalid",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        resource_type = filename.replace(".ndjson", "")
        resources = job.output_files.get(resource_type)

        if resources is None:
            outcome = OperationOutcome.error(
                f"No output file for resource type: {resource_type}",
                code="not-found",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        ndjson = resources_to_ndjson(resources)

        return Response(
            content=ndjson,
            status_code=200,
            media_type="application/fhir+ndjson",
        )

    @router.delete("/bulk-status/{job_id}", tags=["Bulk Data"])
    async def delete_export(
        request: Request,
        job_id: str,
    ) -> Response:
        """Delete/cancel a bulk export job.

        Removes the export job and any generated output files.

        Returns:
            204 No Content on success
        """
        from .bulk import delete_export_job

        if delete_export_job(job_id):
            return Response(status_code=204)

        outcome = OperationOutcome.error(
            f"Export job {job_id} not found",
            code="not-found",
        )
        return JSONResponse(
            content=outcome.model_dump(exclude_none=True),
            status_code=404,
            media_type=FHIR_JSON,
        )

    # =========================================================================
    # Patient Operations
    # =========================================================================

    @router.get("/Patient/{patient_id}/$everything", tags=["Operations"])
    async def patient_everything(
        request: Request,
        patient_id: str,
        _count: int = Query(default=100, ge=1, le=1000, alias="_count"),
        _offset: int = Query(default=0, ge=0, alias="_offset"),
        _elements: str | None = Query(default=None, alias="_elements"),
        _summary: str | None = Query(default=None, alias="_summary"),
    ) -> Response:
        """Return all resources related to a patient.

        Returns a searchset Bundle containing the Patient and all related
        resources (Conditions, Observations, MedicationRequests, Encounters,
        Procedures, etc.) that reference the patient.

        Parameters:
            patient_id: The patient ID
            _count: Maximum number of resources per page (default 100)
            _offset: Pagination offset (default 0)
            _elements: Comma-separated list of elements to include
            _summary: Return summary view (true, text, data, count, false)
        """
        from .compartments import PATIENT_COMPARTMENT, get_patient_reference_paths, get_reference_from_path

        # Get the patient
        patient = store.read("Patient", patient_id)
        if patient is None:
            outcome = OperationOutcome.not_found("Patient", patient_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        # Collect all related resources
        all_resources: list[dict[str, Any]] = [patient]
        patient_ref = f"Patient/{patient_id}"

        for resource_type in PATIENT_COMPARTMENT:
            if resource_type not in SUPPORTED_TYPES:
                continue

            ref_paths = get_patient_reference_paths(resource_type)
            type_resources = store.get_all_resources(resource_type)

            for resource in type_resources:
                for path in ref_paths:
                    ref_value = get_reference_from_path(resource, path)
                    if ref_value == patient_ref:
                        all_resources.append(resource)
                        break

        # Apply pagination
        total = len(all_resources)

        # Handle _summary=count
        if _summary == "count":
            return JSONResponse(
                content={
                    "resourceType": "Bundle",
                    "type": "searchset",
                    "total": total,
                },
                media_type=FHIR_JSON,
            )

        paginated = all_resources[_offset : _offset + _count]

        # Apply _elements filtering
        if _elements:
            element_list = [e.strip() for e in _elements.split(",")]
            paginated = [filter_elements(r, element_list) for r in paginated]

        # Apply _summary filtering
        if _summary and _summary != "false":
            paginated = [filter_summary(r, _summary) for r in paginated]

        # Build bundle
        entries = []
        for i, r in enumerate(paginated):
            rtype = r.get("resourceType", "Unknown")
            rid = r.get("id", "")
            # First entry (patient) is match, rest are include
            mode = "match" if i == 0 and rtype == "Patient" else "include"
            entries.append(
                BundleEntry(
                    fullUrl=f"{get_base_url(request)}/{rtype}/{rid}",
                    resource=r,
                    search={"mode": mode},
                )
            )

        base = get_base_url(request)
        links = [
            BundleLink(relation="self", url=f"{base}/Patient/{patient_id}/$everything"),
        ]

        # Add pagination links
        if _offset > 0:
            prev_offset = max(0, _offset - _count)
            links.append(
                BundleLink(
                    relation="previous",
                    url=f"{base}/Patient/{patient_id}/$everything?_offset={prev_offset}&_count={_count}",
                )
            )
        if _offset + _count < total:
            next_offset = _offset + _count
            links.append(
                BundleLink(
                    relation="next",
                    url=f"{base}/Patient/{patient_id}/$everything?_offset={next_offset}&_count={_count}",
                )
            )

        bundle = Bundle(
            resourceType="Bundle",
            id=str(uuid.uuid4()),
            type="searchset",
            total=total,
            entry=entries,
            link=links,
        )

        return JSONResponse(
            content=bundle.model_dump(exclude_none=True),
            media_type=FHIR_JSON,
        )

    @router.get("/Patient/{patient_id}/$summary", tags=["Operations"])
    async def patient_summary(
        request: Request,
        patient_id: str,
        persist: bool = Query(default=False, description="Persist the generated IPS bundle"),
    ) -> Response:
        """Generate an International Patient Summary (IPS) for a patient.

        Implements the IPS $summary operation per HL7 IPS IG:
        http://hl7.org/fhir/uv/ips/OperationDefinition/summary

        Returns a Document Bundle containing an IPS-compliant Composition with
        sections for allergies, medications, problems, immunizations, procedures,
        and results, along with all referenced resources.

        Parameters:
            patient_id: The patient ID
            persist: Whether to persist the generated Bundle (default false)

        Returns:
            IPS Document Bundle (application/fhir+json)
        """
        from ..operations.ips_summary import IPSSummaryGenerator

        generator = IPSSummaryGenerator(store)
        bundle = generator.generate(patient_id, persist=persist)

        if bundle is None:
            outcome = OperationOutcome.not_found("Patient", patient_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        return JSONResponse(
            content=bundle,
            media_type=FHIR_JSON,
        )

    @router.post("/Patient/$summary", tags=["Operations"])
    async def import_ips(
        request: Request,
    ) -> Response:
        """Import an International Patient Summary (IPS) document.

        Accepts an IPS Document Bundle and extracts all resources into the store.
        The Patient resource from the IPS will be matched or created, and all
        clinical resources (allergies, medications, conditions, etc.) will be
        imported.

        Request Body:
            IPS Document Bundle (application/fhir+json)

        Returns:
            OperationOutcome with import summary
        """
        try:
            body = await request.json()
        except Exception as e:
            outcome = OperationOutcome.error(f"Invalid JSON: {e}", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Validate it's a document bundle
        if body.get("resourceType") != "Bundle" or body.get("type") != "document":
            outcome = OperationOutcome.error("Expected a Document Bundle (type='document')", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        entries = body.get("entry", [])
        if not entries:
            outcome = OperationOutcome.error("Bundle has no entries", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Import all resources
        imported_count = 0
        patient_id = None

        for entry in entries:
            resource = entry.get("resource", {})
            resource_type = resource.get("resourceType")

            if not resource_type:
                continue

            # Skip Composition - it's IPS-specific metadata
            if resource_type == "Composition":
                continue

            # Track patient ID
            if resource_type == "Patient":
                created = store.create(resource)
                patient_id = created.get("id")
                imported_count += 1
            else:
                # Update references to use actual patient ID if needed
                store.create(resource)
                imported_count += 1

        outcome = OperationOutcome(
            resourceType="OperationOutcome",
            issue=[
                OperationOutcomeIssue(
                    severity="information",
                    code="informational",
                    diagnostics=f"Successfully imported {imported_count} resources from IPS document"
                    + (f" for Patient/{patient_id}" if patient_id else ""),
                )
            ],
        )

        return JSONResponse(
            content=outcome.model_dump(exclude_none=True),
            status_code=200,
            media_type=FHIR_JSON,
        )

    # =========================================================================
    # Measure Operations
    # =========================================================================

    @router.get("/Measure/{measure_id}/$evaluate-measure", tags=["Operations"])
    @router.post("/Measure/{measure_id}/$evaluate-measure", tags=["Operations"])
    async def evaluate_measure(
        request: Request,
        measure_id: str,
        subject: str | None = Query(default=None, description="Patient or Group reference"),
        periodStart: str | None = Query(default=None, description="Measurement period start"),
        periodEnd: str | None = Query(default=None, description="Measurement period end"),
        reportType: str = Query(default="summary", description="individual|subject-list|summary"),
    ) -> Response:
        """Evaluate a measure and return a MeasureReport.

        This operation evaluates a Measure against patient data using the
        associated CQL Library and returns a MeasureReport with population
        counts and measure scores.

        Parameters:
            measure_id: The Measure resource ID
            subject: Patient/123 or Group/456 (optional, defaults to all patients)
            periodStart: Start of measurement period (YYYY-MM-DD)
            periodEnd: End of measurement period (YYYY-MM-DD)
            reportType: Type of report (individual, subject-list, summary)

        Returns:
            MeasureReport resource with evaluation results
        """
        import base64

        from fhirkit.engine.cql.evaluator import CQLEvaluator
        from fhirkit.engine.cql.measure import MeasureEvaluator, MeasureScoring

        # Get the Measure resource
        measure = store.read("Measure", measure_id)
        if measure is None:
            outcome = OperationOutcome.not_found("Measure", measure_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        # Get Library reference from Measure
        library_refs = measure.get("library", [])
        if not library_refs:
            outcome = OperationOutcome.error("Measure has no associated Library", code="not-found")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Resolve Library by canonical URL
        library_url = library_refs[0]
        libraries, _ = store.search("Library", {"url": library_url})
        if not libraries:
            # Try by ID if URL search fails
            library_id = library_url.split("/")[-1] if "/" in library_url else library_url
            library = store.read("Library", library_id)
            if library is None:
                outcome = OperationOutcome.error(f"Library not found: {library_url}", code="not-found")
                return JSONResponse(
                    content=outcome.model_dump(exclude_none=True),
                    status_code=400,
                    media_type=FHIR_JSON,
                )
        else:
            library = libraries[0]

        # Extract CQL source from Library content
        cql_source = None
        for content in library.get("content", []):
            content_type = content.get("contentType", "")
            if content_type == "text/cql" or "cql" in content_type.lower():
                data = content.get("data")
                if data:
                    cql_source = base64.b64decode(data).decode("utf-8")
                    break

        if not cql_source:
            outcome = OperationOutcome.error("No CQL content found in Library", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Get patients to evaluate
        patients: list[dict[str, Any]] = []
        if subject:
            if subject.startswith("Patient/"):
                patient_id = subject.split("/")[1]
                patient = store.read("Patient", patient_id)
                if patient:
                    patients = [patient]
            elif subject.startswith("Group/"):
                # Handle Group members
                group_id = subject.split("/")[1]
                group = store.read("Group", group_id)
                if not group:
                    outcome = OperationOutcome.not_found("Group", group_id)
                    return JSONResponse(
                        content=outcome.model_dump(exclude_none=True),
                        status_code=404,
                        media_type=FHIR_JSON,
                    )

                # Extract Patient members from the Group
                for member in group.get("member", []):
                    entity = member.get("entity", {})
                    ref = entity.get("reference", "")
                    if ref.startswith("Patient/"):
                        member_patient_id = ref.split("/")[1]
                        member_patient = store.read("Patient", member_patient_id)
                        if member_patient:
                            patients.append(member_patient)

                if not patients:
                    outcome = OperationOutcome.error(
                        f"Group/{group_id} has no Patient members or members not found",
                        code="not-found",
                    )
                    return JSONResponse(
                        content=outcome.model_dump(exclude_none=True),
                        status_code=422,
                        media_type=FHIR_JSON,
                    )
            else:
                # Try as bare patient ID
                patient = store.read("Patient", subject)
                if patient:
                    patients = [patient]
        else:
            # All patients
            patients, _ = store.search("Patient", {})

        if not patients:
            outcome = OperationOutcome.error("No patients found for evaluation", code="not-found")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Create CQL evaluator with store as data source
        try:
            cql_evaluator = CQLEvaluator(data_source=store)
            measure_evaluator = MeasureEvaluator(cql_evaluator=cql_evaluator, data_source=store)
            measure_evaluator.load_measure(cql_source)

            # Set scoring type from Measure
            scoring = measure.get("scoring", {}).get("coding", [{}])[0].get("code", "proportion")
            if scoring == "proportion":
                measure_evaluator.set_scoring(MeasureScoring.PROPORTION)
            elif scoring == "ratio":
                measure_evaluator.set_scoring(MeasureScoring.RATIO)
            elif scoring == "continuous-variable":
                measure_evaluator.set_scoring(MeasureScoring.CONTINUOUS_VARIABLE)
            elif scoring == "cohort":
                measure_evaluator.set_scoring(MeasureScoring.COHORT)

        except Exception as e:
            outcome = OperationOutcome.error(f"Failed to compile CQL: {e}", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Evaluate the measure
        try:
            report = measure_evaluator.evaluate_population(patients)
            fhir_report = report.to_fhir()

            # Enhance the report with additional metadata
            fhir_report["id"] = str(uuid.uuid4())
            fhir_report["measure"] = measure.get("url", f"Measure/{measure_id}")

            # Set period from parameters or measure
            if periodStart and periodEnd:
                fhir_report["period"] = {
                    "start": periodStart,
                    "end": periodEnd,
                }
            elif measure.get("effectivePeriod"):
                fhir_report["period"] = measure["effectivePeriod"]

            # Set report type
            if reportType == "individual" and len(patients) == 1:
                fhir_report["type"] = "individual"
                fhir_report["subject"] = {"reference": f"Patient/{patients[0].get('id')}"}
            else:
                fhir_report["type"] = reportType if reportType in ("summary", "subject-list") else "summary"

            # Add improvement notation from measure
            if measure.get("improvementNotation"):
                fhir_report["improvementNotation"] = measure["improvementNotation"]

        except Exception as e:
            outcome = OperationOutcome.error(f"Measure evaluation failed: {e}", code="processing")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=500,
                media_type=FHIR_JSON,
            )

        return JSONResponse(
            content=fhir_report,
            media_type=FHIR_JSON,
        )

    # Patient-specific history routes (must come before compartment search)
    @router.get("/Patient/{patient_id}/_history", tags=["History"])
    async def patient_history_instance(
        request: Request,
        patient_id: str,
    ) -> Response:
        """Get the history of a specific Patient.

        Returns all versions of the patient as a Bundle.
        """
        versions = store.history("Patient", patient_id)
        if not versions:
            outcome = OperationOutcome.not_found("Patient", patient_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        bundle = Bundle(
            resourceType="Bundle",
            id=str(uuid.uuid4()),
            type="history",
            total=len(versions),
            entry=[
                BundleEntry(
                    fullUrl=f"{get_base_url(request)}/Patient/{patient_id}",
                    resource=v,
                    request=BundleEntryRequest(
                        method="GET",
                        url=f"Patient/{patient_id}/_history/{v.get('meta', {}).get('versionId', '1')}",
                    ),
                )
                for v in versions
            ],
        )

        return JSONResponse(
            content=bundle.model_dump(exclude_none=True),
            media_type=FHIR_JSON,
        )

    @router.get("/Patient/{patient_id}/_history/{version_id}", tags=["History"])
    async def patient_vread(
        request: Request,
        patient_id: str,
        version_id: str,
    ) -> Response:
        """Read a specific version of a Patient."""
        versions = store.history("Patient", patient_id)
        for v in versions:
            if v.get("meta", {}).get("versionId") == version_id:
                return JSONResponse(
                    content=v,
                    media_type=FHIR_JSON,
                    headers={"ETag": f'W/"{version_id}"'},
                )

        outcome = OperationOutcome.not_found("Patient", f"{patient_id}/_history/{version_id}")
        return JSONResponse(
            content=outcome.model_dump(exclude_none=True),
            status_code=404,
            media_type=FHIR_JSON,
        )

    # Patient-specific $validate route (must be before compartment search)
    @router.get("/Patient/{patient_id}/$validate", tags=["Validation"])
    @router.post("/Patient/{patient_id}/$validate", tags=["Validation"])
    async def validate_patient_resource(
        request: Request,
        patient_id: str,
        mode: str = Query(default="validation"),
    ) -> Response:
        """Validate an existing Patient resource by ID.

        Validates the stored Patient resource against FHIR R4 structure rules,
        required fields, code bindings, and reference validity.
        """
        from ..validation import FHIRValidator

        resource = store.read("Patient", patient_id)
        if resource is None:
            outcome = OperationOutcome.not_found("Patient", patient_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        validator = FHIRValidator(store)
        result = validator.validate(resource, mode)

        return JSONResponse(
            content=result.to_operation_outcome(),
            media_type=FHIR_JSON,
        )

    # =========================================================================
    # Patient-specific $diff (must be before compartment route)
    # =========================================================================

    @router.get("/Patient/{patient_id}/$diff", tags=["Operations"])
    async def diff_patient_versions(
        request: Request,
        patient_id: str,
        version: str = Query(..., description="Version ID to compare against current"),
    ) -> Response:
        """Compare current Patient version with a previous version.

        This specific route is needed to take precedence over the compartment route.
        """
        from .diff import compute_diff, diff_to_parameters

        # Get current version
        current = store.read("Patient", patient_id)
        if not current:
            outcome = OperationOutcome.not_found("Patient", patient_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        # Get previous version from history
        history = store.history("Patient", patient_id)
        previous = None
        for hist_resource in history:
            if hist_resource.get("meta", {}).get("versionId") == version:
                previous = hist_resource
                break

        if not previous:
            outcome = OperationOutcome.error(
                f"Version {version} not found for Patient/{patient_id}",
                code="not-found",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        # Compute diff
        diff = compute_diff(previous, current)
        result = diff_to_parameters(diff)

        return JSONResponse(content=result, media_type=FHIR_JSON)

    @router.get("/Patient/{patient_id}/{resource_type}", tags=["Compartment"])
    async def compartment_search(
        request: Request,
        patient_id: str,
        resource_type: str,
        _count: int = Query(default=100, ge=1, le=1000, alias="_count"),
        _offset: int = Query(default=0, ge=0, alias="_offset"),
        _sort: str | None = Query(default=None, alias="_sort"),
        _elements: str | None = Query(default=None, alias="_elements"),
        _summary: str | None = Query(default=None, alias="_summary"),
    ) -> Response:
        """Search for resources within a patient compartment.

        Returns resources of the specified type that are associated with
        the given patient.

        Example: GET /Patient/123/Condition returns all Conditions for patient 123.

        Parameters:
            patient_id: The patient ID
            resource_type: The resource type to search for
            _count: Maximum number of results per page
            _offset: Pagination offset
            _sort: Sort order (prefix with - for descending)
            _elements: Comma-separated list of elements to include
            _summary: Return summary view (true, text, data, count, false)
        """
        from .compartments import PATIENT_COMPARTMENT, get_patient_reference_paths, get_reference_from_path
        from .search import filter_resources

        # Validate resource type is supported
        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Validate resource type is in Patient compartment or is Patient
        if resource_type != "Patient" and resource_type not in PATIENT_COMPARTMENT:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not part of Patient compartment",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Verify patient exists
        patient = store.read("Patient", patient_id)
        if patient is None:
            outcome = OperationOutcome.not_found("Patient", patient_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        # Get additional search params from query string
        params: dict[str, Any] = {}
        for key, value in request.query_params.multi_items():
            if not key.startswith("_") or key in ("_id", "_lastUpdated"):
                if key in params:
                    if isinstance(params[key], list):
                        params[key].append(value)
                    else:
                        params[key] = [params[key], value]
                else:
                    params[key] = value

        # Handle special case: requesting Patient returns just the patient
        if resource_type == "Patient":
            # Handle _summary=count
            if _summary == "count":
                return JSONResponse(
                    content={
                        "resourceType": "Bundle",
                        "type": "searchset",
                        "total": 1,
                    },
                    media_type=FHIR_JSON,
                )

            # Apply filtering to patient
            filtered_patient = patient
            if _elements:
                element_list = [e.strip() for e in _elements.split(",")]
                filtered_patient = filter_elements(filtered_patient, element_list)
            if _summary and _summary != "false":
                filtered_patient = filter_summary(filtered_patient, _summary)

            bundle = Bundle.searchset(
                resources=[filtered_patient],
                total=1,
                base_url=get_base_url(request),
                resource_type="Patient",
                params=params,
            )
            return JSONResponse(
                content=bundle.model_dump(exclude_none=True),
                media_type=FHIR_JSON,
            )

        # Search for resources in compartment
        patient_ref = f"Patient/{patient_id}"
        ref_paths = get_patient_reference_paths(resource_type)

        all_resources = store.get_all_resources(resource_type)
        compartment_resources = []

        for resource in all_resources:
            for path in ref_paths:
                ref_value = get_reference_from_path(resource, path)
                if ref_value == patient_ref:
                    compartment_resources.append(resource)
                    break

        # Apply additional search params
        if params:
            compartment_resources = filter_resources(compartment_resources, resource_type, params)

        # Apply sorting
        if _sort:
            reverse = _sort.startswith("-")
            sort_field = _sort.lstrip("-")
            try:
                compartment_resources = sorted(
                    compartment_resources,
                    key=lambda r: r.get(sort_field, "") or "",
                    reverse=reverse,
                )
            except (TypeError, KeyError):
                pass

        # Apply pagination
        total = len(compartment_resources)

        # Handle _summary=count
        if _summary == "count":
            return JSONResponse(
                content={
                    "resourceType": "Bundle",
                    "type": "searchset",
                    "total": total,
                },
                media_type=FHIR_JSON,
            )

        paginated = compartment_resources[_offset : _offset + _count]

        # Apply _elements filtering
        if _elements:
            element_list = [e.strip() for e in _elements.split(",")]
            paginated = [filter_elements(r, element_list) for r in paginated]

        # Apply _summary filtering
        if _summary and _summary != "false":
            paginated = [filter_summary(r, _summary) for r in paginated]

        # Build bundle
        bundle = Bundle.searchset(
            resources=paginated,
            total=total,
            base_url=get_base_url(request),
            resource_type=resource_type,
            params=params,
            offset=_offset,
            count=_count,
        )

        return JSONResponse(
            content=bundle.model_dump(exclude_none=True),
            media_type=FHIR_JSON,
        )

    # =========================================================================
    # Terminology Operations
    # =========================================================================
    # NOTE: These must be defined BEFORE generic /{resource_type} routes
    # to ensure proper route matching for paths like /CodeSystem/$subsumes

    @router.get("/ValueSet/$expand", tags=["Terminology"])
    @router.post("/ValueSet/$expand", tags=["Terminology"])
    async def expand_valueset(
        request: Request,
        url: str | None = Query(default=None),
        filter: str | None = Query(default=None),
        count: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0),
    ) -> Response:
        """Expand a ValueSet.

        Expands the ValueSet to include all codes. Supports:
        - Filtering by code/display text
        - CodeSystem expansion (when compose references entire CodeSystem)
        - Hierarchical code inclusion
        - ValueSet references within compose
        """
        # For POST, get parameters from body
        if request.method == "POST":
            try:
                body = await request.json()
                url = body.get("parameter", [{}])[0].get("valueUri", url)
                for param in body.get("parameter", []):
                    if param.get("name") == "url":
                        url = param.get("valueUri")
                    elif param.get("name") == "filter":
                        filter = param.get("valueString")
            except Exception:
                pass

        if not url:
            outcome = OperationOutcome.error("ValueSet URL is required", code="required")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Use terminology provider for enhanced expansion
        from ..terminology import FHIRStoreTerminologyProvider

        provider = FHIRStoreTerminologyProvider(store)
        expansion = provider.expand_valueset(url=url, filter_text=filter, count=count, offset=offset)

        if not expansion:
            outcome = OperationOutcome.error(f"ValueSet not found: {url}", code="not-found")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        return JSONResponse(content=expansion, media_type=FHIR_JSON)

    @router.get("/ValueSet/{valueset_id}/$expand", tags=["Terminology"])
    async def expand_valueset_by_id(
        request: Request,
        valueset_id: str,
        filter: str | None = Query(default=None),
        count: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0),
    ) -> Response:
        """Expand a specific ValueSet by ID.

        Supports:
        - Filtering by code/display text
        - CodeSystem expansion (when compose references entire CodeSystem)
        - Hierarchical code inclusion
        """
        # Use terminology provider for enhanced expansion
        from ..terminology import FHIRStoreTerminologyProvider

        provider = FHIRStoreTerminologyProvider(store)
        expansion = provider.expand_valueset(valueset_id=valueset_id, filter_text=filter, count=count, offset=offset)

        if not expansion:
            outcome = OperationOutcome.not_found("ValueSet", valueset_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        return JSONResponse(content=expansion, media_type=FHIR_JSON)

    @router.get("/ValueSet/$validate-code", tags=["Terminology"])
    @router.post("/ValueSet/$validate-code", tags=["Terminology"])
    async def validate_code(
        request: Request,
        url: str | None = Query(default=None),
        system: str | None = Query(default=None),
        code: str | None = Query(default=None),
    ) -> Response:
        """Validate that a code is in a ValueSet.

        Returns whether the code is valid and its display text.
        Supports:
        - Simple code + system validation
        - Coding object input (POST body)
        - CodeableConcept object input (POST body)
        """
        coding: dict[str, Any] | None = None
        codeable_concept: dict[str, Any] | None = None

        # For POST, get parameters from body
        if request.method == "POST":
            try:
                body = await request.json()
                for param in body.get("parameter", []):
                    if param.get("name") == "url":
                        url = param.get("valueUri")
                    elif param.get("name") == "system":
                        system = param.get("valueUri")
                    elif param.get("name") == "code":
                        code = param.get("valueCode")
                    elif param.get("name") == "coding":
                        coding = param.get("valueCoding")
                    elif param.get("name") == "codeableConcept":
                        codeable_concept = param.get("valueCodeableConcept")
            except Exception:
                pass

        # Must have URL and either code or coding/codeableConcept
        if not url:
            outcome = OperationOutcome.error("ValueSet URL is required", code="required")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        if not code and not coding and not codeable_concept:
            outcome = OperationOutcome.error("Code, coding, or codeableConcept is required", code="required")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Use terminology provider for validation
        from ..terminology import FHIRStoreTerminologyProvider

        provider = FHIRStoreTerminologyProvider(store)
        result = provider.validate_code(
            valueset_url=url,
            code=code,
            system=system,
            coding=coding,
            codeable_concept=codeable_concept,
        )

        return JSONResponse(content=result, media_type=FHIR_JSON)

    @router.get("/CodeSystem/$lookup", tags=["Terminology"])
    @router.post("/CodeSystem/$lookup", tags=["Terminology"])
    async def lookup_code(
        request: Request,
        system: str | None = Query(default=None),
        code: str | None = Query(default=None),
        version: str | None = Query(default=None),
    ) -> Response:
        """Look up a code in a CodeSystem.

        Returns information about the code including display text.
        Supports hierarchical CodeSystems (searches nested concepts).
        """
        # For POST, get parameters from body
        if request.method == "POST":
            try:
                body = await request.json()
                for param in body.get("parameter", []):
                    if param.get("name") == "system":
                        system = param.get("valueUri")
                    elif param.get("name") == "code":
                        code = param.get("valueCode")
                    elif param.get("name") == "version":
                        version = param.get("valueString")
            except Exception:
                pass

        if not system or not code:
            outcome = OperationOutcome.error("Both system and code are required", code="required")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Use terminology provider for hierarchical lookup
        from ..terminology import FHIRStoreTerminologyProvider

        provider = FHIRStoreTerminologyProvider(store)
        result = provider.lookup_code(system, code, version)

        if not result:
            outcome = OperationOutcome.error(f"Code '{code}' not found in CodeSystem", code="not-found")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        return JSONResponse(content=result, media_type=FHIR_JSON)

    @router.get("/CodeSystem/$subsumes", tags=["Terminology"])
    @router.post("/CodeSystem/$subsumes", tags=["Terminology"])
    async def subsumes_code(
        request: Request,
        system: str | None = Query(default=None),
        codeA: str | None = Query(default=None),
        codeB: str | None = Query(default=None),
        version: str | None = Query(default=None),
    ) -> Response:
        """Test subsumption relationship between two codes.

        Returns the relationship between codeA and codeB:
        - equivalent: codes are the same
        - subsumes: codeA is an ancestor of codeB
        - subsumed-by: codeA is a descendant of codeB
        - not-subsumed: codes have no hierarchical relationship
        """
        # For POST, get parameters from body
        if request.method == "POST":
            try:
                body = await request.json()
                for param in body.get("parameter", []):
                    if param.get("name") == "system":
                        system = param.get("valueUri")
                    elif param.get("name") == "codeA":
                        codeA = param.get("valueCode")
                    elif param.get("name") == "codeB":
                        codeB = param.get("valueCode")
                    elif param.get("name") == "version":
                        version = param.get("valueString")
            except Exception:
                pass

        if not system or not codeA or not codeB:
            outcome = OperationOutcome.error("system, codeA, and codeB are required", code="required")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Use terminology provider
        from ..terminology import FHIRStoreTerminologyProvider

        provider = FHIRStoreTerminologyProvider(store)
        result = provider.subsumes(system, codeA, codeB, version)

        return JSONResponse(content=result, media_type=FHIR_JSON)

    @router.get("/CodeSystem/{codesystem_id}/$subsumes", tags=["Terminology"])
    async def subsumes_code_by_id(
        request: Request,
        codesystem_id: str,
        codeA: str = Query(...),
        codeB: str = Query(...),
    ) -> Response:
        """Test subsumption relationship for a specific CodeSystem by ID."""
        codesystem = store.read("CodeSystem", codesystem_id)
        if codesystem is None:
            outcome = OperationOutcome.not_found("CodeSystem", codesystem_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        system = codesystem.get("url")
        if not system:
            outcome = OperationOutcome.error("CodeSystem has no URL", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        from ..terminology import FHIRStoreTerminologyProvider

        provider = FHIRStoreTerminologyProvider(store)
        result = provider.subsumes(system, codeA, codeB)

        return JSONResponse(content=result, media_type=FHIR_JSON)

    @router.get("/terminology/memberOf", tags=["Terminology"])
    async def member_of(
        request: Request,
        code: str = Query(...),
        system: str = Query(...),
        valueSetUrl: str = Query(...),
    ) -> Response:
        """Check if a code is a member of a ValueSet.

        Convenience endpoint that returns a simple boolean result.
        """
        from ..terminology import FHIRStoreTerminologyProvider

        provider = FHIRStoreTerminologyProvider(store)
        is_member = provider.member_of(valueSetUrl, code, system)

        result = {
            "resourceType": "Parameters",
            "parameter": [{"name": "result", "valueBoolean": is_member}],
        }
        return JSONResponse(content=result, media_type=FHIR_JSON)

    # =========================================================================
    # ConceptMap $translate Operation
    # =========================================================================

    @router.get("/ConceptMap/$translate", tags=["Terminology"])
    @router.post("/ConceptMap/$translate", tags=["Terminology"])
    async def translate_code(
        request: Request,
        code: str | None = Query(default=None),
        system: str | None = Query(default=None),
        target: str | None = Query(default=None),
        url: str | None = Query(default=None),
        reverse: bool = Query(default=False),
    ) -> Response:
        """Translate a code from one code system to another using ConceptMap.

        Implements the FHIR $translate operation for code translation.

        Parameters:
            code: The code to translate
            system: Source code system URI
            target: Target code system URI (optional)
            url: ConceptMap URL to use (optional)
            reverse: Translate in reverse direction
        """
        from ..operations import ConceptMapTranslator

        # For POST, get parameters from body
        if request.method == "POST":
            try:
                body = await request.json()
                for param in body.get("parameter", []):
                    name = param.get("name")
                    if name == "code":
                        code = param.get("valueCode")
                    elif name == "system":
                        system = param.get("valueUri")
                    elif name == "target":
                        target = param.get("valueUri")
                    elif name == "url":
                        url = param.get("valueUri")
                    elif name == "reverse":
                        reverse = param.get("valueBoolean", False)
            except Exception:
                pass

        if not code or not system:
            outcome = OperationOutcome.error("Both code and system are required", code="required")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        translator = ConceptMapTranslator(store)
        result = translator.translate(
            code=code,
            system=system,
            target=target,
            concept_map_url=url,
            reverse=reverse,
        )

        return JSONResponse(content=result, media_type=FHIR_JSON)

    @router.get("/ConceptMap/{conceptmap_id}/$translate", tags=["Terminology"])
    @router.post("/ConceptMap/{conceptmap_id}/$translate", tags=["Terminology"])
    async def translate_code_by_id(
        request: Request,
        conceptmap_id: str,
        code: str | None = Query(default=None),
        system: str | None = Query(default=None),
        target: str | None = Query(default=None),
        reverse: bool = Query(default=False),
    ) -> Response:
        """Translate a code using a specific ConceptMap by ID."""
        from ..operations import ConceptMapTranslator

        # For POST, get parameters from body
        if request.method == "POST":
            try:
                body = await request.json()
                for param in body.get("parameter", []):
                    name = param.get("name")
                    if name == "code":
                        code = param.get("valueCode")
                    elif name == "system":
                        system = param.get("valueUri")
                    elif name == "target":
                        target = param.get("valueUri")
                    elif name == "reverse":
                        reverse = param.get("valueBoolean", False)
            except Exception:
                pass

        if not code or not system:
            outcome = OperationOutcome.error("Both code and system are required", code="required")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Check if ConceptMap exists
        concept_map = store.read("ConceptMap", conceptmap_id)
        if concept_map is None:
            outcome = OperationOutcome.not_found("ConceptMap", conceptmap_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        translator = ConceptMapTranslator(store)
        result = translator.translate(
            code=code,
            system=system,
            target=target,
            concept_map_id=conceptmap_id,
            reverse=reverse,
        )

        return JSONResponse(content=result, media_type=FHIR_JSON)

    # =========================================================================
    # Patient $match Operation
    # =========================================================================

    @router.post("/Patient/$match", tags=["Operations"])
    async def patient_match(request: Request) -> Response:
        """Find Patient records matching an input Patient resource.

        Implements the FHIR Patient $match operation for patient matching/deduplication.
        Returns a Bundle of matching patients with match scores and grades.

        Request body should be a Parameters resource containing:
        - resource: The Patient resource to match against
        - onlyCertainMatches (optional): Only return certain matches
        - count (optional): Maximum number of matches to return
        """
        from ..operations import PatientMatcher

        try:
            body = await request.json()
        except Exception:
            outcome = OperationOutcome.error("Invalid JSON body", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Extract parameters
        input_patient = None
        only_certain_matches = False
        count = 10

        if body.get("resourceType") == "Parameters":
            for param in body.get("parameter", []):
                name = param.get("name")
                if name == "resource" and "resource" in param:
                    input_patient = param["resource"]
                elif name == "onlyCertainMatches":
                    only_certain_matches = param.get("valueBoolean", False)
                elif name == "count":
                    count = param.get("valueInteger", 10)
        elif body.get("resourceType") == "Patient":
            # Allow direct Patient resource
            input_patient = body

        if input_patient is None or input_patient.get("resourceType") != "Patient":
            outcome = OperationOutcome.error(
                "Request must contain a Patient resource",
                code="required",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        matcher = PatientMatcher(store)
        result = matcher.match(
            input_patient=input_patient,
            only_certain_matches=only_certain_matches,
            count=count,
        )

        return JSONResponse(content=result, media_type=FHIR_JSON)

    # =========================================================================
    # Composition $document Operation
    # =========================================================================

    @router.get("/Composition/{composition_id}/$document", tags=["Operations"])
    async def composition_document(
        composition_id: str,
        persist: bool = Query(default=True),
    ) -> Response:
        """Generate a Document Bundle from a Composition.

        Implements the FHIR $document operation to create a complete
        document bundle containing the Composition and all referenced resources.

        Parameters:
            composition_id: The ID of the Composition resource
            persist: Whether to persist the generated Bundle (default: True)
        """
        from ..operations import DocumentGenerator

        # Check if Composition exists
        composition = store.read("Composition", composition_id)
        if composition is None:
            outcome = OperationOutcome.not_found("Composition", composition_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        generator = DocumentGenerator(store)
        document = generator.generate_document(composition, persist=persist)

        return JSONResponse(content=document, media_type=FHIR_JSON)

    # =========================================================================
    # Validation Operations
    # =========================================================================

    @router.post("/{resource_type}/$validate", tags=["Validation"])
    async def validate_resource(
        request: Request,
        resource_type: str,
        mode: str = Query(default="validation"),
    ) -> Response:
        """Validate a resource against FHIR R4 rules.

        Validates the resource in the request body against FHIR R4 structure
        rules, required fields, code bindings, and reference validity.

        Parameters:
            resource_type: The expected resource type
            mode: Validation mode (validation, create, update, delete)

        Returns:
            OperationOutcome with validation results
        """
        from ..validation import FHIRValidator

        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        try:
            body = await request.json()
        except Exception as e:
            outcome = OperationOutcome.error(
                f"Invalid JSON in request body: {e}",
                code="invalid",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Handle Parameters wrapper (FHIR $validate can accept Parameters)
        resource = body
        if body.get("resourceType") == "Parameters":
            # Extract resource from Parameters
            for param in body.get("parameter", []):
                if param.get("name") == "resource" and "resource" in param:
                    resource = param["resource"]
                    break

        # Validate resource type matches endpoint
        if resource.get("resourceType") != resource_type:
            outcome = OperationOutcome.error(
                f"Resource type '{resource.get('resourceType')}' does not match endpoint '{resource_type}'",
                code="invalid",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        validator = FHIRValidator(store)
        result = validator.validate(resource, mode)

        # Return 200 even for invalid resources (per FHIR spec)
        return JSONResponse(
            content=result.to_operation_outcome(),
            media_type=FHIR_JSON,
        )

    @router.get("/{resource_type}/{resource_id}/$validate", tags=["Validation"])
    @router.post("/{resource_type}/{resource_id}/$validate", tags=["Validation"])
    async def validate_existing_resource(
        request: Request,
        resource_type: str,
        resource_id: str,
        mode: str = Query(default="validation"),
    ) -> Response:
        """Validate an existing resource by ID.

        Validates the stored resource against FHIR R4 structure rules,
        required fields, code bindings, and reference validity.

        Parameters:
            resource_type: The resource type
            resource_id: The resource ID
            mode: Validation mode (validation, create, update, delete)

        Returns:
            OperationOutcome with validation results
        """
        from ..validation import FHIRValidator

        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        resource = store.read(resource_type, resource_id)
        if resource is None:
            outcome = OperationOutcome.not_found(resource_type, resource_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        validator = FHIRValidator(store)
        result = validator.validate(resource, mode)

        return JSONResponse(
            content=result.to_operation_outcome(),
            media_type=FHIR_JSON,
        )

    # =========================================================================
    # Diff Operations
    # =========================================================================

    @router.get("/{resource_type}/{resource_id}/$diff", tags=["Operations"])
    async def diff_versions(
        request: Request,
        resource_type: str,
        resource_id: str,
        version: str = Query(..., description="Version ID to compare against current"),
    ) -> Response:
        """Compare current version with a previous version.

        Returns the differences as JSON Patch-style operations in a
        Parameters resource.

        Parameters:
            resource_type: The resource type
            resource_id: The resource ID
            version: Version ID to compare against current version
        """
        from .diff import compute_diff, diff_to_parameters

        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Get current version
        current = store.read(resource_type, resource_id)
        if not current:
            outcome = OperationOutcome.not_found(resource_type, resource_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        # Get previous version from history
        history = store.history(resource_type, resource_id)
        previous = None
        for hist_resource in history:
            if hist_resource.get("meta", {}).get("versionId") == version:
                previous = hist_resource
                break

        if not previous:
            outcome = OperationOutcome.error(
                f"Version {version} not found for {resource_type}/{resource_id}",
                code="not-found",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        # Compute diff
        diff = compute_diff(previous, current)
        result = diff_to_parameters(diff)

        return JSONResponse(content=result, media_type=FHIR_JSON)

    @router.post("/{resource_type}/$diff", tags=["Operations"])
    async def diff_resources(
        request: Request,
        resource_type: str,
    ) -> Response:
        """Compare two resources provided in Parameters body.

        The request body should be a Parameters resource with:
        - source: The original resource
        - target: The resource to compare against

        Returns the differences as JSON Patch-style operations.
        """
        from .diff import compute_diff, diff_to_parameters

        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        try:
            body = await request.json()
        except Exception as e:
            outcome = OperationOutcome.error(f"Invalid JSON: {e}", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Extract source and target from Parameters
        source = None
        target = None

        if body.get("resourceType") != "Parameters":
            outcome = OperationOutcome.error(
                "Request body must be a Parameters resource",
                code="invalid",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        for param in body.get("parameter", []):
            name = param.get("name")
            if name == "source" and "resource" in param:
                source = param["resource"]
            elif name == "target" and "resource" in param:
                target = param["resource"]

        if not source or not target:
            outcome = OperationOutcome.error(
                "Parameters must contain 'source' and 'target' resources",
                code="required",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Validate resource types match
        if source.get("resourceType") != resource_type:
            outcome = OperationOutcome.error(
                f"Source resource type ({source.get('resourceType')}) does not match URL ({resource_type})",
                code="invalid",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        if target.get("resourceType") != resource_type:
            outcome = OperationOutcome.error(
                f"Target resource type ({target.get('resourceType')}) does not match URL ({resource_type})",
                code="invalid",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Compute diff
        diff = compute_diff(source, target)
        result = diff_to_parameters(diff)

        return JSONResponse(content=result, media_type=FHIR_JSON)

    # =========================================================================
    # Resource Operations
    # =========================================================================

    @router.get("/{resource_type}", tags=["Search"])
    async def search_type(
        request: Request,
        resource_type: str,
        _count: int = Query(default=100, ge=1, le=1000, alias="_count"),
        _offset: int = Query(default=0, ge=0, alias="_offset"),
        _sort: str | None = Query(default=None, alias="_sort"),
        _include: list[str] | None = Query(default=None, alias="_include"),
        _revinclude: list[str] | None = Query(default=None, alias="_revinclude"),
        _elements: str | None = Query(default=None, alias="_elements"),
        _summary: str | None = Query(default=None, alias="_summary"),
        _total: str | None = Query(default=None, alias="_total"),
        _contained: str | None = Query(default=None, alias="_contained"),
    ) -> Response:
        """Search for resources of a specific type.

        Supports standard FHIR search parameters for each resource type.
        Common parameters:
        - _id: Resource ID
        - _count: Number of results per page (default 100, max 1000)
        - _offset: Offset for pagination
        - _sort: Sort order (prefix with - for descending)
        - _elements: Comma-separated list of elements to include
        - _summary: Return summary view (true, text, data, count, false)
        - _total: Return total count (accurate, estimate, none)
        - _contained: Include contained resources (false, true, both)
        """
        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Get search params from query string
        # Include chained params (contain :) and _has params
        params: dict[str, Any] = {}
        chained_params: dict[str, Any] = {}
        for key, value in request.query_params.multi_items():
            # Skip special params except _id, _lastUpdated, and _has
            if key.startswith("_") and key not in ("_id", "_lastUpdated") and not key.startswith("_has:"):
                continue

            # Separate chained/has params from regular params
            is_chained = ":" in key and "." in key and not key.startswith("_")
            is_has = key.startswith("_has:")

            target_dict = chained_params if (is_chained or is_has) else params

            if key in target_dict:
                if isinstance(target_dict[key], list):
                    target_dict[key].append(value)
                else:
                    target_dict[key] = [target_dict[key], value]
            else:
                target_dict[key] = value

        # Search with pagination (basic params only)
        resources, total = store.search(
            resource_type=resource_type,
            params=params,
            _count=_count,
            _offset=_offset,
        )

        # Apply advanced search filtering (chained and _has parameters)
        if chained_params:
            from .search import filter_resources_advanced

            resources = filter_resources_advanced(resources, resource_type, chained_params, store)
            total = len(resources)  # Update total after filtering

        # Apply sorting if specified
        if _sort:
            reverse = _sort.startswith("-")
            sort_field = _sort.lstrip("-")
            try:
                resources = sorted(
                    resources,
                    key=lambda r: r.get(sort_field, "") or "",
                    reverse=reverse,
                )
            except (TypeError, KeyError):
                pass  # Ignore sort errors

        # Handle _contained parameter
        # _contained=false (default): only top-level resources
        # _contained=true: only contained resources from matched containers
        # _contained=both: both top-level and contained resources
        if _contained in ("true", "both"):
            contained_resources: list[dict[str, Any]] = []
            for resource in resources:
                for contained in resource.get("contained", []):
                    # Add container reference for context
                    contained_copy = dict(contained)
                    # Ensure contained resource has an id for the fullUrl
                    if "id" not in contained_copy:
                        contained_copy["id"] = f"contained-{len(contained_resources)}"
                    contained_resources.append(contained_copy)

            if _contained == "true":
                # Only return contained resources
                resources = contained_resources
                total = len(resources)
            else:  # _contained == "both"
                # Return both top-level and contained resources
                resources = resources + contained_resources
                total = len(resources)

        # Handle _summary=count (return count-only bundle)
        if _summary == "count":
            return JSONResponse(
                content={
                    "resourceType": "Bundle",
                    "type": "searchset",
                    "total": total,
                },
                media_type=FHIR_JSON,
            )

        # Apply _elements filtering
        if _elements:
            element_list = [e.strip() for e in _elements.split(",")]
            resources = [filter_elements(r, element_list) for r in resources]

        # Apply _summary filtering
        if _summary and _summary != "false":
            resources = [filter_summary(r, _summary) for r in resources]

        # Process _include and _revinclude
        included_resources: list[dict[str, Any]] = []

        if _include or _revinclude:
            from .include_handler import IncludeHandler

            handler = IncludeHandler(store)

            if _include:
                included_resources.extend(handler.process_include(resources, _include))

            if _revinclude:
                included_resources.extend(handler.process_revinclude(resources, _revinclude))

            # Apply same filtering to included resources
            if _elements:
                incl_element_list = [e.strip() for e in _elements.split(",")]
                included_resources = [filter_elements(r, incl_element_list) for r in included_resources]
            if _summary and _summary != "false":
                included_resources = [filter_summary(r, _summary) for r in included_resources]

        # Build bundle with both match and include entries
        entries = []

        # Add primary search results with mode="match"
        for resource in resources:
            rid = resource.get("id", "")
            rtype = resource.get("resourceType", resource_type)
            entries.append(
                BundleEntry(
                    fullUrl=f"{get_base_url(request)}/{rtype}/{rid}",
                    resource=resource,
                    search={"mode": "match"},
                )
            )

        # Add included resources with mode="include" (deduplicated)
        seen_refs: set[str] = {f"{r.get('resourceType')}/{r.get('id')}" for r in resources}
        for resource in included_resources:
            ref = f"{resource.get('resourceType')}/{resource.get('id')}"
            if ref not in seen_refs:
                entries.append(
                    BundleEntry(
                        fullUrl=f"{get_base_url(request)}/{resource.get('resourceType')}/{resource.get('id')}",
                        resource=resource,
                        search={"mode": "include"},
                    )
                )
                seen_refs.add(ref)

        # Build pagination links
        links = [
            BundleLink(relation="self", url=f"{get_base_url(request)}/{resource_type}"),
        ]

        if _offset > 0:
            links.append(
                BundleLink(
                    relation="previous",
                    url=f"{get_base_url(request)}/{resource_type}?_offset={max(0, _offset - _count)}&_count={_count}",
                )
            )
        if _offset + _count < total:
            links.append(
                BundleLink(
                    relation="next",
                    url=f"{get_base_url(request)}/{resource_type}?_offset={_offset + _count}&_count={_count}",
                )
            )

        # Build bundle
        # Handle _total parameter (accurate, estimate, none)
        # Default is accurate (include total), none means exclude total
        bundle_total: int | None = total
        if _total == "none":
            bundle_total = None
        # For "estimate" we currently return accurate count (future: optimize for large datasets)

        bundle = Bundle(
            resourceType="Bundle",
            id=str(uuid.uuid4()),
            type="searchset",
            total=bundle_total,
            entry=entries,
            link=links,
        )

        return JSONResponse(
            content=bundle.model_dump(exclude_none=True),
            media_type=FHIR_JSON,
        )

    @router.get("/{resource_type}/{resource_id}", tags=["Read"])
    async def read(
        request: Request,
        resource_type: str,
        resource_id: str,
    ) -> Response:
        """Read a specific resource by ID.

        Returns the current version of the resource.

        Supports conditional read via:
        - If-None-Match: Returns 304 if ETag matches current version
        - If-Modified-Since: Returns 304 if resource not modified since date
        """
        from .conditional import check_conditional_read

        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        resource = store.read(resource_type, resource_id)
        if resource is None:
            outcome = OperationOutcome.not_found(resource_type, resource_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        # Get version for ETag
        version = resource.get("meta", {}).get("versionId", "1")
        etag = f'W/"{version}"'

        # Check conditional read headers
        if_none_match = request.headers.get("If-None-Match")
        if_modified_since = request.headers.get("If-Modified-Since")

        if check_conditional_read(resource, if_none_match, if_modified_since):
            return Response(
                status_code=304,
                headers={"ETag": etag},
            )

        # Special handling for Binary resources - content negotiation
        if resource_type == "Binary":
            accept = request.headers.get("Accept", FHIR_JSON)
            content_type = resource.get("contentType", "application/octet-stream")

            # If Accept header requests non-FHIR format, return raw binary content
            if accept not in (FHIR_JSON, "application/json", "*/*") and "fhir" not in accept.lower():
                import base64

                data = resource.get("data", "")
                try:
                    raw_content = base64.b64decode(data) if data else b""
                except Exception:
                    raw_content = b""

                return Response(
                    content=raw_content,
                    media_type=content_type,
                    headers={"ETag": etag},
                )

        return JSONResponse(
            content=resource,
            media_type=FHIR_JSON,
            headers={"ETag": etag},
        )

    @router.get("/{resource_type}/{resource_id}/_history", tags=["History"])
    async def history_instance(
        request: Request,
        resource_type: str,
        resource_id: str,
    ) -> Response:
        """Get the history of a specific resource.

        Returns all versions of the resource as a Bundle.
        """
        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        versions = store.history(resource_type, resource_id)
        if not versions:
            outcome = OperationOutcome.not_found(resource_type, resource_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        # Build history bundle
        bundle = Bundle(
            resourceType="Bundle",
            id=str(uuid.uuid4()),
            type="history",
            total=len(versions),
            entry=[
                BundleEntry(
                    fullUrl=f"{get_base_url(request)}/{resource_type}/{resource_id}",
                    resource=v,
                    request=BundleEntryRequest(
                        method="GET",
                        url=f"{resource_type}/{resource_id}/_history/{v.get('meta', {}).get('versionId', '1')}",
                    ),
                )
                for v in versions
            ],
        )

        return JSONResponse(
            content=bundle.model_dump(exclude_none=True),
            media_type=FHIR_JSON,
        )

    @router.get("/{resource_type}/{resource_id}/_history/{version_id}", tags=["History"])
    async def vread(
        request: Request,
        resource_type: str,
        resource_id: str,
        version_id: str,
    ) -> Response:
        """Read a specific version of a resource.

        Returns the specified version of the resource.
        """
        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        versions = store.history(resource_type, resource_id)
        for v in versions:
            if v.get("meta", {}).get("versionId") == version_id:
                return JSONResponse(
                    content=v,
                    media_type=FHIR_JSON,
                    headers={"ETag": f'W/"{version_id}"'},
                )

        outcome = OperationOutcome.not_found(resource_type, f"{resource_id}/_history/{version_id}")
        return JSONResponse(
            content=outcome.model_dump(exclude_none=True),
            status_code=404,
            media_type=FHIR_JSON,
        )

    @router.post("/{resource_type}", tags=["Create"], status_code=201)
    async def create(
        request: Request,
        resource_type: str,
    ) -> Response:
        """Create a new resource.

        The server assigns an ID to the resource.
        Returns 201 Created with Location header.

        Supports conditional create with If-None-Exist header:
        - If no match: creates the resource (201)
        - If one match: returns the existing resource (200)
        - If multiple matches: returns 412 Precondition Failed
        """
        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        try:
            body = await request.json()
        except Exception as e:
            outcome = OperationOutcome.error(f"Invalid JSON: {e}", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Validate resource type matches
        if body.get("resourceType") != resource_type:
            outcome = OperationOutcome.error(
                f"Resource type in body ({body.get('resourceType')}) does not match URL ({resource_type})",
                code="invalid",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Handle conditional create with If-None-Exist header
        if_none_exist = request.headers.get("If-None-Exist")
        if if_none_exist:
            # Parse search parameters from header value
            from urllib.parse import parse_qs

            search_params: dict[str, Any] = {}
            for key, values in parse_qs(if_none_exist).items():
                search_params[key] = values[0] if len(values) == 1 else values

            # Search for existing matches
            matches, total = store.search(resource_type, search_params, _count=2, _offset=0)

            if total == 1:
                # Return existing resource (200 OK, not 201)
                existing = matches[0]
                version = existing.get("meta", {}).get("versionId", "1")
                return JSONResponse(
                    content=existing,
                    status_code=200,
                    media_type=FHIR_JSON,
                    headers={
                        "Location": f"{get_base_url(request)}/{resource_type}/{existing['id']}",
                        "ETag": f'W/"{version}"',
                    },
                )
            elif total > 1:
                # Multiple matches - 412 Precondition Failed
                outcome = OperationOutcome.error(
                    f"Conditional create failed: {total} resources match the criteria",
                    code="duplicate",
                )
                return JSONResponse(
                    content=outcome.model_dump(exclude_none=True),
                    status_code=412,
                    media_type=FHIR_JSON,
                )
            # else: no matches, proceed with create

        # Create resource
        created = store.create(body)
        resource_id = created["id"]
        version = created.get("meta", {}).get("versionId", "1")

        return JSONResponse(
            content=created,
            status_code=201,
            media_type=FHIR_JSON,
            headers={
                "Location": f"{get_base_url(request)}/{resource_type}/{resource_id}",
                "ETag": f'W/"{version}"',
            },
        )

    @router.put("/{resource_type}", tags=["Conditional Update"])
    async def conditional_update(
        request: Request,
        resource_type: str,
    ) -> Response:
        """Update a resource by search criteria (conditional update).

        Search parameters are provided as query parameters.
        - If no match: creates a new resource (201)
        - If one match: updates the matched resource (200)
        - If multiple matches: returns 412 Precondition Failed
        """
        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Get search params from query string
        search_params: dict[str, Any] = {}
        for key, value in request.query_params.multi_items():
            if key.startswith("_"):
                continue  # Skip special params
            if key in search_params:
                existing = search_params[key]
                if isinstance(existing, list):
                    existing.append(value)
                else:
                    search_params[key] = [existing, value]
            else:
                search_params[key] = value

        if not search_params:
            outcome = OperationOutcome.error(
                "Conditional update requires search parameters",
                code="required",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        try:
            body = await request.json()
        except Exception as e:
            outcome = OperationOutcome.error(f"Invalid JSON: {e}", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Validate resource type
        if body.get("resourceType") != resource_type:
            outcome = OperationOutcome.error(
                f"Resource type in body ({body.get('resourceType')}) does not match URL ({resource_type})",
                code="invalid",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Search for matching resources
        matches, total = store.search(resource_type, search_params, _count=2, _offset=0)

        if total == 0:
            # No match - create new resource
            created = store.create(body)
            resource_id = created["id"]
            version = created.get("meta", {}).get("versionId", "1")
            return JSONResponse(
                content=created,
                status_code=201,
                media_type=FHIR_JSON,
                headers={
                    "Location": f"{get_base_url(request)}/{resource_type}/{resource_id}",
                    "ETag": f'W/"{version}"',
                },
            )
        elif total == 1:
            # Single match - update the resource
            existing = matches[0]
            resource_id = existing["id"]

            # Validate ID in body if present
            if body.get("id") and body.get("id") != resource_id:
                outcome = OperationOutcome.error(
                    f"Resource ID in body ({body.get('id')}) does not match matched resource ({resource_id})",
                    code="invalid",
                )
                return JSONResponse(
                    content=outcome.model_dump(exclude_none=True),
                    status_code=400,
                    media_type=FHIR_JSON,
                )

            updated = store.update(resource_type, resource_id, body)
            version = updated.get("meta", {}).get("versionId", "1")
            return JSONResponse(
                content=updated,
                status_code=200,
                media_type=FHIR_JSON,
                headers={
                    "Location": f"{get_base_url(request)}/{resource_type}/{resource_id}",
                    "ETag": f'W/"{version}"',
                },
            )
        else:
            # Multiple matches - 412 Precondition Failed
            outcome = OperationOutcome.error(
                f"Conditional update failed: {total} resources match the criteria",
                code="multiple-matches",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=412,
                media_type=FHIR_JSON,
            )

    @router.put("/{resource_type}/{resource_id}", tags=["Update"])
    async def update(
        request: Request,
        resource_type: str,
        resource_id: str,
    ) -> Response:
        """Update an existing resource or create with specific ID.

        If the resource exists, updates it and increments version.
        If not, creates it with the specified ID.
        """
        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        try:
            body = await request.json()
        except Exception as e:
            outcome = OperationOutcome.error(f"Invalid JSON: {e}", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Validate resource type
        if body.get("resourceType") != resource_type:
            outcome = OperationOutcome.error(
                f"Resource type in body ({body.get('resourceType')}) does not match URL ({resource_type})",
                code="invalid",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Validate ID matches
        if body.get("id") and body.get("id") != resource_id:
            outcome = OperationOutcome.error(
                f"Resource ID in body ({body.get('id')}) does not match URL ({resource_id})",
                code="invalid",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Check if creating or updating
        existing = store.read(resource_type, resource_id)
        is_create = existing is None

        # Update or create
        updated = store.update(resource_type, resource_id, body)
        version = updated.get("meta", {}).get("versionId", "1")

        return JSONResponse(
            content=updated,
            status_code=201 if is_create else 200,
            media_type=FHIR_JSON,
            headers={
                "Location": f"{get_base_url(request)}/{resource_type}/{resource_id}",
                "ETag": f'W/"{version}"',
            },
        )

    @router.patch("/{resource_type}/{resource_id}", tags=["Update"])
    async def patch(
        request: Request,
        resource_type: str,
        resource_id: str,
    ) -> Response:
        """Apply partial updates to a resource using JSON Patch (RFC 6902).

        Accepts a list of JSON Patch operations and applies them to the resource.
        Returns the updated resource with an incremented version.

        Supported operations:
        - add: Add a value at a path
        - remove: Remove a value at a path
        - replace: Replace a value at a path
        - move: Move a value from one path to another
        - copy: Copy a value from one path to another
        - test: Test that a value equals the expected value

        Example request body:
        [
            {"op": "replace", "path": "/active", "value": false},
            {"op": "add", "path": "/telecom/-", "value": {"system": "email", "value": "new@example.com"}}
        ]
        """
        from .patch import PatchError, apply_json_patch

        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Read existing resource
        existing = store.read(resource_type, resource_id)
        if not existing:
            outcome = OperationOutcome.not_found(resource_type, resource_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        # Parse patch operations
        try:
            operations = await request.json()
        except Exception as e:
            outcome = OperationOutcome.error(f"Invalid JSON: {e}", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        if not isinstance(operations, list):
            outcome = OperationOutcome.error(
                "Patch body must be a JSON array of operations",
                code="invalid",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Apply patch operations
        try:
            patched = apply_json_patch(existing, operations)
        except PatchError as e:
            # Determine status code based on error type
            if "Test failed" in e.message:
                status_code = 409  # Conflict - test operation failed
            else:
                status_code = 422  # Unprocessable Entity - invalid patch
            outcome = OperationOutcome.error(e.message, code="processing")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=status_code,
                media_type=FHIR_JSON,
            )

        # Validate immutable fields weren't modified
        if patched.get("id") != resource_id:
            outcome = OperationOutcome.error(
                "Cannot modify resource id via PATCH",
                code="processing",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=422,
                media_type=FHIR_JSON,
            )

        if patched.get("resourceType") != resource_type:
            outcome = OperationOutcome.error(
                "Cannot modify resourceType via PATCH",
                code="processing",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=422,
                media_type=FHIR_JSON,
            )

        # Update resource
        updated = store.update(resource_type, resource_id, patched)
        version = updated.get("meta", {}).get("versionId", "1")

        return JSONResponse(
            content=updated,
            status_code=200,
            media_type=FHIR_JSON,
            headers={
                "ETag": f'W/"{version}"',
            },
        )

    @router.delete("/{resource_type}", tags=["Conditional Delete"])
    async def conditional_delete(
        request: Request,
        resource_type: str,
    ) -> Response:
        """Delete resources by search criteria (conditional delete).

        Search parameters are provided as query parameters.
        Deletes all resources that match the criteria.
        Returns 204 No Content on success.
        """
        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Get search params from query string
        search_params: dict[str, Any] = {}
        for key, value in request.query_params.multi_items():
            if key.startswith("_"):
                continue  # Skip special params
            if key in search_params:
                existing = search_params[key]
                if isinstance(existing, list):
                    existing.append(value)
                else:
                    search_params[key] = [existing, value]
            else:
                search_params[key] = value

        if not search_params:
            outcome = OperationOutcome.error(
                "Conditional delete requires search parameters to prevent accidental deletion of all resources",
                code="required",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Search for matching resources
        matches, total = store.search(resource_type, search_params, _count=10000, _offset=0)

        # Delete all matches
        deleted_count = 0
        for resource in matches:
            if store.delete(resource_type, resource["id"]):
                deleted_count += 1

        # Return 204 regardless of whether any were deleted (FHIR spec)
        return Response(status_code=204)

    @router.delete("/{resource_type}/{resource_id}", tags=["Delete"])
    async def delete(
        request: Request,
        resource_type: str,
        resource_id: str,
    ) -> Response:
        """Delete a resource.

        Returns 204 No Content on success, 404 if not found.
        """
        if resource_type not in SUPPORTED_TYPES:
            outcome = OperationOutcome.error(
                f"Resource type '{resource_type}' is not supported",
                code="not-supported",
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        deleted = store.delete(resource_type, resource_id)
        if not deleted:
            outcome = OperationOutcome.not_found(resource_type, resource_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        return Response(status_code=204)

    # =========================================================================
    # Batch/Transaction
    # =========================================================================

    @router.post("/", tags=["Batch"])
    async def batch_transaction(request: Request) -> Response:
        """Process a batch or transaction Bundle.

        Processes all entries in the bundle and returns results.
        """
        try:
            body = await request.json()
        except Exception as e:
            outcome = OperationOutcome.error(f"Invalid JSON: {e}", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        if body.get("resourceType") != "Bundle":
            outcome = OperationOutcome.error("Expected a Bundle resource", code="invalid")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        bundle_type = body.get("type")
        if bundle_type not in ("batch", "transaction"):
            outcome = OperationOutcome.error(
                f"Bundle type must be 'batch' or 'transaction', got '{bundle_type}'", code="invalid"
            )
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        entries = body.get("entry", [])
        response_entries = []

        for entry in entries:
            resource = entry.get("resource")
            req = entry.get("request", {})
            method = req.get("method", "").upper()
            url = req.get("url", "")

            # Parse URL to get resource type and ID
            url_parts = url.strip("/").split("/")
            resource_type = url_parts[0] if url_parts else ""
            resource_id = url_parts[1] if len(url_parts) > 1 else None

            response_entry: dict[str, Any] = {"response": {}}

            try:
                if method == "GET":
                    if resource_id:
                        result = store.read(resource_type, resource_id)
                        if result:
                            response_entry["resource"] = result
                            response_entry["response"]["status"] = "200 OK"
                        else:
                            response_entry["response"]["status"] = "404 Not Found"
                    else:
                        # Search - simplified
                        resources, total = store.search(resource_type, {})
                        response_entry["resource"] = {
                            "resourceType": "Bundle",
                            "type": "searchset",
                            "total": total,
                            "entry": [{"resource": r} for r in resources[:100]],
                        }
                        response_entry["response"]["status"] = "200 OK"

                elif method == "POST":
                    if resource and resource_type:
                        created = store.create(resource)
                        response_entry["resource"] = created
                        response_entry["response"]["status"] = "201 Created"
                        response_entry["response"]["location"] = f"{resource_type}/{created['id']}"
                    else:
                        response_entry["response"]["status"] = "400 Bad Request"

                elif method == "PUT":
                    if resource and resource_type and resource_id:
                        updated = store.update(resource_type, resource_id, resource)
                        response_entry["resource"] = updated
                        response_entry["response"]["status"] = "200 OK"
                    else:
                        response_entry["response"]["status"] = "400 Bad Request"

                elif method == "DELETE":
                    if resource_type and resource_id:
                        deleted = store.delete(resource_type, resource_id)
                        response_entry["response"]["status"] = "204 No Content" if deleted else "404 Not Found"
                    else:
                        response_entry["response"]["status"] = "400 Bad Request"

                else:
                    response_entry["response"]["status"] = "400 Bad Request"

            except Exception as e:
                response_entry["response"]["status"] = "500 Internal Server Error"
                response_entry["response"]["outcome"] = OperationOutcome.error(str(e)).model_dump(exclude_none=True)

            response_entries.append(response_entry)

        response_bundle = {
            "resourceType": "Bundle",
            "id": str(uuid.uuid4()),
            "type": "batch-response" if bundle_type == "batch" else "transaction-response",
            "entry": response_entries,
        }

        return JSONResponse(content=response_bundle, media_type=FHIR_JSON)

    return router
