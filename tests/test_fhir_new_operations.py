"""Tests for new FHIR operations ($translate, $match, $document)."""

import pytest
from fastapi.testclient import TestClient

from fhir_cql.server.api.app import create_app
from fhir_cql.server.config.settings import FHIRServerSettings
from fhir_cql.server.generator import CompositionGenerator, ConceptMapGenerator
from fhir_cql.server.operations import ConceptMapTranslator, DocumentGenerator, PatientMatcher
from fhir_cql.server.storage.fhir_store import FHIRStore


@pytest.fixture
def store_with_concept_maps() -> FHIRStore:
    """Create store with ConceptMap resources for translation tests."""
    store = FHIRStore()

    # Create a SNOMED to ICD-10 ConceptMap
    store.create(
        {
            "resourceType": "ConceptMap",
            "id": "snomed-to-icd10",
            "url": "http://example.org/fhir/ConceptMap/snomed-to-icd10",
            "status": "active",
            "sourceUri": "http://snomed.info/sct",
            "targetUri": "http://hl7.org/fhir/sid/icd-10-cm",
            "group": [
                {
                    "source": "http://snomed.info/sct",
                    "target": "http://hl7.org/fhir/sid/icd-10-cm",
                    "element": [
                        {
                            "code": "73211009",
                            "display": "Diabetes mellitus",
                            "target": [
                                {
                                    "code": "E11.9",
                                    "display": "Type 2 diabetes mellitus without complications",
                                    "equivalence": "equivalent",
                                }
                            ],
                        },
                        {
                            "code": "38341003",
                            "display": "Hypertensive disorder",
                            "target": [
                                {
                                    "code": "I10",
                                    "display": "Essential (primary) hypertension",
                                    "equivalence": "equivalent",
                                }
                            ],
                        },
                    ],
                }
            ],
        }
    )

    return store


@pytest.fixture
def store_with_patients() -> FHIRStore:
    """Create store with Patient resources for matching tests."""
    store = FHIRStore()

    # Create patients for matching
    store.create(
        {
            "resourceType": "Patient",
            "id": "patient-1",
            "identifier": [{"system": "http://example.org/mrn", "value": "MRN-12345"}],
            "name": [{"family": "Smith", "given": ["John"]}],
            "gender": "male",
            "birthDate": "1990-01-15",
            "telecom": [
                {"system": "phone", "value": "555-1234"},
                {"system": "email", "value": "john.smith@example.com"},
            ],
            "address": [{"postalCode": "12345"}],
        }
    )

    store.create(
        {
            "resourceType": "Patient",
            "id": "patient-2",
            "name": [{"family": "Smith", "given": ["Jonathan"]}],
            "gender": "male",
            "birthDate": "1990-01-15",
            "address": [{"postalCode": "12345"}],
        }
    )

    store.create(
        {
            "resourceType": "Patient",
            "id": "patient-3",
            "name": [{"family": "Doe", "given": ["Jane"]}],
            "gender": "female",
            "birthDate": "1985-06-20",
        }
    )

    return store


@pytest.fixture
def store_with_composition() -> FHIRStore:
    """Create store with Composition and related resources."""
    store = FHIRStore()

    # Create patient
    store.create(
        {
            "resourceType": "Patient",
            "id": "patient-1",
            "name": [{"family": "Smith", "given": ["John"]}],
        }
    )

    # Create practitioner
    store.create(
        {
            "resourceType": "Practitioner",
            "id": "practitioner-1",
            "name": [{"family": "Wilson", "given": ["Sarah"]}],
        }
    )

    # Create conditions
    store.create(
        {
            "resourceType": "Condition",
            "id": "condition-1",
            "subject": {"reference": "Patient/patient-1"},
            "code": {"text": "Hypertension"},
        }
    )

    # Create composition
    store.create(
        {
            "resourceType": "Composition",
            "id": "composition-1",
            "status": "final",
            "type": {"coding": [{"system": "http://loinc.org", "code": "11488-4"}]},
            "subject": {"reference": "Patient/patient-1"},
            "date": "2024-01-15",
            "author": [{"reference": "Practitioner/practitioner-1"}],
            "title": "Consultation Note",
            "section": [
                {
                    "title": "Problem List",
                    "code": {"coding": [{"system": "http://loinc.org", "code": "11450-4"}]},
                    "entry": [{"reference": "Condition/condition-1"}],
                }
            ],
        }
    )

    return store


@pytest.fixture
def translate_client(store_with_concept_maps: FHIRStore) -> TestClient:
    """Create test client for translate tests."""
    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings, store=store_with_concept_maps)
    return TestClient(app)


@pytest.fixture
def match_client(store_with_patients: FHIRStore) -> TestClient:
    """Create test client for match tests."""
    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings, store=store_with_patients)
    return TestClient(app)


@pytest.fixture
def document_client(store_with_composition: FHIRStore) -> TestClient:
    """Create test client for document tests."""
    settings = FHIRServerSettings(patients=0, enable_docs=False, enable_ui=False, api_base_path="")
    app = create_app(settings=settings, store=store_with_composition)
    return TestClient(app)


class TestConceptMapTranslate:
    """Tests for ConceptMap $translate operation."""

    def test_translate_snomed_to_icd10(self, translate_client: TestClient) -> None:
        """Test basic code translation."""
        response = translate_client.get(
            "/ConceptMap/$translate",
            params={
                "code": "73211009",
                "system": "http://snomed.info/sct",
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Parameters"

        # Find result parameter
        result_param = next(p for p in data["parameter"] if p["name"] == "result")
        assert result_param["valueBoolean"] is True

        # Find match parameter
        match_param = next(p for p in data["parameter"] if p["name"] == "match")
        concept_part = next(p for p in match_param["part"] if p["name"] == "concept")
        assert concept_part["valueCoding"]["code"] == "E11.9"

    def test_translate_code_not_found(self, translate_client: TestClient) -> None:
        """Test translation with unmapped code."""
        response = translate_client.get(
            "/ConceptMap/$translate",
            params={
                "code": "99999999",
                "system": "http://snomed.info/sct",
            },
        )
        assert response.status_code == 200

        data = response.json()
        result_param = next(p for p in data["parameter"] if p["name"] == "result")
        assert result_param["valueBoolean"] is False

    def test_translate_requires_code_and_system(self, translate_client: TestClient) -> None:
        """Test that code and system are required."""
        response = translate_client.get("/ConceptMap/$translate")
        assert response.status_code == 400

    def test_translate_by_conceptmap_id(self, translate_client: TestClient) -> None:
        """Test translation using specific ConceptMap ID."""
        response = translate_client.get(
            "/ConceptMap/snomed-to-icd10/$translate",
            params={
                "code": "38341003",
                "system": "http://snomed.info/sct",
            },
        )
        assert response.status_code == 200

        data = response.json()
        result_param = next(p for p in data["parameter"] if p["name"] == "result")
        assert result_param["valueBoolean"] is True


class TestPatientMatch:
    """Tests for Patient $match operation."""

    def test_match_exact_identifier(self, match_client: TestClient) -> None:
        """Test matching by exact identifier returns 100% match."""
        response = match_client.post(
            "/Patient/$match",
            json={
                "resourceType": "Patient",
                "identifier": [{"system": "http://example.org/mrn", "value": "MRN-12345"}],
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "searchset"
        assert data["total"] >= 1

        # First match should be exact (score = 1.0)
        first_match = data["entry"][0]
        assert first_match["search"]["score"] == 1.0

    def test_match_by_demographics(self, match_client: TestClient) -> None:
        """Test matching by demographics."""
        response = match_client.post(
            "/Patient/$match",
            json={
                "resourceType": "Patient",
                "name": [{"family": "Smith", "given": ["John"]}],
                "gender": "male",
                "birthDate": "1990-01-15",
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        # Should find at least 2 Smith patients
        assert data["total"] >= 1

    def test_match_no_matches(self, match_client: TestClient) -> None:
        """Test match with no matching patients."""
        response = match_client.post(
            "/Patient/$match",
            json={
                "resourceType": "Patient",
                "name": [{"family": "Nonexistent"}],
                "birthDate": "1800-01-01",
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["total"] == 0

    def test_match_with_parameters_wrapper(self, match_client: TestClient) -> None:
        """Test match with Parameters wrapper."""
        response = match_client.post(
            "/Patient/$match",
            json={
                "resourceType": "Parameters",
                "parameter": [
                    {
                        "name": "resource",
                        "resource": {
                            "resourceType": "Patient",
                            "name": [{"family": "Smith"}],
                        },
                    },
                    {"name": "count", "valueInteger": 5},
                ],
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"

    def test_match_requires_patient(self, match_client: TestClient) -> None:
        """Test that Patient resource is required."""
        response = match_client.post(
            "/Patient/$match",
            json={
                "resourceType": "Parameters",
                "parameter": [],
            },
        )
        assert response.status_code == 400


class TestCompositionDocument:
    """Tests for Composition $document operation."""

    def test_document_generation(self, document_client: TestClient) -> None:
        """Test basic document bundle generation."""
        response = document_client.get("/Composition/composition-1/$document")
        assert response.status_code == 200

        data = response.json()
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "document"

        # Check that entries exist
        assert len(data["entry"]) >= 1

        # First entry should be the Composition
        assert data["entry"][0]["resource"]["resourceType"] == "Composition"

        # Should include referenced resources
        resource_types = [e["resource"]["resourceType"] for e in data["entry"]]
        assert "Patient" in resource_types
        assert "Practitioner" in resource_types
        assert "Condition" in resource_types

    def test_document_not_found(self, document_client: TestClient) -> None:
        """Test $document with non-existent Composition."""
        response = document_client.get("/Composition/nonexistent/$document")
        assert response.status_code == 404


class TestConceptMapGenerator:
    """Tests for ConceptMap generator."""

    def test_generate_conceptmap(self) -> None:
        """Test basic ConceptMap generation."""
        gen = ConceptMapGenerator()
        cm = gen.generate()

        assert cm["resourceType"] == "ConceptMap"
        assert "id" in cm
        assert cm["status"] == "active"
        assert "group" in cm
        assert len(cm["group"]) > 0

    def test_generate_from_template(self) -> None:
        """Test generating from specific template."""
        gen = ConceptMapGenerator()
        cm = gen.generate(template_name="snomed-to-icd10")

        assert cm["sourceUri"] == "http://snomed.info/sct"
        assert cm["targetUri"] == "http://hl7.org/fhir/sid/icd-10-cm"

    def test_generate_all_templates(self) -> None:
        """Test generating all templates."""
        gen = ConceptMapGenerator()
        maps = gen.generate_all_templates()

        assert len(maps) == 3  # snomed-to-icd10, loinc-to-local, rxnorm-to-ndc


class TestCompositionGenerator:
    """Tests for Composition generator."""

    def test_generate_composition(self) -> None:
        """Test basic Composition generation."""
        gen = CompositionGenerator()
        comp = gen.generate(patient_ref="Patient/123")

        assert comp["resourceType"] == "Composition"
        assert "id" in comp
        assert comp["status"] == "final"
        assert comp["subject"]["reference"] == "Patient/123"
        assert "section" in comp
        assert len(comp["section"]) > 0

    def test_generate_discharge_summary(self) -> None:
        """Test discharge summary generation."""
        gen = CompositionGenerator()
        comp = gen.generate_discharge_summary(
            patient_ref="Patient/123",
            condition_refs=["Condition/c1", "Condition/c2"],
        )

        assert comp["type"]["coding"][0]["code"] == "18842-5"  # Discharge summary
        assert comp["subject"]["reference"] == "Patient/123"

    def test_generate_with_sections(self) -> None:
        """Test Composition with section references."""
        gen = CompositionGenerator()
        # Use discharge summary which includes the problem list section
        comp = gen.generate_discharge_summary(
            patient_ref="Patient/123",
            condition_refs=["Condition/c1", "Condition/c2"],
        )

        # Find problem list section (11450-4)
        problem_section = next(
            (
                s
                for s in comp["section"]
                if any(c.get("code") == "11450-4" for c in s.get("code", {}).get("coding", []))
            ),
            None,
        )

        assert problem_section is not None
        assert len(problem_section.get("entry", [])) == 2


class TestPatientMatcherUnit:
    """Unit tests for PatientMatcher."""

    def test_identifier_match_returns_1(self) -> None:
        """Test that exact identifier match returns score of 1.0."""
        store = FHIRStore()
        store.create(
            {
                "resourceType": "Patient",
                "id": "p1",
                "identifier": [{"system": "mrn", "value": "123"}],
            }
        )

        matcher = PatientMatcher(store)
        result = matcher.match({"resourceType": "Patient", "identifier": [{"system": "mrn", "value": "123"}]})

        assert len(result["entry"]) == 1
        assert result["entry"][0]["search"]["score"] == 1.0

    def test_match_grade_thresholds(self) -> None:
        """Test match grade assignment."""
        store = FHIRStore()
        matcher = PatientMatcher(store)

        # Test grade thresholds
        assert matcher._get_match_grade(0.96) == "certain"
        assert matcher._get_match_grade(0.85) == "probable"
        assert matcher._get_match_grade(0.65) == "possible"
        assert matcher._get_match_grade(0.40) == "certainly-not"


class TestConceptMapTranslatorUnit:
    """Unit tests for ConceptMapTranslator."""

    def test_no_conceptmaps_returns_not_found(self) -> None:
        """Test translation with no ConceptMaps."""
        store = FHIRStore()
        translator = ConceptMapTranslator(store)

        result = translator.translate(
            code="123",
            system="http://example.org",
        )

        result_param = next(p for p in result["parameter"] if p["name"] == "result")
        assert result_param["valueBoolean"] is False


class TestDocumentGeneratorUnit:
    """Unit tests for DocumentGenerator."""

    def test_generate_from_composition(self) -> None:
        """Test document generation from Composition."""
        store = FHIRStore()
        store.create(
            {
                "resourceType": "Patient",
                "id": "p1",
                "name": [{"family": "Test"}],
            }
        )

        composition = {
            "resourceType": "Composition",
            "id": "c1",
            "status": "final",
            "subject": {"reference": "Patient/p1"},
            "author": [],
            "section": [],
        }

        generator = DocumentGenerator(store)
        document = generator.generate_document(composition, persist=False)

        assert document["resourceType"] == "Bundle"
        assert document["type"] == "document"
        assert len(document["entry"]) >= 2  # Composition + Patient
