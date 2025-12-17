"""GraphQL schema generation for FHIR resources.

This module dynamically generates a GraphQL schema that supports all FHIR
resource types defined in SUPPORTED_TYPES. It creates:

- Single resource queries: Patient(_id: "123")
- List queries with search: PatientList(name: "Smith", _count: 10)
- Connection queries: PatientConnection(first: 10, after: "cursor")
- Mutations: PatientCreate, PatientUpdate, PatientDelete

The schema is generated dynamically at runtime to support all resource types
without manually defining each one.
"""

import logging
from typing import Annotated, Any, Optional

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.scalars import JSON

from ..api.routes import SUPPORTED_TYPES
from ..storage.fhir_store import FHIRStore
from .resolvers import ConnectionResolver, ListResolver, MutationResolver, ResourceResolver
from .types import Resource, ResourceConnection

logger = logging.getLogger(__name__)

# Type aliases for FHIR-specific argument names (underscore prefix)
# Strawberry would normally convert _id to Id, but FHIR uses _id
FhirId = Annotated[str, strawberry.argument(name="_id")]
FhirCount = Annotated[int, strawberry.argument(name="_count")]
FhirOffset = Annotated[int, strawberry.argument(name="_offset")]
FhirSort = Annotated[Optional[str], strawberry.argument(name="_sort")]


def create_schema(store: FHIRStore) -> strawberry.Schema:
    """Create the GraphQL schema with all FHIR resource queries and mutations.

    This function dynamically generates:
    - Query fields for each resource type (read, list, connection)
    - Mutation fields for each resource type (create, update, delete)

    Args:
        store: FHIRStore instance for data access

    Returns:
        Configured Strawberry GraphQL schema
    """
    # Initialize resolvers
    resource_resolver = ResourceResolver(store)
    list_resolver = ListResolver(store)
    connection_resolver = ConnectionResolver(store)
    mutation_resolver = MutationResolver(store)

    # =========================================================================
    # Query Type
    # =========================================================================

    @strawberry.type(description="GraphQL queries for FHIR resources")
    class Query:
        """Root query type with all FHIR resource queries.

        Provides three query patterns for each resource type:
        - {Type}(_id): Fetch single resource by ID
        - {Type}List(...): Search with parameters and offset pagination
        - {Type}Connection(...): Search with cursor-based pagination
        """

        # Generic resource query (for any type)
        @strawberry.field(description="Fetch any FHIR resource by type and ID")
        def resource(
            self,
            resourceType: str,
            _id: FhirId,
        ) -> Optional[Resource]:
            """Generic resource query for any type."""
            if resourceType not in SUPPORTED_TYPES:
                return None
            return resource_resolver.resolve(resourceType, _id)

        @strawberry.field(description="Search any FHIR resource type")
        def resourceList(
            self,
            resourceType: str,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
        ) -> list[Resource]:
            """Generic resource list query for any type."""
            if resourceType not in SUPPORTED_TYPES:
                return []
            return list_resolver.resolve(resourceType, _count=_count, _offset=_offset, _sort=_sort)

        @strawberry.field(description="Search any FHIR resource type with cursor pagination")
        def resourceConnection(
            self,
            resourceType: str,
            first: Optional[int] = None,
            after: Optional[str] = None,
            last: Optional[int] = None,
            before: Optional[str] = None,
            _sort: FhirSort = None,
        ) -> ResourceConnection:
            """Generic resource connection query for any type."""
            return connection_resolver.resolve(
                resourceType, first=first, after=after, last=last, before=before, _sort=_sort
            )

        # =====================================================================
        # Administrative Resources
        # =====================================================================

        @strawberry.field(description="Fetch a Patient by ID")
        def Patient(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Patient", _id)

        @strawberry.field(description="Search Patient resources")
        def PatientList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            # Patient-specific search params
            identifier: Optional[str] = None,
            name: Optional[str] = None,
            family: Optional[str] = None,
            given: Optional[str] = None,
            gender: Optional[str] = None,
            birthdate: Optional[str] = None,
            address: Optional[str] = None,
            phone: Optional[str] = None,
            email: Optional[str] = None,
            general_practitioner: Optional[str] = None,
            organization: Optional[str] = None,
            active: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Patient",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                identifier=identifier,
                name=name,
                family=family,
                given=given,
                gender=gender,
                birthdate=birthdate,
                address=address,
                phone=phone,
                email=email,
                general_practitioner=general_practitioner,
                organization=organization,
                active=active,
            )

        @strawberry.field(description="Search Patient resources with cursor pagination")
        def PatientConnection(
            self,
            first: Optional[int] = None,
            after: Optional[str] = None,
            last: Optional[int] = None,
            before: Optional[str] = None,
            _sort: FhirSort = None,
            name: Optional[str] = None,
            gender: Optional[str] = None,
            birthdate: Optional[str] = None,
        ) -> ResourceConnection:
            return connection_resolver.resolve(
                "Patient",
                first=first,
                after=after,
                last=last,
                before=before,
                _sort=_sort,
                name=name,
                gender=gender,
                birthdate=birthdate,
            )

        @strawberry.field(description="Fetch a Practitioner by ID")
        def Practitioner(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Practitioner", _id)

        @strawberry.field(description="Search Practitioner resources")
        def PractitionerList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            identifier: Optional[str] = None,
            name: Optional[str] = None,
            family: Optional[str] = None,
            given: Optional[str] = None,
            active: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Practitioner",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                identifier=identifier,
                name=name,
                family=family,
                given=given,
                active=active,
            )

        @strawberry.field(description="Fetch an Organization by ID")
        def Organization(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Organization", _id)

        @strawberry.field(description="Search Organization resources")
        def OrganizationList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            identifier: Optional[str] = None,
            name: Optional[str] = None,
            type: Optional[str] = None,
            active: Optional[str] = None,
            partof: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Organization",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                identifier=identifier,
                name=name,
                type=type,
                active=active,
                partof=partof,
            )

        @strawberry.field(description="Fetch a Location by ID")
        def Location(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Location", _id)

        @strawberry.field(description="Search Location resources")
        def LocationList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            identifier: Optional[str] = None,
            name: Optional[str] = None,
            status: Optional[str] = None,
            type: Optional[str] = None,
            organization: Optional[str] = None,
            partof: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Location",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                identifier=identifier,
                name=name,
                status=status,
                type=type,
                organization=organization,
                partof=partof,
            )

        @strawberry.field(description="Fetch a PractitionerRole by ID")
        def PractitionerRole(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("PractitionerRole", _id)

        @strawberry.field(description="Search PractitionerRole resources")
        def PractitionerRoleList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            practitioner: Optional[str] = None,
            organization: Optional[str] = None,
            specialty: Optional[str] = None,
            active: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "PractitionerRole",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                practitioner=practitioner,
                organization=organization,
                specialty=specialty,
                active=active,
            )

        @strawberry.field(description="Fetch a RelatedPerson by ID")
        def RelatedPerson(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("RelatedPerson", _id)

        @strawberry.field(description="Search RelatedPerson resources")
        def RelatedPersonList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            name: Optional[str] = None,
            relationship: Optional[str] = None,
            active: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "RelatedPerson",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                name=name,
                relationship=relationship,
                active=active,
            )

        # =====================================================================
        # Clinical Resources
        # =====================================================================

        @strawberry.field(description="Fetch an Encounter by ID")
        def Encounter(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Encounter", _id)

        @strawberry.field(description="Search Encounter resources")
        def EncounterList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            status: Optional[str] = None,
            class_: Optional[str] = None,
            type: Optional[str] = None,
            date: Optional[str] = None,
            participant: Optional[str] = None,
            service_provider: Optional[str] = None,
        ) -> list[Resource]:
            params: dict[str, Any] = {
                "patient": patient,
                "subject": subject,
                "status": status,
                "type": type,
                "date": date,
                "participant": participant,
                "service_provider": service_provider,
            }
            if class_:
                params["class"] = class_
            return list_resolver.resolve(
                "Encounter",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                **params,
            )

        @strawberry.field(description="Fetch a Condition by ID")
        def Condition(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Condition", _id)

        @strawberry.field(description="Search Condition resources")
        def ConditionList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            code: Optional[str] = None,
            clinical_status: Optional[str] = None,
            verification_status: Optional[str] = None,
            category: Optional[str] = None,
            onset_date: Optional[str] = None,
            encounter: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Condition",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                subject=subject,
                code=code,
                clinical_status=clinical_status,
                verification_status=verification_status,
                category=category,
                onset_date=onset_date,
                encounter=encounter,
            )

        @strawberry.field(description="Fetch an Observation by ID")
        def Observation(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Observation", _id)

        @strawberry.field(description="Search Observation resources")
        def ObservationList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            code: Optional[str] = None,
            category: Optional[str] = None,
            status: Optional[str] = None,
            date: Optional[str] = None,
            encounter: Optional[str] = None,
            performer: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Observation",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                subject=subject,
                code=code,
                category=category,
                status=status,
                date=date,
                encounter=encounter,
                performer=performer,
            )

        @strawberry.field(description="Fetch a Procedure by ID")
        def Procedure(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Procedure", _id)

        @strawberry.field(description="Search Procedure resources")
        def ProcedureList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            code: Optional[str] = None,
            status: Optional[str] = None,
            date: Optional[str] = None,
            encounter: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Procedure",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                subject=subject,
                code=code,
                status=status,
                date=date,
                encounter=encounter,
            )

        @strawberry.field(description="Fetch a DiagnosticReport by ID")
        def DiagnosticReport(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("DiagnosticReport", _id)

        @strawberry.field(description="Search DiagnosticReport resources")
        def DiagnosticReportList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            code: Optional[str] = None,
            category: Optional[str] = None,
            status: Optional[str] = None,
            date: Optional[str] = None,
            encounter: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "DiagnosticReport",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                subject=subject,
                code=code,
                category=category,
                status=status,
                date=date,
                encounter=encounter,
            )

        @strawberry.field(description="Fetch an AllergyIntolerance by ID")
        def AllergyIntolerance(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("AllergyIntolerance", _id)

        @strawberry.field(description="Search AllergyIntolerance resources")
        def AllergyIntoleranceList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            code: Optional[str] = None,
            clinical_status: Optional[str] = None,
            verification_status: Optional[str] = None,
            type: Optional[str] = None,
            category: Optional[str] = None,
            criticality: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "AllergyIntolerance",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                code=code,
                clinical_status=clinical_status,
                verification_status=verification_status,
                type=type,
                category=category,
                criticality=criticality,
            )

        @strawberry.field(description="Fetch an Immunization by ID")
        def Immunization(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Immunization", _id)

        @strawberry.field(description="Search Immunization resources")
        def ImmunizationList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            vaccine_code: Optional[str] = None,
            status: Optional[str] = None,
            date: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Immunization",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                vaccine_code=vaccine_code,
                status=status,
                date=date,
            )

        # =====================================================================
        # Medication Resources
        # =====================================================================

        @strawberry.field(description="Fetch a Medication by ID")
        def Medication(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Medication", _id)

        @strawberry.field(description="Search Medication resources")
        def MedicationList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            code: Optional[str] = None,
            status: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Medication",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                code=code,
                status=status,
            )

        @strawberry.field(description="Fetch a MedicationRequest by ID")
        def MedicationRequest(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("MedicationRequest", _id)

        @strawberry.field(description="Search MedicationRequest resources")
        def MedicationRequestList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            status: Optional[str] = None,
            intent: Optional[str] = None,
            medication: Optional[str] = None,
            authoredon: Optional[str] = None,
            encounter: Optional[str] = None,
            requester: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "MedicationRequest",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                subject=subject,
                status=status,
                intent=intent,
                medication=medication,
                authoredon=authoredon,
                encounter=encounter,
                requester=requester,
            )

        # =====================================================================
        # Care Management Resources
        # =====================================================================

        @strawberry.field(description="Fetch a CarePlan by ID")
        def CarePlan(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("CarePlan", _id)

        @strawberry.field(description="Search CarePlan resources")
        def CarePlanList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            status: Optional[str] = None,
            intent: Optional[str] = None,
            category: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "CarePlan",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                subject=subject,
                status=status,
                intent=intent,
                category=category,
            )

        @strawberry.field(description="Fetch a CareTeam by ID")
        def CareTeam(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("CareTeam", _id)

        @strawberry.field(description="Search CareTeam resources")
        def CareTeamList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            status: Optional[str] = None,
            category: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "CareTeam",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                subject=subject,
                status=status,
                category=category,
            )

        @strawberry.field(description="Fetch a Goal by ID")
        def Goal(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Goal", _id)

        @strawberry.field(description="Search Goal resources")
        def GoalList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            lifecycle_status: Optional[str] = None,
            category: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Goal",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                subject=subject,
                lifecycle_status=lifecycle_status,
                category=category,
            )

        @strawberry.field(description="Fetch a Task by ID")
        def Task(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Task", _id)

        @strawberry.field(description="Search Task resources")
        def TaskList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            status: Optional[str] = None,
            intent: Optional[str] = None,
            owner: Optional[str] = None,
            requester: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Task",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                status=status,
                intent=intent,
                owner=owner,
                requester=requester,
            )

        # =====================================================================
        # Scheduling Resources
        # =====================================================================

        @strawberry.field(description="Fetch an Appointment by ID")
        def Appointment(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Appointment", _id)

        @strawberry.field(description="Search Appointment resources")
        def AppointmentList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            actor: Optional[str] = None,
            status: Optional[str] = None,
            date: Optional[str] = None,
            service_type: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Appointment",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                actor=actor,
                status=status,
                date=date,
                service_type=service_type,
            )

        @strawberry.field(description="Fetch a Schedule by ID")
        def Schedule(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Schedule", _id)

        @strawberry.field(description="Search Schedule resources")
        def ScheduleList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            actor: Optional[str] = None,
            active: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Schedule",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                actor=actor,
                active=active,
            )

        @strawberry.field(description="Fetch a Slot by ID")
        def Slot(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Slot", _id)

        @strawberry.field(description="Search Slot resources")
        def SlotList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            schedule: Optional[str] = None,
            status: Optional[str] = None,
            start: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Slot",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                schedule=schedule,
                status=status,
                start=start,
            )

        # =====================================================================
        # Financial Resources
        # =====================================================================

        @strawberry.field(description="Fetch a Coverage by ID")
        def Coverage(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Coverage", _id)

        @strawberry.field(description="Search Coverage resources")
        def CoverageList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            beneficiary: Optional[str] = None,
            payor: Optional[str] = None,
            status: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Coverage",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                beneficiary=beneficiary,
                payor=payor,
                status=status,
            )

        @strawberry.field(description="Fetch a Claim by ID")
        def Claim(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Claim", _id)

        @strawberry.field(description="Search Claim resources")
        def ClaimList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            status: Optional[str] = None,
            created: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Claim",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                status=status,
                created=created,
            )

        @strawberry.field(description="Fetch an ExplanationOfBenefit by ID")
        def ExplanationOfBenefit(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("ExplanationOfBenefit", _id)

        @strawberry.field(description="Search ExplanationOfBenefit resources")
        def ExplanationOfBenefitList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            status: Optional[str] = None,
            created: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "ExplanationOfBenefit",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                status=status,
                created=created,
            )

        # =====================================================================
        # Device Resources
        # =====================================================================

        @strawberry.field(description="Fetch a Device by ID")
        def Device(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Device", _id)

        @strawberry.field(description="Search Device resources")
        def DeviceList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            status: Optional[str] = None,
            type: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Device",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                status=status,
                type=type,
            )

        # =====================================================================
        # Document Resources
        # =====================================================================

        @strawberry.field(description="Fetch a ServiceRequest by ID")
        def ServiceRequest(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("ServiceRequest", _id)

        @strawberry.field(description="Search ServiceRequest resources")
        def ServiceRequestList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            status: Optional[str] = None,
            code: Optional[str] = None,
            encounter: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "ServiceRequest",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                subject=subject,
                status=status,
                code=code,
                encounter=encounter,
            )

        @strawberry.field(description="Fetch a DocumentReference by ID")
        def DocumentReference(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("DocumentReference", _id)

        @strawberry.field(description="Search DocumentReference resources")
        def DocumentReferenceList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            status: Optional[str] = None,
            type: Optional[str] = None,
            category: Optional[str] = None,
            date: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "DocumentReference",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                subject=subject,
                status=status,
                type=type,
                category=category,
                date=date,
            )

        @strawberry.field(description="Fetch a Binary by ID")
        def Binary(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Binary", _id)

        @strawberry.field(description="Search Binary resources")
        def BinaryList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Binary",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
            )

        # =====================================================================
        # Quality Measure Resources
        # =====================================================================

        @strawberry.field(description="Fetch a Measure by ID")
        def Measure(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Measure", _id)

        @strawberry.field(description="Search Measure resources")
        def MeasureList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            name: Optional[str] = None,
            status: Optional[str] = None,
            title: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Measure",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                name=name,
                status=status,
                title=title,
            )

        @strawberry.field(description="Fetch a MeasureReport by ID")
        def MeasureReport(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("MeasureReport", _id)

        @strawberry.field(description="Search MeasureReport resources")
        def MeasureReportList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            status: Optional[str] = None,
            measure: Optional[str] = None,
            period: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "MeasureReport",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                subject=subject,
                status=status,
                measure=measure,
                period=period,
            )

        @strawberry.field(description="Fetch a Library by ID")
        def Library(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Library", _id)

        @strawberry.field(description="Search Library resources")
        def LibraryList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            name: Optional[str] = None,
            status: Optional[str] = None,
            title: Optional[str] = None,
            type: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Library",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                name=name,
                status=status,
                title=title,
                type=type,
            )

        # =====================================================================
        # Terminology Resources
        # =====================================================================

        @strawberry.field(description="Fetch a ValueSet by ID")
        def ValueSet(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("ValueSet", _id)

        @strawberry.field(description="Search ValueSet resources")
        def ValueSetList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            name: Optional[str] = None,
            status: Optional[str] = None,
            title: Optional[str] = None,
            url: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "ValueSet",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                name=name,
                status=status,
                title=title,
                url=url,
            )

        @strawberry.field(description="Fetch a CodeSystem by ID")
        def CodeSystem(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("CodeSystem", _id)

        @strawberry.field(description="Search CodeSystem resources")
        def CodeSystemList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            name: Optional[str] = None,
            status: Optional[str] = None,
            title: Optional[str] = None,
            url: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "CodeSystem",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                name=name,
                status=status,
                title=title,
                url=url,
            )

        @strawberry.field(description="Fetch a ConceptMap by ID")
        def ConceptMap(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("ConceptMap", _id)

        @strawberry.field(description="Search ConceptMap resources")
        def ConceptMapList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            name: Optional[str] = None,
            status: Optional[str] = None,
            title: Optional[str] = None,
            url: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "ConceptMap",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                name=name,
                status=status,
                title=title,
                url=url,
            )

        # =====================================================================
        # Clinical Document Resources
        # =====================================================================

        @strawberry.field(description="Fetch a Composition by ID")
        def Composition(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Composition", _id)

        @strawberry.field(description="Search Composition resources")
        def CompositionList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            status: Optional[str] = None,
            type: Optional[str] = None,
            date: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Composition",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                subject=subject,
                status=status,
                type=type,
                date=date,
            )

        # =====================================================================
        # Form Resources
        # =====================================================================

        @strawberry.field(description="Fetch a Questionnaire by ID")
        def Questionnaire(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Questionnaire", _id)

        @strawberry.field(description="Search Questionnaire resources")
        def QuestionnaireList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            name: Optional[str] = None,
            status: Optional[str] = None,
            title: Optional[str] = None,
            url: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Questionnaire",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                name=name,
                status=status,
                title=title,
                url=url,
            )

        @strawberry.field(description="Fetch a QuestionnaireResponse by ID")
        def QuestionnaireResponse(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("QuestionnaireResponse", _id)

        @strawberry.field(description="Search QuestionnaireResponse resources")
        def QuestionnaireResponseList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            patient: Optional[str] = None,
            subject: Optional[str] = None,
            status: Optional[str] = None,
            questionnaire: Optional[str] = None,
            authored: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "QuestionnaireResponse",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                patient=patient,
                subject=subject,
                status=status,
                questionnaire=questionnaire,
                authored=authored,
            )

        # =====================================================================
        # Group Resources
        # =====================================================================

        @strawberry.field(description="Fetch a Group by ID")
        def Group(self, _id: FhirId) -> Optional[Resource]:
            return resource_resolver.resolve("Group", _id)

        @strawberry.field(description="Search Group resources")
        def GroupList(
            self,
            _count: FhirCount = 100,
            _offset: FhirOffset = 0,
            _sort: FhirSort = None,
            type: Optional[str] = None,
            actual: Optional[str] = None,
            code: Optional[str] = None,
        ) -> list[Resource]:
            return list_resolver.resolve(
                "Group",
                _count=_count,
                _offset=_offset,
                _sort=_sort,
                type=type,
                actual=actual,
                code=code,
            )

    # =========================================================================
    # Mutation Type
    # =========================================================================

    @strawberry.type(description="GraphQL mutations for FHIR resources")
    class Mutation:
        """Root mutation type with all FHIR resource mutations.

        Provides Create, Update, and Delete mutations for each resource type.
        """

        # Generic mutations (for any type)
        @strawberry.mutation(description="Create a FHIR resource of any type")
        def resourceCreate(
            self,
            resourceType: str,
            data: JSON,
        ) -> Resource:
            """Generic resource create mutation."""
            if resourceType not in SUPPORTED_TYPES:
                raise ValueError(f"Unsupported resource type: {resourceType}")
            return mutation_resolver.create(resourceType, dict(data))

        @strawberry.mutation(description="Update a FHIR resource of any type")
        def resourceUpdate(
            self,
            resourceType: str,
            _id: str,
            data: JSON,
        ) -> Optional[Resource]:
            """Generic resource update mutation."""
            if resourceType not in SUPPORTED_TYPES:
                raise ValueError(f"Unsupported resource type: {resourceType}")
            return mutation_resolver.update(resourceType, _id, dict(data))

        @strawberry.mutation(description="Delete a FHIR resource of any type")
        def resourceDelete(
            self,
            resourceType: str,
            _id: str,
        ) -> Optional[Resource]:
            """Generic resource delete mutation."""
            if resourceType not in SUPPORTED_TYPES:
                raise ValueError(f"Unsupported resource type: {resourceType}")
            return mutation_resolver.delete(resourceType, _id)

        # =====================================================================
        # Resource-specific mutations
        # =====================================================================

        @strawberry.mutation(description="Create a Patient resource")
        def PatientCreate(self, data: JSON) -> Resource:
            return mutation_resolver.create("Patient", dict(data))

        @strawberry.mutation(description="Update a Patient resource")
        def PatientUpdate(self, _id: FhirId, data: JSON) -> Optional[Resource]:
            return mutation_resolver.update("Patient", _id, dict(data))

        @strawberry.mutation(description="Delete a Patient resource")
        def PatientDelete(self, _id: FhirId) -> Optional[Resource]:
            return mutation_resolver.delete("Patient", _id)

        @strawberry.mutation(description="Create a Practitioner resource")
        def PractitionerCreate(self, data: JSON) -> Resource:
            return mutation_resolver.create("Practitioner", dict(data))

        @strawberry.mutation(description="Update a Practitioner resource")
        def PractitionerUpdate(self, _id: FhirId, data: JSON) -> Optional[Resource]:
            return mutation_resolver.update("Practitioner", _id, dict(data))

        @strawberry.mutation(description="Delete a Practitioner resource")
        def PractitionerDelete(self, _id: FhirId) -> Optional[Resource]:
            return mutation_resolver.delete("Practitioner", _id)

        @strawberry.mutation(description="Create an Organization resource")
        def OrganizationCreate(self, data: JSON) -> Resource:
            return mutation_resolver.create("Organization", dict(data))

        @strawberry.mutation(description="Update an Organization resource")
        def OrganizationUpdate(self, _id: FhirId, data: JSON) -> Optional[Resource]:
            return mutation_resolver.update("Organization", _id, dict(data))

        @strawberry.mutation(description="Delete an Organization resource")
        def OrganizationDelete(self, _id: FhirId) -> Optional[Resource]:
            return mutation_resolver.delete("Organization", _id)

        @strawberry.mutation(description="Create an Observation resource")
        def ObservationCreate(self, data: JSON) -> Resource:
            return mutation_resolver.create("Observation", dict(data))

        @strawberry.mutation(description="Update an Observation resource")
        def ObservationUpdate(self, _id: FhirId, data: JSON) -> Optional[Resource]:
            return mutation_resolver.update("Observation", _id, dict(data))

        @strawberry.mutation(description="Delete an Observation resource")
        def ObservationDelete(self, _id: FhirId) -> Optional[Resource]:
            return mutation_resolver.delete("Observation", _id)

        @strawberry.mutation(description="Create a Condition resource")
        def ConditionCreate(self, data: JSON) -> Resource:
            return mutation_resolver.create("Condition", dict(data))

        @strawberry.mutation(description="Update a Condition resource")
        def ConditionUpdate(self, _id: FhirId, data: JSON) -> Optional[Resource]:
            return mutation_resolver.update("Condition", _id, dict(data))

        @strawberry.mutation(description="Delete a Condition resource")
        def ConditionDelete(self, _id: FhirId) -> Optional[Resource]:
            return mutation_resolver.delete("Condition", _id)

        @strawberry.mutation(description="Create an Encounter resource")
        def EncounterCreate(self, data: JSON) -> Resource:
            return mutation_resolver.create("Encounter", dict(data))

        @strawberry.mutation(description="Update an Encounter resource")
        def EncounterUpdate(self, _id: FhirId, data: JSON) -> Optional[Resource]:
            return mutation_resolver.update("Encounter", _id, dict(data))

        @strawberry.mutation(description="Delete an Encounter resource")
        def EncounterDelete(self, _id: FhirId) -> Optional[Resource]:
            return mutation_resolver.delete("Encounter", _id)

        @strawberry.mutation(description="Create a MedicationRequest resource")
        def MedicationRequestCreate(self, data: JSON) -> Resource:
            return mutation_resolver.create("MedicationRequest", dict(data))

        @strawberry.mutation(description="Update a MedicationRequest resource")
        def MedicationRequestUpdate(self, _id: FhirId, data: JSON) -> Optional[Resource]:
            return mutation_resolver.update("MedicationRequest", _id, dict(data))

        @strawberry.mutation(description="Delete a MedicationRequest resource")
        def MedicationRequestDelete(self, _id: FhirId) -> Optional[Resource]:
            return mutation_resolver.delete("MedicationRequest", _id)

    # Create and return schema
    return strawberry.Schema(query=Query, mutation=Mutation)


def create_graphql_router(store: FHIRStore) -> GraphQLRouter:
    """Create a FastAPI router for the GraphQL endpoint.

    This creates a GraphQL router that can be mounted in the FastAPI app
    at the desired path (typically /$graphql per FHIR spec).

    Args:
        store: FHIRStore instance for data access

    Returns:
        Configured GraphQLRouter ready to be mounted
    """
    schema = create_schema(store)

    def get_context():
        """Provide context to resolvers."""
        return {"store": store}

    # Default query to show in GraphiQL with multiple examples
    default_query = """\
# FHIR GraphQL API - Example Queries
# Press the Play button or Ctrl+Enter to run

# 1. List patients (first 5)
{
  PatientList(_count: 5) {
    id
    resourceType
    data
  }
}

# ============================================
# More example queries (uncomment to try):
# ============================================

# 2. Search patients by gender
# {
#   PatientList(gender: "female", _count: 5) {
#     id
#     data
#   }
# }

# 3. Cursor-based pagination
# {
#   PatientConnection(first: 3) {
#     edges {
#       cursor
#       node { id data }
#     }
#     pageInfo {
#       hasNextPage
#       endCursor
#     }
#     total
#   }
# }

# 4. Get a specific patient by ID
# {
#   Patient(_id: "PATIENT_ID_HERE") {
#     id
#     data
#   }
# }

# 5. List observations for a patient
# {
#   ObservationList(patient: "Patient/PATIENT_ID", _count: 10) {
#     id
#     data
#   }
# }

# 6. List conditions with clinical status
# {
#   ConditionList(clinicalStatus: "active", _count: 10) {
#     id
#     data
#   }
# }

# 7. Search practitioners
# {
#   PractitionerList(_count: 5) {
#     id
#     data
#   }
# }

# 8. List organizations
# {
#   OrganizationList(_count: 5) {
#     id
#     data
#   }
# }

# 9. Search encounters by status
# {
#   EncounterList(status: "finished", _count: 5) {
#     id
#     data
#   }
# }

# 10. List medication requests
# {
#   MedicationRequestList(_count: 5) {
#     id
#     data
#   }
# }

# 11. Search questionnaires
# {
#   QuestionnaireList(_count: 5) {
#     id
#     data
#   }
# }

# 12. Create a new patient (mutation)
# mutation {
#   PatientCreate(data: {
#     resourceType: "Patient",
#     name: [{family: "Smith", given: ["John"]}],
#     gender: "male",
#     birthDate: "1990-01-15"
#   }) {
#     id
#     data
#   }
# }

# 13. Fetch multiple resource types at once
# {
#   patients: PatientList(_count: 3) { id data }
#   practitioners: PractitionerList(_count: 3) { id data }
#   organizations: OrganizationList(_count: 3) { id data }
# }

# 14. List locations
# {
#   LocationList(_count: 5) {
#     id
#     data
#   }
# }

# 15. Search immunizations
# {
#   ImmunizationList(_count: 5) {
#     id
#     data
#   }
# }
"""

    import json
    from fastapi.responses import HTMLResponse

    # Custom GraphQL router with default query in GraphiQL
    class FHIRGraphQLRouter(GraphQLRouter):
        """GraphQL router with custom GraphiQL default query."""

        _custom_html: str = ""

        async def render_graphql_ide(self, request) -> HTMLResponse:
            return HTMLResponse(self._custom_html)

    router = FHIRGraphQLRouter(
        schema=schema,
        context_getter=get_context,
        graphql_ide="graphiql",
    )

    # Set custom GraphiQL HTML with default query
    router._custom_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>FHIR GraphQL</title>
    <style>
        body {{ height: 100%; margin: 0; width: 100%; overflow: hidden; }}
        #graphiql {{ height: 100vh; }}
    </style>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/graphiql@3/graphiql.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/graphiql@3/graphiql.min.css" />
</head>
<body>
    <div id="graphiql"></div>
    <script>
        const fetcher = GraphiQL.createFetcher({{
            url: window.location.href,
        }});

        const defaultQuery = {json.dumps(default_query)};

        const root = ReactDOM.createRoot(document.getElementById('graphiql'));
        root.render(
            React.createElement(GraphiQL, {{
                fetcher: fetcher,
                defaultQuery: defaultQuery,
            }})
        );
    </script>
</body>
</html>"""

    logger.info("GraphQL schema created with %d resource types", len(SUPPORTED_TYPES))

    return router
