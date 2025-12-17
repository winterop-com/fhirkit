"""FHIR synthetic data generators.

This module provides generators for creating realistic synthetic FHIR data
using Faker for randomization and clinical code templates.
"""

from .adverse_event import AdverseEventGenerator
from .allergy_intolerance import AllergyIntoleranceGenerator
from .appointment import AppointmentGenerator
from .audit_event import AuditEventGenerator
from .base import FHIRResourceGenerator
from .binary import BinaryGenerator
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

# Orchestrator (in separate module)
from .patient_record import PatientRecordGenerator
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
    # Documents & Binary
    "ServiceRequestGenerator",
    "DocumentReferenceGenerator",
    "MediaGenerator",
    "BinaryGenerator",
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
