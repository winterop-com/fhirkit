"""Bulk Data Export implementation for FHIR Bulk Data Access IG.

This module provides async bulk data export operations for exporting
large amounts of FHIR data in NDJSON format.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class ExportJob:
    """Represents a bulk export job."""

    id: str
    status: str  # accepted, in-progress, complete, error
    request_time: datetime
    resource_types: list[str]
    patient_ids: list[str] | None
    since: datetime | None
    output_files: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    error: str | None = None
    progress: int = 0


# In-memory job storage
export_jobs: dict[str, ExportJob] = {}


def create_export_job(
    resource_types: list[str],
    patient_ids: list[str] | None = None,
    since: datetime | None = None,
) -> ExportJob:
    """Create a new export job.

    Args:
        resource_types: List of resource types to export
        patient_ids: Optional list of patient IDs to filter by
        since: Optional datetime to filter by lastUpdated

    Returns:
        The created ExportJob
    """
    job_id = str(uuid.uuid4())
    job = ExportJob(
        id=job_id,
        status="accepted",
        request_time=datetime.now(UTC),
        resource_types=resource_types,
        patient_ids=patient_ids,
        since=since,
    )
    export_jobs[job_id] = job
    return job


async def run_export(job: ExportJob, store: Any) -> None:
    """Run the export job asynchronously.

    Args:
        job: The export job to run
        store: The FHIRStore instance to read from
    """
    try:
        job.status = "in-progress"
        total_types = len(job.resource_types)

        for idx, resource_type in enumerate(job.resource_types):
            # Update progress
            job.progress = int((idx / total_types) * 100)

            # Get all resources of this type
            resources = store.get_all_resources(resource_type)

            # Filter by patient IDs if specified
            if job.patient_ids:
                filtered = []
                for resource in resources:
                    # Check if resource is related to any of the patients
                    if resource_type == "Patient":
                        if resource.get("id") in job.patient_ids:
                            filtered.append(resource)
                    else:
                        # Check reference fields
                        if _is_related_to_patients(resource, job.patient_ids):
                            filtered.append(resource)
                resources = filtered

            # Filter by _since if specified
            if job.since:
                resources = [r for r in resources if _resource_updated_after(r, job.since)]

            # Store resources for this type
            if resources:
                job.output_files[resource_type] = resources

        job.status = "complete"
        job.progress = 100

    except Exception as e:
        job.status = "error"
        job.error = str(e)


def _is_related_to_patients(resource: dict[str, Any], patient_ids: list[str]) -> bool:
    """Check if a resource is related to any of the given patients.

    Args:
        resource: The resource to check
        patient_ids: List of patient IDs

    Returns:
        True if the resource references any of the patients
    """
    # Check common reference fields
    subject = resource.get("subject", {})
    patient = resource.get("patient", {})

    subject_ref = subject.get("reference", "") if isinstance(subject, dict) else ""
    patient_ref = patient.get("reference", "") if isinstance(patient, dict) else ""

    for pid in patient_ids:
        if f"Patient/{pid}" in subject_ref or f"Patient/{pid}" in patient_ref:
            return True

    return False


def _resource_updated_after(resource: dict[str, Any], since: datetime) -> bool:
    """Check if a resource was updated after the given datetime.

    Args:
        resource: The resource to check
        since: The datetime to compare against

    Returns:
        True if the resource was updated after 'since'
    """
    last_updated = resource.get("meta", {}).get("lastUpdated")
    if not last_updated:
        return True  # If no lastUpdated, include it

    try:
        # Parse ISO datetime
        resource_time = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
        return resource_time >= since
    except (ValueError, TypeError):
        return True


def get_export_job(job_id: str) -> ExportJob | None:
    """Get an export job by ID.

    Args:
        job_id: The job ID

    Returns:
        The ExportJob or None if not found
    """
    return export_jobs.get(job_id)


def delete_export_job(job_id: str) -> bool:
    """Delete an export job.

    Args:
        job_id: The job ID

    Returns:
        True if deleted, False if not found
    """
    if job_id in export_jobs:
        del export_jobs[job_id]
        return True
    return False


def resources_to_ndjson(resources: list[dict[str, Any]]) -> str:
    """Convert a list of resources to NDJSON format.

    Args:
        resources: List of FHIR resources

    Returns:
        NDJSON string (one JSON object per line)
    """
    lines = [json.dumps(r, separators=(",", ":")) for r in resources]
    return "\n".join(lines) + "\n" if lines else ""


# Default resource types for patient export
PATIENT_EXPORT_TYPES = [
    "Patient",
    "Observation",
    "Condition",
    "Encounter",
    "MedicationRequest",
    "Procedure",
    "DiagnosticReport",
    "AllergyIntolerance",
    "Immunization",
    "CarePlan",
    "Goal",
    "ServiceRequest",
    "DocumentReference",
]

# All exportable resource types
ALL_EXPORT_TYPES = [
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
    "Group",
]
