"""FHIR Resource Pydantic models for schema generation."""

from typing import Any

from pydantic import BaseModel, Field


# Common FHIR types
class Coding(BaseModel):
    """FHIR Coding type."""

    system: str | None = Field(default=None, description="Identity of the terminology system")
    version: str | None = Field(default=None, description="Version of the system")
    code: str | None = Field(default=None, description="Symbol in syntax defined by the system")
    display: str | None = Field(default=None, description="Representation defined by the system")
    userSelected: bool | None = Field(default=None, description="If this coding was chosen directly by the user")


class CodeableConcept(BaseModel):
    """FHIR CodeableConcept type."""

    coding: list[Coding] = Field(default_factory=list, description="Code defined by a terminology system")
    text: str | None = Field(default=None, description="Plain text representation of the concept")


class Reference(BaseModel):
    """FHIR Reference type."""

    reference: str | None = Field(default=None, description="Literal reference, Relative, internal or absolute URL")
    type: str | None = Field(default=None, description="Type the reference refers to (e.g. 'Patient')")
    display: str | None = Field(default=None, description="Text alternative for the resource")


class Identifier(BaseModel):
    """FHIR Identifier type."""

    use: str | None = Field(default=None, description="usual | official | temp | secondary | old")
    type: CodeableConcept | None = Field(default=None, description="Description of identifier")
    system: str | None = Field(default=None, description="The namespace for the identifier value")
    value: str | None = Field(default=None, description="The value that is unique")


class Period(BaseModel):
    """FHIR Period type."""

    start: str | None = Field(default=None, description="Starting time with inclusive boundary")
    end: str | None = Field(default=None, description="End time with inclusive boundary, if not ongoing")


class HumanName(BaseModel):
    """FHIR HumanName type."""

    use: str | None = Field(default=None, description="usual | official | temp | nickname | anonymous | old | maiden")
    text: str | None = Field(default=None, description="Text representation of the full name")
    family: str | None = Field(default=None, description="Family name (often called 'Surname')")
    given: list[str] = Field(default_factory=list, description="Given names (not always 'first')")
    prefix: list[str] = Field(default_factory=list, description="Parts that come before the name")
    suffix: list[str] = Field(default_factory=list, description="Parts that come after the name")
    period: Period | None = Field(default=None, description="Time period when name was/is in use")


class ContactPoint(BaseModel):
    """FHIR ContactPoint type."""

    system: str | None = Field(default=None, description="phone | fax | email | pager | url | sms | other")
    value: str | None = Field(default=None, description="The actual contact point details")
    use: str | None = Field(default=None, description="home | work | temp | old | mobile")
    rank: int | None = Field(default=None, description="Specify preferred order of use (1 = highest)")
    period: Period | None = Field(default=None, description="Time period when the contact point was/is in use")


class Address(BaseModel):
    """FHIR Address type."""

    use: str | None = Field(default=None, description="home | work | temp | old | billing")
    type: str | None = Field(default=None, description="postal | physical | both")
    text: str | None = Field(default=None, description="Text representation of the address")
    line: list[str] = Field(default_factory=list, description="Street name, number, direction & P.O. Box etc.")
    city: str | None = Field(default=None, description="Name of city, town etc.")
    district: str | None = Field(default=None, description="District name (aka county)")
    state: str | None = Field(default=None, description="Sub-unit of country (abbreviations ok)")
    postalCode: str | None = Field(default=None, description="Postal code for area")
    country: str | None = Field(default=None, description="Country (e.g. may be ISO 3166 2 or 3 letter code)")
    period: Period | None = Field(default=None, description="Time period when address was/is in use")


class Quantity(BaseModel):
    """FHIR Quantity type."""

    value: float | None = Field(default=None, description="Numerical value (with implicit precision)")
    comparator: str | None = Field(default=None, description="< | <= | >= | > - how to understand the value")
    unit: str | None = Field(default=None, description="Unit representation")
    system: str | None = Field(default=None, description="System that defines coded unit form")
    code: str | None = Field(default=None, description="Coded form of the unit")


class Meta(BaseModel):
    """FHIR Meta type."""

    versionId: str | None = Field(default=None, description="Version specific identifier")
    lastUpdated: str | None = Field(default=None, description="When the resource version last changed")
    source: str | None = Field(default=None, description="Identifies where the resource comes from")
    profile: list[str] = Field(default_factory=list, description="Profiles this resource claims to conform to")
    security: list[Coding] = Field(default_factory=list, description="Security Labels applied to this resource")
    tag: list[Coding] = Field(default_factory=list, description="Tags applied to this resource")


# Base resource
class Resource(BaseModel):
    """Base FHIR Resource."""

    resourceType: str = Field(..., description="Type of resource")
    id: str | None = Field(default=None, description="Logical id of this artifact")
    meta: Meta | None = Field(default=None, description="Metadata about the resource")


# Clinical resources
class Patient(Resource):
    """FHIR Patient resource."""

    resourceType: str = Field(default="Patient", description="Type of resource")
    identifier: list[Identifier] = Field(default_factory=list, description="An identifier for this patient")
    active: bool | None = Field(default=None, description="Whether this patient's record is in active use")
    name: list[HumanName] = Field(default_factory=list, description="A name associated with the patient")
    telecom: list[ContactPoint] = Field(default_factory=list, description="A contact detail for the individual")
    gender: str | None = Field(default=None, description="male | female | other | unknown")
    birthDate: str | None = Field(default=None, description="The date of birth for the individual")
    deceasedBoolean: bool | None = Field(default=None, description="Indicates if the individual is deceased")
    deceasedDateTime: str | None = Field(default=None, description="Date/time of death if deceased")
    address: list[Address] = Field(default_factory=list, description="An address for the individual")
    maritalStatus: CodeableConcept | None = Field(default=None, description="Marital (civil) status of a patient")
    multipleBirthBoolean: bool | None = Field(default=None, description="Whether patient is part of a multiple birth")
    multipleBirthInteger: int | None = Field(default=None, description="Birth order if part of multiple birth")


class Practitioner(Resource):
    """FHIR Practitioner resource."""

    resourceType: str = Field(default="Practitioner", description="Type of resource")
    identifier: list[Identifier] = Field(default_factory=list, description="An identifier for the person")
    active: bool | None = Field(default=None, description="Whether this practitioner's record is in active use")
    name: list[HumanName] = Field(default_factory=list, description="The name(s) associated with the practitioner")
    telecom: list[ContactPoint] = Field(default_factory=list, description="A contact detail for the practitioner")
    address: list[Address] = Field(default_factory=list, description="Address(es) of the practitioner")
    gender: str | None = Field(default=None, description="male | female | other | unknown")
    birthDate: str | None = Field(default=None, description="The date on which the practitioner was born")


class Organization(Resource):
    """FHIR Organization resource."""

    resourceType: str = Field(default="Organization", description="Type of resource")
    identifier: list[Identifier] = Field(default_factory=list, description="Identifies this organization")
    active: bool | None = Field(default=None, description="Whether the organization's record is still in active use")
    type: list[CodeableConcept] = Field(default_factory=list, description="Kind of organization")
    name: str | None = Field(default=None, description="Name used for the organization")
    alias: list[str] = Field(default_factory=list, description="A list of alternate names")
    telecom: list[ContactPoint] = Field(default_factory=list, description="A contact detail for the organization")
    address: list[Address] = Field(default_factory=list, description="An address for the organization")
    partOf: Reference | None = Field(
        default=None, description="The organization of which this organization forms a part"
    )


class Condition(Resource):
    """FHIR Condition resource."""

    resourceType: str = Field(default="Condition", description="Type of resource")
    identifier: list[Identifier] = Field(default_factory=list, description="External Ids for this condition")
    clinicalStatus: CodeableConcept | None = Field(
        default=None, description="active | recurrence | relapse | inactive | remission | resolved"
    )
    verificationStatus: CodeableConcept | None = Field(
        default=None, description="unconfirmed | provisional | differential | confirmed | refuted | entered-in-error"
    )
    category: list[CodeableConcept] = Field(default_factory=list, description="problem-list-item | encounter-diagnosis")
    severity: CodeableConcept | None = Field(default=None, description="Subjective severity of condition")
    code: CodeableConcept | None = Field(
        default=None, description="Identification of the condition, problem or diagnosis"
    )
    bodySite: list[CodeableConcept] = Field(default_factory=list, description="Anatomical location, if relevant")
    subject: Reference | None = Field(default=None, description="Who has the condition?")
    encounter: Reference | None = Field(default=None, description="Encounter created as part of")
    onsetDateTime: str | None = Field(default=None, description="Estimated or actual date, date-time, or age")
    onsetAge: Quantity | None = Field(default=None, description="Onset age")
    onsetPeriod: Period | None = Field(default=None, description="Onset period")
    onsetString: str | None = Field(default=None, description="Onset as text")
    abatementDateTime: str | None = Field(default=None, description="When in resolution/remission")
    recordedDate: str | None = Field(default=None, description="Date record was first recorded")
    recorder: Reference | None = Field(default=None, description="Who recorded the condition")
    asserter: Reference | None = Field(default=None, description="Person who asserts this condition")


class Observation(Resource):
    """FHIR Observation resource."""

    resourceType: str = Field(default="Observation", description="Type of resource")
    identifier: list[Identifier] = Field(default_factory=list, description="Business Identifier for observation")
    status: str = Field(
        ...,
        description="registered | preliminary | final | amended | corrected | cancelled | entered-in-error | unknown",
    )
    category: list[CodeableConcept] = Field(default_factory=list, description="Classification of type of observation")
    code: CodeableConcept = Field(..., description="Type of observation (code / type)")
    subject: Reference | None = Field(default=None, description="Who and/or what the observation is about")
    encounter: Reference | None = Field(
        default=None, description="Healthcare event during which this observation is made"
    )
    effectiveDateTime: str | None = Field(
        default=None, description="Clinically relevant time/time-period for observation"
    )
    effectivePeriod: Period | None = Field(default=None, description="Clinically relevant time period")
    issued: str | None = Field(default=None, description="Date/Time this version was made available")
    performer: list[Reference] = Field(default_factory=list, description="Who is responsible for the observation")
    valueQuantity: Quantity | None = Field(default=None, description="Actual result")
    valueCodeableConcept: CodeableConcept | None = Field(default=None, description="Actual result as CodeableConcept")
    valueString: str | None = Field(default=None, description="Actual result as string")
    valueBoolean: bool | None = Field(default=None, description="Actual result as boolean")
    valueInteger: int | None = Field(default=None, description="Actual result as integer")
    interpretation: list[CodeableConcept] = Field(default_factory=list, description="High, low, normal, etc.")
    note: list[dict[str, Any]] = Field(default_factory=list, description="Comments about the observation")
    bodySite: CodeableConcept | None = Field(default=None, description="Observed body part")


class Encounter(Resource):
    """FHIR Encounter resource."""

    resourceType: str = Field(default="Encounter", description="Type of resource")
    identifier: list[Identifier] = Field(
        default_factory=list, description="Identifier(s) by which this encounter is known"
    )
    status: str = Field(
        ...,
        description="Encounter status (planned|arrived|triaged|in-progress|onleave|finished|cancelled)",
    )
    class_: CodeableConcept | None = Field(
        default=None, alias="class", description="Classification of patient encounter"
    )
    type: list[CodeableConcept] = Field(default_factory=list, description="Specific type of encounter")
    serviceType: CodeableConcept | None = Field(default=None, description="Specific type of service")
    priority: CodeableConcept | None = Field(default=None, description="Indicates the urgency of the encounter")
    subject: Reference | None = Field(default=None, description="The patient or group present at the encounter")
    participant: list[dict[str, Any]] = Field(
        default_factory=list, description="List of participants involved in the encounter"
    )
    period: Period | None = Field(default=None, description="The start and end time of the encounter")
    reasonCode: list[CodeableConcept] = Field(
        default_factory=list, description="Coded reason the encounter takes place"
    )
    reasonReference: list[Reference] = Field(
        default_factory=list, description="Reason the encounter takes place (reference)"
    )


class MedicationRequest(Resource):
    """FHIR MedicationRequest resource."""

    resourceType: str = Field(default="MedicationRequest", description="Type of resource")
    identifier: list[Identifier] = Field(default_factory=list, description="External ids for this request")
    status: str = Field(
        ..., description="active | on-hold | cancelled | completed | entered-in-error | stopped | draft | unknown"
    )
    statusReason: CodeableConcept | None = Field(default=None, description="Reason for current status")
    intent: str = Field(
        ...,
        description="proposal | plan | order | original-order | reflex-order | filler-order | instance-order | option",
    )
    category: list[CodeableConcept] = Field(default_factory=list, description="Type of medication usage")
    priority: str | None = Field(default=None, description="routine | urgent | asap | stat")
    medicationCodeableConcept: CodeableConcept | None = Field(default=None, description="Medication to be taken")
    medicationReference: Reference | None = Field(default=None, description="Medication to be taken (reference)")
    subject: Reference | None = Field(default=None, description="Who or group medication request is for")
    encounter: Reference | None = Field(
        default=None, description="Encounter created as part of encounter/admission/stay"
    )
    authoredOn: str | None = Field(default=None, description="When request was initially authored")
    requester: Reference | None = Field(default=None, description="Who/What requested the Request")
    performer: Reference | None = Field(default=None, description="Intended performer of administration")
    reasonCode: list[CodeableConcept] = Field(
        default_factory=list, description="Reason or indication for ordering or not ordering the medication"
    )
    reasonReference: list[Reference] = Field(
        default_factory=list, description="Condition or observation that supports why the prescription is being written"
    )
    dosageInstruction: list[dict[str, Any]] = Field(
        default_factory=list, description="How the medication should be taken"
    )


class Procedure(Resource):
    """FHIR Procedure resource."""

    resourceType: str = Field(default="Procedure", description="Type of resource")
    identifier: list[Identifier] = Field(default_factory=list, description="External Identifiers for this procedure")
    status: str = Field(
        ...,
        description="preparation | in-progress | not-done | on-hold | stopped | completed | entered-in-error | unknown",
    )
    statusReason: CodeableConcept | None = Field(default=None, description="Reason for current status")
    category: CodeableConcept | None = Field(default=None, description="Classification of the procedure")
    code: CodeableConcept | None = Field(default=None, description="Identification of the procedure")
    subject: Reference | None = Field(default=None, description="Who the procedure was performed on")
    encounter: Reference | None = Field(default=None, description="Encounter created as part of")
    performedDateTime: str | None = Field(default=None, description="When the procedure was performed")
    performedPeriod: Period | None = Field(default=None, description="When the procedure was performed (period)")
    recorder: Reference | None = Field(default=None, description="Who recorded the procedure")
    asserter: Reference | None = Field(default=None, description="Person who asserts this procedure")
    performer: list[dict[str, Any]] = Field(default_factory=list, description="The people who performed the procedure")
    reasonCode: list[CodeableConcept] = Field(default_factory=list, description="Coded reason procedure performed")
    reasonReference: list[Reference] = Field(
        default_factory=list, description="The justification that the procedure was performed"
    )
    bodySite: list[CodeableConcept] = Field(default_factory=list, description="Target body sites")
    outcome: CodeableConcept | None = Field(default=None, description="The result of procedure")


# Terminology resources
class ValueSet(Resource):
    """FHIR ValueSet resource."""

    resourceType: str = Field(default="ValueSet", description="Type of resource")
    url: str | None = Field(default=None, description="Canonical identifier for this value set")
    identifier: list[Identifier] = Field(default_factory=list, description="Additional identifier for the value set")
    version: str | None = Field(default=None, description="Business version of the value set")
    name: str | None = Field(default=None, description="Name for this value set (computer friendly)")
    title: str | None = Field(default=None, description="Name for this value set (human friendly)")
    status: str = Field(..., description="draft | active | retired | unknown")
    experimental: bool | None = Field(default=None, description="For testing purposes, not real usage")
    date: str | None = Field(default=None, description="Date last changed")
    publisher: str | None = Field(default=None, description="Name of the publisher")
    description: str | None = Field(default=None, description="Natural language description of the value set")
    compose: dict[str, Any] | None = Field(default=None, description="Content logical definition of the value set")
    expansion: dict[str, Any] | None = Field(default=None, description="Used when the value set is 'expanded'")


class CodeSystem(Resource):
    """FHIR CodeSystem resource."""

    resourceType: str = Field(default="CodeSystem", description="Type of resource")
    url: str | None = Field(default=None, description="Canonical identifier for this code system")
    identifier: list[Identifier] = Field(default_factory=list, description="Additional identifier for the code system")
    version: str | None = Field(default=None, description="Business version of the code system")
    name: str | None = Field(default=None, description="Name for this code system (computer friendly)")
    title: str | None = Field(default=None, description="Name for this code system (human friendly)")
    status: str = Field(..., description="draft | active | retired | unknown")
    experimental: bool | None = Field(default=None, description="For testing purposes, not real usage")
    date: str | None = Field(default=None, description="Date last changed")
    publisher: str | None = Field(default=None, description="Name of the publisher")
    description: str | None = Field(default=None, description="Natural language description of the code system")
    content: str = Field(..., description="not-present | example | fragment | complete | supplement")
    count: int | None = Field(default=None, description="Total concepts in the code system")
    concept: list[dict[str, Any]] = Field(default_factory=list, description="Concepts in the code system")


# Registry of all resource models
RESOURCE_MODELS: dict[str, type[Resource]] = {
    "Patient": Patient,
    "Practitioner": Practitioner,
    "Organization": Organization,
    "Condition": Condition,
    "Observation": Observation,
    "Encounter": Encounter,
    "MedicationRequest": MedicationRequest,
    "Procedure": Procedure,
    "ValueSet": ValueSet,
    "CodeSystem": CodeSystem,
}


def get_resource_schema(resource_type: str) -> dict[str, Any] | None:
    """Get JSON Schema for a resource type.

    Args:
        resource_type: FHIR resource type name

    Returns:
        JSON Schema dict or None if not found
    """
    model = RESOURCE_MODELS.get(resource_type)
    if model:
        return model.model_json_schema()
    return None


def get_all_schemas() -> dict[str, dict[str, Any]]:
    """Get JSON Schemas for all resource types.

    Returns:
        Dict mapping resource type to JSON Schema
    """
    return {name: model.model_json_schema() for name, model in RESOURCE_MODELS.items()}
