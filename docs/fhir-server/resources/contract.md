# Contract

## Overview

A Contract represents a legally enforceable agreement between parties. In healthcare, contracts are used for various purposes including insurance policies, consent agreements, service level agreements, and business associate agreements.

This resource supports the representation of contract terms, signatories, and legal provisions. It can reference other resources that are the subject of the contract.

**Common use cases:**
- Insurance policies
- Consent agreements
- Service level agreements
- Business associate agreements
- Patient agreements

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/contract.html](https://hl7.org/fhir/R4/contract.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `identifier` | Identifier[] | Business identifiers |
| `url` | uri | Canonical URL |
| `status` | code | amended, appended, cancelled, disputed, entered-in-error, executable, executed, negotiable, offered, policy, rejected, renewed, revoked, resolved, terminated |
| `issued` | dateTime | When issued |
| `applies` | Period | Effective period |
| `subject` | Reference(Any)[] | Contract subject |
| `authority` | Reference(Organization)[] | Authority under which contract exists |
| `domain` | Reference(Location)[] | Domain of applicability |
| `type` | CodeableConcept | Contract type |
| `signer` | BackboneElement[] | Contract signatories |
| `term` | BackboneElement[] | Contract terms |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=contract-001` |
| `identifier` | token | Business identifier | `identifier=CTR-12345` |
| `status` | token | Contract status | `status=executed` |
| `issued` | date | Issue date | `issued=2024-01-15` |
| `subject` | reference | Contract subject | `subject=Patient/123` |
| `patient` | reference | Patient subject | `patient=Patient/123` |
| `authority` | reference | Authority | `authority=Organization/org-001` |
| `domain` | reference | Domain | `domain=Location/loc-001` |
| `signer` | reference | Signer reference | `signer=Patient/123` |
| `url` | uri | Canonical URL | `url=http://example.org/contracts/privacy` |

## Examples

### Create a Contract

```bash
curl -X POST http://localhost:8080/baseR4/Contract \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Contract",
    "identifier": [{
      "system": "http://hospital.example.org/contracts",
      "value": "CTR-2024-001"
    }],
    "status": "executed",
    "issued": "2024-01-15T10:00:00Z",
    "applies": {
      "start": "2024-01-15",
      "end": "2025-01-14"
    },
    "subject": [{"reference": "Patient/123"}],
    "type": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/contract-type",
        "code": "consent",
        "display": "Consent"
      }]
    },
    "signer": [{
      "type": {
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/contract-signer-type",
          "code": "CONSENTER"
        }]
      },
      "party": {"reference": "Patient/123"},
      "signature": [{
        "type": [{
          "system": "urn:iso-astm:E1762-95:2013",
          "code": "1.2.840.10065.1.12.1.1"
        }],
        "when": "2024-01-15T10:00:00Z",
        "who": {"reference": "Patient/123"}
      }]
    }]
  }'
```

### Search Contracts

```bash
# By patient
curl "http://localhost:8080/baseR4/Contract?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/Contract?status=executed"

# By issue date
curl "http://localhost:8080/baseR4/Contract?issued=ge2024-01-01"
```

## Generator Usage

```python
from fhirkit.server.generator import ContractGenerator

generator = ContractGenerator(seed=42)

# Generate a random contract
contract = generator.generate()

# Generate for specific patient
patient_contract = generator.generate(
    subject_reference="Patient/123",
    status="executed"
)

# Generate batch
contracts = generator.generate_batch(count=10)
```

## Status Codes

| Code | Description |
|------|-------------|
| amended | Contract has been amended |
| appended | Additional content appended |
| cancelled | Contract cancelled |
| disputed | Contract is disputed |
| entered-in-error | Entered in error |
| executable | Contract can be executed |
| executed | Contract has been executed |
| negotiable | Contract is negotiable |
| offered | Contract has been offered |
| policy | Contract is a policy |
| rejected | Contract was rejected |
| renewed | Contract was renewed |
| revoked | Contract was revoked |
| resolved | Dispute resolved |
| terminated | Contract terminated |

## Related Resources

- [Patient](./patient.md) - Contract subject
- [Consent](./consent.md) - Related consent
- [Organization](./organization.md) - Contract authority
