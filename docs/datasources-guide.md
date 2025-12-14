# Data Sources Guide

This guide covers FHIR data sources for CQL evaluation. Data sources provide the bridge between your FHIR data and the CQL engine, enabling retrieve operations, patient-scoped queries, and code filtering.

## Introduction

### What are Data Sources?

Data sources are abstractions that provide FHIR resources to the CQL evaluator during execution. When a CQL expression includes a retrieve statement like `[Condition]` or `[Observation: "Blood Pressure"]`, the data source is responsible for:

1. Finding all resources of the requested type
2. Filtering by patient context
3. Applying code/valueset filters
4. Applying date range filters

### Available Data Sources

| Data Source | Use Case |
|-------------|----------|
| `InMemoryDataSource` | General-purpose storage for testing and simple scenarios |
| `BundleDataSource` | Load data from a FHIR Bundle |
| `PatientBundleDataSource` | Patient-centric bundle with automatic patient context |
| Custom implementations | Connect to FHIR servers, databases, etc. |

---

## Quick Start

### Basic Usage

```python
from fhirkit.engine.cql import CQLEvaluator, InMemoryDataSource

# Create and populate data source
data_source = InMemoryDataSource()

# Add a patient
data_source.add_resource({
    "resourceType": "Patient",
    "id": "patient-1",
    "birthDate": "1980-05-15"
})

# Add a condition
data_source.add_resource({
    "resourceType": "Condition",
    "id": "condition-1",
    "subject": {"reference": "Patient/patient-1"},
    "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]}
})

# Create evaluator with data source
evaluator = CQLEvaluator(data_source=data_source)

# Compile and run CQL
evaluator.compile("""
    library Test version '1.0'
    using FHIR version '4.0.1'
    context Patient
    define HasCondition: exists([Condition])
""")

patient = {"resourceType": "Patient", "id": "patient-1"}
result = evaluator.evaluate_definition("HasCondition", resource=patient)
print(result)  # True
```

### Using Bundle Data Source

```python
from fhirkit.engine.cql import CQLEvaluator, BundleDataSource

# Load from a FHIR Bundle
bundle = {
    "resourceType": "Bundle",
    "entry": [
        {"resource": {"resourceType": "Patient", "id": "p1", "birthDate": "1990-01-01"}},
        {"resource": {"resourceType": "Observation", "id": "o1", "subject": {"reference": "Patient/p1"}}}
    ]
}

data_source = BundleDataSource(bundle)
evaluator = CQLEvaluator(data_source=data_source)
```

---

## InMemoryDataSource

The most flexible data source, storing resources in memory with full filtering support.

### Creating and Populating

```python
from fhirkit.engine.cql import InMemoryDataSource

ds = InMemoryDataSource()

# Add single resource
ds.add_resource({
    "resourceType": "Patient",
    "id": "p1",
    "birthDate": "1985-03-15"
})

# Add multiple resources
ds.add_resources([
    {"resourceType": "Patient", "id": "p2", "birthDate": "1990-06-20"},
    {"resourceType": "Patient", "id": "p3", "birthDate": "1975-12-01"},
])
```

### Retrieving Resources

```python
# Retrieve all resources of a type
patients = ds.retrieve("Patient")
print(f"Found {len(patients)} patients")

# Retrieve with patient context
from fhirkit.engine.cql import PatientContext

context = PatientContext(resource={"resourceType": "Patient", "id": "p1"})
conditions = ds.retrieve("Condition", context=context)
# Returns only conditions for patient p1
```

### Resolving References

```python
# Resolve a FHIR reference
patient = ds.resolve_reference("Patient/p1")
if patient:
    print(f"Found: {patient['id']}")
else:
    print("Not found")
```

### Working with ValueSets

```python
from fhirkit.engine.cql import CQLCode

# Add expanded valueset
ds.add_valueset(
    "http://example.org/valueset/diabetes",
    [
        CQLCode(code="44054006", system="http://snomed.info/sct"),  # Type 2 DM
        CQLCode(code="46635009", system="http://snomed.info/sct"),  # Type 1 DM
    ]
)

# Retrieve with valueset filter
diabetes_conditions = ds.retrieve(
    "Condition",
    code_path="code",
    valueset="http://example.org/valueset/diabetes"
)
```

### Clearing Data

```python
# Clear all resources and valuesets
ds.clear()
```

---

## BundleDataSource

Load FHIR resources from a Bundle for evaluation.

### Creating from Bundle

```python
from fhirkit.engine.cql import BundleDataSource

bundle = {
    "resourceType": "Bundle",
    "type": "collection",
    "entry": [
        {"resource": {"resourceType": "Patient", "id": "p1"}},
        {"resource": {"resourceType": "Condition", "id": "c1", "subject": {"reference": "Patient/p1"}}},
        {"resource": {"resourceType": "Observation", "id": "o1", "subject": {"reference": "Patient/p1"}}}
    ]
}

ds = BundleDataSource(bundle)
```

### Loading Single Resource

You can also pass a single resource:

```python
patient = {"resourceType": "Patient", "id": "p1", "birthDate": "1990-01-01"}
ds = BundleDataSource(patient)
```

### Accessing Resources

```python
# Get all resources by type
print(ds.resources)  # {"Patient": [...], "Condition": [...], ...}

# Count resources
for resource_type, resources in ds.resources.items():
    print(f"{resource_type}: {len(resources)}")
```

### Adding ValueSets

```python
from fhirkit.engine.cql import CQLCode

ds.add_valueset(
    "http://example.org/valueset/labs",
    [CQLCode(code="2339-0", system="http://loinc.org")]
)
```

---

## PatientBundleDataSource

Specialized for patient-centric bundles with automatic patient context.

### Usage

```python
from fhirkit.engine.cql import PatientBundleDataSource

# Patient bundle (like Synthea output)
bundle = {
    "resourceType": "Bundle",
    "entry": [
        {"resource": {"resourceType": "Patient", "id": "p1", "name": [{"family": "Smith"}]}},
        {"resource": {"resourceType": "Condition", "id": "c1", "subject": {"reference": "Patient/p1"}}},
        {"resource": {"resourceType": "Condition", "id": "c2", "subject": {"reference": "Patient/p2"}}},  # Different patient
    ]
}

ds = PatientBundleDataSource(bundle)

# Access the extracted patient
print(ds.patient)  # {"resourceType": "Patient", "id": "p1", ...}

# Retrieves are automatically filtered to the patient
conditions = ds.retrieve("Condition")
print(len(conditions))  # 1 (only c1, which belongs to p1)
```

### Key Differences from BundleDataSource

| Feature | BundleDataSource | PatientBundleDataSource |
|---------|------------------|-------------------------|
| Patient extraction | Manual | Automatic |
| Default context | None | Patient from bundle |
| Resource filtering | Requires explicit context | Automatic patient scope |

---

## Filtering Capabilities

### Code Filtering

Filter resources by code values:

```python
from fhirkit.engine.cql import CQLCode

# Using CQLCode
diabetes_code = CQLCode(code="44054006", system="http://snomed.info/sct")
conditions = ds.retrieve(
    "Condition",
    code_path="code",
    codes=[diabetes_code]
)

# Using simple string (matches any system)
conditions = ds.retrieve(
    "Condition",
    code_path="code",
    codes=["44054006"]
)

# Using dict
conditions = ds.retrieve(
    "Condition",
    code_path="code",
    codes=[{"code": "44054006", "system": "http://snomed.info/sct"}]
)
```

### ValueSet Filtering

Filter by valueset membership:

```python
# First, add the valueset
ds.add_valueset(
    "http://example.org/valueset/diabetes",
    [
        CQLCode(code="44054006", system="http://snomed.info/sct"),
        CQLCode(code="46635009", system="http://snomed.info/sct"),
    ]
)

# Then filter by valueset
conditions = ds.retrieve(
    "Condition",
    code_path="code",
    valueset="http://example.org/valueset/diabetes"
)
```

### Date Range Filtering

Filter resources by date:

```python
from fhirkit.engine.cql import CQLInterval
from fhirkit.engine.types import FHIRDateTime

date_range = CQLInterval(
    low=FHIRDateTime.parse("2024-01-01T00:00:00"),
    high=FHIRDateTime.parse("2024-12-31T23:59:59"),
    low_closed=True,
    high_closed=True
)

observations = ds.retrieve(
    "Observation",
    date_path="effectiveDateTime",
    date_range=date_range
)
```

### Combined Filtering

Apply multiple filters:

```python
# Get blood pressure observations from 2024 for a specific patient
observations = ds.retrieve(
    "Observation",
    context=patient_context,
    code_path="code",
    valueset="http://example.org/valueset/blood-pressure",
    date_path="effectiveDateTime",
    date_range=date_range
)
```

---

## Nested Value Access

Data sources support dot notation for accessing nested values:

```python
# Simple path
# {"patient": {"name": "John"}} -> "John"
value = ds._get_nested_value(resource, "patient.name")

# Array index
# {"name": [{"family": "Smith"}, {"family": "Jones"}]} -> "Smith"
value = ds._get_nested_value(resource, "name.0.family")

# Array property (returns all values)
# {"name": [{"family": "Smith"}, {"family": "Jones"}]} -> ["Smith", "Jones"]
value = ds._get_nested_value(resource, "name.family")
```

### Supported Code Paths

Common code paths for FHIR resources:

| Resource Type | Code Path |
|---------------|-----------|
| Condition | `code` |
| Observation | `code` |
| Procedure | `code` |
| MedicationRequest | `medicationCodeableConcept` |
| AllergyIntolerance | `code` |
| Immunization | `vaccineCode` |

---

## Patient Reference Resolution

Data sources automatically extract patient references from resources:

```python
# The data source knows how to find patient references for each resource type
# Condition: subject.reference or patient.reference
# Observation: subject.reference or patient.reference
# AllergyIntolerance: patient.reference
# etc.
```

### Supported Resource Types

| Resource Type | Patient Reference Path(s) |
|---------------|---------------------------|
| Condition | `subject.reference`, `patient.reference` |
| Observation | `subject.reference`, `patient.reference` |
| MedicationRequest | `subject.reference`, `patient.reference` |
| Procedure | `subject.reference`, `patient.reference` |
| Encounter | `subject.reference`, `patient.reference` |
| DiagnosticReport | `subject.reference`, `patient.reference` |
| AllergyIntolerance | `patient.reference` |
| Immunization | `patient.reference` |
| Coverage | `beneficiary.reference` |
| Claim | `patient.reference` |

---

## Creating Custom Data Sources

Implement your own data source for specific needs.

### Interface

```python
from fhirkit.engine.cql.datasource import FHIRDataSource
from fhirkit.engine.cql import CQLInterval
from typing import Any

class MyDataSource(FHIRDataSource):
    """Custom data source implementation."""

    def retrieve(
        self,
        resource_type: str,
        context: "CQLContext | None" = None,
        code_path: str | None = None,
        codes: list[Any] | None = None,
        valueset: str | None = None,
        date_path: str | None = None,
        date_range: CQLInterval | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Retrieve FHIR resources.

        Args:
            resource_type: FHIR resource type (e.g., "Patient", "Condition")
            context: CQL context (for patient-scoped queries)
            code_path: Path to code element for filtering
            codes: List of codes to filter by
            valueset: ValueSet URL to filter by
            date_path: Path to date element for filtering
            date_range: Date interval for filtering

        Returns:
            List of matching FHIR resources
        """
        # Implement your retrieval logic
        pass

    def resolve_reference(self, reference: str) -> dict[str, Any] | None:
        """Resolve a FHIR reference.

        Args:
            reference: Reference string (e.g., "Patient/123")

        Returns:
            The referenced resource or None
        """
        # Implement reference resolution
        pass
```

### Example: HTTP FHIR Server Data Source

```python
import requests
from fhirkit.engine.cql.datasource import FHIRDataSource

class FHIRServerDataSource(FHIRDataSource):
    """Data source backed by a FHIR server."""

    def __init__(self, base_url: str, auth: tuple | None = None):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self._session = requests.Session()
        if auth:
            self._session.auth = auth

    def retrieve(
        self,
        resource_type: str,
        context=None,
        code_path=None,
        codes=None,
        valueset=None,
        date_path=None,
        date_range=None,
        **kwargs,
    ) -> list[dict]:
        # Build search parameters
        params = {}

        # Add patient filter if context provided
        if context and context.resource:
            patient_id = context.resource.get("id")
            if patient_id and resource_type != "Patient":
                params["patient"] = f"Patient/{patient_id}"

        # Add code filter
        if codes:
            code_values = [c.code if hasattr(c, 'code') else c for c in codes]
            params["code"] = ",".join(code_values)

        # Make request
        url = f"{self.base_url}/{resource_type}"
        response = self._session.get(url, params=params)
        response.raise_for_status()

        bundle = response.json()
        return [entry["resource"] for entry in bundle.get("entry", [])]

    def resolve_reference(self, reference: str) -> dict | None:
        url = f"{self.base_url}/{reference}"
        response = self._session.get(url)
        if response.status_code == 200:
            return response.json()
        return None
```

### Example: Database Data Source

```python
from fhirkit.engine.cql.datasource import FHIRDataSource
import json

class SQLiteDataSource(FHIRDataSource):
    """Data source backed by SQLite database."""

    def __init__(self, db_path: str):
        import sqlite3
        self.conn = sqlite3.connect(db_path)

    def retrieve(
        self,
        resource_type: str,
        context=None,
        code_path=None,
        codes=None,
        **kwargs,
    ) -> list[dict]:
        cursor = self.conn.cursor()

        query = "SELECT data FROM resources WHERE type = ?"
        params = [resource_type]

        # Add patient filter
        if context and context.resource:
            patient_id = context.resource.get("id")
            if patient_id:
                query += " AND patient_id = ?"
                params.append(patient_id)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        resources = [json.loads(row[0]) for row in rows]

        # Apply code filter in memory
        if code_path and codes:
            resources = [
                r for r in resources
                if self._matches_code(r, code_path, codes)
            ]

        return resources

    def resolve_reference(self, reference: str) -> dict | None:
        resource_type, resource_id = reference.split("/")
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT data FROM resources WHERE type = ? AND id = ?",
            (resource_type, resource_id)
        )
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None
```

---

## Integration with CQL Evaluator

### Setting Data Source

```python
from fhirkit.engine.cql import CQLEvaluator, InMemoryDataSource

# Method 1: Pass to constructor
data_source = InMemoryDataSource()
evaluator = CQLEvaluator(data_source=data_source)

# Method 2: Set after creation
evaluator = CQLEvaluator()
evaluator._data_source = data_source
```

### Using with Retrieve Expressions

```python
data_source = InMemoryDataSource()
data_source.add_resources([
    {"resourceType": "Patient", "id": "p1", "birthDate": "1980-01-01"},
    {
        "resourceType": "Condition",
        "id": "c1",
        "subject": {"reference": "Patient/p1"},
        "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]}
    }
])

evaluator = CQLEvaluator(data_source=data_source)

# CQL with retrieve
evaluator.compile("""
    library Test version '1.0'
    using FHIR version '4.0.1'

    codesystem "SNOMED": 'http://snomed.info/sct'
    code "Diabetes": '44054006' from "SNOMED"

    context Patient

    define AllConditions: [Condition]

    define DiabetesConditions: [Condition: "Diabetes"]

    define HasDiabetes: exists(DiabetesConditions)
""")

patient = {"resourceType": "Patient", "id": "p1"}

# Evaluate
all_conditions = evaluator.evaluate_definition("AllConditions", resource=patient)
has_diabetes = evaluator.evaluate_definition("HasDiabetes", resource=patient)

print(f"Conditions: {len(all_conditions)}")  # 1
print(f"Has diabetes: {has_diabetes}")  # True
```

### Using with Measure Evaluation

```python
from fhirkit.engine.cql import MeasureEvaluator, InMemoryDataSource

# Set up data
data_source = InMemoryDataSource()
data_source.add_resources([...])

# Create measure evaluator with data source
evaluator = MeasureEvaluator(data_source=data_source)
evaluator.load_measure(measure_cql)

# Evaluate population
patients = data_source.retrieve("Patient")
report = evaluator.evaluate_population(patients, data_source=data_source)
```

---

## Performance Tips

### Batch Loading

```python
# Good: Load all resources at once
ds.add_resources(all_resources)

# Less efficient: Add one at a time in a loop
for resource in all_resources:
    ds.add_resource(resource)
```

### Pre-expand ValueSets

```python
# Expand valuesets once, upfront
ds.add_valueset("http://example.org/vs/diabetes", expanded_codes)

# Instead of expanding during each retrieve
```

### Use Specific Resource Types

```python
# Good: Specific type
ds.retrieve("Condition")

# Avoid: Retrieving all and filtering in code
all_resources = ds._resources
conditions = [r for r in all_resources.get("Condition", [])]
```

### Patient Context Early

```python
# Good: Filter by patient early
conditions = ds.retrieve("Condition", context=patient_context)

# Less efficient: Retrieve all, filter later
all_conditions = ds.retrieve("Condition")
patient_conditions = [c for c in all_conditions if matches_patient(c)]
```

---

## Examples

### Loading Synthea Data

```python
import json
from pathlib import Path
from fhirkit.engine.cql import PatientBundleDataSource, CQLEvaluator

def load_synthea_patient(patient_file: Path):
    """Load a Synthea patient bundle."""
    with open(patient_file) as f:
        bundle = json.load(f)

    ds = PatientBundleDataSource(bundle)
    return ds

# Load patient
ds = load_synthea_patient(Path("synthea/John_Smith.json"))

# Patient is automatically extracted
print(f"Patient: {ds.patient['id']}")

# Use with evaluator
evaluator = CQLEvaluator(data_source=ds)
evaluator.compile(my_cql)
result = evaluator.evaluate_definition("HasCondition", resource=ds.patient)
```

### Multi-Patient Evaluation

```python
from fhirkit.engine.cql import InMemoryDataSource, CQLEvaluator, PatientContext

# Load all patients and resources into one data source
ds = InMemoryDataSource()
ds.add_resources(all_patients)
ds.add_resources(all_conditions)
ds.add_resources(all_observations)

evaluator = CQLEvaluator(data_source=ds)
evaluator.compile(cql_source)

# Evaluate for each patient
results = {}
for patient in ds.retrieve("Patient"):
    context = PatientContext(resource=patient)
    evaluator._context = context
    results[patient["id"]] = evaluator.evaluate_definition("Result", resource=patient)
```

### Testing with Mock Data

```python
import pytest
from fhirkit.engine.cql import InMemoryDataSource, CQLEvaluator

@pytest.fixture
def test_data_source():
    """Create a data source with test data."""
    ds = InMemoryDataSource()
    ds.add_resources([
        {"resourceType": "Patient", "id": "test-patient", "birthDate": "1980-01-01"},
        {
            "resourceType": "Condition",
            "id": "test-condition",
            "subject": {"reference": "Patient/test-patient"},
            "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]}
        }
    ])
    return ds

def test_diabetes_detection(test_data_source):
    """Test that diabetes is correctly detected."""
    evaluator = CQLEvaluator(data_source=test_data_source)
    evaluator.compile("""
        library Test version '1.0'
        using FHIR version '4.0.1'
        context Patient
        define HasDiabetes: exists([Condition])
    """)

    patient = {"resourceType": "Patient", "id": "test-patient"}
    result = evaluator.evaluate_definition("HasDiabetes", resource=patient)

    assert result is True
```

---

## Troubleshooting

### No Resources Returned

1. Check resource type spelling (case-sensitive)
2. Verify patient context is set correctly
3. Check code paths match FHIR structure
4. Verify valueset is loaded

```python
# Debug: List all resources
print(ds._resources)

# Debug: Check specific type
print(ds.retrieve("Condition"))
```

### Code Filtering Not Working

```python
# Check the resource structure
resource = ds.retrieve("Condition")[0]
print(resource.get("code"))

# Verify code path
print(ds._get_nested_value(resource, "code"))
print(ds._get_nested_value(resource, "code.coding"))
```

### Patient Context Issues

```python
# Check patient reference in resources
for condition in ds.retrieve("Condition"):
    print(ds._get_patient_reference(condition))

# Verify context patient ID matches
print(context.resource.get("id"))
```

---

## See Also

- [CQL Tutorial](cql-tutorial.md) - CQL language basics
- [CQL Python API](cql-api.md) - CQL evaluator reference
- [Measure Evaluation Guide](measure-guide.md) - Quality measures
- [FHIR Server Guide](fhir-server-guide.md) - Built-in FHIR server
