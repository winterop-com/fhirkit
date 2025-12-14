"""FHIR synthetic data generators.

This module provides generators for creating realistic synthetic FHIR data
using Faker for randomization and clinical code templates.
"""

from typing import Any

from faker import Faker

from .adverse_event import AdverseEventGenerator
from .allergy_intolerance import AllergyIntoleranceGenerator
from .appointment import AppointmentGenerator
from .audit_event import AuditEventGenerator
from .base import FHIRResourceGenerator
from .care_team import CareTeamGenerator
from .careplan import CarePlanGenerator
from .claim import ClaimGenerator
from .clinical_impression import ClinicalImpressionGenerator
from .code_system import CodeSystemGenerator
from .communication import CommunicationGenerator
from .composition import CompositionGenerator
from .concept_map import ConceptMapGenerator
from .condition import ConditionGenerator
from .consent import ConsentGenerator
from .coverage import CoverageGenerator
from .detected_issue import DetectedIssueGenerator
from .device import DeviceGenerator
from .diagnostic_report import DiagnosticReportGenerator
from .document_reference import DocumentReferenceGenerator
from .encounter import EncounterGenerator
from .explanation_of_benefit import ExplanationOfBenefitGenerator
from .family_member_history import FamilyMemberHistoryGenerator
from .flag import FlagGenerator
from .goal import GoalGenerator
from .group import GroupGenerator
from .healthcare_service import HealthcareServiceGenerator
from .immunization import ImmunizationGenerator
from .library import LibraryGenerator
from .location import LocationGenerator
from .measure import MeasureGenerator
from .measure_report import MeasureReportGenerator
from .media import MediaGenerator
from .medication import MedicationGenerator
from .medication_administration import MedicationAdministrationGenerator
from .medication_dispense import MedicationDispenseGenerator
from .medication_request import MedicationRequestGenerator
from .medication_statement import MedicationStatementGenerator
from .nutrition_order import NutritionOrderGenerator
from .observation import ObservationGenerator
from .organization import OrganizationGenerator
from .patient import PatientGenerator
from .practitioner import PractitionerGenerator
from .practitioner_role import PractitionerRoleGenerator
from .procedure import ProcedureGenerator
from .provenance import ProvenanceGenerator
from .questionnaire import QuestionnaireGenerator
from .questionnaire_response import QuestionnaireResponseGenerator
from .related_person import RelatedPersonGenerator
from .risk_assessment import RiskAssessmentGenerator
from .schedule import ScheduleGenerator
from .service_request import ServiceRequestGenerator
from .slot import SlotGenerator
from .specimen import SpecimenGenerator
from .task import TaskGenerator
from .value_set import ValueSetGenerator


class PatientRecordGenerator:
    """Generates complete patient records with all related resources.

    This orchestrator creates a patient along with associated encounters,
    conditions, observations, medications, and procedures.
    """

    def __init__(self, seed: int | None = None):
        """Initialize the generator.

        Args:
            seed: Random seed for reproducibility
        """
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
            self.faker.seed_instance(seed)

        self.patient_gen = PatientGenerator(self.faker, seed)
        self.practitioner_gen = PractitionerGenerator(self.faker, seed)
        self.organization_gen = OrganizationGenerator(self.faker, seed)
        self.encounter_gen = EncounterGenerator(self.faker, seed)
        self.condition_gen = ConditionGenerator(self.faker, seed)
        self.observation_gen = ObservationGenerator(self.faker, seed)
        self.medication_gen = MedicationRequestGenerator(self.faker, seed)
        self.procedure_gen = ProcedureGenerator(self.faker, seed)

    def generate_patient_record(
        self,
        num_conditions: tuple[int, int] = (2, 6),
        num_encounters: tuple[int, int] = (3, 10),
        num_observations_per_encounter: tuple[int, int] = (2, 5),
        num_medications: tuple[int, int] = (1, 5),
        num_procedures: tuple[int, int] = (0, 3),
    ) -> list[dict[str, Any]]:
        """Generate a complete patient record with all related resources.

        Args:
            num_conditions: Min/max number of conditions
            num_encounters: Min/max number of encounters
            num_observations_per_encounter: Min/max observations per encounter
            num_medications: Min/max number of active medications
            num_procedures: Min/max number of procedures

        Returns:
            List of all generated FHIR resources
        """
        resources: list[dict[str, Any]] = []

        # Generate supporting resources first
        practitioner = self.practitioner_gen.generate()
        organization = self.organization_gen.generate()
        resources.extend([practitioner, organization])

        practitioner_ref = f"Practitioner/{practitioner['id']}"
        organization_ref = f"Organization/{organization['id']}"

        # Generate patient
        patient = self.patient_gen.generate()
        resources.append(patient)
        patient_ref = f"Patient/{patient['id']}"

        # Generate conditions
        num_cond = self.faker.random_int(min=num_conditions[0], max=num_conditions[1])
        for _ in range(num_cond):
            condition = self.condition_gen.generate(patient_ref=patient_ref)
            resources.append(condition)

        # Generate encounters and associated observations
        num_enc = self.faker.random_int(min=num_encounters[0], max=num_encounters[1])
        for _ in range(num_enc):
            encounter = self.encounter_gen.generate(
                patient_ref=patient_ref,
                practitioner_ref=practitioner_ref,
                organization_ref=organization_ref,
            )
            resources.append(encounter)
            encounter_ref = f"Encounter/{encounter['id']}"

            # Generate observations for this encounter
            num_obs = self.faker.random_int(
                min=num_observations_per_encounter[0],
                max=num_observations_per_encounter[1],
            )

            # Mix of vitals and labs
            for i in range(num_obs):
                obs_type = "vital-signs" if i < num_obs // 2 else "laboratory"
                observation = self.observation_gen.generate(
                    patient_ref=patient_ref,
                    encounter_ref=encounter_ref,
                    observation_type=obs_type,
                    effective_date=encounter["period"]["start"],
                )
                resources.append(observation)

        # Generate medications
        num_meds = self.faker.random_int(min=num_medications[0], max=num_medications[1])
        for _ in range(num_meds):
            medication = self.medication_gen.generate(
                patient_ref=patient_ref,
                practitioner_ref=practitioner_ref,
            )
            resources.append(medication)

        # Generate procedures
        num_procs = self.faker.random_int(min=num_procedures[0], max=num_procedures[1])
        for _ in range(num_procs):
            procedure = self.procedure_gen.generate(
                patient_ref=patient_ref,
                practitioner_ref=practitioner_ref,
            )
            resources.append(procedure)

        return resources

    def generate_population(
        self,
        num_patients: int,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Generate a population of patients with all related resources.

        Args:
            num_patients: Number of patients to generate
            **kwargs: Arguments passed to generate_patient_record

        Returns:
            List of all generated FHIR resources
        """
        all_resources: list[dict[str, Any]] = []

        for _ in range(num_patients):
            patient_resources = self.generate_patient_record(**kwargs)
            all_resources.extend(patient_resources)

        return all_resources


__all__ = [
    # Base
    "FHIRResourceGenerator",
    "PatientRecordGenerator",
    # Administrative
    "PatientGenerator",
    "PractitionerGenerator",
    "PractitionerRoleGenerator",
    "OrganizationGenerator",
    "LocationGenerator",
    "RelatedPersonGenerator",
    # Clinical
    "EncounterGenerator",
    "ConditionGenerator",
    "ObservationGenerator",
    "ProcedureGenerator",
    "DiagnosticReportGenerator",
    "AllergyIntoleranceGenerator",
    "ImmunizationGenerator",
    "ClinicalImpressionGenerator",
    "FamilyMemberHistoryGenerator",
    # Medications
    "MedicationGenerator",
    "MedicationRequestGenerator",
    "MedicationAdministrationGenerator",
    "MedicationStatementGenerator",
    "MedicationDispenseGenerator",
    # Care Management
    "CarePlanGenerator",
    "CareTeamGenerator",
    "GoalGenerator",
    "TaskGenerator",
    # Scheduling
    "AppointmentGenerator",
    "ScheduleGenerator",
    "SlotGenerator",
    "HealthcareServiceGenerator",
    # Financial
    "CoverageGenerator",
    "ClaimGenerator",
    "ExplanationOfBenefitGenerator",
    # Devices
    "DeviceGenerator",
    # Documents
    "ServiceRequestGenerator",
    "DocumentReferenceGenerator",
    "MediaGenerator",
    # Quality Measures
    "MeasureGenerator",
    "MeasureReportGenerator",
    "LibraryGenerator",
    # Terminology
    "ValueSetGenerator",
    "CodeSystemGenerator",
    "ConceptMapGenerator",
    # Documents (Clinical)
    "CompositionGenerator",
    # Groups
    "GroupGenerator",
    # Forms & Consent
    "QuestionnaireGenerator",
    "QuestionnaireResponseGenerator",
    "ConsentGenerator",
    # Communication & Alerts
    "CommunicationGenerator",
    "FlagGenerator",
    # Diagnostics
    "SpecimenGenerator",
    # Orders
    "NutritionOrderGenerator",
    # Clinical Decision Support
    "RiskAssessmentGenerator",
    "DetectedIssueGenerator",
    # Safety
    "AdverseEventGenerator",
    # Infrastructure
    "ProvenanceGenerator",
    "AuditEventGenerator",
]
