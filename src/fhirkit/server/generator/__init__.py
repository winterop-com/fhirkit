"""FHIR synthetic data generators.

This module provides generators for creating realistic synthetic FHIR data
using Faker for randomization and clinical code templates.
"""

from .account import AccountGenerator
from .activity_definition import ActivityDefinitionGenerator
from .adverse_event import AdverseEventGenerator
from .allergy_intolerance import AllergyIntoleranceGenerator
from .appointment import AppointmentGenerator
from .appointment_response import AppointmentResponseGenerator
from .audit_event import AuditEventGenerator
from .base import FHIRResourceGenerator
from .basic import BasicGenerator
from .binary import BinaryGenerator
from .biologically_derived_product import BiologicallyDerivedProductGenerator
from .body_structure import BodyStructureGenerator
from .bundle import BundleGenerator
from .capability_statement import CapabilityStatementGenerator
from .care_team import CareTeamGenerator
from .careplan import CarePlanGenerator
from .catalog_entry import CatalogEntryGenerator
from .charge_item import ChargeItemGenerator
from .charge_item_definition import ChargeItemDefinitionGenerator
from .claim import ClaimGenerator
from .claim_response import ClaimResponseGenerator
from .clinical_impression import ClinicalImpressionGenerator
from .code_system import CodeSystemGenerator
from .communication import CommunicationGenerator
from .communication_request import CommunicationRequestGenerator
from .compartment_definition import CompartmentDefinitionGenerator
from .composition import CompositionGenerator
from .concept_map import ConceptMapGenerator
from .condition import ConditionGenerator
from .consent import ConsentGenerator
from .contract import ContractGenerator
from .coverage import CoverageGenerator
from .coverage_eligibility_request import CoverageEligibilityRequestGenerator
from .coverage_eligibility_response import CoverageEligibilityResponseGenerator
from .detected_issue import DetectedIssueGenerator
from .device import DeviceGenerator
from .device_definition import DeviceDefinitionGenerator
from .device_metric import DeviceMetricGenerator
from .device_request import DeviceRequestGenerator
from .device_use_statement import DeviceUseStatementGenerator
from .diagnostic_report import DiagnosticReportGenerator
from .document_manifest import DocumentManifestGenerator
from .document_reference import DocumentReferenceGenerator

# Phase 4: FMM 0 Resources
from .effect_evidence_synthesis import EffectEvidenceSynthesisGenerator
from .encounter import EncounterGenerator
from .endpoint import EndpointGenerator
from .enrollment_request import EnrollmentRequestGenerator
from .enrollment_response import EnrollmentResponseGenerator
from .episode_of_care import EpisodeOfCareGenerator
from .event_definition import EventDefinitionGenerator
from .evidence import EvidenceGenerator
from .evidence_variable import EvidenceVariableGenerator
from .example_scenario import ExampleScenarioGenerator
from .explanation_of_benefit import ExplanationOfBenefitGenerator
from .family_member_history import FamilyMemberHistoryGenerator
from .flag import FlagGenerator
from .goal import GoalGenerator
from .graph_definition import GraphDefinitionGenerator
from .group import GroupGenerator
from .guidance_response import GuidanceResponseGenerator
from .healthcare_service import HealthcareServiceGenerator
from .imaging_study import ImagingStudyGenerator
from .immunization import ImmunizationGenerator
from .immunization_evaluation import ImmunizationEvaluationGenerator
from .immunization_recommendation import ImmunizationRecommendationGenerator
from .implementation_guide import ImplementationGuideGenerator
from .insurance_plan import InsurancePlanGenerator
from .invoice import InvoiceGenerator
from .library import LibraryGenerator
from .linkage import LinkageGenerator
from .list_resource import ListGenerator
from .location import LocationGenerator
from .measure import MeasureGenerator
from .measure_report import MeasureReportGenerator
from .media import MediaGenerator
from .medication import MedicationGenerator
from .medication_administration import MedicationAdministrationGenerator
from .medication_dispense import MedicationDispenseGenerator
from .medication_knowledge import MedicationKnowledgeGenerator
from .medication_request import MedicationRequestGenerator
from .medication_statement import MedicationStatementGenerator
from .message_definition import MessageDefinitionGenerator
from .message_header import MessageHeaderGenerator
from .molecular_sequence import MolecularSequenceGenerator
from .naming_system import NamingSystemGenerator
from .nutrition_order import NutritionOrderGenerator
from .observation import ObservationGenerator
from .observation_definition import ObservationDefinitionGenerator
from .operation_definition import OperationDefinitionGenerator
from .operation_outcome import OperationOutcomeGenerator
from .organization import OrganizationGenerator
from .organization_affiliation import OrganizationAffiliationGenerator
from .parameters import ParametersGenerator
from .patient import PatientGenerator

# Orchestrator (in separate module)
from .patient_record import PatientRecordGenerator
from .payment_notice import PaymentNoticeGenerator
from .payment_reconciliation import PaymentReconciliationGenerator
from .person import PersonGenerator
from .plan_definition import PlanDefinitionGenerator
from .practitioner import PractitionerGenerator
from .practitioner_role import PractitionerRoleGenerator
from .procedure import ProcedureGenerator
from .provenance import ProvenanceGenerator
from .questionnaire import QuestionnaireGenerator
from .questionnaire_response import QuestionnaireResponseGenerator
from .related_person import RelatedPersonGenerator
from .request_group import RequestGroupGenerator
from .research_definition import ResearchDefinitionGenerator
from .research_element_definition import ResearchElementDefinitionGenerator
from .research_study import ResearchStudyGenerator
from .research_subject import ResearchSubjectGenerator
from .risk_assessment import RiskAssessmentGenerator
from .risk_evidence_synthesis import RiskEvidenceSynthesisGenerator
from .schedule import ScheduleGenerator
from .search_parameter import SearchParameterGenerator
from .service_request import ServiceRequestGenerator
from .slot import SlotGenerator
from .specimen import SpecimenGenerator
from .specimen_definition import SpecimenDefinitionGenerator
from .structure_map import StructureMapGenerator
from .subscription import SubscriptionGenerator
from .substance import SubstanceGenerator
from .substance_nucleic_acid import SubstanceNucleicAcidGenerator
from .substance_polymer import SubstancePolymerGenerator
from .substance_protein import SubstanceProteinGenerator
from .substance_reference_information import SubstanceReferenceInformationGenerator
from .substance_source_material import SubstanceSourceMaterialGenerator
from .substance_specification import SubstanceSpecificationGenerator
from .supply_delivery import SupplyDeliveryGenerator
from .supply_request import SupplyRequestGenerator
from .task import TaskGenerator
from .terminology_capabilities import TerminologyCapabilitiesGenerator
from .test_report import TestReportGenerator
from .test_script import TestScriptGenerator
from .value_set import ValueSetGenerator
from .verification_result import VerificationResultGenerator
from .vision_prescription import VisionPrescriptionGenerator

__all__ = [
    # Base
    "FHIRResourceGenerator",
    "PatientRecordGenerator",
    # Administrative
    "PatientGenerator",
    "PractitionerGenerator",
    "PractitionerRoleGenerator",
    "OrganizationGenerator",
    "OrganizationAffiliationGenerator",
    "LocationGenerator",
    "RelatedPersonGenerator",
    "EndpointGenerator",
    "PersonGenerator",
    # Clinical
    "EncounterGenerator",
    "EpisodeOfCareGenerator",
    "ConditionGenerator",
    "ObservationGenerator",
    "ProcedureGenerator",
    "DiagnosticReportGenerator",
    "AllergyIntoleranceGenerator",
    "ImmunizationGenerator",
    "ClinicalImpressionGenerator",
    "FamilyMemberHistoryGenerator",
    "BodyStructureGenerator",
    # Imaging
    "ImagingStudyGenerator",
    # Medications
    "MedicationGenerator",
    "MedicationRequestGenerator",
    "MedicationAdministrationGenerator",
    "MedicationStatementGenerator",
    "MedicationDispenseGenerator",
    "MedicationKnowledgeGenerator",
    # Care Management
    "CarePlanGenerator",
    "CareTeamGenerator",
    "GoalGenerator",
    "TaskGenerator",
    "RequestGroupGenerator",
    # Clinical Workflow
    "ActivityDefinitionGenerator",
    "PlanDefinitionGenerator",
    "GuidanceResponseGenerator",
    "DeviceRequestGenerator",
    # Substances
    "SubstanceGenerator",
    # Immunization
    "ImmunizationRecommendationGenerator",
    # Vision
    "VisionPrescriptionGenerator",
    # Lists
    "ListGenerator",
    # Scheduling
    "AppointmentGenerator",
    "AppointmentResponseGenerator",
    "ScheduleGenerator",
    "SlotGenerator",
    "HealthcareServiceGenerator",
    # Financial
    "CoverageGenerator",
    "ClaimGenerator",
    "ClaimResponseGenerator",
    "ExplanationOfBenefitGenerator",
    "AccountGenerator",
    "CoverageEligibilityRequestGenerator",
    "CoverageEligibilityResponseGenerator",
    "PaymentNoticeGenerator",
    "PaymentReconciliationGenerator",
    "ChargeItemGenerator",
    "ChargeItemDefinitionGenerator",
    "ContractGenerator",
    "InvoiceGenerator",
    # Devices
    "DeviceGenerator",
    "DeviceDefinitionGenerator",
    "DeviceMetricGenerator",
    # Documents & Binary
    "ServiceRequestGenerator",
    "DocumentReferenceGenerator",
    "DocumentManifestGenerator",
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
    "CommunicationRequestGenerator",
    "FlagGenerator",
    # Diagnostics
    "SpecimenGenerator",
    # Orders
    "NutritionOrderGenerator",
    # Supply Chain
    "SupplyRequestGenerator",
    "SupplyDeliveryGenerator",
    # Clinical Decision Support
    "RiskAssessmentGenerator",
    "DetectedIssueGenerator",
    # Safety
    "AdverseEventGenerator",
    # Research
    "ResearchStudyGenerator",
    "ResearchSubjectGenerator",
    # Infrastructure
    "ProvenanceGenerator",
    "AuditEventGenerator",
    # Messaging
    "MessageHeaderGenerator",
    "MessageDefinitionGenerator",
    # Conformance
    "SearchParameterGenerator",
    "ImplementationGuideGenerator",
    "CompartmentDefinitionGenerator",
    "StructureMapGenerator",
    "GraphDefinitionGenerator",
    "NamingSystemGenerator",
    # Testing
    "TestScriptGenerator",
    "TestReportGenerator",
    # Verification
    "VerificationResultGenerator",
    # Definitions
    "EventDefinitionGenerator",
    "ObservationDefinitionGenerator",
    "SpecimenDefinitionGenerator",
    # Insurance
    "InsurancePlanGenerator",
    "EnrollmentRequestGenerator",
    "EnrollmentResponseGenerator",
    # Linkage
    "LinkageGenerator",
    # Device Usage
    "DeviceUseStatementGenerator",
    # Other
    "BasicGenerator",
    # Subscriptions
    "SubscriptionGenerator",
    # Foundation
    "BundleGenerator",
    "OperationDefinitionGenerator",
    "ParametersGenerator",
    # Phase 4: Evidence-Based Medicine
    "EvidenceGenerator",
    "EvidenceVariableGenerator",
    "EffectEvidenceSynthesisGenerator",
    "RiskEvidenceSynthesisGenerator",
    "ResearchDefinitionGenerator",
    "ResearchElementDefinitionGenerator",
    # Laboratory & Genomics
    "MolecularSequenceGenerator",
    "BiologicallyDerivedProductGenerator",
    # Catalog
    "CatalogEntryGenerator",
    # Immunization
    "ImmunizationEvaluationGenerator",
    # Terminology & Conformance
    "TerminologyCapabilitiesGenerator",
    "CapabilityStatementGenerator",
    "OperationOutcomeGenerator",
    # Substance specialized types
    "SubstanceNucleicAcidGenerator",
    "SubstancePolymerGenerator",
    "SubstanceProteinGenerator",
    "SubstanceReferenceInformationGenerator",
    "SubstanceSourceMaterialGenerator",
    "SubstanceSpecificationGenerator",
    # Workflow examples
    "ExampleScenarioGenerator",
]
