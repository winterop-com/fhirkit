"""Patient record generator for complete synthetic patient data.

This module provides the PatientRecordGenerator class that orchestrates
the generation of complete patient records with all related FHIR resources.
"""

from typing import Any

from faker import Faker

from .allergy_intolerance import AllergyIntoleranceGenerator
from .appointment import AppointmentGenerator
from .care_team import CareTeamGenerator
from .careplan import CarePlanGenerator
from .claim import ClaimGenerator
from .code_system import CodeSystemGenerator
from .composition import CompositionGenerator
from .concept_map import ConceptMapGenerator
from .condition import ConditionGenerator
from .coverage import CoverageGenerator
from .device import DeviceGenerator
from .diagnostic_report import DiagnosticReportGenerator
from .document_reference import DocumentReferenceGenerator
from .encounter import EncounterGenerator
from .explanation_of_benefit import ExplanationOfBenefitGenerator
from .goal import GoalGenerator
from .group import GroupGenerator
from .immunization import ImmunizationGenerator
from .library import LibraryGenerator
from .location import LocationGenerator
from .measure import MeasureGenerator
from .measure_report import MeasureReportGenerator
from .medication import MedicationGenerator
from .medication_request import MedicationRequestGenerator
from .observation import ObservationGenerator
from .organization import OrganizationGenerator
from .patient import PatientGenerator
from .practitioner import PractitionerGenerator
from .practitioner_role import PractitionerRoleGenerator
from .procedure import ProcedureGenerator
from .related_person import RelatedPersonGenerator
from .schedule import ScheduleGenerator
from .service_request import ServiceRequestGenerator
from .slot import SlotGenerator
from .task import TaskGenerator
from .value_set import ValueSetGenerator


class PatientRecordGenerator:
    """Generates complete patient records with all related resources.

    This orchestrator creates a patient along with associated encounters,
    conditions, observations, medications, procedures, and all other
    supported FHIR resource types.
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

        # Core generators (existing)
        self.patient_gen = PatientGenerator(self.faker, seed)
        self.practitioner_gen = PractitionerGenerator(self.faker, seed)
        self.organization_gen = OrganizationGenerator(self.faker, seed)
        self.encounter_gen = EncounterGenerator(self.faker, seed)
        self.condition_gen = ConditionGenerator(self.faker, seed)
        self.observation_gen = ObservationGenerator(self.faker, seed)
        self.medication_request_gen = MedicationRequestGenerator(self.faker, seed)
        self.procedure_gen = ProcedureGenerator(self.faker, seed)

        # Administrative generators
        self.practitioner_role_gen = PractitionerRoleGenerator(self.faker, seed)
        self.location_gen = LocationGenerator(self.faker, seed)
        self.related_person_gen = RelatedPersonGenerator(self.faker, seed)

        # Clinical generators
        self.allergy_gen = AllergyIntoleranceGenerator(self.faker, seed)
        self.immunization_gen = ImmunizationGenerator(self.faker, seed)
        self.diagnostic_report_gen = DiagnosticReportGenerator(self.faker, seed)

        # Medications (standalone)
        self.medication_gen = MedicationGenerator(self.faker, seed)

        # Care Management generators
        self.careplan_gen = CarePlanGenerator(self.faker, seed)
        self.careteam_gen = CareTeamGenerator(self.faker, seed)
        self.goal_gen = GoalGenerator(self.faker, seed)
        self.task_gen = TaskGenerator(self.faker, seed)

        # Scheduling generators
        self.appointment_gen = AppointmentGenerator(self.faker, seed)
        self.schedule_gen = ScheduleGenerator(self.faker, seed)
        self.slot_gen = SlotGenerator(self.faker, seed)

        # Financial generators
        self.coverage_gen = CoverageGenerator(self.faker, seed)
        self.claim_gen = ClaimGenerator(self.faker, seed)
        self.eob_gen = ExplanationOfBenefitGenerator(self.faker, seed)

        # Device generator
        self.device_gen = DeviceGenerator(self.faker, seed)

        # Document generators
        self.service_request_gen = ServiceRequestGenerator(self.faker, seed)
        self.document_ref_gen = DocumentReferenceGenerator(self.faker, seed)
        self.composition_gen = CompositionGenerator(self.faker, seed)

        # Quality Measure generators
        self.measure_gen = MeasureGenerator(self.faker, seed)
        self.measure_report_gen = MeasureReportGenerator(self.faker, seed)
        self.library_gen = LibraryGenerator(self.faker, seed)

        # Terminology generators
        self.valueset_gen = ValueSetGenerator(self.faker, seed)
        self.codesystem_gen = CodeSystemGenerator(self.faker, seed)
        self.conceptmap_gen = ConceptMapGenerator(self.faker, seed)

        # Group generator
        self.group_gen = GroupGenerator(self.faker, seed)

        # Caches for shared resources
        self._shared_resources: list[dict[str, Any]] = []
        self._locations: list[dict[str, Any]] = []
        self._schedules: list[dict[str, Any]] = []
        self._slots: list[dict[str, Any]] = []
        self._measures: list[dict[str, Any]] = []
        self._organization: dict[str, Any] | None = None
        self._practitioner: dict[str, Any] | None = None

    def _generate_shared_resources(self) -> list[dict[str, Any]]:
        """Generate terminology and quality measure resources (once per population)."""
        if self._shared_resources:
            return []  # Already generated

        resources: list[dict[str, Any]] = []

        # CodeSystem (3 templates)
        for template in self.codesystem_gen.CODE_SYSTEM_TEMPLATES:
            cs = self.codesystem_gen.generate(template=template)
            self._shared_resources.append(cs)
            resources.append(cs)

        # ValueSet (4 templates)
        for template in self.valueset_gen.VALUE_SET_TEMPLATES:
            vs = self.valueset_gen.generate(template=template)
            self._shared_resources.append(vs)
            resources.append(vs)

        # ConceptMap (all templates)
        concept_maps = self.conceptmap_gen.generate_all_templates()
        self._shared_resources.extend(concept_maps)
        resources.extend(concept_maps)

        # Library + Measure pairs (3)
        for _ in range(3):
            lib = self.library_gen.generate()
            self._shared_resources.append(lib)
            resources.append(lib)

            measure = self.measure_gen.generate()
            self._measures.append(measure)
            self._shared_resources.append(measure)
            resources.append(measure)

        return resources

    def _generate_infrastructure(
        self,
        organization_ref: str,
        practitioner_ref: str,
    ) -> list[dict[str, Any]]:
        """Generate infrastructure resources (locations, schedules, slots)."""
        resources: list[dict[str, Any]] = []

        # Locations (2-4 per population, cached)
        if not self._locations:
            for _ in range(self.faker.random_int(2, 4)):
                loc = self.location_gen.generate(managing_organization_ref=organization_ref)
                self._locations.append(loc)
                resources.append(loc)

        # Schedule + Slots (cached)
        if not self._schedules:
            location_ref = f"Location/{self._locations[0]['id']}" if self._locations else None
            schedule = self.schedule_gen.generate(
                practitioner_ref=practitioner_ref,
                location_ref=location_ref,
            )
            self._schedules.append(schedule)
            resources.append(schedule)

            # Generate slots for the schedule
            schedule_ref = f"Schedule/{schedule['id']}"
            for _ in range(10):
                slot = self.slot_gen.generate(schedule_ref=schedule_ref, status="free")
                self._slots.append(slot)
                resources.append(slot)

        return resources

    def generate_patient_record(
        self,
        # Existing parameters
        num_conditions: tuple[int, int] = (2, 6),
        num_encounters: tuple[int, int] = (3, 10),
        num_observations_per_encounter: tuple[int, int] = (2, 5),
        num_medications: tuple[int, int] = (1, 5),
        num_procedures: tuple[int, int] = (0, 3),
        # New parameters
        num_allergies: tuple[int, int] = (0, 4),
        num_immunizations: tuple[int, int] = (2, 6),
        num_diagnostic_reports: tuple[int, int] = (0, 2),
        num_related_persons: tuple[int, int] = (0, 2),
        num_careplans: tuple[int, int] = (0, 2),
        num_goals: tuple[int, int] = (0, 3),
        num_tasks: tuple[int, int] = (0, 2),
        num_appointments: tuple[int, int] = (0, 2),
        num_coverages: tuple[int, int] = (0, 1),
        num_devices: tuple[int, int] = (0, 2),
        num_service_requests: tuple[int, int] = (0, 2),
        num_document_refs: tuple[int, int] = (0, 2),
    ) -> list[dict[str, Any]]:
        """Generate a complete patient record with all related resources.

        Args:
            num_conditions: Min/max number of conditions
            num_encounters: Min/max number of encounters
            num_observations_per_encounter: Min/max observations per encounter
            num_medications: Min/max number of active medications
            num_procedures: Min/max number of procedures
            num_allergies: Min/max number of allergies
            num_immunizations: Min/max number of immunizations
            num_diagnostic_reports: Min/max number of diagnostic reports
            num_related_persons: Min/max number of related persons
            num_careplans: Min/max number of care plans
            num_goals: Min/max number of goals
            num_tasks: Min/max number of tasks
            num_appointments: Min/max number of appointments
            num_coverages: Min/max number of coverage records
            num_devices: Min/max number of devices
            num_service_requests: Min/max number of service requests
            num_document_refs: Min/max number of document references

        Returns:
            List of all generated FHIR resources
        """
        resources: list[dict[str, Any]] = []

        # Generate or reuse supporting resources
        if self._practitioner is None:
            self._practitioner = self.practitioner_gen.generate()
        if self._organization is None:
            self._organization = self.organization_gen.generate()

        practitioner = self._practitioner
        organization = self._organization
        resources.extend([practitioner, organization])

        practitioner_ref = f"Practitioner/{practitioner['id']}"
        organization_ref = f"Organization/{organization['id']}"

        # Generate infrastructure (locations, schedules, slots) - shared
        infra_resources = self._generate_infrastructure(organization_ref, practitioner_ref)
        resources.extend(infra_resources)

        location_ref = f"Location/{self._locations[0]['id']}" if self._locations else None

        # Generate PractitionerRole (per patient record, links practitioner to location)
        practitioner_role = self.practitioner_role_gen.generate(
            practitioner_ref=practitioner_ref,
            organization_ref=organization_ref,
            location_ref=location_ref,
        )
        resources.append(practitioner_role)

        # Generate patient
        patient = self.patient_gen.generate()
        resources.append(patient)
        patient_ref = f"Patient/{patient['id']}"

        # Generate related persons
        num_related = self.faker.random_int(min=num_related_persons[0], max=num_related_persons[1])
        for _ in range(num_related):
            related = self.related_person_gen.generate(patient_ref=patient_ref)
            resources.append(related)

        # Generate coverage (insurance)
        coverages: list[dict[str, Any]] = []
        num_cov = self.faker.random_int(min=num_coverages[0], max=num_coverages[1])
        for _ in range(num_cov):
            coverage = self.coverage_gen.generate(
                beneficiary_ref=patient_ref,
                payor_ref=organization_ref,
            )
            coverages.append(coverage)
            resources.append(coverage)

        # Generate devices
        num_dev = self.faker.random_int(min=num_devices[0], max=num_devices[1])
        for _ in range(num_dev):
            device = self.device_gen.generate(
                patient_ref=patient_ref,
                owner_ref=organization_ref,
                location_ref=location_ref,
            )
            resources.append(device)

        # Generate conditions
        conditions: list[dict[str, Any]] = []
        num_cond = self.faker.random_int(min=num_conditions[0], max=num_conditions[1])
        for _ in range(num_cond):
            condition = self.condition_gen.generate(patient_ref=patient_ref)
            conditions.append(condition)
            resources.append(condition)

        # Generate allergies
        num_allergy = self.faker.random_int(min=num_allergies[0], max=num_allergies[1])
        for _ in range(num_allergy):
            allergy = self.allergy_gen.generate(
                patient_ref=patient_ref,
                recorder_ref=practitioner_ref,
            )
            resources.append(allergy)

        # Generate encounters and associated observations
        encounters: list[dict[str, Any]] = []
        observations: list[dict[str, Any]] = []
        num_enc = self.faker.random_int(min=num_encounters[0], max=num_encounters[1])
        for _ in range(num_enc):
            encounter = self.encounter_gen.generate(
                patient_ref=patient_ref,
                practitioner_ref=practitioner_ref,
                organization_ref=organization_ref,
            )
            encounters.append(encounter)
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
                observations.append(observation)
                resources.append(observation)

        # Generate immunizations
        num_imm = self.faker.random_int(min=num_immunizations[0], max=num_immunizations[1])
        for i in range(num_imm):
            encounter = encounters[i % len(encounters)] if encounters else None
            immunization = self.immunization_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=f"Encounter/{encounter['id']}" if encounter else None,
                performer_ref=practitioner_ref,
            )
            resources.append(immunization)

        # Generate diagnostic reports (referencing observations)
        num_dr = self.faker.random_int(min=num_diagnostic_reports[0], max=num_diagnostic_reports[1])
        for i in range(num_dr):
            encounter = encounters[i % len(encounters)] if encounters else None
            # Get lab observations for this encounter
            lab_obs = [
                o
                for o in observations
                if o.get("category", [{}])[0].get("coding", [{}])[0].get("code") == "laboratory"
            ]
            result_refs = [f"Observation/{o['id']}" for o in lab_obs[:3]]

            diagnostic_report = self.diagnostic_report_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=f"Encounter/{encounter['id']}" if encounter else None,
                performer_ref=practitioner_ref,
                result_refs=result_refs if result_refs else None,
            )
            resources.append(diagnostic_report)

        # Generate standalone Medication resources and MedicationRequests
        medications: list[dict[str, Any]] = []
        medication_requests: list[dict[str, Any]] = []
        num_meds = self.faker.random_int(min=num_medications[0], max=num_medications[1])
        for _ in range(num_meds):
            # Standalone Medication resource
            medication = self.medication_gen.generate()
            medications.append(medication)
            resources.append(medication)

            # MedicationRequest referencing the Medication
            med_request = self.medication_request_gen.generate(
                patient_ref=patient_ref,
                practitioner_ref=practitioner_ref,
            )
            medication_requests.append(med_request)
            resources.append(med_request)

        # Generate procedures
        procedures: list[dict[str, Any]] = []
        num_procs = self.faker.random_int(min=num_procedures[0], max=num_procedures[1])
        for _ in range(num_procs):
            procedure = self.procedure_gen.generate(
                patient_ref=patient_ref,
                practitioner_ref=practitioner_ref,
            )
            procedures.append(procedure)
            resources.append(procedure)

        # Generate service requests
        num_sr = self.faker.random_int(min=num_service_requests[0], max=num_service_requests[1])
        for i in range(num_sr):
            encounter = encounters[i % len(encounters)] if encounters else None
            service_request = self.service_request_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=f"Encounter/{encounter['id']}" if encounter else None,
                requester_ref=practitioner_ref,
            )
            resources.append(service_request)

        # Generate document references
        num_doc = self.faker.random_int(min=num_document_refs[0], max=num_document_refs[1])
        for i in range(num_doc):
            encounter = encounters[i % len(encounters)] if encounters else None
            doc_ref = self.document_ref_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=f"Encounter/{encounter['id']}" if encounter else None,
                author_ref=practitioner_ref,
                custodian_ref=organization_ref,
            )
            resources.append(doc_ref)

        # Generate goals
        goals: list[dict[str, Any]] = []
        num_goal = self.faker.random_int(min=num_goals[0], max=num_goals[1])
        for _ in range(num_goal):
            goal = self.goal_gen.generate(
                patient_ref=patient_ref,
                expressed_by_ref=practitioner_ref,
            )
            goals.append(goal)
            resources.append(goal)

        # Generate care plans (referencing conditions and goals)
        careplans: list[dict[str, Any]] = []
        num_cp = self.faker.random_int(min=num_careplans[0], max=num_careplans[1])
        for _ in range(num_cp):
            condition_refs = [f"Condition/{c['id']}" for c in conditions[:2]] if conditions else None
            goal_refs = [f"Goal/{g['id']}" for g in goals[:2]] if goals else None
            encounter = encounters[-1] if encounters else None

            careplan = self.careplan_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=f"Encounter/{encounter['id']}" if encounter else None,
                author_ref=practitioner_ref,
                addresses_refs=condition_refs,
                goal_refs=goal_refs,
            )
            careplans.append(careplan)
            resources.append(careplan)

        # Generate care team
        if self.faker.random.random() < 0.5 and encounters:
            careteam = self.careteam_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=f"Encounter/{encounters[-1]['id']}",
                participant_refs=[practitioner_ref],
            )
            resources.append(careteam)

        # Generate tasks (referencing care plans)
        num_task = self.faker.random_int(min=num_tasks[0], max=num_tasks[1])
        for _ in range(num_task):
            focus_ref = f"CarePlan/{careplans[0]['id']}" if careplans else None
            task = self.task_gen.generate(
                patient_ref=patient_ref,
                requester_ref=practitioner_ref,
                owner_ref=practitioner_ref,
                focus_ref=focus_ref,
            )
            resources.append(task)

        # Generate appointments (using available slots)
        available_slots = [s for s in self._slots if s.get("status") == "free"]
        num_appt = self.faker.random_int(min=num_appointments[0], max=num_appointments[1])
        for _ in range(min(num_appt, len(available_slots))):
            if available_slots:
                slot = available_slots.pop(0)
                slot["status"] = "busy"  # Mark as used

                appointment = self.appointment_gen.generate(
                    patient_ref=patient_ref,
                    practitioner_ref=practitioner_ref,
                    location_ref=location_ref,
                    slot_ref=f"Slot/{slot['id']}",
                )
                resources.append(appointment)

        # Generate claims and EOBs (if coverage exists)
        if coverages and encounters:
            coverage_ref = f"Coverage/{coverages[0]['id']}"

            # Generate claim for first encounter
            claim = self.claim_gen.generate(
                patient_ref=patient_ref,
                provider_ref=practitioner_ref,
                insurer_ref=organization_ref,
            )
            resources.append(claim)

            # Generate EOB
            eob = self.eob_gen.generate(
                patient_ref=patient_ref,
                provider_ref=practitioner_ref,
                insurer_ref=organization_ref,
            )
            resources.append(eob)

        # Generate measure reports (if measures exist)
        if self._measures:
            for measure in self._measures[:2]:
                report = self.measure_report_gen.generate(
                    measure_ref=f"Measure/{measure['id']}",
                    patient_ref=patient_ref,
                    reporter_ref=organization_ref,
                )
                resources.append(report)

        # Generate composition (clinical document summary)
        if encounters and self.faker.random.random() < 0.3:  # 30% chance
            composition = self.composition_gen.generate(
                patient_ref=patient_ref,
                encounter_ref=f"Encounter/{encounters[-1]['id']}",
                author_ref=practitioner_ref,
                custodian_ref=organization_ref,
            )
            resources.append(composition)

        return resources

    def generate_population(
        self,
        num_patients: int,
        include_terminology: bool = True,
        include_group: bool = True,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Generate a population of patients with all related resources.

        Args:
            num_patients: Number of patients to generate
            include_terminology: Generate CodeSystem, ValueSet, ConceptMap resources
            include_group: Generate Group resource for patient cohort
            **kwargs: Arguments passed to generate_patient_record

        Returns:
            List of all generated FHIR resources
        """
        all_resources: list[dict[str, Any]] = []
        patient_refs: list[str] = []

        # Generate shared terminology resources first
        if include_terminology:
            terminology_resources = self._generate_shared_resources()
            all_resources.extend(terminology_resources)

        # Generate patients
        for _ in range(num_patients):
            patient_resources = self.generate_patient_record(**kwargs)
            all_resources.extend(patient_resources)

            # Extract patient reference for groups
            for r in patient_resources:
                if r.get("resourceType") == "Patient":
                    patient_refs.append(f"Patient/{r['id']}")
                    break

        # Generate patient group
        if include_group and patient_refs:
            org_ref = f"Organization/{self._organization['id']}" if self._organization else None
            group = self.group_gen.generate(
                member_refs=patient_refs,
                managing_entity_ref=org_ref,
            )
            all_resources.append(group)

        return all_resources
