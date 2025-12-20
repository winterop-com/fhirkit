"""FHIR search parameter handling."""

import re
from datetime import date, datetime
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs

if TYPE_CHECKING:
    from ..storage.fhir_store import FHIRStore

# Search parameter definitions by resource type
SEARCH_PARAMS: dict[str, dict[str, dict[str, Any]]] = {
    "Patient": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string", "search_name": True},
        "family": {"path": "name.family", "type": "string"},
        "given": {"path": "name.given", "type": "string"},
        "gender": {"path": "gender", "type": "token"},
        "birthdate": {"path": "birthDate", "type": "date"},
        "address": {"path": "address", "type": "string", "search_address": True},
        "address-city": {"path": "address.city", "type": "string"},
        "address-state": {"path": "address.state", "type": "string"},
        "address-postalcode": {"path": "address.postalCode", "type": "string"},
        "telecom": {"path": "telecom.value", "type": "token"},
        "active": {"path": "active", "type": "token"},
    },
    "Condition": {
        "_id": {"path": "id", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "code": {"path": "code.coding", "type": "token"},
        "clinical-status": {"path": "clinicalStatus.coding", "type": "token"},
        "verification-status": {"path": "verificationStatus.coding", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "onset-date": {"path": "onsetDateTime", "type": "date"},
        "severity": {"path": "severity.coding", "type": "token"},
    },
    "Observation": {
        "_id": {"path": "id", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "code": {"path": "code.coding", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "effectiveDateTime", "type": "date"},
        "value-quantity": {"path": "valueQuantity.value", "type": "quantity"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
    },
    "MedicationRequest": {
        "_id": {"path": "id", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "code": {"path": "medicationCodeableConcept.coding", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "intent": {"path": "intent", "type": "token"},
        "authoredon": {"path": "authoredOn", "type": "date"},
        "requester": {"path": "requester.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
    },
    "Encounter": {
        "_id": {"path": "id", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "class": {"path": "class.code", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "date": {"path": "period.start", "type": "date"},
        "participant": {"path": "participant.individual.reference", "type": "reference"},
        "service-provider": {"path": "serviceProvider.reference", "type": "reference"},
    },
    "Procedure": {
        "_id": {"path": "id", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "code": {"path": "code.coding", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "performedDateTime", "type": "date"},
        "category": {"path": "category.coding", "type": "token"},
        "performer": {"path": "performer.actor.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
    },
    "Practitioner": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string", "search_name": True},
        "family": {"path": "name.family", "type": "string"},
        "given": {"path": "name.given", "type": "string"},
        "active": {"path": "active", "type": "token"},
    },
    "Organization": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "active": {"path": "active", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "address": {"path": "address", "type": "string", "search_address": True},
        "address-city": {"path": "address.city", "type": "string"},
        "address-state": {"path": "address.state", "type": "string"},
        "partof": {"path": "partOf.reference", "type": "reference"},
    },
    "ValueSet": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
    },
    "CodeSystem": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
    },
    "Library": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
    },
    "DiagnosticReport": {
        "_id": {"path": "id", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "code": {"path": "code.coding", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "effectiveDateTime", "type": "date"},
        "issued": {"path": "issued", "type": "date"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
        "performer": {"path": "performer.reference", "type": "reference"},
        "result": {"path": "result.reference", "type": "reference"},
        "conclusion": {"path": "conclusion", "type": "string"},
    },
    "AllergyIntolerance": {
        "_id": {"path": "id", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "code": {"path": "code.coding", "type": "token"},
        "clinical-status": {"path": "clinicalStatus.coding", "type": "token"},
        "verification-status": {"path": "verificationStatus.coding", "type": "token"},
        "category": {"path": "category", "type": "token"},
        "criticality": {"path": "criticality", "type": "token"},
        "type": {"path": "type", "type": "token"},
        "onset": {"path": "onsetDateTime", "type": "date"},
        "date": {"path": "recordedDate", "type": "date"},
        "recorder": {"path": "recorder.reference", "type": "reference"},
        "asserter": {"path": "asserter.reference", "type": "reference"},
    },
    "Immunization": {
        "_id": {"path": "id", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "vaccine-code": {"path": "vaccineCode.coding", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "occurrenceDateTime", "type": "date"},
        "lot-number": {"path": "lotNumber", "type": "string"},
        "performer": {"path": "performer.actor.reference", "type": "reference"},
        "location": {"path": "location.reference", "type": "reference"},
        "reaction": {"path": "reaction.detail.reference", "type": "reference"},
        "site": {"path": "site.coding", "type": "token"},
        "route": {"path": "route.coding", "type": "token"},
    },
    "CarePlan": {
        "_id": {"path": "id", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "intent": {"path": "intent", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "date": {"path": "period.start", "type": "date"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
        "condition": {"path": "addresses.reference", "type": "reference"},
    },
    "Goal": {
        "_id": {"path": "id", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "lifecycle-status": {"path": "lifecycleStatus", "type": "token"},
        "achievement-status": {"path": "achievementStatus.coding", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "start-date": {"path": "startDate", "type": "date"},
        "target-date": {"path": "target.dueDate", "type": "date"},
    },
    "ServiceRequest": {
        "_id": {"path": "id", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "code": {"path": "code.coding", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "intent": {"path": "intent", "type": "token"},
        "priority": {"path": "priority", "type": "token"},
        "authored": {"path": "authoredOn", "type": "date"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
        "requester": {"path": "requester.reference", "type": "reference"},
        "performer": {"path": "performer.reference", "type": "reference"},
    },
    "DocumentReference": {
        "_id": {"path": "id", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "type": {"path": "type.coding", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "author": {"path": "author.reference", "type": "reference"},
        "encounter": {"path": "context.encounter.reference", "type": "reference"},
        "custodian": {"path": "custodian.reference", "type": "reference"},
    },
    "Medication": {
        "_id": {"path": "id", "type": "token"},
        "code": {"path": "code.coding", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "form": {"path": "form.coding", "type": "token"},
        "manufacturer": {"path": "manufacturer.reference", "type": "reference"},
        "lot-number": {"path": "batch.lotNumber", "type": "string"},
        "expiration-date": {"path": "batch.expirationDate", "type": "date"},
    },
    "Measure": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "description": {"path": "description", "type": "string"},
        "publisher": {"path": "publisher", "type": "string"},
        "date": {"path": "date", "type": "date"},
        "effective": {"path": "effectivePeriod.start", "type": "date"},
        "context-type": {"path": "useContext.code", "type": "token"},
        "topic": {"path": "topic.coding", "type": "token"},
    },
    "MeasureReport": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "measure": {"path": "measure", "type": "uri"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "date": {"path": "date", "type": "date"},
        "reporter": {"path": "reporter.reference", "type": "reference"},
        "period": {"path": "period.start", "type": "date"},
        "evaluated-resource": {"path": "evaluatedResource.reference", "type": "reference"},
    },
    "Group": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "type": {"path": "type", "type": "token"},
        "actual": {"path": "actual", "type": "token"},
        "code": {"path": "code.coding", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "member": {"path": "member.entity.reference", "type": "reference"},
        "managing-entity": {"path": "managingEntity.reference", "type": "reference"},
        "characteristic": {"path": "characteristic.code.coding", "type": "token"},
    },
    # === New Resource Types ===
    "Coverage": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "beneficiary.reference", "type": "reference"},
        "beneficiary": {"path": "beneficiary.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "payor": {"path": "payor.reference", "type": "reference"},
        "subscriber": {"path": "subscriber.reference", "type": "reference"},
        "policy-holder": {"path": "policyHolder.reference", "type": "reference"},
        "class-type": {"path": "class.type.coding", "type": "token"},
        "class-value": {"path": "class.value", "type": "string"},
    },
    "Claim": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "created": {"path": "created", "type": "date"},
        "provider": {"path": "provider.reference", "type": "reference"},
        "use": {"path": "use", "type": "token"},
        "priority": {"path": "priority.coding", "type": "token"},
        "insurer": {"path": "insurer.reference", "type": "reference"},
        "facility": {"path": "facility.reference", "type": "reference"},
        "care-team": {"path": "careTeam.provider.reference", "type": "reference"},
    },
    "ExplanationOfBenefit": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "created": {"path": "created", "type": "date"},
        "claim": {"path": "claim.reference", "type": "reference"},
        "provider": {"path": "provider.reference", "type": "reference"},
        "insurer": {"path": "insurer.reference", "type": "reference"},
        "outcome": {"path": "outcome", "type": "token"},
        "use": {"path": "use", "type": "token"},
        "disposition": {"path": "disposition", "type": "string"},
        "facility": {"path": "facility.reference", "type": "reference"},
        "coverage": {"path": "insurance.coverage.reference", "type": "reference"},
        "care-team": {"path": "careTeam.provider.reference", "type": "reference"},
    },
    "ClaimResponse": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "created": {"path": "created", "type": "date"},
        "request": {"path": "request.reference", "type": "reference"},
        "insurer": {"path": "insurer.reference", "type": "reference"},
        "outcome": {"path": "outcome", "type": "token"},
        "use": {"path": "use", "type": "token"},
        "disposition": {"path": "disposition", "type": "string"},
        "requestor": {"path": "requestor.reference", "type": "reference"},
        "payment-date": {"path": "payment.date", "type": "date"},
    },
    "Account": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "owner": {"path": "owner.reference", "type": "reference"},
        "period": {"path": "servicePeriod", "type": "date"},
    },
    "CoverageEligibilityRequest": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "created": {"path": "created", "type": "date"},
        "provider": {"path": "provider.reference", "type": "reference"},
        "insurer": {"path": "insurer.reference", "type": "reference"},
        "facility": {"path": "facility.reference", "type": "reference"},
    },
    "CoverageEligibilityResponse": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "created": {"path": "created", "type": "date"},
        "request": {"path": "request.reference", "type": "reference"},
        "insurer": {"path": "insurer.reference", "type": "reference"},
        "outcome": {"path": "outcome", "type": "token"},
        "requestor": {"path": "requestor.reference", "type": "reference"},
        "disposition": {"path": "disposition", "type": "string"},
    },
    "PaymentNotice": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "created": {"path": "created", "type": "date"},
        "provider": {"path": "provider.reference", "type": "reference"},
        "request": {"path": "request.reference", "type": "reference"},
        "response": {"path": "response.reference", "type": "reference"},
        "payment-status": {"path": "paymentStatus.coding", "type": "token"},
        "payment-date": {"path": "paymentDate", "type": "date"},
    },
    "PaymentReconciliation": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "created": {"path": "created", "type": "date"},
        "outcome": {"path": "outcome", "type": "token"},
        "payment-issuer": {"path": "paymentIssuer.reference", "type": "reference"},
        "request": {"path": "request.reference", "type": "reference"},
        "requestor": {"path": "requestor.reference", "type": "reference"},
        "disposition": {"path": "disposition", "type": "string"},
        "payment-date": {"path": "paymentDate", "type": "date"},
    },
    "ActivityDefinition": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
        "kind": {"path": "kind", "type": "token"},
        "context-type": {"path": "useContext.code", "type": "token"},
        "topic": {"path": "topic.coding", "type": "token"},
    },
    "PlanDefinition": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
        "type": {"path": "type.coding", "type": "token"},
        "context-type": {"path": "useContext.code", "type": "token"},
        "definition": {"path": "action.definitionCanonical", "type": "reference"},
    },
    "GuidanceResponse": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "request": {"path": "requestIdentifier", "type": "token"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
    },
    "DeviceRequest": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "intent": {"path": "intent", "type": "token"},
        "code": {"path": "codeCodeableConcept.coding", "type": "token"},
        "authored-on": {"path": "authoredOn", "type": "date"},
        "requester": {"path": "requester.reference", "type": "reference"},
        "performer": {"path": "performer.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
        "event-date": {"path": "occurrenceDateTime", "type": "date"},
        "device": {"path": "codeReference.reference", "type": "reference"},
        "group-identifier": {"path": "groupIdentifier", "type": "token"},
        "instantiates-canonical": {"path": "instantiatesCanonical", "type": "reference"},
        "instantiates-uri": {"path": "instantiatesUri", "type": "uri"},
        "insurance": {"path": "insurance.reference", "type": "reference"},
        "based-on": {"path": "basedOn.reference", "type": "reference"},
        "prior-request": {"path": "priorRequest.reference", "type": "reference"},
    },
    "Person": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string", "search_name": True},
        "gender": {"path": "gender", "type": "token"},
        "birthdate": {"path": "birthDate", "type": "date"},
        "address": {"path": "address", "type": "string", "search_address": True},
        "telecom": {"path": "telecom.value", "type": "token"},
        "organization": {"path": "managingOrganization.reference", "type": "reference"},
        "patient": {"path": "link.target.reference", "type": "reference"},
        "practitioner": {"path": "link.target.reference", "type": "reference"},
        "relatedperson": {"path": "link.target.reference", "type": "reference"},
    },
    "Substance": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "code": {"path": "code.coding", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "container-identifier": {"path": "instance.identifier", "type": "token"},
        "expiry": {"path": "instance.expiry", "type": "date"},
        "quantity": {"path": "instance.quantity.value", "type": "quantity"},
    },
    "ImmunizationRecommendation": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "date": {"path": "date", "type": "date"},
        "vaccine-type": {"path": "recommendation.vaccineCode.coding", "type": "token"},
        "target-disease": {"path": "recommendation.targetDisease.coding", "type": "token"},
        "status": {"path": "recommendation.forecastStatus.coding", "type": "token"},
        "support": {"path": "recommendation.supportingImmunization.reference", "type": "reference"},
    },
    "VisionPrescription": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "datewritten": {"path": "dateWritten", "type": "date"},
        "prescriber": {"path": "prescriber.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
    },
    "ChargeItem": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "code": {"path": "code.coding", "type": "token"},
        "context": {"path": "context.reference", "type": "reference"},
        "occurrence": {"path": "occurrenceDateTime", "type": "date"},
        "enterer": {"path": "enterer.reference", "type": "reference"},
        "entered-date": {"path": "enteredDate", "type": "date"},
        "performer-actor": {"path": "performer.actor.reference", "type": "reference"},
        "performing-organization": {"path": "performingOrganization.reference", "type": "reference"},
        "requesting-organization": {"path": "requestingOrganization.reference", "type": "reference"},
        "quantity": {"path": "quantity.value", "type": "quantity"},
        "account": {"path": "account.reference", "type": "reference"},
        "service": {"path": "service.reference", "type": "reference"},
    },
    "ChargeItemDefinition": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
        "description": {"path": "description", "type": "string"},
    },
    "DocumentManifest": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "created": {"path": "created", "type": "date"},
        "author": {"path": "author.reference", "type": "reference"},
        "recipient": {"path": "recipient.reference", "type": "reference"},
        "description": {"path": "description", "type": "string"},
        "source": {"path": "source", "type": "uri"},
        "item": {"path": "content.reference", "type": "reference"},
    },
    "Contract": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "issued": {"path": "issued", "type": "date"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "authority": {"path": "authority.reference", "type": "reference"},
        "domain": {"path": "domain.reference", "type": "reference"},
        "signer": {"path": "signer.party.reference", "type": "reference"},
        "url": {"path": "url", "type": "uri"},
    },
    "Invoice": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "date": {"path": "date", "type": "date"},
        "issuer": {"path": "issuer.reference", "type": "reference"},
        "recipient": {"path": "recipient.reference", "type": "reference"},
        "account": {"path": "account.reference", "type": "reference"},
        "type": {"path": "type.coding", "type": "token"},
        "participant": {"path": "participant.actor.reference", "type": "reference"},
        "participant-role": {"path": "participant.role.coding", "type": "token"},
        "totalgross": {"path": "totalGross.value", "type": "quantity"},
        "totalnet": {"path": "totalNet.value", "type": "quantity"},
    },
    "Basic": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "code": {"path": "code.coding", "type": "token"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "created": {"path": "created", "type": "date"},
        "author": {"path": "author.reference", "type": "reference"},
    },
    "ImplementationGuide": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "publisher": {"path": "publisher", "type": "string"},
        "date": {"path": "date", "type": "date"},
        "description": {"path": "description", "type": "string"},
        "depends-on": {"path": "dependsOn.uri", "type": "reference"},
        "resource": {"path": "definition.resource.reference.reference", "type": "reference"},
    },
    "CompartmentDefinition": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "code": {"path": "code", "type": "token"},
        "publisher": {"path": "publisher", "type": "string"},
        "date": {"path": "date", "type": "date"},
        "resource": {"path": "resource.code", "type": "token"},
    },
    "MessageDefinition": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "publisher": {"path": "publisher", "type": "string"},
        "date": {"path": "date", "type": "date"},
        "category": {"path": "category", "type": "token"},
        "event": {"path": "eventCoding", "type": "token"},
        "focus": {"path": "focus.code", "type": "token"},
        "parent": {"path": "parent", "type": "reference"},
    },
    "StructureMap": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "publisher": {"path": "publisher", "type": "string"},
        "date": {"path": "date", "type": "date"},
        "description": {"path": "description", "type": "string"},
        "identifier": {"path": "identifier", "type": "token"},
    },
    "TestScript": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "publisher": {"path": "publisher", "type": "string"},
        "date": {"path": "date", "type": "date"},
        "description": {"path": "description", "type": "string"},
        "identifier": {"path": "identifier", "type": "token"},
        "testscript-capability": {"path": "metadata.capability.description", "type": "string"},
    },
    "TestReport": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "testscript": {"path": "testScript.reference", "type": "reference"},
        "result": {"path": "result", "type": "token"},
        "tester": {"path": "tester", "type": "string"},
        "issued": {"path": "issued", "type": "date"},
    },
    "GraphDefinition": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "start": {"path": "start", "type": "token"},
    },
    "NamingSystem": {
        "_id": {"path": "id", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "kind": {"path": "kind", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
        "responsible": {"path": "responsible", "type": "string"},
        "type": {"path": "type.coding", "type": "token"},
        "value": {"path": "uniqueId.value", "type": "string"},
    },
    "VerificationResult": {
        "_id": {"path": "id", "type": "token"},
        "target": {"path": "target.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
    },
    "EventDefinition": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
    },
    "ObservationDefinition": {
        "_id": {"path": "id", "type": "token"},
        "code": {"path": "code.coding", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
    },
    "SpecimenDefinition": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "type": {"path": "typeCollected.coding", "type": "token"},
        "container": {"path": "typeTested.container.type.coding", "type": "token"},
    },
    "InsurancePlan": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "owned-by": {"path": "ownedBy.reference", "type": "reference"},
        "administered-by": {"path": "administeredBy.reference", "type": "reference"},
    },
    "EnrollmentRequest": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "subject": {"path": "candidate.reference", "type": "reference"},
        "patient": {"path": "candidate.reference", "type": "reference"},
    },
    "EnrollmentResponse": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "request": {"path": "request.reference", "type": "reference"},
    },
    "Linkage": {
        "_id": {"path": "id", "type": "token"},
        "author": {"path": "author.reference", "type": "reference"},
        "item": {"path": "item.resource.reference", "type": "reference"},
        "source": {"path": "item.resource.reference", "type": "reference"},
    },
    "DeviceUseStatement": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "device": {"path": "device.reference", "type": "reference"},
    },
    "Device": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "manufacturer": {"path": "manufacturer", "type": "string"},
        "model": {"path": "modelNumber", "type": "string"},
        "udi-carrier": {"path": "udiCarrier.carrierHRF", "type": "string"},
        "udi-di": {"path": "udiCarrier.deviceIdentifier", "type": "string"},
        "device-name": {"path": "deviceName.name", "type": "string"},
        "organization": {"path": "owner.reference", "type": "reference"},
        "location": {"path": "location.reference", "type": "reference"},
    },
    "Location": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "address": {"path": "address", "type": "string", "search_address": True},
        "address-city": {"path": "address.city", "type": "string"},
        "address-state": {"path": "address.state", "type": "string"},
        "address-postalcode": {"path": "address.postalCode", "type": "string"},
        "address-country": {"path": "address.country", "type": "string"},
        "operational-status": {"path": "operationalStatus.coding", "type": "token"},
        "organization": {"path": "managingOrganization.reference", "type": "reference"},
        "partof": {"path": "partOf.reference", "type": "reference"},
    },
    "Slot": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "schedule": {"path": "schedule.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "start": {"path": "start", "type": "date"},
        "end": {"path": "end", "type": "date"},
        "service-category": {"path": "serviceCategory.coding", "type": "token"},
        "service-type": {"path": "serviceType.coding", "type": "token"},
        "specialty": {"path": "specialty.coding", "type": "token"},
        "appointment-type": {"path": "appointmentType.coding", "type": "token"},
    },
    "Appointment": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "participant.actor.reference", "type": "reference"},
        "actor": {"path": "participant.actor.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "start", "type": "date"},
        "start": {"path": "start", "type": "date"},
        "end": {"path": "end", "type": "date"},
        "service-category": {"path": "serviceCategory.coding", "type": "token"},
        "service-type": {"path": "serviceType.coding", "type": "token"},
        "specialty": {"path": "specialty.coding", "type": "token"},
        "appointment-type": {"path": "appointmentType.coding", "type": "token"},
        "reason-code": {"path": "reasonCode.coding", "type": "token"},
        "slot": {"path": "slot.reference", "type": "reference"},
        "location": {"path": "participant.actor.reference", "type": "reference"},
        "practitioner": {"path": "participant.actor.reference", "type": "reference"},
    },
    "AppointmentResponse": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "appointment": {"path": "appointment.reference", "type": "reference"},
        "actor": {"path": "actor.reference", "type": "reference"},
        "patient": {"path": "actor.reference", "type": "reference"},
        "practitioner": {"path": "actor.reference", "type": "reference"},
        "location": {"path": "actor.reference", "type": "reference"},
        "part-status": {"path": "participantStatus", "type": "token"},
    },
    "Schedule": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "actor": {"path": "actor.reference", "type": "reference"},
        "active": {"path": "active", "type": "token"},
        "date": {"path": "planningHorizon.start", "type": "date"},
        "service-category": {"path": "serviceCategory.coding", "type": "token"},
        "service-type": {"path": "serviceType.coding", "type": "token"},
        "specialty": {"path": "specialty.coding", "type": "token"},
    },
    "PractitionerRole": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "practitioner": {"path": "practitioner.reference", "type": "reference"},
        "organization": {"path": "organization.reference", "type": "reference"},
        "role": {"path": "code.coding", "type": "token"},
        "specialty": {"path": "specialty.coding", "type": "token"},
        "active": {"path": "active", "type": "token"},
        "location": {"path": "location.reference", "type": "reference"},
        "service": {"path": "healthcareService.reference", "type": "reference"},
        "telecom": {"path": "telecom.value", "type": "token"},
        "date": {"path": "period.start", "type": "date"},
    },
    "RelatedPerson": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "name": {"path": "name", "type": "string", "search_name": True},
        "active": {"path": "active", "type": "token"},
        "gender": {"path": "gender", "type": "token"},
        "birthdate": {"path": "birthDate", "type": "date"},
        "relationship": {"path": "relationship.coding", "type": "token"},
        "telecom": {"path": "telecom.value", "type": "token"},
        "address": {"path": "address", "type": "string", "search_address": True},
        "address-city": {"path": "address.city", "type": "string"},
        "address-state": {"path": "address.state", "type": "string"},
    },
    "CareTeam": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "participant": {"path": "participant.member.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
        "date": {"path": "period.start", "type": "date"},
        "name": {"path": "name", "type": "string"},
    },
    "Task": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "for.reference", "type": "reference"},
        "subject": {"path": "for.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "intent": {"path": "intent", "type": "token"},
        "code": {"path": "code.coding", "type": "token"},
        "owner": {"path": "owner.reference", "type": "reference"},
        "requester": {"path": "requester.reference", "type": "reference"},
        "focus": {"path": "focus.reference", "type": "reference"},
        "based-on": {"path": "basedOn.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
        "priority": {"path": "priority", "type": "token"},
        "authored-on": {"path": "authoredOn", "type": "date"},
        "modified": {"path": "lastModified", "type": "date"},
        "period": {"path": "executionPeriod.start", "type": "date"},
        "business-status": {"path": "businessStatus.coding", "type": "token"},
    },
    # === Forms ===
    "Questionnaire": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "publisher": {"path": "publisher", "type": "string"},
        "date": {"path": "date", "type": "date"},
        "description": {"path": "description", "type": "string"},
        "code": {"path": "code.coding", "type": "token"},
        "context-type": {"path": "useContext.code", "type": "token"},
        "subject-type": {"path": "subjectType", "type": "token"},
    },
    "QuestionnaireResponse": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "questionnaire": {"path": "questionnaire", "type": "uri"},
        "status": {"path": "status", "type": "token"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "author": {"path": "author.reference", "type": "reference"},
        "authored": {"path": "authored", "type": "date"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
        "source": {"path": "source.reference", "type": "reference"},
        "based-on": {"path": "basedOn.reference", "type": "reference"},
        "part-of": {"path": "partOf.reference", "type": "reference"},
    },
    # === Binary ===
    "Binary": {
        "_id": {"path": "id", "type": "token"},
        "contenttype": {"path": "contentType", "type": "token"},
    },
    # === HealthcareService ===
    "HealthcareService": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "active": {"path": "active", "type": "token"},
        "organization": {"path": "providedBy.reference", "type": "reference"},
        "location": {"path": "location.reference", "type": "reference"},
        "service-category": {"path": "category.coding", "type": "token"},
        "service-type": {"path": "type.coding", "type": "token"},
    },
    # === FamilyMemberHistory ===
    "FamilyMemberHistory": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "relationship": {"path": "relationship.coding", "type": "token"},
        "sex": {"path": "sex.coding", "type": "token"},
        "date": {"path": "date", "type": "date"},
    },
    # === ClinicalImpression ===
    "ClinicalImpression": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "assessor": {"path": "assessor.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
    },
    # === RiskAssessment ===
    "RiskAssessment": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "occurrenceDateTime", "type": "date"},
        "condition": {"path": "condition.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
        "method": {"path": "method.coding", "type": "token"},
    },
    # === AdverseEvent ===
    "AdverseEvent": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "actuality": {"path": "actuality", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "event": {"path": "event.coding", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "seriousness": {"path": "seriousness.coding", "type": "token"},
        "severity": {"path": "severity.coding", "type": "token"},
    },
    # === DetectedIssue ===
    "DetectedIssue": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "code": {"path": "code.coding", "type": "token"},
        "identified": {"path": "identifiedDateTime", "type": "date"},
        "severity": {"path": "severity", "type": "token"},
        "author": {"path": "author.reference", "type": "reference"},
    },
    # === Flag ===
    "Flag": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "code": {"path": "code.coding", "type": "token"},
        "date": {"path": "period.start", "type": "date"},
        "author": {"path": "author.reference", "type": "reference"},
    },
    # === MedicationAdministration ===
    "MedicationAdministration": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "code": {"path": "medicationCodeableConcept.coding", "type": "token"},
        "effective-time": {"path": "effectiveDateTime", "type": "date"},
        "performer": {"path": "performer.actor.reference", "type": "reference"},
        "request": {"path": "request.reference", "type": "reference"},
        "encounter": {"path": "context.reference", "type": "reference"},
    },
    # === MedicationDispense ===
    "MedicationDispense": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "code": {"path": "medicationCodeableConcept.coding", "type": "token"},
        "whenhandedover": {"path": "whenHandedOver", "type": "date"},
        "whenprepared": {"path": "whenPrepared", "type": "date"},
        "performer": {"path": "performer.actor.reference", "type": "reference"},
        "prescription": {"path": "authorizingPrescription.reference", "type": "reference"},
    },
    # === MedicationStatement ===
    "MedicationStatement": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "code": {"path": "medicationCodeableConcept.coding", "type": "token"},
        "effective": {"path": "effectiveDateTime", "type": "date"},
        "category": {"path": "category.coding", "type": "token"},
        "source": {"path": "informationSource.reference", "type": "reference"},
        "context": {"path": "context.reference", "type": "reference"},
    },
    # === NutritionOrder ===
    "NutritionOrder": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "datetime": {"path": "dateTime", "type": "date"},
        "orderer": {"path": "orderer.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
    },
    # === Media ===
    "Media": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "created": {"path": "createdDateTime", "type": "date"},
        "operator": {"path": "operator.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
    },
    # === Specimen ===
    "Specimen": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "collected": {"path": "collection.collectedDateTime", "type": "date"},
        "collector": {"path": "collection.collector.reference", "type": "reference"},
        "bodysite": {"path": "collection.bodySite.coding", "type": "token"},
    },
    # === Communication ===
    "Communication": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "sent": {"path": "sent", "type": "date"},
        "received": {"path": "received", "type": "date"},
        "sender": {"path": "sender.reference", "type": "reference"},
        "recipient": {"path": "recipient.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
    },
    # === AuditEvent ===
    "AuditEvent": {
        "_id": {"path": "id", "type": "token"},
        "type": {"path": "type.code", "type": "token"},
        "subtype": {"path": "subtype.code", "type": "token"},
        "action": {"path": "action", "type": "token"},
        "date": {"path": "recorded", "type": "date"},
        "outcome": {"path": "outcome", "type": "token"},
        "agent": {"path": "agent.who.reference", "type": "reference"},
        "patient": {"path": "agent.who.reference", "type": "reference"},
        "entity": {"path": "entity.what.reference", "type": "reference"},
    },
    # === Consent ===
    "Consent": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "scope": {"path": "scope.coding", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "date": {"path": "dateTime", "type": "date"},
        "organization": {"path": "organization.reference", "type": "reference"},
    },
    # === Provenance ===
    "Provenance": {
        "_id": {"path": "id", "type": "token"},
        "target": {"path": "target.reference", "type": "reference"},
        "recorded": {"path": "recorded", "type": "date"},
        "agent": {"path": "agent.who.reference", "type": "reference"},
        "patient": {"path": "target.reference", "type": "reference"},
        "activity": {"path": "activity.coding", "type": "token"},
    },
    # === ConceptMap ===
    "ConceptMap": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "source": {"path": "sourceUri", "type": "uri"},
        "target": {"path": "targetUri", "type": "uri"},
    },
    # === Composition ===
    "Composition": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "author": {"path": "author.reference", "type": "reference"},
        "title": {"path": "title", "type": "string"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
    },
    # === ImagingStudy ===
    "ImagingStudy": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "modality": {"path": "modality.code", "type": "token"},
        "started": {"path": "started", "type": "date"},
        "referrer": {"path": "referrer.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
        "endpoint": {"path": "endpoint.reference", "type": "reference"},
    },
    # === BodyStructure ===
    "BodyStructure": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "morphology": {"path": "morphology.coding", "type": "token"},
        "location": {"path": "location.coding", "type": "token"},
    },
    # === EpisodeOfCare ===
    "EpisodeOfCare": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "organization": {"path": "managingOrganization.reference", "type": "reference"},
        "care-manager": {"path": "careManager.reference", "type": "reference"},
        "date": {"path": "period.start", "type": "date"},
    },
    # === List ===
    "List": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "code": {"path": "code.coding", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "source": {"path": "source.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
    },
    # === CommunicationRequest ===
    "CommunicationRequest": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "priority": {"path": "priority", "type": "token"},
        "authored": {"path": "authoredOn", "type": "date"},
        "requester": {"path": "requester.reference", "type": "reference"},
        "recipient": {"path": "recipient.reference", "type": "reference"},
        "sender": {"path": "sender.reference", "type": "reference"},
    },
    # === RequestGroup ===
    "RequestGroup": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "subject.reference", "type": "reference"},
        "subject": {"path": "subject.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "intent": {"path": "intent", "type": "token"},
        "priority": {"path": "priority", "type": "token"},
        "code": {"path": "code.coding", "type": "token"},
        "authored": {"path": "authoredOn", "type": "date"},
        "author": {"path": "author.reference", "type": "reference"},
        "encounter": {"path": "encounter.reference", "type": "reference"},
    },
    # === MedicationKnowledge ===
    "MedicationKnowledge": {
        "_id": {"path": "id", "type": "token"},
        "code": {"path": "code.coding", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "manufacturer": {"path": "manufacturer.reference", "type": "reference"},
        "doseform": {"path": "doseForm.coding", "type": "token"},
    },
    # === DeviceMetric ===
    "DeviceMetric": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "source": {"path": "source.reference", "type": "reference"},
        "parent": {"path": "parent.reference", "type": "reference"},
        "category": {"path": "category", "type": "token"},
    },
    # === DeviceDefinition ===
    "DeviceDefinition": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "type": {"path": "type.coding", "type": "token"},
        "manufacturer": {"path": "manufacturerString", "type": "string"},
    },
    # === ResearchStudy ===
    "ResearchStudy": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "phase": {"path": "phase.coding", "type": "token"},
        "focus": {"path": "focus.coding", "type": "token"},
        "sponsor": {"path": "sponsor.reference", "type": "reference"},
        "principalinvestigator": {"path": "principalInvestigator.reference", "type": "reference"},
        "site": {"path": "site.reference", "type": "reference"},
        "date": {"path": "period.start", "type": "date"},
    },
    # === ResearchSubject ===
    "ResearchSubject": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "individual.reference", "type": "reference"},
        "individual": {"path": "individual.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "study": {"path": "study.reference", "type": "reference"},
        "date": {"path": "period.start", "type": "date"},
    },
    # === Endpoint ===
    "Endpoint": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "connection-type": {"path": "connectionType.code", "type": "token"},
        "organization": {"path": "managingOrganization.reference", "type": "reference"},
        "payload-type": {"path": "payloadType.coding", "type": "token"},
    },
    # === OrganizationAffiliation ===
    "OrganizationAffiliation": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "active": {"path": "active", "type": "token"},
        "primary-organization": {"path": "organization.reference", "type": "reference"},
        "participating-organization": {"path": "participatingOrganization.reference", "type": "reference"},
        "role": {"path": "code.coding", "type": "token"},
        "specialty": {"path": "specialty.coding", "type": "token"},
        "location": {"path": "location.reference", "type": "reference"},
        "service": {"path": "healthcareService.reference", "type": "reference"},
    },
    # === SupplyRequest ===
    "SupplyRequest": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "category": {"path": "category.coding", "type": "token"},
        "supplier": {"path": "supplier.reference", "type": "reference"},
        "requester": {"path": "requester.reference", "type": "reference"},
        "date": {"path": "authoredOn", "type": "date"},
    },
    # === SupplyDelivery ===
    "SupplyDelivery": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "supplier": {"path": "supplier.reference", "type": "reference"},
        "receiver": {"path": "receiver.reference", "type": "reference"},
    },
    # === StructureDefinition ===
    "StructureDefinition": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "version": {"path": "version", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "publisher": {"path": "publisher", "type": "string"},
        "description": {"path": "description", "type": "string"},
        "type": {"path": "type", "type": "token"},
        "base": {"path": "baseDefinition", "type": "uri"},
        "kind": {"path": "kind", "type": "token"},
        "derivation": {"path": "derivation", "type": "token"},
        "abstract": {"path": "abstract", "type": "token"},
        "context-type": {"path": "context.type", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "date": {"path": "date", "type": "date"},
    },
    # === SearchParameter ===
    "SearchParameter": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "code": {"path": "code", "type": "token"},
        "base": {"path": "base", "type": "token"},
        "type": {"path": "type", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "publisher": {"path": "publisher", "type": "string"},
        "description": {"path": "description", "type": "string"},
        "date": {"path": "date", "type": "date"},
        "target": {"path": "target", "type": "token"},
        "derived-from": {"path": "derivedFrom", "type": "reference"},
    },
    # === Bundle ===
    "Bundle": {
        "_id": {"path": "id", "type": "token"},
        "type": {"path": "type", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "timestamp": {"path": "timestamp", "type": "date"},
        "composition": {"path": "entry.resource", "type": "reference"},
        "message": {"path": "entry.resource", "type": "reference"},
    },
    # === OperationDefinition ===
    "OperationDefinition": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "code": {"path": "code", "type": "token"},
        "kind": {"path": "kind", "type": "token"},
        "base": {"path": "base", "type": "reference"},
        "system": {"path": "system", "type": "token"},
        "type": {"path": "type", "type": "token"},
        "instance": {"path": "instance", "type": "token"},
        "input-profile": {"path": "inputProfile", "type": "reference"},
        "output-profile": {"path": "outputProfile", "type": "reference"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
    },
    # === Parameters ===
    "Parameters": {
        "_id": {"path": "id", "type": "token"},
    },
    # === Subscription ===
    "Subscription": {
        "_id": {"path": "id", "type": "token"},
        "status": {"path": "status", "type": "token"},
        "type": {"path": "channel.type", "type": "token"},
        "url": {"path": "channel.endpoint", "type": "uri"},
        "payload": {"path": "channel.payload", "type": "token"},
        "criteria": {"path": "criteria", "type": "string"},
        "contact": {"path": "contact", "type": "token"},
    },
    # === MessageHeader ===
    "MessageHeader": {
        "_id": {"path": "id", "type": "token"},
        "event": {"path": "eventCoding", "type": "token"},
        "source": {"path": "source.name", "type": "string"},
        "source-uri": {"path": "source.endpoint", "type": "uri"},
        "destination": {"path": "destination.name", "type": "string"},
        "destination-uri": {"path": "destination.endpoint", "type": "uri"},
        "sender": {"path": "sender.reference", "type": "reference"},
        "author": {"path": "author.reference", "type": "reference"},
        "enterer": {"path": "enterer.reference", "type": "reference"},
        "responsible": {"path": "responsible.reference", "type": "reference"},
        "focus": {"path": "focus.reference", "type": "reference"},
        "target": {"path": "destination.target.reference", "type": "reference"},
        "receiver": {"path": "destination.receiver.reference", "type": "reference"},
        "response-id": {"path": "response.identifier", "type": "token"},
        "code": {"path": "response.code", "type": "token"},
    },
    # === Phase 4: Foundation ===
    "OperationOutcome": {
        "_id": {"path": "id", "type": "token"},
    },
    "CapabilityStatement": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
        "fhirversion": {"path": "fhirVersion", "type": "token"},
        "format": {"path": "format", "type": "token"},
        "mode": {"path": "rest.mode", "type": "token"},
        "resource": {"path": "rest.resource.type", "type": "token"},
        "security-service": {"path": "rest.security.service.coding", "type": "token"},
    },
    "TerminologyCapabilities": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
    },
    # === Evidence-Based Medicine ===
    "Evidence": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
        "description": {"path": "description", "type": "string"},
    },
    "EvidenceVariable": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
        "description": {"path": "description", "type": "string"},
        "type": {"path": "type", "type": "token"},
    },
    "EffectEvidenceSynthesis": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
        "description": {"path": "description", "type": "string"},
    },
    "RiskEvidenceSynthesis": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
        "description": {"path": "description", "type": "string"},
    },
    "ResearchDefinition": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
        "description": {"path": "description", "type": "string"},
    },
    "ResearchElementDefinition": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "identifier": {"path": "identifier", "type": "token"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
        "description": {"path": "description", "type": "string"},
        "type": {"path": "type", "type": "token"},
    },
    # === Laboratory & Genomics ===
    "MolecularSequence": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "type": {"path": "type", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "chromosome": {"path": "referenceSeq.chromosome.coding", "type": "token"},
    },
    "BiologicallyDerivedProduct": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "product-category": {"path": "productCategory", "type": "token"},
        "product-code": {"path": "productCode.coding", "type": "token"},
        "status": {"path": "status", "type": "token"},
    },
    # === Catalog ===
    "CatalogEntry": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "type": {"path": "type", "type": "token"},
        "orderable": {"path": "orderable", "type": "token"},
        "status": {"path": "status", "type": "token"},
    },
    # === Immunization Assessment ===
    "ImmunizationEvaluation": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "patient": {"path": "patient.reference", "type": "reference"},
        "status": {"path": "status", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "target-disease": {"path": "targetDisease.coding", "type": "token"},
        "immunization-event": {"path": "immunizationEvent.reference", "type": "reference"},
        "dose-status": {"path": "doseStatus.coding", "type": "token"},
    },
    # === Substance Specialized Types ===
    "SubstanceNucleicAcid": {
        "_id": {"path": "id", "type": "token"},
    },
    "SubstancePolymer": {
        "_id": {"path": "id", "type": "token"},
    },
    "SubstanceProtein": {
        "_id": {"path": "id", "type": "token"},
    },
    "SubstanceReferenceInformation": {
        "_id": {"path": "id", "type": "token"},
    },
    "SubstanceSourceMaterial": {
        "_id": {"path": "id", "type": "token"},
    },
    "SubstanceSpecification": {
        "_id": {"path": "id", "type": "token"},
        "identifier": {"path": "identifier", "type": "token"},
        "status": {"path": "status.coding", "type": "token"},
    },
    # === Workflow Examples ===
    "ExampleScenario": {
        "_id": {"path": "id", "type": "token"},
        "url": {"path": "url", "type": "uri"},
        "name": {"path": "name", "type": "string"},
        "title": {"path": "title", "type": "string"},
        "status": {"path": "status", "type": "token"},
        "version": {"path": "version", "type": "token"},
        "date": {"path": "date", "type": "date"},
        "publisher": {"path": "publisher", "type": "string"},
    },
}


def get_nested_value(resource: dict[str, Any], path: str) -> Any:
    """Get a value from a nested path in a resource.

    Args:
        resource: The FHIR resource
        path: Dot-separated path (e.g., "subject.reference")

    Returns:
        The value at the path, or None if not found
    """
    parts = path.split(".")
    current: Any = resource

    for part in parts:
        if current is None:
            return None
        if isinstance(current, list):
            # For lists, collect all values at this path
            values = []
            for item in current:
                if isinstance(item, dict) and part in item:
                    values.append(item[part])
            return values if values else None
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None

    return current


def match_token(resource_value: Any, search_value: str) -> bool:
    """Match a token search parameter.

    Token format: [system|]code or |code (no system) or system| (any code)

    Args:
        resource_value: Value from the resource
        search_value: Search parameter value

    Returns:
        True if matches
    """
    if resource_value is None:
        return False

    # Parse search value
    if "|" in search_value:
        system, code = search_value.split("|", 1)
    else:
        system, code = None, search_value

    # Handle different value types
    if isinstance(resource_value, str):
        # Simple string match (e.g., status field)
        return code.lower() == resource_value.lower() if code else True

    if isinstance(resource_value, bool):
        return code.lower() in ("true", "1") if resource_value else code.lower() in ("false", "0")

    if isinstance(resource_value, list):
        # List of codings or identifiers
        for item in resource_value:
            if match_token(item, search_value):
                return True
        return False

    if isinstance(resource_value, dict):
        # Coding or Identifier
        if "coding" in resource_value:
            # CodeableConcept - check each coding
            return match_token(resource_value["coding"], search_value)

        item_system = resource_value.get("system", "")
        item_code = resource_value.get("code") or resource_value.get("value", "")

        if system and code:
            return system == item_system and code.lower() == str(item_code).lower()
        if system and not code:
            return system == item_system
        if code:
            return code.lower() == str(item_code).lower()

    return False


def match_string(resource_value: Any, search_value: str) -> bool:
    """Match a string search parameter (case-insensitive, starts-with).

    Args:
        resource_value: Value from the resource
        search_value: Search parameter value

    Returns:
        True if matches
    """
    if resource_value is None:
        return False

    search_lower = search_value.lower()

    if isinstance(resource_value, str):
        return resource_value.lower().startswith(search_lower)

    if isinstance(resource_value, list):
        for item in resource_value:
            if match_string(item, search_value):
                return True
        return False

    if isinstance(resource_value, dict):
        # For HumanName, search across all text fields
        for key in ["text", "family", "given", "prefix", "suffix"]:
            if key in resource_value:
                if match_string(resource_value[key], search_value):
                    return True
        # For Address
        for key in ["text", "line", "city", "state", "postalCode", "country"]:
            if key in resource_value:
                if match_string(resource_value[key], search_value):
                    return True
        return False

    return False


def match_reference(resource_value: Any, search_value: str) -> bool:
    """Match a reference search parameter.

    Reference format: [Type/]id or full URL

    Args:
        resource_value: Value from the resource (e.g., "Patient/123")
        search_value: Search parameter value

    Returns:
        True if matches
    """
    if resource_value is None:
        return False

    if isinstance(resource_value, str):
        # Normalize both to just the reference part
        if "/" in search_value:
            return resource_value == search_value or resource_value.endswith(f"/{search_value}")
        # Search by ID only
        return resource_value.endswith(f"/{search_value}")

    if isinstance(resource_value, list):
        for item in resource_value:
            if match_reference(item, search_value):
                return True
        return False

    return False


def match_date(resource_value: Any, search_value: str) -> bool:
    """Match a date search parameter.

    Date format: [prefix]YYYY[-MM[-DD[Thh:mm:ss[Z]]]]
    Prefixes: eq, ne, gt, lt, ge, le, sa, eb, ap

    Args:
        resource_value: Value from the resource (ISO date string)
        search_value: Search parameter value

    Returns:
        True if matches
    """
    if resource_value is None:
        return False

    # Parse prefix
    prefixes = ["eq", "ne", "gt", "lt", "ge", "le", "sa", "eb", "ap"]
    prefix = "eq"
    date_str = search_value

    for p in prefixes:
        if search_value.startswith(p):
            prefix = p
            date_str = search_value[len(p) :]
            break

    # Parse resource date
    try:
        if "T" in str(resource_value):
            resource_dt = datetime.fromisoformat(str(resource_value).replace("Z", "+00:00"))
            resource_date = resource_dt.date()
        else:
            resource_date = date.fromisoformat(str(resource_value)[:10])
    except (ValueError, TypeError):
        return False

    # Parse search date
    try:
        search_date = date.fromisoformat(date_str[:10])
    except (ValueError, TypeError):
        return False

    # Apply prefix comparison
    if prefix == "eq":
        return resource_date == search_date
    if prefix == "ne":
        return resource_date != search_date
    if prefix == "gt" or prefix == "sa":
        return resource_date > search_date
    if prefix == "lt" or prefix == "eb":
        return resource_date < search_date
    if prefix == "ge":
        return resource_date >= search_date
    if prefix == "le":
        return resource_date <= search_date
    if prefix == "ap":
        # Approximate - within a reasonable range (let's say 7 days)

        return abs((resource_date - search_date).days) <= 7

    return False


def match_uri(resource_value: Any, search_value: str) -> bool:
    """Match a URI search parameter (exact match).

    Args:
        resource_value: Value from the resource
        search_value: Search parameter value

    Returns:
        True if matches
    """
    if resource_value is None:
        return False

    if isinstance(resource_value, str):
        return resource_value == search_value

    return False


def matches_search_param(
    resource: dict[str, Any],
    param_name: str,
    param_value: str,
    param_def: dict[str, Any],
) -> bool:
    """Check if a resource matches a single search parameter.

    Args:
        resource: The FHIR resource
        param_name: Name of the search parameter
        param_value: Value to search for
        param_def: Parameter definition from SEARCH_PARAMS

    Returns:
        True if the resource matches
    """
    path = param_def["path"]
    param_type = param_def["type"]

    # Handle special search flags
    if param_def.get("search_name"):
        # Search across all name parts
        names = resource.get("name", [])
        if isinstance(names, dict):
            names = [names]
        for name in names:
            if match_string(name, param_value):
                return True
        return False

    if param_def.get("search_address"):
        # Search across all address parts
        addresses = resource.get("address", [])
        if isinstance(addresses, dict):
            addresses = [addresses]
        for addr in addresses:
            if match_string(addr, param_value):
                return True
        return False

    # Get value from resource
    value = get_nested_value(resource, path)

    # Match based on type
    if param_type == "token":
        return match_token(value, param_value)
    if param_type == "string":
        return match_string(value, param_value)
    if param_type == "reference":
        return match_reference(value, param_value)
    if param_type == "date":
        return match_date(value, param_value)
    if param_type == "uri":
        return match_uri(value, param_value)
    if param_type == "quantity":
        # Simple quantity comparison
        try:
            search_val = float(param_value)
            return value is not None and float(value) == search_val
        except (ValueError, TypeError):
            return False

    return False


def filter_resources(
    resources: list[dict[str, Any]],
    resource_type: str,
    params: dict[str, str | list[str]],
) -> list[dict[str, Any]]:
    """Filter resources based on search parameters.

    Args:
        resources: List of FHIR resources
        resource_type: The resource type
        params: Search parameters

    Returns:
        Filtered list of resources
    """
    if not params:
        return resources

    # Get search param definitions for this type
    type_params = SEARCH_PARAMS.get(resource_type, {})

    # Add common params
    common_params = {
        "_id": {"path": "id", "type": "token"},
        "_lastUpdated": {"path": "meta.lastUpdated", "type": "date"},
    }
    type_params = {**common_params, **type_params}

    filtered = resources

    for param_name, param_values in params.items():
        # Skip special parameters handled elsewhere
        if param_name.startswith("_") and param_name not in ("_id", "_lastUpdated"):
            continue

        # Get param definition
        param_def = type_params.get(param_name)
        if param_def is None:
            # Unknown parameter - skip (could also raise error)
            continue

        # Ensure values is a list
        if isinstance(param_values, str):
            param_values = [param_values]

        # Filter: resource must match at least one value (OR within param)
        filtered = [r for r in filtered if any(matches_search_param(r, param_name, v, param_def) for v in param_values)]

    return filtered


def parse_search_params(query_string: str) -> dict[str, list[str]]:
    """Parse a query string into search parameters.

    Args:
        query_string: URL query string

    Returns:
        Dict of parameter name to list of values
    """
    return parse_qs(query_string)


# =============================================================================
# Chained Search Parameters
# =============================================================================

# Pattern to match chained parameters: param:Type.targetParam
CHAINED_PARAM_PATTERN = re.compile(r"^([a-zA-Z\-]+):([A-Z][a-zA-Z]+)\.(.+)$")


def parse_chained_param(param_name: str) -> tuple[str, str, str] | None:
    """Parse a chained search parameter.

    Chained parameters have the format: refParam:TargetType.targetSearchParam
    Example: subject:Patient.name -> ("subject", "Patient", "name")

    Args:
        param_name: The parameter name to parse

    Returns:
        Tuple of (reference_param, target_type, target_search_param) or None
    """
    match = CHAINED_PARAM_PATTERN.match(param_name)
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None


def resolve_chained_search(
    resources: list[dict[str, Any]],
    resource_type: str,
    ref_param: str,
    target_type: str,
    target_param: str,
    target_value: str,
    store: "FHIRStore",
) -> list[dict[str, Any]]:
    """Resolve a chained search parameter.

    Finds resources where the referenced resource matches the search criteria.

    Example: Condition?subject:Patient.name=John
    1. Find all Patients with name containing "John"
    2. Return Conditions that reference those Patients

    Args:
        resources: List of source resources to filter
        resource_type: The source resource type (e.g., "Condition")
        ref_param: The reference parameter name (e.g., "subject")
        target_type: The target resource type (e.g., "Patient")
        target_param: The search parameter on target (e.g., "name")
        target_value: The search value (e.g., "John")
        store: The FHIR data store

    Returns:
        Filtered list of resources matching the chained criteria
    """
    # Get the parameter definition for the reference param
    type_params = SEARCH_PARAMS.get(resource_type, {})
    ref_param_def = type_params.get(ref_param)

    if ref_param_def is None or ref_param_def.get("type") != "reference":
        # Not a valid reference parameter
        return resources

    ref_path = ref_param_def["path"]

    # First, search for matching target resources
    target_resources, _ = store.search(
        resource_type=target_type,
        params={target_param: target_value},
    )

    if not target_resources:
        # No matching targets, so no source resources match
        return []

    # Build set of matching target references
    matching_refs: set[str] = set()
    for target in target_resources:
        target_id = target.get("id")
        if target_id:
            matching_refs.add(f"{target_type}/{target_id}")

    # Filter source resources by reference to matching targets
    result = []
    for resource in resources:
        ref_value = get_nested_value(resource, ref_path)
        if ref_value is None:
            continue

        # Handle single or multiple references
        if isinstance(ref_value, str):
            if ref_value in matching_refs:
                result.append(resource)
        elif isinstance(ref_value, list):
            for rv in ref_value:
                if rv in matching_refs:
                    result.append(resource)
                    break

    return result


def filter_resources_with_chaining(
    resources: list[dict[str, Any]],
    resource_type: str,
    params: dict[str, str | list[str]],
    store: "FHIRStore",
) -> list[dict[str, Any]]:
    """Filter resources with support for chained parameters.

    Handles both regular search parameters and chained parameters
    (e.g., subject:Patient.name=John).

    Args:
        resources: List of FHIR resources to filter
        resource_type: The resource type
        params: Search parameters (may include chained params)
        store: The FHIR data store for resolving chains

    Returns:
        Filtered list of resources
    """
    if not params:
        return resources

    # Separate regular params from chained params
    regular_params: dict[str, str | list[str]] = {}
    chained_params: list[tuple[str, str, str, str | list[str]]] = []

    for param_name, param_values in params.items():
        # Skip special parameters
        if param_name.startswith("_") and param_name not in ("_id", "_lastUpdated"):
            continue

        # Check if this is a chained parameter
        chained = parse_chained_param(param_name)
        if chained:
            ref_param, target_type, target_param = chained
            chained_params.append((ref_param, target_type, target_param, param_values))
        else:
            regular_params[param_name] = param_values

    # First apply regular filters
    filtered = filter_resources(resources, resource_type, regular_params)

    # Then apply chained filters
    for ref_param, target_type, target_param, param_values in chained_params:
        if isinstance(param_values, str):
            param_values = [param_values]

        # For multiple values, OR them together
        chained_matches: list[dict[str, Any]] = []
        for value in param_values:
            matches = resolve_chained_search(
                filtered,
                resource_type,
                ref_param,
                target_type,
                target_param,
                value,
                store,
            )
            for match in matches:
                if match not in chained_matches:
                    chained_matches.append(match)

        filtered = chained_matches

    return filtered


# =============================================================================
# Reverse Chained Search Parameters (_has)
# =============================================================================

# Pattern to match _has parameters: _has:Type:refParam:searchParam
HAS_PARAM_PATTERN = re.compile(r"^_has:([A-Z][a-zA-Z]+):([a-zA-Z\-]+):(.+)$")


def parse_has_param(param_name: str) -> tuple[str, str, str] | None:
    """Parse a reverse chained (_has) search parameter.

    _has parameters have the format: _has:SourceType:refParam:searchParam
    Example: _has:Condition:patient:code -> ("Condition", "patient", "code")

    This means: find resources that are referenced by a Condition
    via the 'patient' reference, where that Condition has matching code.

    Args:
        param_name: The parameter name to parse

    Returns:
        Tuple of (source_type, ref_param, search_param) or None
    """
    match = HAS_PARAM_PATTERN.match(param_name)
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None


def resolve_has_search(
    resources: list[dict[str, Any]],
    resource_type: str,
    source_type: str,
    ref_param: str,
    search_param: str,
    search_value: str,
    store: "FHIRStore",
) -> list[dict[str, Any]]:
    """Resolve a reverse chained (_has) search parameter.

    Finds resources that are referenced by other resources matching criteria.

    Example: Patient?_has:Condition:patient:code=diabetes
    1. Find all Conditions with code=diabetes
    2. Extract patient references from those Conditions
    3. Return Patients that are referenced

    Args:
        resources: List of target resources to filter
        resource_type: The target resource type (e.g., "Patient")
        source_type: The referencing resource type (e.g., "Condition")
        ref_param: The reference parameter in source (e.g., "patient")
        search_param: The search parameter on source (e.g., "code")
        search_value: The search value (e.g., "diabetes")
        store: The FHIR data store

    Returns:
        Filtered list of resources that are referenced by matching sources
    """
    # Get the reference path from source type's search params
    source_params = SEARCH_PARAMS.get(source_type, {})
    ref_param_def = source_params.get(ref_param)

    if ref_param_def is None or ref_param_def.get("type") != "reference":
        return resources

    ref_path = ref_param_def["path"]

    # Search for matching source resources
    source_resources, _ = store.search(
        resource_type=source_type,
        params={search_param: search_value},
    )

    if not source_resources:
        return []

    # Extract references from matching source resources
    referenced_ids: set[str] = set()
    for source in source_resources:
        ref_value = get_nested_value(source, ref_path)
        if ref_value is None:
            continue

        if isinstance(ref_value, str):
            # Extract ID from reference (e.g., "Patient/123" -> "123")
            if ref_value.startswith(f"{resource_type}/"):
                referenced_ids.add(ref_value.split("/", 1)[1])
        elif isinstance(ref_value, list):
            for rv in ref_value:
                if isinstance(rv, str) and rv.startswith(f"{resource_type}/"):
                    referenced_ids.add(rv.split("/", 1)[1])

    # Filter target resources by ID
    return [r for r in resources if r.get("id") in referenced_ids]


def filter_resources_with_has(
    resources: list[dict[str, Any]],
    resource_type: str,
    params: dict[str, str | list[str]],
    store: "FHIRStore",
) -> list[dict[str, Any]]:
    """Filter resources with support for _has parameters.

    Handles reverse chained parameters (e.g., _has:Condition:patient:code=diabetes).

    Args:
        resources: List of FHIR resources to filter
        resource_type: The resource type
        params: Search parameters (may include _has params)
        store: The FHIR data store for resolving chains

    Returns:
        Filtered list of resources
    """
    if not params:
        return resources

    filtered = resources

    for param_name, param_values in params.items():
        # Check if this is a _has parameter
        has_parsed = parse_has_param(param_name)
        if not has_parsed:
            continue

        source_type, ref_param, search_param = has_parsed

        if isinstance(param_values, str):
            param_values = [param_values]

        # For multiple values, OR them together
        has_matches: list[dict[str, Any]] = []
        for value in param_values:
            matches = resolve_has_search(
                filtered,
                resource_type,
                source_type,
                ref_param,
                search_param,
                value,
                store,
            )
            for match in matches:
                if match not in has_matches:
                    has_matches.append(match)

        filtered = has_matches

    return filtered


# =============================================================================
# Combined Advanced Search
# =============================================================================


def filter_resources_advanced(
    resources: list[dict[str, Any]],
    resource_type: str,
    params: dict[str, str | list[str]],
    store: "FHIRStore",
) -> list[dict[str, Any]]:
    """Filter resources with support for all advanced search features.

    Handles:
    - Regular search parameters
    - Chained parameters (e.g., subject:Patient.name=John)
    - Reverse chained _has parameters (e.g., _has:Condition:patient:code=diabetes)

    Args:
        resources: List of FHIR resources to filter
        resource_type: The resource type
        params: Search parameters
        store: The FHIR data store for resolving chains

    Returns:
        Filtered list of resources
    """
    # Apply chained search (which also applies regular filters)
    filtered = filter_resources_with_chaining(resources, resource_type, params, store)

    # Apply _has search
    filtered = filter_resources_with_has(filtered, resource_type, params, store)

    return filtered


# =============================================================================
# Sorting
# =============================================================================


def parse_sort_param(sort_param: str) -> list[tuple[str, bool]]:
    """Parse a _sort parameter value.

    Supports comma-separated fields and - prefix for descending order.
    Example: "_sort=date,-name" -> [("date", False), ("name", True)]

    Args:
        sort_param: The _sort parameter value

    Returns:
        List of (field_name, descending) tuples
    """
    sort_fields = []
    for field in sort_param.split(","):
        field = field.strip()
        if not field:
            continue
        descending = field.startswith("-")
        field_name = field.lstrip("-")
        sort_fields.append((field_name, descending))
    return sort_fields


def get_sort_key(
    resource: dict[str, Any],
    field: str,
    resource_type: str,
) -> Any:
    """Get the sort key value for a resource.

    Uses search parameter definitions to resolve paths.

    Args:
        resource: The FHIR resource
        field: The sort field name
        resource_type: The resource type

    Returns:
        The sortable value (or None for missing values)
    """
    # Get search parameter definitions
    type_params = SEARCH_PARAMS.get(resource_type, {})

    # Add common params
    common_params = {
        "_id": {"path": "id", "type": "token"},
        "_lastUpdated": {"path": "meta.lastUpdated", "type": "date"},
    }
    all_params = {**common_params, **type_params}

    # Check if field is a search parameter
    param_def = all_params.get(field)
    if param_def:
        path = param_def["path"]
        param_type = param_def["type"]
        value = get_nested_value(resource, path)
    else:
        # Try direct field access
        value = get_nested_value(resource, field)
        param_type = None

    # Handle None values - sort to end
    if value is None:
        return (1, "")  # Tuple ensures None sorts last

    # Convert to sortable format based on type
    if param_type == "date" or (isinstance(value, str) and _looks_like_date(value)):
        return (0, _normalize_date(value))

    if isinstance(value, (int, float)):
        return (0, value)

    if isinstance(value, list):
        # For lists, use first value for sorting
        if value:
            first_val = value[0]
            if isinstance(first_val, dict):
                # Handle complex types like Coding
                if "code" in first_val:
                    return (0, str(first_val.get("code", "")))
                if "value" in first_val:
                    return (0, str(first_val.get("value", "")))
                if "family" in first_val:
                    return (0, str(first_val.get("family", "")))
            return (0, str(first_val))
        return (1, "")

    if isinstance(value, dict):
        # Handle complex types
        if "value" in value:
            return (0, value["value"])
        if "code" in value:
            return (0, str(value["code"]))
        if "family" in value:
            return (0, str(value["family"]))

    return (0, str(value).lower())


def _looks_like_date(value: str) -> bool:
    """Check if a string looks like a date/datetime."""
    if not isinstance(value, str):
        return False
    # ISO date patterns
    return bool(re.match(r"^\d{4}(-\d{2})?(-\d{2})?(T.*)?$", value))


def _normalize_date(value: Any) -> str:
    """Normalize a date value for sorting."""
    if value is None:
        return ""
    if isinstance(value, str):
        # Already ISO format, just ensure consistent format
        return value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def sort_resources(
    resources: list[dict[str, Any]],
    sort_param: str,
    resource_type: str,
) -> list[dict[str, Any]]:
    """Sort resources according to _sort parameter.

    Supports:
    - Multiple fields: "_sort=date,-name"
    - Descending order with - prefix: "_sort=-date"
    - Search parameter paths: "_sort=birthdate" resolves to "birthDate"
    - Direct paths: "_sort=meta.lastUpdated"

    Args:
        resources: List of FHIR resources to sort
        sort_param: The _sort parameter value
        resource_type: The resource type

    Returns:
        Sorted list of resources
    """
    if not resources or not sort_param:
        return resources

    sort_fields = parse_sort_param(sort_param)
    if not sort_fields:
        return resources

    # Create a multi-key sort function
    def multi_sort_key(resource: dict[str, Any]) -> tuple[Any, ...]:
        keys = []
        for field, descending in sort_fields:
            key = get_sort_key(resource, field, resource_type)
            if descending:
                # For descending, we need to invert the comparison
                # We use a wrapper class for this
                key = _DescendingKey(key)
            keys.append(key)
        return tuple(keys)

    try:
        return sorted(resources, key=multi_sort_key)
    except TypeError:
        # Fall back to original order if sorting fails
        return resources


class _DescendingKey:
    """Wrapper to invert comparison for descending sort."""

    __slots__ = ("key",)

    def __init__(self, key: Any):
        self.key = key

    def __lt__(self, other: "_DescendingKey") -> bool:
        try:
            return self.key > other.key
        except TypeError:
            return False

    def __gt__(self, other: "_DescendingKey") -> bool:
        try:
            return self.key < other.key
        except TypeError:
            return False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _DescendingKey):
            return self.key == other.key
        return False

    def __le__(self, other: "_DescendingKey") -> bool:
        return self == other or self < other

    def __ge__(self, other: "_DescendingKey") -> bool:
        return self == other or self > other
