"""IPS (International Patient Summary) $summary operation implementation.

Generates IPS-compliant Document bundles for patients following the HL7 IPS IG.
http://hl7.org/fhir/uv/ips/
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from ..storage.fhir_store import FHIRStore

# IPS Section LOINC codes per HL7 IPS IG
IPS_SECTIONS = {
    "allergies": {
        "code": "48765-2",
        "display": "Allergies and adverse reactions Document",
        "title": "Allergies and Intolerances",
        "resource_type": "AllergyIntolerance",
    },
    "medications": {
        "code": "10160-0",
        "display": "History of Medication use Narrative",
        "title": "Medication Summary",
        "resource_type": "MedicationRequest",
    },
    "problems": {
        "code": "11450-4",
        "display": "Problem list - Reported",
        "title": "Active Problems",
        "resource_type": "Condition",
    },
    "immunizations": {
        "code": "11369-6",
        "display": "History of Immunization Narrative",
        "title": "Immunizations",
        "resource_type": "Immunization",
    },
    "procedures": {
        "code": "47519-4",
        "display": "History of Procedures Document",
        "title": "History of Procedures",
        "resource_type": "Procedure",
    },
    "results": {
        "code": "30954-2",
        "display": "Relevant diagnostic tests/laboratory data Narrative",
        "title": "Results",
        "resource_type": "Observation",
        "category": "laboratory",
    },
    "vital_signs": {
        "code": "8716-3",
        "display": "Vital signs",
        "title": "Vital Signs",
        "resource_type": "Observation",
        "category": "vital-signs",
    },
}

IPS_PROFILE = "http://hl7.org/fhir/uv/ips/StructureDefinition/Bundle-uv-ips"
IPS_COMPOSITION_PROFILE = "http://hl7.org/fhir/uv/ips/StructureDefinition/Composition-uv-ips"


class IPSSummaryGenerator:
    """Generator for IPS Document bundles.

    Implements the FHIR Patient $summary operation per IPS IG:
    http://hl7.org/fhir/uv/ips/OperationDefinition/summary
    """

    def __init__(self, store: FHIRStore):
        """Initialize the IPS summary generator.

        Args:
            store: FHIR store containing resources
        """
        self.store = store

    def generate(self, patient_id: str, persist: bool = False) -> dict[str, Any] | None:
        """Generate an IPS Document bundle for a patient.

        Args:
            patient_id: The ID of the Patient resource
            persist: Whether to persist the generated Bundle

        Returns:
            IPS Document Bundle, or None if Patient not found
        """
        # Get the patient
        patient = self.store.read("Patient", patient_id)
        if patient is None:
            return None

        # Gather clinical data
        clinical_data = self._gather_clinical_data(patient_id)

        # Build IPS Composition
        composition = self._build_composition(patient, clinical_data)

        # Build Document Bundle
        bundle = self._build_bundle(patient, composition, clinical_data)

        # Optionally persist
        if persist:
            self.store.create(bundle)

        return bundle

    def _gather_clinical_data(self, patient_id: str) -> dict[str, list[dict[str, Any]]]:
        """Gather all clinical data for the patient.

        Args:
            patient_id: The patient ID

        Returns:
            Dictionary mapping section keys to resource lists
        """
        data: dict[str, list[dict[str, Any]]] = {}
        patient_ref = f"Patient/{patient_id}"

        # Allergies
        allergies, _ = self.store.search("AllergyIntolerance", {"patient": patient_ref}, _count=100)
        data["allergies"] = allergies

        # Medications
        medications, _ = self.store.search("MedicationRequest", {"patient": patient_ref}, _count=100)
        data["medications"] = medications

        # Problems/Conditions
        conditions, _ = self.store.search("Condition", {"patient": patient_ref}, _count=100)
        data["problems"] = conditions

        # Immunizations
        immunizations, _ = self.store.search("Immunization", {"patient": patient_ref}, _count=100)
        data["immunizations"] = immunizations

        # Procedures
        procedures, _ = self.store.search("Procedure", {"patient": patient_ref}, _count=100)
        data["procedures"] = procedures

        # Lab Results
        lab_results, _ = self.store.search(
            "Observation",
            {"patient": patient_ref, "category": "laboratory"},
            _count=100,
        )
        data["results"] = lab_results

        # Vital Signs
        vital_signs, _ = self.store.search(
            "Observation",
            {"patient": patient_ref, "category": "vital-signs"},
            _count=50,
        )
        data["vital_signs"] = vital_signs

        return data

    def _build_composition(
        self, patient: dict[str, Any], clinical_data: dict[str, list[dict[str, Any]]]
    ) -> dict[str, Any]:
        """Build the IPS Composition resource.

        Args:
            patient: The Patient resource
            clinical_data: Dictionary of clinical data by section

        Returns:
            IPS Composition resource
        """
        patient_id = patient.get("id", "")
        patient_name = self._get_patient_name(patient)

        composition_id = str(uuid.uuid4())

        composition: dict[str, Any] = {
            "resourceType": "Composition",
            "id": composition_id,
            "meta": {
                "profile": [IPS_COMPOSITION_PROFILE],
            },
            "status": "final",
            "type": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "60591-5",
                        "display": "Patient summary Document",
                    }
                ]
            },
            "subject": {"reference": f"Patient/{patient_id}", "display": patient_name},
            "date": datetime.now(timezone.utc).isoformat(),
            "author": [
                {
                    "reference": "Device/fhirkit-server",
                    "display": "FHIRKit Server",
                }
            ],
            "title": f"International Patient Summary for {patient_name}",
            "confidentiality": "N",
            "section": [],
        }

        # Build sections
        for section_key, section_info in IPS_SECTIONS.items():
            resources = clinical_data.get(section_key, [])
            section = self._build_section(section_info, resources)
            composition["section"].append(section)

        return composition

    def _build_section(self, section_info: dict[str, str], resources: list[dict[str, Any]]) -> dict[str, Any]:
        """Build an IPS section.

        Args:
            section_info: Section metadata (code, display, title)
            resources: Resources to include in the section

        Returns:
            Composition section dictionary
        """
        section: dict[str, Any] = {
            "title": section_info["title"],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": section_info["code"],
                        "display": section_info["display"],
                    }
                ]
            },
        }

        if resources:
            # Add entries
            section["entry"] = []
            for resource in resources:
                resource_type = resource.get("resourceType", "")
                resource_id = resource.get("id", "")
                section["entry"].append({"reference": f"{resource_type}/{resource_id}"})

            # Generate narrative
            section["text"] = self._generate_section_narrative(section_info, resources)
        else:
            # Empty section with appropriate narrative
            section["emptyReason"] = {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/list-empty-reason",
                        "code": "unavailable",
                        "display": "Unavailable",
                    }
                ]
            }
            title_lower = section_info["title"].lower()
            section["text"] = {
                "status": "generated",
                "div": f'<div xmlns="http://www.w3.org/1999/xhtml"><p>No {title_lower} on file.</p></div>',
            }

        return section

    def _generate_section_narrative(
        self, section_info: dict[str, str], resources: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Generate narrative for a section.

        Args:
            section_info: Section metadata
            resources: Resources in the section

        Returns:
            Narrative dictionary with status and div
        """
        items = []
        resource_type = section_info.get("resource_type", "")

        for resource in resources[:20]:  # Limit narrative to 20 items
            display = self._get_resource_display(resource, resource_type)
            if display:
                items.append(f"<li>{display}</li>")

        if not items:
            html = f"<p>No {section_info['title'].lower()} recorded.</p>"
        else:
            html = f"<ul>{''.join(items)}</ul>"
            if len(resources) > 20:
                html += f"<p>... and {len(resources) - 20} more</p>"

        return {
            "status": "generated",
            "div": f'<div xmlns="http://www.w3.org/1999/xhtml">{html}</div>',
        }

    def _get_resource_display(self, resource: dict[str, Any], resource_type: str) -> str:
        """Get display text for a resource.

        Args:
            resource: The FHIR resource
            resource_type: Type of resource

        Returns:
            Human-readable display string
        """
        if resource_type == "AllergyIntolerance":
            code = resource.get("code", {})
            text = code.get("text") or self._get_coding_display(code)
            severity = resource.get("criticality", "")
            return f"{text}" + (f" ({severity})" if severity else "")

        elif resource_type == "MedicationRequest":
            med = resource.get("medicationCodeableConcept", {})
            text = med.get("text") or self._get_coding_display(med)
            status = resource.get("status", "")
            return f"{text}" + (f" - {status}" if status else "")

        elif resource_type == "Condition":
            code = resource.get("code", {})
            text = code.get("text") or self._get_coding_display(code)
            status = resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code", "")
            return f"{text}" + (f" ({status})" if status else "")

        elif resource_type == "Immunization":
            vaccine = resource.get("vaccineCode", {})
            text = vaccine.get("text") or self._get_coding_display(vaccine)
            date = resource.get("occurrenceDateTime", "")[:10] if resource.get("occurrenceDateTime") else ""
            return f"{text}" + (f" ({date})" if date else "")

        elif resource_type == "Procedure":
            code = resource.get("code", {})
            text = code.get("text") or self._get_coding_display(code)
            date = resource.get("performedDateTime", "")[:10] if resource.get("performedDateTime") else ""
            return f"{text}" + (f" ({date})" if date else "")

        elif resource_type == "Observation":
            code = resource.get("code", {})
            text = code.get("text") or self._get_coding_display(code)
            value = self._get_observation_value(resource)
            return f"{text}: {value}" if value else text

        return resource.get("id", "Unknown")

    def _get_coding_display(self, codeable_concept: dict[str, Any]) -> str:
        """Extract display from CodeableConcept."""
        coding = codeable_concept.get("coding", [])
        if coding:
            return coding[0].get("display", coding[0].get("code", ""))
        return ""

    def _get_observation_value(self, observation: dict[str, Any]) -> str:
        """Extract value from Observation."""
        if "valueQuantity" in observation:
            qty = observation["valueQuantity"]
            return f"{qty.get('value', '')} {qty.get('unit', '')}"
        elif "valueCodeableConcept" in observation:
            return self._get_coding_display(observation["valueCodeableConcept"])
        elif "valueString" in observation:
            return observation["valueString"]
        return ""

    def _get_patient_name(self, patient: dict[str, Any]) -> str:
        """Get patient display name."""
        names = patient.get("name", [])
        if names:
            name = names[0]
            given = " ".join(name.get("given", []))
            family = name.get("family", "")
            return f"{given} {family}".strip()
        return "Unknown Patient"

    def _build_bundle(
        self,
        patient: dict[str, Any],
        composition: dict[str, Any],
        clinical_data: dict[str, list[dict[str, Any]]],
    ) -> dict[str, Any]:
        """Build the IPS Document Bundle.

        Args:
            patient: The Patient resource
            composition: The IPS Composition
            clinical_data: Clinical data by section

        Returns:
            IPS Document Bundle
        """
        bundle_id = str(uuid.uuid4())
        entries: list[dict[str, Any]] = []

        # Composition must be first
        entries.append(self._create_entry(composition))

        # Add Patient
        entries.append(self._create_entry(patient))

        # Add all clinical resources
        added_ids: set[str] = {
            f"Composition/{composition['id']}",
            f"Patient/{patient['id']}",
        }

        for section_key, resources in clinical_data.items():
            for resource in resources:
                resource_type = resource.get("resourceType", "")
                resource_id = resource.get("id", "")
                ref = f"{resource_type}/{resource_id}"
                if ref not in added_ids:
                    entries.append(self._create_entry(resource))
                    added_ids.add(ref)

        bundle: dict[str, Any] = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "meta": {
                "profile": [IPS_PROFILE],
                "lastUpdated": datetime.now(timezone.utc).isoformat(),
            },
            "identifier": {
                "system": "urn:ietf:rfc:3986",
                "value": f"urn:uuid:{bundle_id}",
            },
            "type": "document",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entry": entries,
        }

        return bundle

    def _create_entry(self, resource: dict[str, Any]) -> dict[str, Any]:
        """Create a bundle entry."""
        resource_id = resource.get("id", "")

        return {
            "fullUrl": f"urn:uuid:{resource_id}",
            "resource": resource,
        }
