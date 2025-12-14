"""Tests for terminology service."""

import pytest

from fhirkit.terminology import (
    InMemoryTerminologyService,
    MemberOfRequest,
    SubsumesRequest,
    ValidateCodeRequest,
    ValueSet,
    ValueSetCompose,
    ValueSetComposeInclude,
    ValueSetComposeIncludeConcept,
    ValueSetExpansion,
    ValueSetExpansionContains,
)


@pytest.fixture
def service() -> InMemoryTerminologyService:
    """Create a service with test value sets."""
    service = InMemoryTerminologyService()

    # Add observation status value set
    obs_status_vs = ValueSet(
        url="http://hl7.org/fhir/ValueSet/observation-status",
        name="ObservationStatus",
        compose=ValueSetCompose(
            include=[
                ValueSetComposeInclude(
                    system="http://hl7.org/fhir/observation-status",
                    concept=[
                        ValueSetComposeIncludeConcept(code="registered", display="Registered"),
                        ValueSetComposeIncludeConcept(code="preliminary", display="Preliminary"),
                        ValueSetComposeIncludeConcept(code="final", display="Final"),
                        ValueSetComposeIncludeConcept(code="amended", display="Amended"),
                    ],
                )
            ]
        ),
    )
    service.add_value_set(obs_status_vs)

    # Add expanded value set
    gender_vs = ValueSet(
        url="http://hl7.org/fhir/ValueSet/administrative-gender",
        name="AdministrativeGender",
        expansion=ValueSetExpansion(
            contains=[
                ValueSetExpansionContains(
                    system="http://hl7.org/fhir/administrative-gender",
                    code="male",
                    display="Male",
                ),
                ValueSetExpansionContains(
                    system="http://hl7.org/fhir/administrative-gender",
                    code="female",
                    display="Female",
                ),
                ValueSetExpansionContains(
                    system="http://hl7.org/fhir/administrative-gender",
                    code="other",
                    display="Other",
                ),
                ValueSetExpansionContains(
                    system="http://hl7.org/fhir/administrative-gender",
                    code="unknown",
                    display="Unknown",
                ),
            ]
        ),
    )
    service.add_value_set(gender_vs)

    return service


class TestValidateCode:
    """Test $validate-code operation."""

    def test_validate_code_in_compose(self, service):
        request = ValidateCodeRequest(
            url="http://hl7.org/fhir/ValueSet/observation-status",
            code="final",
            system="http://hl7.org/fhir/observation-status",
        )
        result = service.validate_code(request)
        assert result.result is True

    def test_validate_code_not_in_valueset(self, service):
        request = ValidateCodeRequest(
            url="http://hl7.org/fhir/ValueSet/observation-status",
            code="invalid-code",
            system="http://hl7.org/fhir/observation-status",
        )
        result = service.validate_code(request)
        assert result.result is False

    def test_validate_code_in_expansion(self, service):
        request = ValidateCodeRequest(
            url="http://hl7.org/fhir/ValueSet/administrative-gender",
            code="male",
            system="http://hl7.org/fhir/administrative-gender",
        )
        result = service.validate_code(request)
        assert result.result is True

    def test_validate_code_wrong_system(self, service):
        request = ValidateCodeRequest(
            url="http://hl7.org/fhir/ValueSet/observation-status",
            code="final",
            system="http://wrong-system.org",
        )
        result = service.validate_code(request)
        assert result.result is False

    def test_validate_code_without_system(self, service):
        # Should match if code exists in any system within the value set
        request = ValidateCodeRequest(
            url="http://hl7.org/fhir/ValueSet/observation-status",
            code="final",
        )
        result = service.validate_code(request)
        assert result.result is True

    def test_validate_valueset_not_found(self, service):
        request = ValidateCodeRequest(
            url="http://nonexistent/ValueSet",
            code="some-code",
        )
        result = service.validate_code(request)
        assert result.result is False
        assert result.message == "Value set not found"


class TestMemberOf:
    """Test memberOf operation."""

    def test_member_of_true(self, service):
        request = MemberOfRequest(
            code="final",
            system="http://hl7.org/fhir/observation-status",
            valueSetUrl="http://hl7.org/fhir/ValueSet/observation-status",
        )
        result = service.member_of(request)
        assert result.result is True

    def test_member_of_false(self, service):
        request = MemberOfRequest(
            code="invalid",
            system="http://hl7.org/fhir/observation-status",
            valueSetUrl="http://hl7.org/fhir/ValueSet/observation-status",
        )
        result = service.member_of(request)
        assert result.result is False

    def test_member_of_valueset_not_found(self, service):
        request = MemberOfRequest(
            code="final",
            system="http://hl7.org/fhir/observation-status",
            valueSetUrl="http://nonexistent/ValueSet",
        )
        result = service.member_of(request)
        assert result.result is False


class TestSubsumes:
    """Test $subsumes operation."""

    def test_subsumes_equivalent(self, service):
        request = SubsumesRequest(
            codeA="final",
            codeB="final",
            system="http://hl7.org/fhir/observation-status",
        )
        result = service.subsumes(request)
        assert result.outcome == "equivalent"

    def test_subsumes_not_subsumed(self, service):
        request = SubsumesRequest(
            codeA="final",
            codeB="preliminary",
            system="http://hl7.org/fhir/observation-status",
        )
        result = service.subsumes(request)
        assert result.outcome == "not-subsumed"


class TestValueSetRetrieval:
    """Test value set retrieval."""

    def test_get_value_set(self, service):
        vs = service.get_value_set("http://hl7.org/fhir/ValueSet/observation-status")
        assert vs is not None
        assert vs.name == "ObservationStatus"

    def test_get_value_set_not_found(self, service):
        vs = service.get_value_set("http://nonexistent/ValueSet")
        assert vs is None

    def test_get_value_set_with_version(self, service):
        """Test retrieving value set by URL and version."""
        # Add a versioned value set
        vs = ValueSet(
            url="http://example.org/ValueSet/test",
            version="2.0.0",
            name="TestValueSet",
        )
        service.add_value_set(vs)

        # Should be retrievable by URL|version
        result = service.get_value_set("http://example.org/ValueSet/test", "2.0.0")
        assert result is not None
        assert result.version == "2.0.0"


class TestCodingValidation:
    """Test validation with Coding objects."""

    def test_validate_with_coding(self, service):
        """Test validate code with Coding input."""
        from fhirkit.terminology import Coding

        request = ValidateCodeRequest(
            url="http://hl7.org/fhir/ValueSet/observation-status",
            coding=Coding(
                system="http://hl7.org/fhir/observation-status",
                code="final",
                display="Final",
            ),
        )
        result = service.validate_code(request)
        assert result.result is True

    def test_validate_with_coding_invalid(self, service):
        """Test validate code with invalid Coding."""
        from fhirkit.terminology import Coding

        request = ValidateCodeRequest(
            url="http://hl7.org/fhir/ValueSet/observation-status",
            coding=Coding(
                system="http://hl7.org/fhir/observation-status",
                code="invalid",
            ),
        )
        result = service.validate_code(request)
        assert result.result is False


class TestCodeableConceptValidation:
    """Test validation with CodeableConcept objects."""

    def test_validate_with_codeable_concept(self, service):
        """Test validate code with CodeableConcept input."""
        from fhirkit.terminology import CodeableConcept, Coding

        request = ValidateCodeRequest(
            url="http://hl7.org/fhir/ValueSet/observation-status",
            codeableConcept=CodeableConcept(
                coding=[
                    Coding(
                        system="http://hl7.org/fhir/observation-status",
                        code="final",
                    ),
                ]
            ),
        )
        result = service.validate_code(request)
        assert result.result is True

    def test_validate_with_codeable_concept_multiple_codings(self, service):
        """Test validate code with CodeableConcept with multiple codings."""
        from fhirkit.terminology import CodeableConcept, Coding

        request = ValidateCodeRequest(
            url="http://hl7.org/fhir/ValueSet/observation-status",
            codeableConcept=CodeableConcept(
                coding=[
                    Coding(system="http://other-system", code="unknown"),
                    Coding(
                        system="http://hl7.org/fhir/observation-status",
                        code="final",
                    ),
                ]
            ),
        )
        result = service.validate_code(request)
        assert result.result is True  # At least one coding matches

    def test_validate_with_codeable_concept_none_match(self, service):
        """Test validate code with CodeableConcept where no codings match."""
        from fhirkit.terminology import CodeableConcept, Coding

        request = ValidateCodeRequest(
            url="http://hl7.org/fhir/ValueSet/observation-status",
            codeableConcept=CodeableConcept(
                coding=[
                    Coding(system="http://other-system", code="unknown"),
                    Coding(system="http://wrong-system", code="invalid"),
                ]
            ),
        )
        result = service.validate_code(request)
        assert result.result is False


class TestInlineValueSet:
    """Test validation with inline ValueSet."""

    def test_validate_with_inline_valueset(self, service):
        """Test validate code with inline ValueSet."""
        inline_vs = ValueSet(
            name="InlineTest",
            compose=ValueSetCompose(
                include=[
                    ValueSetComposeInclude(
                        system="http://test-system",
                        concept=[
                            ValueSetComposeIncludeConcept(code="ABC", display="Alpha"),
                            ValueSetComposeIncludeConcept(code="DEF", display="Delta"),
                        ],
                    )
                ]
            ),
        )
        request = ValidateCodeRequest(
            valueSet=inline_vs,
            code="ABC",
            system="http://test-system",
        )
        result = service.validate_code(request)
        assert result.result is True


class TestFileLoading:
    """Test loading value sets from files."""

    def test_load_valueset_from_json(self, tmp_path):
        """Test loading value set from JSON data."""
        service = InMemoryTerminologyService()
        json_data = {
            "resourceType": "ValueSet",
            "url": "http://test.org/ValueSet/test",
            "name": "TestFromJson",
            "status": "active",
            "compose": {
                "include": [
                    {
                        "system": "http://test-system",
                        "concept": [{"code": "TEST", "display": "Test Code"}],
                    }
                ]
            },
        }
        service.add_value_set_from_json(json_data)

        vs = service.get_value_set("http://test.org/ValueSet/test")
        assert vs is not None
        assert vs.name == "TestFromJson"

    def test_load_valueset_from_file(self, tmp_path):
        """Test loading value set from file."""
        import json

        service = InMemoryTerminologyService()
        vs_file = tmp_path / "test_valueset.json"
        vs_file.write_text(
            json.dumps(
                {
                    "resourceType": "ValueSet",
                    "url": "http://file.org/ValueSet/test",
                    "name": "TestFromFile",
                    "status": "active",
                }
            )
        )

        service.load_value_set_file(vs_file)
        vs = service.get_value_set("http://file.org/ValueSet/test")
        assert vs is not None
        assert vs.name == "TestFromFile"

    def test_load_valuesets_from_directory(self, tmp_path):
        """Test loading multiple value sets from directory."""
        import json

        service = InMemoryTerminologyService()

        # Create multiple value set files
        for i in range(3):
            vs_file = tmp_path / f"valueset_{i}.json"
            vs_file.write_text(
                json.dumps(
                    {
                        "resourceType": "ValueSet",
                        "url": f"http://dir.org/ValueSet/test-{i}",
                        "name": f"TestValueSet{i}",
                        "status": "active",
                    }
                )
            )

        count = service.load_value_sets_from_directory(tmp_path)
        assert count == 3

        for i in range(3):
            vs = service.get_value_set(f"http://dir.org/ValueSet/test-{i}")
            assert vs is not None

    def test_load_from_nonexistent_file(self, tmp_path):
        """Test loading from non-existent file does not raise error."""
        service = InMemoryTerminologyService()
        service.load_value_set_file(tmp_path / "nonexistent.json")
        # Should not raise, just skip

    def test_load_from_nonexistent_directory(self, tmp_path):
        """Test loading from non-existent directory returns 0."""
        service = InMemoryTerminologyService()
        count = service.load_value_sets_from_directory(tmp_path / "nonexistent")
        assert count == 0


class TestNoCodeProvided:
    """Test edge cases with no code provided."""

    def test_validate_without_code(self, service):
        """Test validate code request without any code."""
        request = ValidateCodeRequest(
            url="http://hl7.org/fhir/ValueSet/observation-status",
        )
        result = service.validate_code(request)
        assert result.result is False
        assert "No code provided" in result.message
