"""FHIR REST API routes."""

import uuid
from datetime import datetime, timezone
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
)
from ..storage.fhir_store import FHIRStore

# FHIR content type
FHIR_JSON = "application/fhir+json"

# Supported resource types
SUPPORTED_TYPES = [
    "Patient",
    "Practitioner",
    "Organization",
    "Encounter",
    "Condition",
    "Observation",
    "MedicationRequest",
    "Procedure",
    "DiagnosticReport",
    "AllergyIntolerance",
    "Immunization",
    "CarePlan",
    "Goal",
    "ServiceRequest",
    "DocumentReference",
    "Medication",
    "Measure",
    "MeasureReport",
    "ValueSet",
    "CodeSystem",
    "Library",
]

# Summary elements per resource type (per FHIR spec)
SUMMARY_ELEMENTS: dict[str, list[str]] = {
    "Patient": ["identifier", "active", "name", "telecom", "gender", "birthDate", "address"],
    "Practitioner": ["identifier", "active", "name", "telecom", "address"],
    "Organization": ["identifier", "active", "name", "type", "telecom", "address"],
    "Encounter": ["identifier", "status", "class", "type", "subject", "period"],
    "Condition": ["identifier", "clinicalStatus", "verificationStatus", "code", "subject", "onsetDateTime"],
    "Observation": ["identifier", "status", "category", "code", "subject", "effectiveDateTime", "valueQuantity"],
    "MedicationRequest": ["identifier", "status", "intent", "medicationCodeableConcept", "subject", "authoredOn"],
    "Procedure": ["identifier", "status", "code", "subject", "performedDateTime", "performedPeriod"],
    "DiagnosticReport": ["identifier", "status", "category", "code", "subject", "effectiveDateTime", "issued"],
    "AllergyIntolerance": ["identifier", "clinicalStatus", "verificationStatus", "code", "patient", "onsetDateTime"],
    "Immunization": ["identifier", "status", "vaccineCode", "patient", "occurrenceDateTime"],
    "CarePlan": ["identifier", "status", "intent", "category", "subject", "period"],
    "Goal": ["identifier", "lifecycleStatus", "category", "description", "subject"],
    "ServiceRequest": ["identifier", "status", "intent", "code", "subject", "authoredOn"],
    "DocumentReference": ["identifier", "status", "type", "subject", "date", "author"],
    "Medication": ["identifier", "code", "status"],
    "Measure": ["identifier", "url", "name", "status", "title", "date"],
    "MeasureReport": ["identifier", "status", "type", "measure", "subject", "date"],
    "ValueSet": ["identifier", "url", "name", "status", "title"],
    "CodeSystem": ["identifier", "url", "name", "status", "title"],
    "Library": ["identifier", "url", "name", "status", "title", "date"],
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

        from fhir_cql.engine.cql.evaluator import CQLEvaluator
        from fhir_cql.engine.cql.measure import MeasureEvaluator, MeasureScoring

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
                # TODO: Handle Group members
                pass
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
        bundle = Bundle(
            resourceType="Bundle",
            id=str(uuid.uuid4()),
            type="searchset",
            total=total,  # Total is primary results only
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

        resource = store.read(resource_type, resource_id)
        if resource is None:
            outcome = OperationOutcome.not_found(resource_type, resource_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        # Set ETag header
        version = resource.get("meta", {}).get("versionId", "1")
        return JSONResponse(
            content=resource,
            media_type=FHIR_JSON,
            headers={"ETag": f'W/"{version}"'},
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
    # Terminology Operations
    # =========================================================================

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

        Expands the ValueSet to include all codes.
        Supports filtering by code/display text.
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

        # Find ValueSet by URL
        valuesets, _ = store.search("ValueSet", {"url": url})
        if not valuesets:
            outcome = OperationOutcome.error(f"ValueSet not found: {url}", code="not-found")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        valueset = valuesets[0]

        # Extract codes from compose
        codes = []
        compose = valueset.get("compose", {})
        for include in compose.get("include", []):
            system = include.get("system", "")
            for concept in include.get("concept", []):
                codes.append(
                    {
                        "system": system,
                        "code": concept.get("code"),
                        "display": concept.get("display"),
                    }
                )

        # Apply filter if specified
        if filter:
            filter_lower = filter.lower()
            codes = [
                c
                for c in codes
                if filter_lower in (c.get("display", "").lower()) or filter_lower in (c.get("code", "").lower())
            ]

        # Apply pagination
        total = len(codes)
        codes = codes[offset : offset + count]

        # Build expansion
        expansion = {
            "resourceType": "ValueSet",
            "id": valueset.get("id"),
            "url": url,
            "status": valueset.get("status", "active"),
            "expansion": {
                "identifier": f"urn:uuid:{uuid.uuid4()}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total": total,
                "offset": offset,
                "contains": codes,
            },
        }

        return JSONResponse(content=expansion, media_type=FHIR_JSON)

    @router.get("/ValueSet/{valueset_id}/$expand", tags=["Terminology"])
    async def expand_valueset_by_id(
        request: Request,
        valueset_id: str,
        filter: str | None = Query(default=None),
        count: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0),
    ) -> Response:
        """Expand a specific ValueSet by ID."""
        valueset = store.read("ValueSet", valueset_id)
        if valueset is None:
            outcome = OperationOutcome.not_found("ValueSet", valueset_id)
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        # Extract codes
        codes = []
        compose = valueset.get("compose", {})
        for include in compose.get("include", []):
            system = include.get("system", "")
            for concept in include.get("concept", []):
                codes.append(
                    {
                        "system": system,
                        "code": concept.get("code"),
                        "display": concept.get("display"),
                    }
                )

        # Apply filter
        if filter:
            filter_lower = filter.lower()
            codes = [
                c
                for c in codes
                if filter_lower in (c.get("display", "").lower()) or filter_lower in (c.get("code", "").lower())
            ]

        # Pagination
        total = len(codes)
        codes = codes[offset : offset + count]

        expansion = {
            "resourceType": "ValueSet",
            "id": valueset_id,
            "url": valueset.get("url"),
            "status": valueset.get("status", "active"),
            "expansion": {
                "identifier": f"urn:uuid:{uuid.uuid4()}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total": total,
                "offset": offset,
                "contains": codes,
            },
        }

        return JSONResponse(content=expansion, media_type=FHIR_JSON)

    @router.get("/CodeSystem/$lookup", tags=["Terminology"])
    @router.post("/CodeSystem/$lookup", tags=["Terminology"])
    async def lookup_code(
        request: Request,
        system: str | None = Query(default=None),
        code: str | None = Query(default=None),
    ) -> Response:
        """Look up a code in a CodeSystem.

        Returns information about the code including display text.
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
            except Exception:
                pass

        if not system or not code:
            outcome = OperationOutcome.error("Both system and code are required", code="required")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Find CodeSystem by URL
        codesystems, _ = store.search("CodeSystem", {"url": system})
        if not codesystems:
            outcome = OperationOutcome.error(f"CodeSystem not found: {system}", code="not-found")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        codesystem = codesystems[0]

        # Find the code
        for concept in codesystem.get("concept", []):
            if concept.get("code") == code:
                params: list[dict[str, Any]] = [
                    {"name": "name", "valueString": codesystem.get("name")},
                    {"name": "display", "valueString": concept.get("display")},
                    {"name": "code", "valueCode": code},
                    {"name": "system", "valueUri": system},
                ]
                if concept.get("definition"):
                    params.append({"name": "definition", "valueString": concept.get("definition")})
                result = {"resourceType": "Parameters", "parameter": params}
                return JSONResponse(content=result, media_type=FHIR_JSON)

        outcome = OperationOutcome.error(f"Code '{code}' not found in CodeSystem", code="not-found")
        return JSONResponse(
            content=outcome.model_dump(exclude_none=True),
            status_code=404,
            media_type=FHIR_JSON,
        )

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
        """
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
            except Exception:
                pass

        if not url or not code:
            outcome = OperationOutcome.error("ValueSet URL and code are required", code="required")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=400,
                media_type=FHIR_JSON,
            )

        # Find ValueSet
        valuesets, _ = store.search("ValueSet", {"url": url})
        if not valuesets:
            outcome = OperationOutcome.error(f"ValueSet not found: {url}", code="not-found")
            return JSONResponse(
                content=outcome.model_dump(exclude_none=True),
                status_code=404,
                media_type=FHIR_JSON,
            )

        valueset = valuesets[0]

        # Check if code is in ValueSet
        found = False
        display = None
        compose = valueset.get("compose", {})
        for include in compose.get("include", []):
            include_system = include.get("system", "")
            if system and include_system != system:
                continue
            for concept in include.get("concept", []):
                if concept.get("code") == code:
                    found = True
                    display = concept.get("display")
                    break
            if found:
                break

        params: list[dict[str, Any]] = [{"name": "result", "valueBoolean": found}]
        if found and display:
            params.append({"name": "display", "valueString": display})
        if not found:
            params.append({"name": "message", "valueString": f"Code '{code}' not found in ValueSet"})

        result = {"resourceType": "Parameters", "parameter": params}
        return JSONResponse(content=result, media_type=FHIR_JSON)

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
