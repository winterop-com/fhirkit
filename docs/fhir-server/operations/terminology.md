# Terminology Operations

Full terminology support through standard FHIR operations on CodeSystem and ValueSet resources.

## Overview

| Operation | Endpoint | Description |
|-----------|----------|-------------|
| `$expand` | `/ValueSet/$expand` | Expand a ValueSet to list all codes |
| `$validate-code` | `/ValueSet/$validate-code` | Validate a code against a ValueSet |
| `$lookup` | `/CodeSystem/$lookup` | Look up code information |
| `$subsumes` | `/CodeSystem/$subsumes` | Test subsumption relationship |
| `memberOf` | `/terminology/memberOf` | Check code membership |

### Key Concepts

| Term | Description |
|------|-------------|
| **CodeSystem** | A collection of codes (e.g., SNOMED CT, LOINC, ICD-10) |
| **ValueSet** | A selection of codes from one or more code systems |
| **Coding** | A single code with its system and display text |
| **CodeableConcept** | Multiple codings representing the same concept |

---

## Quick Start

### Start the FHIR Server

```bash
# Start the FHIR server
uv run fhir serve

# With options
uv run fhir serve --port 8000 --patients 100

# Or with uvicorn directly
uvicorn fhirkit.server.api.app:create_app --factory --reload --port 8000
```

### Create a CodeSystem

```bash
curl -X PUT http://localhost:8000/CodeSystem/diabetes-types \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "CodeSystem",
    "id": "diabetes-types",
    "url": "http://example.org/fhir/CodeSystem/diabetes-types",
    "name": "DiabetesTypes",
    "status": "active",
    "concept": [
      {
        "code": "diabetes",
        "display": "Diabetes mellitus",
        "concept": [
          {"code": "type1", "display": "Type 1 diabetes"},
          {"code": "type2", "display": "Type 2 diabetes"},
          {"code": "gestational", "display": "Gestational diabetes"}
        ]
      }
    ]
  }'
```

### Create a ValueSet

```bash
curl -X PUT http://localhost:8000/ValueSet/diabetes-codes \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "ValueSet",
    "id": "diabetes-codes",
    "url": "http://example.org/fhir/ValueSet/diabetes-codes",
    "name": "DiabetesCodes",
    "status": "active",
    "compose": {
      "include": [
        {
          "system": "http://example.org/fhir/CodeSystem/diabetes-types",
          "concept": [
            {"code": "type1", "display": "Type 1 diabetes"},
            {"code": "type2", "display": "Type 2 diabetes"}
          ]
        }
      ]
    }
  }'
```

### Validate a Code

```bash
curl "http://localhost:8000/ValueSet/\$validate-code?url=http://example.org/fhir/ValueSet/diabetes-codes&code=type1&system=http://example.org/fhir/CodeSystem/diabetes-types"
```

Response:
```json
{
  "resourceType": "Parameters",
  "parameter": [
    {"name": "result", "valueBoolean": true},
    {"name": "display", "valueString": "Type 1 diabetes"}
  ]
}
```

---

## REST API Reference

### ValueSet $expand

Expand a ValueSet to list all codes.

```http
GET /ValueSet/$expand?url={valueSetUrl}
GET /ValueSet/$expand?url={valueSetUrl}&filter={searchText}
GET /ValueSet/{id}/$expand
POST /ValueSet/$expand
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | uri | ValueSet canonical URL |
| `filter` | string | Filter by code or display text |
| `count` | integer | Maximum codes to return (default 100) |
| `offset` | integer | Pagination offset |

#### Example - Expand by URL

```bash
curl "http://localhost:8000/ValueSet/\$expand?url=http://example.org/fhir/ValueSet/diabetes-codes"
```

#### Example - Expand with Filter

```bash
curl "http://localhost:8000/ValueSet/\$expand?url=http://example.org/fhir/ValueSet/diabetes-codes&filter=type"
```

#### Example - Expand by ID

```bash
curl "http://localhost:8000/ValueSet/diabetes-codes/\$expand"
```

#### Response

```json
{
  "resourceType": "ValueSet",
  "id": "diabetes-codes",
  "url": "http://example.org/fhir/ValueSet/diabetes-codes",
  "status": "active",
  "expansion": {
    "identifier": "urn:uuid:abc123",
    "timestamp": "2024-01-15T10:30:00Z",
    "total": 2,
    "contains": [
      {
        "system": "http://example.org/fhir/CodeSystem/diabetes-types",
        "code": "type1",
        "display": "Type 1 diabetes"
      },
      {
        "system": "http://example.org/fhir/CodeSystem/diabetes-types",
        "code": "type2",
        "display": "Type 2 diabetes"
      }
    ]
  }
}
```

### ValueSet $validate-code

Validate that a code is in a ValueSet.

```http
GET /ValueSet/$validate-code?url={valueSetUrl}&code={code}&system={system}
POST /ValueSet/$validate-code
```

#### GET Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | uri | Yes | ValueSet canonical URL |
| `code` | string | Yes* | Code to validate |
| `system` | uri | No | Code system URL |

*Required unless using POST with coding or codeableConcept.

#### GET Example

```bash
curl "http://localhost:8000/ValueSet/\$validate-code?url=http://example.org/fhir/ValueSet/diabetes-codes&code=type1&system=http://example.org/fhir/CodeSystem/diabetes-types"
```

#### POST Example - With Coding

```bash
curl -X POST http://localhost:8000/ValueSet/\$validate-code \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Parameters",
    "parameter": [
      {"name": "url", "valueUri": "http://example.org/fhir/ValueSet/diabetes-codes"},
      {
        "name": "coding",
        "valueCoding": {
          "system": "http://example.org/fhir/CodeSystem/diabetes-types",
          "code": "type2"
        }
      }
    ]
  }'
```

#### POST Example - With CodeableConcept

```bash
curl -X POST http://localhost:8000/ValueSet/\$validate-code \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Parameters",
    "parameter": [
      {"name": "url", "valueUri": "http://example.org/fhir/ValueSet/diabetes-codes"},
      {
        "name": "codeableConcept",
        "valueCodeableConcept": {
          "coding": [
            {"system": "http://other", "code": "WRONG"},
            {"system": "http://example.org/fhir/CodeSystem/diabetes-types", "code": "type1"}
          ]
        }
      }
    ]
  }'
```

#### Response

```json
{
  "resourceType": "Parameters",
  "parameter": [
    {"name": "result", "valueBoolean": true},
    {"name": "display", "valueString": "Type 1 diabetes"}
  ]
}
```

### CodeSystem $lookup

Look up information about a code.

```http
GET /CodeSystem/$lookup?system={systemUrl}&code={code}
POST /CodeSystem/$lookup
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `system` | uri | Yes | Code system URL |
| `code` | string | Yes | Code to look up |
| `version` | string | No | Code system version |

#### Example

```bash
curl "http://localhost:8000/CodeSystem/\$lookup?system=http://example.org/fhir/CodeSystem/diabetes-types&code=type1"
```

#### Response

```json
{
  "resourceType": "Parameters",
  "parameter": [
    {"name": "name", "valueString": "DiabetesTypes"},
    {"name": "display", "valueString": "Type 1 diabetes"},
    {"name": "code", "valueCode": "type1"},
    {"name": "system", "valueUri": "http://example.org/fhir/CodeSystem/diabetes-types"}
  ]
}
```

### CodeSystem $subsumes

Test if one code subsumes another (hierarchical relationship).

```http
GET /CodeSystem/$subsumes?system={systemUrl}&codeA={codeA}&codeB={codeB}
GET /CodeSystem/{id}/$subsumes?codeA={codeA}&codeB={codeB}
POST /CodeSystem/$subsumes
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `system` | uri | Yes | Code system URL |
| `codeA` | string | Yes | First code (potential ancestor) |
| `codeB` | string | Yes | Second code (potential descendant) |
| `version` | string | No | Code system version |

#### Response Outcomes

| Outcome | Meaning |
|---------|---------|
| `equivalent` | Codes are the same |
| `subsumes` | codeA is an ancestor of codeB |
| `subsumed-by` | codeA is a descendant of codeB |
| `not-subsumed` | No hierarchical relationship |

#### Example - Parent Subsumes Child

```bash
curl "http://localhost:8000/CodeSystem/\$subsumes?system=http://example.org/fhir/CodeSystem/diabetes-types&codeA=diabetes&codeB=type1"
```

Response:
```json
{
  "resourceType": "Parameters",
  "parameter": [{"name": "outcome", "valueCode": "subsumes"}]
}
```

#### Example - Child Subsumed By Parent

```bash
curl "http://localhost:8000/CodeSystem/\$subsumes?system=http://example.org/fhir/CodeSystem/diabetes-types&codeA=type1&codeB=diabetes"
```

Response:
```json
{
  "resourceType": "Parameters",
  "parameter": [{"name": "outcome", "valueCode": "subsumed-by"}]
}
```

### memberOf Endpoint

Convenience endpoint to check code membership in a ValueSet.

```http
GET /terminology/memberOf?code={code}&system={system}&valueSetUrl={url}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | string | Yes | Code to check |
| `system` | uri | Yes | Code system URL |
| `valueSetUrl` | uri | Yes | ValueSet URL |

#### Example

```bash
curl "http://localhost:8000/terminology/memberOf?code=type1&system=http://example.org/fhir/CodeSystem/diabetes-types&valueSetUrl=http://example.org/fhir/ValueSet/diabetes-codes"
```

Response:
```json
{
  "resourceType": "Parameters",
  "parameter": [{"name": "result", "valueBoolean": true}]
}
```

---

## Hierarchical CodeSystems

The terminology provider supports hierarchical CodeSystems where codes can have nested child concepts:

```json
{
  "resourceType": "CodeSystem",
  "url": "http://example.org/fhir/CodeSystem/conditions",
  "concept": [
    {
      "code": "metabolic",
      "display": "Metabolic disorders",
      "concept": [
        {
          "code": "diabetes",
          "display": "Diabetes mellitus",
          "concept": [
            {"code": "type1", "display": "Type 1 diabetes"},
            {"code": "type2", "display": "Type 2 diabetes"}
          ]
        },
        {"code": "obesity", "display": "Obesity"}
      ]
    },
    {
      "code": "cardiovascular",
      "display": "Cardiovascular diseases"
    }
  ]
}
```

With this structure:
- `$lookup` finds codes at any level of the hierarchy
- `$subsumes` tests hierarchical relationships
- `$expand` includes all codes when referencing the CodeSystem

---

## Integration with CQL

### CQLTerminologyAdapter

For CQL evaluation, use the `CQLTerminologyAdapter` which integrates with the FHIR server's terminology provider:

```python
from fhirkit.server.storage.fhir_store import FHIRStore
from fhirkit.engine.cql import (
    CQLEvaluator,
    CQLTerminologyAdapter,
    InMemoryDataSource,
)

# Create store with terminology resources
store = FHIRStore()

# Load CodeSystem
store.update("CodeSystem", "diabetes-types", {
    "resourceType": "CodeSystem",
    "id": "diabetes-types",
    "url": "http://example.org/fhir/CodeSystem/diabetes-types",
    "concept": [
        {"code": "type1", "display": "Type 1 diabetes"},
        {"code": "type2", "display": "Type 2 diabetes"},
    ]
})

# Load ValueSet
store.update("ValueSet", "diabetes-codes", {
    "resourceType": "ValueSet",
    "id": "diabetes-codes",
    "url": "http://example.org/fhir/ValueSet/diabetes-codes",
    "compose": {
        "include": [{
            "system": "http://example.org/fhir/CodeSystem/diabetes-types"
        }]
    }
})

# Create terminology adapter
adapter = CQLTerminologyAdapter(store)

# Expand ValueSet for CQL
codes = adapter.expand_valueset("http://example.org/fhir/ValueSet/diabetes-codes")
for code in codes:
    print(f"{code.system}|{code.code}: {code.display}")

# Create data source with terminology
data_source = InMemoryDataSource()
data_source.add_valueset("http://example.org/fhir/ValueSet/diabetes-codes", codes)

# Create evaluator
evaluator = CQLEvaluator(data_source=data_source)
```

### Convenience Function

```python
from fhirkit.engine.cql import create_terminology_datasource

# Create data source with preloaded ValueSets
data_source, adapter = create_terminology_datasource(
    store,
    valueset_urls=[
        "http://example.org/fhir/ValueSet/diabetes-codes",
        "http://example.org/fhir/ValueSet/vital-signs"
    ]
)

# Use with CQL evaluator
evaluator = CQLEvaluator(data_source=data_source)
```

### CQL with ValueSet References

```cql
library DiabetesScreening version '1.0'

using FHIR version '4.0.1'

// Reference ValueSets by URL
valueset "Diabetes Conditions": 'http://example.org/fhir/ValueSet/diabetes-codes'

context Patient

// Use ValueSet in retrieve
define HasDiabetes:
  exists([Condition: "Diabetes Conditions"])

// Explicit membership check
define DiabetesConditions:
  [Condition] C
    where C.code in "Diabetes Conditions"
```

---

## Python API

### Using the Terminology Provider Directly

```python
from fhirkit.server.storage.fhir_store import FHIRStore
from fhirkit.server.terminology import FHIRStoreTerminologyProvider

# Create store and provider
store = FHIRStore()
provider = FHIRStoreTerminologyProvider(store)

# Expand a ValueSet
expansion = provider.expand_valueset(url="http://example.org/fhir/ValueSet/test")
for item in expansion["expansion"]["contains"]:
    print(f"{item['code']}: {item['display']}")

# Validate a code
result = provider.validate_code(
    valueset_url="http://example.org/fhir/ValueSet/test",
    code="type1",
    system="http://example.org/fhir/CodeSystem/test"
)
is_valid = result["parameter"][0]["valueBoolean"]

# Check membership
is_member = provider.member_of(
    valueset_url="http://example.org/fhir/ValueSet/test",
    code="type1",
    system="http://example.org/fhir/CodeSystem/test"
)

# Lookup code
info = provider.lookup_code(
    system="http://example.org/fhir/CodeSystem/test",
    code="type1"
)

# Test subsumption
result = provider.subsumes(
    system="http://example.org/fhir/CodeSystem/test",
    code_a="parent",
    code_b="child"
)
```

---

## Examples

### Loading Terminology from Files

```python
import json
from pathlib import Path
from fhirkit.server.storage.fhir_store import FHIRStore

def load_terminology_directory(store: FHIRStore, directory: Path):
    """Load all CodeSystem and ValueSet files from a directory."""
    for file_path in directory.glob("*.json"):
        with open(file_path) as f:
            resource = json.load(f)

        resource_type = resource.get("resourceType")
        resource_id = resource.get("id")

        if resource_type in ("CodeSystem", "ValueSet") and resource_id:
            store.update(resource_type, resource_id, resource)
            print(f"Loaded {resource_type}/{resource_id}")

# Usage
store = FHIRStore()
load_terminology_directory(store, Path("./terminology"))
```

### Example CodeSystem with Definitions

```json
{
  "resourceType": "CodeSystem",
  "id": "observation-status",
  "url": "http://hl7.org/fhir/observation-status",
  "name": "ObservationStatus",
  "status": "active",
  "concept": [
    {
      "code": "registered",
      "display": "Registered",
      "definition": "The existence of the observation is registered, but there is no result yet available."
    },
    {
      "code": "preliminary",
      "display": "Preliminary",
      "definition": "This is an initial or interim observation: data may be incomplete or unverified."
    },
    {
      "code": "final",
      "display": "Final",
      "definition": "The observation is complete and verified."
    },
    {
      "code": "amended",
      "display": "Amended",
      "definition": "Subsequent to being Final, the observation has been modified."
    }
  ]
}
```

### Example ValueSet Referencing Entire CodeSystem

```json
{
  "resourceType": "ValueSet",
  "id": "all-observation-status",
  "url": "http://example.org/fhir/ValueSet/all-observation-status",
  "name": "AllObservationStatus",
  "status": "active",
  "compose": {
    "include": [
      {
        "system": "http://hl7.org/fhir/observation-status"
      }
    ]
  }
}
```

When expanded, this ValueSet includes all codes from the referenced CodeSystem.

---

## Supported Code Systems

The terminology service works with any code system. Common healthcare code systems:

| System URL | Name | Description |
|------------|------|-------------|
| `http://snomed.info/sct` | SNOMED CT | Clinical terminology |
| `http://loinc.org` | LOINC | Laboratory and clinical observations |
| `http://www.nlm.nih.gov/research/umls/rxnorm` | RxNorm | Medications |
| `http://hl7.org/fhir/sid/icd-10` | ICD-10 | Diagnoses |
| `http://hl7.org/fhir/sid/icd-10-cm` | ICD-10-CM | US diagnosis codes |
| `http://www.ama-assn.org/go/cpt` | CPT | Procedures |
| `http://hl7.org/fhir/sid/cvx` | CVX | Vaccines |
| `http://hl7.org/fhir/sid/ndc` | NDC | Drug codes |
