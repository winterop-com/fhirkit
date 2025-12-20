"""Validation rules for FHIR R4 resources.

This module defines the validation rules for each supported FHIR resource type,
including required fields and code bindings to ValueSets.
"""

from typing import Any

# Valid resource types
VALID_RESOURCE_TYPES = {
    # Administrative
    "Patient",
    "Practitioner",
    "PractitionerRole",
    "Organization",
    "OrganizationAffiliation",
    "Location",
    "RelatedPerson",
    "HealthcareService",
    "Endpoint",
    # Clinical
    "Encounter",
    "EpisodeOfCare",
    "Condition",
    "Observation",
    "Procedure",
    "DiagnosticReport",
    "AllergyIntolerance",
    "Immunization",
    "ClinicalImpression",
    "FamilyMemberHistory",
    "BodyStructure",
    # Imaging
    "ImagingStudy",
    # Medications
    "Medication",
    "MedicationRequest",
    "MedicationAdministration",
    "MedicationStatement",
    "MedicationDispense",
    "MedicationKnowledge",
    # Care Management
    "CarePlan",
    "CareTeam",
    "Goal",
    "Task",
    "RequestGroup",
    "List",
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
    "DeviceDefinition",
    "DeviceMetric",
    # Documents
    "ServiceRequest",
    "DocumentReference",
    "Media",
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
    # Groups
    "Group",
    # Forms & Consent
    "Questionnaire",
    "QuestionnaireResponse",
    "Consent",
    # Communication & Alerts
    "Communication",
    "CommunicationRequest",
    "Flag",
    # Diagnostics
    "Specimen",
    # Orders
    "NutritionOrder",
    # Supply Chain
    "SupplyRequest",
    "SupplyDelivery",
    # Clinical Decision Support
    "RiskAssessment",
    "DetectedIssue",
    # Safety
    "AdverseEvent",
    # Research
    "ResearchStudy",
    "ResearchSubject",
    # Infrastructure
    "Bundle",
    "Binary",
    "OperationOutcome",
    "Parameters",
    "CapabilityStatement",
    "TerminologyCapabilities",
    "Provenance",
    "AuditEvent",
    # Conformance
    "StructureDefinition",
    "SearchParameter",
    "ImplementationGuide",
    "CompartmentDefinition",
    "MessageDefinition",
    "StructureMap",
    "GraphDefinition",
    "NamingSystem",
    "OperationDefinition",
    "Subscription",
    # Messaging
    "MessageHeader",
    # Testing
    "TestScript",
    "TestReport",
    # Verification
    "VerificationResult",
    # Definitions
    "EventDefinition",
    "ObservationDefinition",
    "SpecimenDefinition",
    # Insurance
    "InsurancePlan",
    "EnrollmentRequest",
    "EnrollmentResponse",
    # Linkage
    "Linkage",
    # Device Usage
    "DeviceUseStatement",
    # Administrative
    "Person",
    # Financial (additional)
    "Account",
    "ClaimResponse",
    "CoverageEligibilityRequest",
    "CoverageEligibilityResponse",
    "PaymentNotice",
    "PaymentReconciliation",
    "ChargeItem",
    "ChargeItemDefinition",
    "Contract",
    "Invoice",
    "DocumentManifest",
    # Clinical Workflow
    "ActivityDefinition",
    "PlanDefinition",
    "GuidanceResponse",
    "DeviceRequest",
    # Substances
    "Substance",
    # Immunization
    "ImmunizationRecommendation",
    # Vision
    "VisionPrescription",
    # Scheduling
    "AppointmentResponse",
    # Other
    "Basic",
    # Evidence-Based Medicine
    "Evidence",
    "EvidenceVariable",
    "EffectEvidenceSynthesis",
    "RiskEvidenceSynthesis",
    "ResearchDefinition",
    "ResearchElementDefinition",
    # Laboratory & Genomics
    "MolecularSequence",
    "BiologicallyDerivedProduct",
    # Catalog
    "CatalogEntry",
    # Immunization Assessment
    "ImmunizationEvaluation",
    # Substance Specialized
    "SubstanceNucleicAcid",
    "SubstancePolymer",
    "SubstanceProtein",
    "SubstanceReferenceInformation",
    "SubstanceSourceMaterial",
    "SubstanceSpecification",
    # Workflow Examples
    "ExampleScenario",
}

# Validation rules per resource type
# Each rule defines:
#   - required: list of required field paths (using dot notation for nested)
#   - code_bindings: dict mapping field paths to ValueSet URLs
#   - cardinality: dict mapping field paths to (min, max) where max can be "*"
RESOURCE_RULES: dict[str, dict[str, Any]] = {
    "Patient": {
        "required": [],
        "code_bindings": {
            "gender": {
                "valueset": "http://hl7.org/fhir/ValueSet/administrative-gender",
                "strength": "required",
                "allowed_values": ["male", "female", "other", "unknown"],
            },
            "maritalStatus.coding.code": {
                "valueset": "http://hl7.org/fhir/ValueSet/marital-status",
                "strength": "extensible",
            },
        },
    },
    "Observation": {
        "required": ["status", "code"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/observation-status",
                "strength": "required",
                "allowed_values": [
                    "registered",
                    "preliminary",
                    "final",
                    "amended",
                    "corrected",
                    "cancelled",
                    "entered-in-error",
                    "unknown",
                ],
            },
        },
    },
    "Condition": {
        "required": ["subject"],
        "code_bindings": {
            "clinicalStatus.coding.code": {
                "valueset": "http://hl7.org/fhir/ValueSet/condition-clinical",
                "strength": "required",
                "allowed_values": ["active", "recurrence", "relapse", "inactive", "remission", "resolved"],
            },
            "verificationStatus.coding.code": {
                "valueset": "http://hl7.org/fhir/ValueSet/condition-ver-status",
                "strength": "required",
                "allowed_values": [
                    "unconfirmed",
                    "provisional",
                    "differential",
                    "confirmed",
                    "refuted",
                    "entered-in-error",
                ],
            },
        },
    },
    "Encounter": {
        "required": ["status", "class"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/encounter-status",
                "strength": "required",
                "allowed_values": [
                    "planned",
                    "arrived",
                    "triaged",
                    "in-progress",
                    "onleave",
                    "finished",
                    "cancelled",
                    "entered-in-error",
                    "unknown",
                ],
            },
        },
    },
    "MedicationRequest": {
        "required": ["status", "intent", "medication[x]", "subject"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/medicationrequest-status",
                "strength": "required",
                "allowed_values": [
                    "active",
                    "on-hold",
                    "cancelled",
                    "completed",
                    "entered-in-error",
                    "stopped",
                    "draft",
                    "unknown",
                ],
            },
            "intent": {
                "valueset": "http://hl7.org/fhir/ValueSet/medicationrequest-intent",
                "strength": "required",
                "allowed_values": [
                    "proposal",
                    "plan",
                    "order",
                    "original-order",
                    "reflex-order",
                    "filler-order",
                    "instance-order",
                    "option",
                ],
            },
        },
    },
    "Procedure": {
        "required": ["status", "subject"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/event-status",
                "strength": "required",
                "allowed_values": [
                    "preparation",
                    "in-progress",
                    "not-done",
                    "on-hold",
                    "stopped",
                    "completed",
                    "entered-in-error",
                    "unknown",
                ],
            },
        },
    },
    "DiagnosticReport": {
        "required": ["status", "code"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/diagnostic-report-status",
                "strength": "required",
                "allowed_values": [
                    "registered",
                    "partial",
                    "preliminary",
                    "final",
                    "amended",
                    "corrected",
                    "appended",
                    "cancelled",
                    "entered-in-error",
                    "unknown",
                ],
            },
        },
    },
    "AllergyIntolerance": {
        "required": ["patient"],
        "code_bindings": {
            "clinicalStatus.coding.code": {
                "valueset": "http://hl7.org/fhir/ValueSet/allergyintolerance-clinical",
                "strength": "required",
                "allowed_values": ["active", "inactive", "resolved"],
            },
            "verificationStatus.coding.code": {
                "valueset": "http://hl7.org/fhir/ValueSet/allergyintolerance-verification",
                "strength": "required",
                "allowed_values": ["unconfirmed", "confirmed", "refuted", "entered-in-error"],
            },
        },
    },
    "Immunization": {
        "required": ["status", "vaccineCode", "patient", "occurrence[x]"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/immunization-status",
                "strength": "required",
                "allowed_values": ["completed", "entered-in-error", "not-done"],
            },
        },
    },
    "CarePlan": {
        "required": ["status", "intent", "subject"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/request-status",
                "strength": "required",
                "allowed_values": [
                    "draft",
                    "active",
                    "on-hold",
                    "revoked",
                    "completed",
                    "entered-in-error",
                    "unknown",
                ],
            },
            "intent": {
                "valueset": "http://hl7.org/fhir/ValueSet/care-plan-intent",
                "strength": "required",
                "allowed_values": ["proposal", "plan", "order", "option"],
            },
        },
    },
    "Goal": {
        "required": ["lifecycleStatus", "description", "subject"],
        "code_bindings": {
            "lifecycleStatus": {
                "valueset": "http://hl7.org/fhir/ValueSet/goal-status",
                "strength": "required",
                "allowed_values": [
                    "proposed",
                    "planned",
                    "accepted",
                    "active",
                    "on-hold",
                    "completed",
                    "cancelled",
                    "entered-in-error",
                    "rejected",
                ],
            },
        },
    },
    "ServiceRequest": {
        "required": ["status", "intent", "subject"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/request-status",
                "strength": "required",
                "allowed_values": [
                    "draft",
                    "active",
                    "on-hold",
                    "revoked",
                    "completed",
                    "entered-in-error",
                    "unknown",
                ],
            },
            "intent": {
                "valueset": "http://hl7.org/fhir/ValueSet/request-intent",
                "strength": "required",
                "allowed_values": [
                    "proposal",
                    "plan",
                    "directive",
                    "order",
                    "original-order",
                    "reflex-order",
                    "filler-order",
                    "instance-order",
                    "option",
                ],
            },
        },
    },
    "DocumentReference": {
        "required": ["status", "content"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/document-reference-status",
                "strength": "required",
                "allowed_values": ["current", "superseded", "entered-in-error"],
            },
        },
    },
    "Medication": {
        "required": [],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/medication-status",
                "strength": "required",
                "allowed_values": ["active", "inactive", "entered-in-error"],
            },
        },
    },
    "Practitioner": {
        "required": [],
        "code_bindings": {
            "gender": {
                "valueset": "http://hl7.org/fhir/ValueSet/administrative-gender",
                "strength": "required",
                "allowed_values": ["male", "female", "other", "unknown"],
            },
        },
    },
    "Organization": {
        "required": [],
        "code_bindings": {},
    },
    "Measure": {
        "required": ["status"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/publication-status",
                "strength": "required",
                "allowed_values": ["draft", "active", "retired", "unknown"],
            },
        },
    },
    "MeasureReport": {
        "required": ["status", "type", "measure"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/measure-report-status",
                "strength": "required",
                "allowed_values": ["complete", "pending", "error"],
            },
            "type": {
                "valueset": "http://hl7.org/fhir/ValueSet/measure-report-type",
                "strength": "required",
                "allowed_values": [
                    "individual",
                    "subject-list",
                    "summary",
                    "data-collection",
                ],
            },
        },
    },
    "ValueSet": {
        "required": ["status"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/publication-status",
                "strength": "required",
                "allowed_values": ["draft", "active", "retired", "unknown"],
            },
        },
    },
    "CodeSystem": {
        "required": ["status", "content"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/publication-status",
                "strength": "required",
                "allowed_values": ["draft", "active", "retired", "unknown"],
            },
            "content": {
                "valueset": "http://hl7.org/fhir/ValueSet/codesystem-content-mode",
                "strength": "required",
                "allowed_values": ["not-present", "example", "fragment", "complete", "supplement"],
            },
        },
    },
    "ConceptMap": {
        "required": ["status"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/publication-status",
                "strength": "required",
                "allowed_values": ["draft", "active", "retired", "unknown"],
            },
        },
    },
    "Composition": {
        "required": ["status", "type", "date", "author", "title"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/composition-status",
                "strength": "required",
                "allowed_values": ["preliminary", "final", "amended", "entered-in-error"],
            },
        },
    },
    "Library": {
        "required": ["status", "type"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/publication-status",
                "strength": "required",
                "allowed_values": ["draft", "active", "retired", "unknown"],
            },
        },
    },
    "Bundle": {
        "required": ["type"],
        "code_bindings": {
            "type": {
                "valueset": "http://hl7.org/fhir/ValueSet/bundle-type",
                "strength": "required",
                "allowed_values": [
                    "document",
                    "message",
                    "transaction",
                    "transaction-response",
                    "batch",
                    "batch-response",
                    "history",
                    "searchset",
                    "collection",
                ],
            },
        },
    },
    "Binary": {
        "required": ["contentType"],
        "code_bindings": {},
    },
    "Group": {
        "required": ["type", "actual"],
        "code_bindings": {
            "type": {
                "valueset": "http://hl7.org/fhir/ValueSet/group-type",
                "strength": "required",
                "allowed_values": ["person", "animal", "practitioner", "device", "medication", "substance"],
            },
        },
    },
    # === New Resource Types ===
    "Coverage": {
        "required": ["status", "beneficiary"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/fm-status",
                "strength": "required",
                "allowed_values": ["active", "cancelled", "draft", "entered-in-error"],
            },
        },
    },
    "Claim": {
        "required": ["status", "type", "use", "patient", "provider", "priority"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/fm-status",
                "strength": "required",
                "allowed_values": ["active", "cancelled", "draft", "entered-in-error"],
            },
            "use": {
                "valueset": "http://hl7.org/fhir/ValueSet/claim-use",
                "strength": "required",
                "allowed_values": ["claim", "preauthorization", "predetermination"],
            },
        },
    },
    "ExplanationOfBenefit": {
        "required": ["status", "type", "use", "patient", "outcome"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/explanationofbenefit-status",
                "strength": "required",
                "allowed_values": ["active", "cancelled", "draft", "entered-in-error"],
            },
            "use": {
                "valueset": "http://hl7.org/fhir/ValueSet/claim-use",
                "strength": "required",
                "allowed_values": ["claim", "preauthorization", "predetermination"],
            },
            "outcome": {
                "valueset": "http://hl7.org/fhir/ValueSet/remittance-outcome",
                "strength": "required",
                "allowed_values": ["queued", "complete", "error", "partial"],
            },
        },
    },
    "Device": {
        "required": [],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/device-status",
                "strength": "required",
                "allowed_values": ["active", "inactive", "entered-in-error", "unknown"],
            },
        },
    },
    "Location": {
        "required": [],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/location-status",
                "strength": "required",
                "allowed_values": ["active", "suspended", "inactive"],
            },
            "mode": {
                "valueset": "http://hl7.org/fhir/ValueSet/location-mode",
                "strength": "required",
                "allowed_values": ["instance", "kind"],
            },
        },
    },
    "Slot": {
        "required": ["schedule", "status", "start", "end"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/slotstatus",
                "strength": "required",
                "allowed_values": ["busy", "free", "busy-unavailable", "busy-tentative", "entered-in-error"],
            },
        },
    },
    "Appointment": {
        "required": ["status", "participant"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/appointmentstatus",
                "strength": "required",
                "allowed_values": [
                    "proposed",
                    "pending",
                    "booked",
                    "arrived",
                    "fulfilled",
                    "cancelled",
                    "noshow",
                    "entered-in-error",
                    "checked-in",
                    "waitlist",
                ],
            },
        },
    },
    "Schedule": {
        "required": ["actor"],
        "code_bindings": {},
    },
    "PractitionerRole": {
        "required": [],
        "code_bindings": {},
    },
    "RelatedPerson": {
        "required": ["patient"],
        "code_bindings": {
            "gender": {
                "valueset": "http://hl7.org/fhir/ValueSet/administrative-gender",
                "strength": "required",
                "allowed_values": ["male", "female", "other", "unknown"],
            },
        },
    },
    "CareTeam": {
        "required": [],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/care-team-status",
                "strength": "required",
                "allowed_values": ["proposed", "active", "suspended", "inactive", "entered-in-error"],
            },
        },
    },
    "Task": {
        "required": ["status", "intent"],
        "code_bindings": {
            "status": {
                "valueset": "http://hl7.org/fhir/ValueSet/task-status",
                "strength": "required",
                "allowed_values": [
                    "draft",
                    "requested",
                    "received",
                    "accepted",
                    "rejected",
                    "ready",
                    "cancelled",
                    "in-progress",
                    "on-hold",
                    "failed",
                    "completed",
                    "entered-in-error",
                ],
            },
            "intent": {
                "valueset": "http://hl7.org/fhir/ValueSet/task-intent",
                "strength": "required",
                "allowed_values": [
                    "unknown",
                    "proposal",
                    "plan",
                    "order",
                    "original-order",
                    "reflex-order",
                    "filler-order",
                    "instance-order",
                    "option",
                ],
            },
        },
    },
}


def get_rules(resource_type: str) -> dict[str, Any]:
    """Get validation rules for a resource type.

    Args:
        resource_type: The FHIR resource type

    Returns:
        Validation rules dict, or empty rules if not defined
    """
    return RESOURCE_RULES.get(
        resource_type,
        {
            "required": [],
            "code_bindings": {},
        },
    )
