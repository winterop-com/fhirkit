"""Tests for CQL data source implementations."""

from fhirkit.engine.cql import (
    BundleDataSource,
    CQLCode,
    CQLEvaluator,
    InMemoryDataSource,
    PatientBundleDataSource,
    PatientContext,
)


class TestInMemoryDataSource:
    """Tests for InMemoryDataSource."""

    def test_add_resource(self) -> None:
        """Test adding a single resource."""
        ds = InMemoryDataSource()
        patient = {"resourceType": "Patient", "id": "123", "name": [{"family": "Smith"}]}

        ds.add_resource(patient)

        assert "Patient" in ds._resources
        assert len(ds._resources["Patient"]) == 1
        assert ds._resources["Patient"][0]["id"] == "123"

    def test_add_resources(self) -> None:
        """Test adding multiple resources."""
        ds = InMemoryDataSource()
        resources = [
            {"resourceType": "Patient", "id": "1"},
            {"resourceType": "Patient", "id": "2"},
            {"resourceType": "Condition", "id": "c1"},
        ]

        ds.add_resources(resources)

        assert len(ds._resources["Patient"]) == 2
        assert len(ds._resources["Condition"]) == 1

    def test_retrieve_by_type(self) -> None:
        """Test retrieving resources by type."""
        ds = InMemoryDataSource()
        ds.add_resources(
            [
                {"resourceType": "Patient", "id": "1"},
                {"resourceType": "Condition", "id": "c1"},
                {"resourceType": "Condition", "id": "c2"},
            ]
        )

        conditions = ds.retrieve("Condition")

        assert len(conditions) == 2

    def test_retrieve_with_patient_context(self) -> None:
        """Test retrieving resources filtered by patient context."""
        ds = InMemoryDataSource()
        ds.add_resources(
            [
                {"resourceType": "Patient", "id": "p1"},
                {"resourceType": "Patient", "id": "p2"},
                {"resourceType": "Condition", "id": "c1", "subject": {"reference": "Patient/p1"}},
                {"resourceType": "Condition", "id": "c2", "subject": {"reference": "Patient/p1"}},
                {"resourceType": "Condition", "id": "c3", "subject": {"reference": "Patient/p2"}},
            ]
        )

        # Create patient context
        context = PatientContext(resource={"resourceType": "Patient", "id": "p1"})

        conditions = ds.retrieve("Condition", context=context)

        assert len(conditions) == 2
        assert all(c["subject"]["reference"] == "Patient/p1" for c in conditions)

    def test_resolve_reference(self) -> None:
        """Test resolving a FHIR reference."""
        ds = InMemoryDataSource()
        patient = {"resourceType": "Patient", "id": "123"}
        ds.add_resource(patient)

        resolved = ds.resolve_reference("Patient/123")

        assert resolved is not None
        assert resolved["id"] == "123"

    def test_resolve_reference_not_found(self) -> None:
        """Test resolving a nonexistent reference."""
        ds = InMemoryDataSource()

        resolved = ds.resolve_reference("Patient/999")

        assert resolved is None

    def test_retrieve_with_code_filter(self) -> None:
        """Test retrieving resources filtered by code."""
        ds = InMemoryDataSource()
        ds.add_resources(
            [
                {
                    "resourceType": "Condition",
                    "id": "c1",
                    "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]},
                },
                {
                    "resourceType": "Condition",
                    "id": "c2",
                    "code": {"coding": [{"system": "http://snomed.info/sct", "code": "73211009"}]},
                },
            ]
        )

        diabetes_code = CQLCode(code="44054006", system="http://snomed.info/sct")
        conditions = ds.retrieve(
            "Condition",
            code_path="code",
            codes=[diabetes_code],
        )

        assert len(conditions) == 1
        assert conditions[0]["id"] == "c1"

    def test_retrieve_with_valueset_filter(self) -> None:
        """Test retrieving resources filtered by valueset."""
        ds = InMemoryDataSource()
        ds.add_resources(
            [
                {
                    "resourceType": "Condition",
                    "id": "c1",
                    "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]},
                },
                {
                    "resourceType": "Condition",
                    "id": "c2",
                    "code": {"coding": [{"system": "http://snomed.info/sct", "code": "OTHER"}]},
                },
            ]
        )

        # Add valueset
        ds.add_valueset(
            "http://example.org/valueset/diabetes",
            [CQLCode(code="44054006", system="http://snomed.info/sct")],
        )

        conditions = ds.retrieve(
            "Condition",
            code_path="code",
            valueset="http://example.org/valueset/diabetes",
        )

        assert len(conditions) == 1
        assert conditions[0]["id"] == "c1"

    def test_clear(self) -> None:
        """Test clearing all resources."""
        ds = InMemoryDataSource()
        ds.add_resource({"resourceType": "Patient", "id": "1"})
        ds.add_valueset("http://example.org/vs", [])

        ds.clear()

        assert len(ds._resources) == 0
        assert len(ds._by_id) == 0
        assert len(ds._valuesets) == 0


class TestBundleDataSource:
    """Tests for BundleDataSource."""

    def test_load_bundle(self) -> None:
        """Test loading a FHIR Bundle."""
        bundle = {
            "resourceType": "Bundle",
            "entry": [
                {"resource": {"resourceType": "Patient", "id": "p1"}},
                {"resource": {"resourceType": "Condition", "id": "c1"}},
            ],
        }

        ds = BundleDataSource(bundle)

        assert len(ds.resources["Patient"]) == 1
        assert len(ds.resources["Condition"]) == 1

    def test_load_single_resource(self) -> None:
        """Test loading a single resource (not a bundle)."""
        patient = {"resourceType": "Patient", "id": "p1"}

        ds = BundleDataSource(patient)

        assert len(ds.resources["Patient"]) == 1

    def test_retrieve_from_bundle(self) -> None:
        """Test retrieving resources from a bundle."""
        bundle = {
            "resourceType": "Bundle",
            "entry": [
                {"resource": {"resourceType": "Patient", "id": "p1"}},
                {"resource": {"resourceType": "Observation", "id": "o1"}},
                {"resource": {"resourceType": "Observation", "id": "o2"}},
            ],
        }

        ds = BundleDataSource(bundle)
        observations = ds.retrieve("Observation")

        assert len(observations) == 2

    def test_resolve_reference_from_bundle(self) -> None:
        """Test resolving references within a bundle."""
        bundle = {
            "resourceType": "Bundle",
            "entry": [
                {"resource": {"resourceType": "Patient", "id": "p1"}},
            ],
        }

        ds = BundleDataSource(bundle)
        patient = ds.resolve_reference("Patient/p1")

        assert patient is not None
        assert patient["id"] == "p1"


class TestPatientBundleDataSource:
    """Tests for PatientBundleDataSource."""

    def test_extract_patient(self) -> None:
        """Test automatic patient extraction from bundle."""
        bundle = {
            "resourceType": "Bundle",
            "entry": [
                {"resource": {"resourceType": "Patient", "id": "p1", "name": [{"family": "Smith"}]}},
                {"resource": {"resourceType": "Condition", "id": "c1", "subject": {"reference": "Patient/p1"}}},
            ],
        }

        ds = PatientBundleDataSource(bundle)

        assert ds.patient is not None
        assert ds.patient["id"] == "p1"

    def test_automatic_patient_filtering(self) -> None:
        """Test that retrieval is automatically filtered to the patient."""
        bundle = {
            "resourceType": "Bundle",
            "entry": [
                {"resource": {"resourceType": "Patient", "id": "p1"}},
                {"resource": {"resourceType": "Condition", "id": "c1", "subject": {"reference": "Patient/p1"}}},
                {"resource": {"resourceType": "Condition", "id": "c2", "subject": {"reference": "Patient/p2"}}},
            ],
        }

        ds = PatientBundleDataSource(bundle)
        conditions = ds.retrieve("Condition")

        # Should only get conditions for patient p1
        assert len(conditions) == 1
        assert conditions[0]["id"] == "c1"


class TestDataSourceIntegration:
    """Integration tests for data sources with CQL evaluator."""

    def test_retrieve_with_evaluator(self) -> None:
        """Test CQL retrieve with data source."""
        # Set up data source
        ds = InMemoryDataSource()
        ds.add_resources(
            [
                {"resourceType": "Patient", "id": "p1", "birthDate": "1990-01-01"},
                {
                    "resourceType": "Condition",
                    "id": "c1",
                    "subject": {"reference": "Patient/p1"},
                    "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]},
                },
            ]
        )

        # Create evaluator with data source
        evaluator = CQLEvaluator(data_source=ds)

        # Compile library with retrieve
        evaluator.compile("""
            library RetrieveTest version '1.0'
            using FHIR version '4.0.1'

            context Patient

            define AllConditions: [Condition]
        """)

        # Evaluate with patient context
        patient = {"resourceType": "Patient", "id": "p1"}
        conditions = evaluator.evaluate_definition("AllConditions", resource=patient)

        assert isinstance(conditions, list)
        assert len(conditions) == 1

    def test_retrieve_with_bundle(self) -> None:
        """Test CQL retrieve with bundle data source."""
        bundle = {
            "resourceType": "Bundle",
            "entry": [
                {"resource": {"resourceType": "Patient", "id": "p1", "birthDate": "1990-01-01"}},
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "o1",
                        "subject": {"reference": "Patient/p1"},
                        "code": {"coding": [{"system": "http://loinc.org", "code": "2339-0"}]},
                        "valueQuantity": {"value": 100, "unit": "mg/dL"},
                    }
                },
            ],
        }

        ds = BundleDataSource(bundle)
        evaluator = CQLEvaluator(data_source=ds)

        evaluator.compile("""
            library BundleTest version '1.0'
            using FHIR version '4.0.1'

            context Patient

            define Observations: [Observation]
        """)

        patient = {"resourceType": "Patient", "id": "p1"}
        observations = evaluator.evaluate_definition("Observations", resource=patient)

        assert isinstance(observations, list)
        assert len(observations) == 1
        assert observations[0]["id"] == "o1"


class TestNestedValueAccess:
    """Tests for nested value access in data sources."""

    def test_get_nested_value_simple(self) -> None:
        """Test getting a simple nested value."""
        ds = InMemoryDataSource()
        resource = {"patient": {"name": "John"}}

        value = ds._get_nested_value(resource, "patient.name")

        assert value == "John"

    def test_get_nested_value_array_index(self) -> None:
        """Test getting a value from array by index."""
        ds = InMemoryDataSource()
        resource = {"name": [{"family": "Smith"}, {"family": "Jones"}]}

        value = ds._get_nested_value(resource, "name.0.family")

        assert value == "Smith"

    def test_get_nested_value_array_property(self) -> None:
        """Test getting property from all array elements."""
        ds = InMemoryDataSource()
        resource = {"name": [{"family": "Smith"}, {"family": "Jones"}]}

        value = ds._get_nested_value(resource, "name.family")

        assert value == ["Smith", "Jones"]

    def test_get_nested_value_missing(self) -> None:
        """Test getting a missing nested value."""
        ds = InMemoryDataSource()
        resource = {"patient": {}}

        value = ds._get_nested_value(resource, "patient.name.family")

        assert value is None


class TestCodeMatching:
    """Tests for code matching in data sources."""

    def test_matches_code_with_cql_code(self) -> None:
        """Test matching with CQLCode."""
        ds = InMemoryDataSource()
        resource = {"code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]}}

        code = CQLCode(code="44054006", system="http://snomed.info/sct")

        assert ds._matches_code(resource, "code", codes=[code])

    def test_matches_code_no_match(self) -> None:
        """Test code that doesn't match."""
        ds = InMemoryDataSource()
        resource = {"code": {"coding": [{"system": "http://snomed.info/sct", "code": "OTHER"}]}}

        code = CQLCode(code="44054006", system="http://snomed.info/sct")

        assert not ds._matches_code(resource, "code", codes=[code])

    def test_matches_code_with_string(self) -> None:
        """Test matching with simple string code."""
        ds = InMemoryDataSource()
        resource = {"code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]}}

        assert ds._matches_code(resource, "code", codes=["44054006"])

    def test_matches_code_multiple_codings(self) -> None:
        """Test matching with multiple codings in CodeableConcept."""
        ds = InMemoryDataSource()
        resource = {
            "code": {
                "coding": [
                    {"system": "http://icd10.info", "code": "E11"},
                    {"system": "http://snomed.info/sct", "code": "44054006"},
                ]
            }
        }

        code = CQLCode(code="44054006", system="http://snomed.info/sct")

        assert ds._matches_code(resource, "code", codes=[code])


class TestPatientReference:
    """Tests for patient reference extraction."""

    def test_get_patient_reference_condition(self) -> None:
        """Test getting patient reference from Condition."""
        ds = InMemoryDataSource()
        resource = {
            "resourceType": "Condition",
            "subject": {"reference": "Patient/123"},
        }

        ref = ds._get_patient_reference(resource)

        assert ref == "Patient/123"

    def test_get_patient_reference_observation(self) -> None:
        """Test getting patient reference from Observation."""
        ds = InMemoryDataSource()
        resource = {
            "resourceType": "Observation",
            "subject": {"reference": "Patient/456"},
        }

        ref = ds._get_patient_reference(resource)

        assert ref == "Patient/456"

    def test_get_patient_reference_allergy(self) -> None:
        """Test getting patient reference from AllergyIntolerance."""
        ds = InMemoryDataSource()
        resource = {
            "resourceType": "AllergyIntolerance",
            "patient": {"reference": "Patient/789"},
        }

        ref = ds._get_patient_reference(resource)

        assert ref == "Patient/789"

    def test_get_patient_reference_missing(self) -> None:
        """Test getting patient reference when missing."""
        ds = InMemoryDataSource()
        resource = {
            "resourceType": "Condition",
        }

        ref = ds._get_patient_reference(resource)

        assert ref is None
