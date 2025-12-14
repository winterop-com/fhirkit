"""Tests for FHIR server terminology operations."""

import pytest
from fastapi.testclient import TestClient

from fhirkit.server.api.app import create_app
from fhirkit.server.config.settings import FHIRServerSettings
from fhirkit.server.storage.fhir_store import FHIRStore


@pytest.fixture
def store():
    """Create a fresh FHIR store for testing."""
    return FHIRStore()


@pytest.fixture
def client(store):
    """Create a test client with the FHIR app."""
    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings, store=store)
    return TestClient(app)


@pytest.fixture
def store_with_terminology(store, client):
    """Populate store with test terminology resources."""
    # Create a hierarchical CodeSystem
    codesystem = {
        "resourceType": "CodeSystem",
        "id": "test-codesystem",
        "url": "http://example.org/fhir/CodeSystem/test",
        "name": "TestCodeSystem",
        "status": "active",
        "concept": [
            {
                "code": "A",
                "display": "Category A",
                "concept": [
                    {"code": "A1", "display": "Subcategory A1"},
                    {"code": "A2", "display": "Subcategory A2"},
                ],
            },
            {
                "code": "B",
                "display": "Category B",
                "definition": "This is category B",
            },
        ],
    }
    client.put("/CodeSystem/test-codesystem", json=codesystem)

    # Create a ValueSet with compose
    valueset = {
        "resourceType": "ValueSet",
        "id": "test-valueset",
        "url": "http://example.org/fhir/ValueSet/test",
        "name": "TestValueSet",
        "status": "active",
        "compose": {
            "include": [
                {
                    "system": "http://example.org/fhir/CodeSystem/test",
                    "concept": [
                        {"code": "A1", "display": "Subcategory A1"},
                        {"code": "B", "display": "Category B"},
                    ],
                }
            ]
        },
    }
    client.put("/ValueSet/test-valueset", json=valueset)

    # Create a ValueSet that references entire CodeSystem
    valueset_full = {
        "resourceType": "ValueSet",
        "id": "test-valueset-full",
        "url": "http://example.org/fhir/ValueSet/test-full",
        "name": "TestValueSetFull",
        "status": "active",
        "compose": {
            "include": [
                {
                    "system": "http://example.org/fhir/CodeSystem/test",
                    # No concepts - should expand from CodeSystem
                }
            ]
        },
    }
    client.put("/ValueSet/test-valueset-full", json=valueset_full)

    return store


class TestSubsumesOperation:
    """Tests for $subsumes operation."""

    def test_subsumes_equivalent(self, client, store_with_terminology):
        """Test that same codes are equivalent."""
        response = client.get("/CodeSystem/$subsumes?system=http://example.org/fhir/CodeSystem/test&codeA=A&codeB=A")
        assert response.status_code == 200
        result = response.json()
        assert result["resourceType"] == "Parameters"
        outcome = next(p for p in result["parameter"] if p["name"] == "outcome")
        assert outcome["valueCode"] == "equivalent"

    def test_subsumes_parent_child(self, client, store_with_terminology):
        """Test that parent subsumes child."""
        response = client.get("/CodeSystem/$subsumes?system=http://example.org/fhir/CodeSystem/test&codeA=A&codeB=A1")
        assert response.status_code == 200
        result = response.json()
        outcome = next(p for p in result["parameter"] if p["name"] == "outcome")
        assert outcome["valueCode"] == "subsumes"

    def test_subsumes_child_parent(self, client, store_with_terminology):
        """Test that child is subsumed-by parent."""
        response = client.get("/CodeSystem/$subsumes?system=http://example.org/fhir/CodeSystem/test&codeA=A1&codeB=A")
        assert response.status_code == 200
        result = response.json()
        outcome = next(p for p in result["parameter"] if p["name"] == "outcome")
        assert outcome["valueCode"] == "subsumed-by"

    def test_subsumes_not_related(self, client, store_with_terminology):
        """Test unrelated codes."""
        response = client.get("/CodeSystem/$subsumes?system=http://example.org/fhir/CodeSystem/test&codeA=A&codeB=B")
        assert response.status_code == 200
        result = response.json()
        outcome = next(p for p in result["parameter"] if p["name"] == "outcome")
        assert outcome["valueCode"] == "not-subsumed"

    def test_subsumes_by_id(self, client, store_with_terminology):
        """Test $subsumes on specific CodeSystem by ID."""
        response = client.get("/CodeSystem/test-codesystem/$subsumes?codeA=A&codeB=A1")
        assert response.status_code == 200
        result = response.json()
        outcome = next(p for p in result["parameter"] if p["name"] == "outcome")
        assert outcome["valueCode"] == "subsumes"

    def test_subsumes_missing_params(self, client, store_with_terminology):
        """Test error when parameters are missing."""
        response = client.get("/CodeSystem/$subsumes?system=http://example.org/fhir/CodeSystem/test")
        assert response.status_code == 400

    def test_subsumes_post(self, client, store_with_terminology):
        """Test $subsumes via POST."""
        response = client.post(
            "/CodeSystem/$subsumes",
            json={
                "resourceType": "Parameters",
                "parameter": [
                    {"name": "system", "valueUri": "http://example.org/fhir/CodeSystem/test"},
                    {"name": "codeA", "valueCode": "A"},
                    {"name": "codeB", "valueCode": "A2"},
                ],
            },
        )
        assert response.status_code == 200
        result = response.json()
        outcome = next(p for p in result["parameter"] if p["name"] == "outcome")
        assert outcome["valueCode"] == "subsumes"


class TestExpandOperation:
    """Tests for enhanced $expand operation."""

    def test_expand_by_url(self, client, store_with_terminology):
        """Test $expand by ValueSet URL."""
        response = client.get("/ValueSet/$expand?url=http://example.org/fhir/ValueSet/test")
        assert response.status_code == 200
        result = response.json()
        assert result["resourceType"] == "ValueSet"
        assert "expansion" in result
        assert result["expansion"]["total"] == 2

    def test_expand_by_id(self, client, store_with_terminology):
        """Test $expand by ValueSet ID."""
        response = client.get("/ValueSet/test-valueset/$expand")
        assert response.status_code == 200
        result = response.json()
        assert result["expansion"]["total"] == 2

    def test_expand_with_filter(self, client, store_with_terminology):
        """Test $expand with filter parameter."""
        response = client.get("/ValueSet/$expand?url=http://example.org/fhir/ValueSet/test&filter=A1")
        assert response.status_code == 200
        result = response.json()
        # Should only match A1
        assert result["expansion"]["total"] == 1
        assert result["expansion"]["contains"][0]["code"] == "A1"

    def test_expand_codesystem_reference(self, client, store_with_terminology):
        """Test $expand when ValueSet references entire CodeSystem."""
        response = client.get("/ValueSet/$expand?url=http://example.org/fhir/ValueSet/test-full")
        assert response.status_code == 200
        result = response.json()
        # Should include all codes from CodeSystem (A, A1, A2, B)
        assert result["expansion"]["total"] == 4
        codes = {c["code"] for c in result["expansion"]["contains"]}
        assert codes == {"A", "A1", "A2", "B"}

    def test_expand_not_found(self, client, store_with_terminology):
        """Test $expand for non-existent ValueSet."""
        response = client.get("/ValueSet/$expand?url=http://example.org/nonexistent")
        assert response.status_code == 404


class TestLookupOperation:
    """Tests for enhanced $lookup operation."""

    def test_lookup_top_level_code(self, client, store_with_terminology):
        """Test $lookup for top-level code."""
        response = client.get("/CodeSystem/$lookup?system=http://example.org/fhir/CodeSystem/test&code=A")
        assert response.status_code == 200
        result = response.json()
        display = next(p for p in result["parameter"] if p["name"] == "display")
        assert display["valueString"] == "Category A"

    def test_lookup_nested_code(self, client, store_with_terminology):
        """Test $lookup finds codes in hierarchy."""
        response = client.get("/CodeSystem/$lookup?system=http://example.org/fhir/CodeSystem/test&code=A1")
        assert response.status_code == 200
        result = response.json()
        display = next(p for p in result["parameter"] if p["name"] == "display")
        assert display["valueString"] == "Subcategory A1"

    def test_lookup_with_definition(self, client, store_with_terminology):
        """Test $lookup returns definition."""
        response = client.get("/CodeSystem/$lookup?system=http://example.org/fhir/CodeSystem/test&code=B")
        assert response.status_code == 200
        result = response.json()
        definition = next((p for p in result["parameter"] if p["name"] == "definition"), None)
        assert definition is not None
        assert definition["valueString"] == "This is category B"

    def test_lookup_not_found(self, client, store_with_terminology):
        """Test $lookup for non-existent code."""
        response = client.get("/CodeSystem/$lookup?system=http://example.org/fhir/CodeSystem/test&code=NOTFOUND")
        assert response.status_code == 404


class TestValidateCodeOperation:
    """Tests for enhanced $validate-code operation."""

    def test_validate_code_found(self, client, store_with_terminology):
        """Test $validate-code for valid code."""
        response = client.get(
            "/ValueSet/$validate-code"
            "?url=http://example.org/fhir/ValueSet/test"
            "&code=A1"
            "&system=http://example.org/fhir/CodeSystem/test"
        )
        assert response.status_code == 200
        result = response.json()
        is_valid = next(p for p in result["parameter"] if p["name"] == "result")
        assert is_valid["valueBoolean"] is True

    def test_validate_code_not_found(self, client, store_with_terminology):
        """Test $validate-code for invalid code."""
        response = client.get("/ValueSet/$validate-code?url=http://example.org/fhir/ValueSet/test&code=NOTFOUND")
        assert response.status_code == 200
        result = response.json()
        is_valid = next(p for p in result["parameter"] if p["name"] == "result")
        assert is_valid["valueBoolean"] is False

    def test_validate_code_with_coding(self, client, store_with_terminology):
        """Test $validate-code with Coding input."""
        response = client.post(
            "/ValueSet/$validate-code",
            json={
                "resourceType": "Parameters",
                "parameter": [
                    {"name": "url", "valueUri": "http://example.org/fhir/ValueSet/test"},
                    {
                        "name": "coding",
                        "valueCoding": {
                            "system": "http://example.org/fhir/CodeSystem/test",
                            "code": "B",
                        },
                    },
                ],
            },
        )
        assert response.status_code == 200
        result = response.json()
        is_valid = next(p for p in result["parameter"] if p["name"] == "result")
        assert is_valid["valueBoolean"] is True

    def test_validate_code_with_codeable_concept(self, client, store_with_terminology):
        """Test $validate-code with CodeableConcept input."""
        response = client.post(
            "/ValueSet/$validate-code",
            json={
                "resourceType": "Parameters",
                "parameter": [
                    {"name": "url", "valueUri": "http://example.org/fhir/ValueSet/test"},
                    {
                        "name": "codeableConcept",
                        "valueCodeableConcept": {
                            "coding": [
                                {"system": "http://other", "code": "WRONG"},
                                {"system": "http://example.org/fhir/CodeSystem/test", "code": "A1"},
                            ]
                        },
                    },
                ],
            },
        )
        assert response.status_code == 200
        result = response.json()
        is_valid = next(p for p in result["parameter"] if p["name"] == "result")
        assert is_valid["valueBoolean"] is True  # A1 should match


class TestMemberOfOperation:
    """Tests for memberOf convenience endpoint."""

    def test_member_of_true(self, client, store_with_terminology):
        """Test memberOf returns true for valid member."""
        response = client.get(
            "/terminology/memberOf"
            "?code=A1"
            "&system=http://example.org/fhir/CodeSystem/test"
            "&valueSetUrl=http://example.org/fhir/ValueSet/test"
        )
        assert response.status_code == 200
        result = response.json()
        is_member = next(p for p in result["parameter"] if p["name"] == "result")
        assert is_member["valueBoolean"] is True

    def test_member_of_false(self, client, store_with_terminology):
        """Test memberOf returns false for non-member."""
        response = client.get(
            "/terminology/memberOf"
            "?code=A2"
            "&system=http://example.org/fhir/CodeSystem/test"
            "&valueSetUrl=http://example.org/fhir/ValueSet/test"
        )
        assert response.status_code == 200
        result = response.json()
        is_member = next(p for p in result["parameter"] if p["name"] == "result")
        assert is_member["valueBoolean"] is False  # A2 not in the ValueSet


class TestTerminologyProvider:
    """Tests for terminology provider directly."""

    def test_provider_expand_codes_from_codesystem(self, store_with_terminology):
        """Test that provider expands codes from CodeSystem correctly."""
        from fhirkit.server.terminology import FHIRStoreTerminologyProvider

        provider = FHIRStoreTerminologyProvider(store_with_terminology)
        result = provider.expand_valueset(url="http://example.org/fhir/ValueSet/test-full")

        assert result is not None
        codes = {c["code"] for c in result["expansion"]["contains"]}
        assert "A" in codes
        assert "A1" in codes
        assert "A2" in codes
        assert "B" in codes

    def test_provider_hierarchy_building(self, store_with_terminology):
        """Test that hierarchy is built correctly."""
        from fhirkit.server.terminology import FHIRStoreTerminologyProvider

        provider = FHIRStoreTerminologyProvider(store_with_terminology)

        # A should subsume A1
        result = provider.subsumes("http://example.org/fhir/CodeSystem/test", "A", "A1")
        outcome = next(p for p in result["parameter"] if p["name"] == "outcome")
        assert outcome["valueCode"] == "subsumes"

        # A1 should be subsumed-by A
        result = provider.subsumes("http://example.org/fhir/CodeSystem/test", "A1", "A")
        outcome = next(p for p in result["parameter"] if p["name"] == "outcome")
        assert outcome["valueCode"] == "subsumed-by"
