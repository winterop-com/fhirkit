"""Tests for Questionnaire and QuestionnaireResponse generators."""

from fhirkit.server.generator.questionnaire import QuestionnaireGenerator
from fhirkit.server.generator.questionnaire_response import QuestionnaireResponseGenerator


class TestQuestionnaireGenerator:
    """Tests for QuestionnaireGenerator."""

    def test_generate_default(self):
        """Test generating a questionnaire with defaults."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate()

        assert q["resourceType"] == "Questionnaire"
        assert "id" in q
        assert q["status"] == "active"
        assert "item" in q
        assert len(q["item"]) > 0

    def test_generate_with_id(self):
        """Test generating with specific ID."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(questionnaire_id="test-123")

        assert q["id"] == "test-123"

    def test_generate_with_template_phq9(self):
        """Test generating PHQ-9 questionnaire."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(template="phq-9")

        assert q["title"] == "Patient Health Questionnaire (PHQ-9)"
        assert q["name"] == "phq_9"
        assert len(q["item"]) == 9
        # PHQ-9 uses choice items with answer options
        assert q["item"][0]["type"] == "choice"
        assert "answerOption" in q["item"][0]

    def test_generate_with_template_gad7(self):
        """Test generating GAD-7 questionnaire."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(template="gad-7")

        assert q["title"] == "Generalized Anxiety Disorder Assessment (GAD-7)"
        assert len(q["item"]) == 7

    def test_generate_with_template_health_intake(self):
        """Test generating health intake questionnaire with groups."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(template="health-intake")

        assert q["title"] == "Patient Health Intake Form"
        # Has group items with nested items
        emergency_contact = q["item"][0]
        assert emergency_contact["type"] == "group"
        assert "item" in emergency_contact
        assert len(emergency_contact["item"]) == 3

    def test_generate_with_template_pain_assessment(self):
        """Test generating pain assessment questionnaire."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(template="pain-assessment")

        assert q["title"] == "Pain Assessment Questionnaire"
        # Has integer, string, choice, text, and boolean items
        types = {item["type"] for item in q["item"]}
        assert "integer" in types
        assert "string" in types
        assert "boolean" in types

    def test_generate_with_template_covid_screening(self):
        """Test generating COVID screening questionnaire."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(template="covid-screening")

        assert q["title"] == "COVID-19 Screening Questionnaire"
        # All items are boolean
        for item in q["item"]:
            assert item["type"] == "boolean"

    def test_generate_with_template_audit_c(self):
        """Test generating AUDIT-C questionnaire."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(template="audit-c")

        assert q["title"] == "AUDIT-C Alcohol Screening"
        assert len(q["item"]) == 3

    def test_generate_with_template_falls_risk(self):
        """Test generating falls risk questionnaire."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(template="falls-risk")

        assert q["title"] == "Falls Risk Assessment"

    def test_generate_with_template_sdoh(self):
        """Test generating SDOH questionnaire with nested groups."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(template="sdoh")

        assert q["title"] == "Social Determinants of Health Screening"
        # Has housing and food groups
        housing = next(i for i in q["item"] if i["linkId"] == "housing")
        assert housing["type"] == "group"
        assert "item" in housing

    def test_generate_with_custom_name_and_title(self):
        """Test generating with custom name and title."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(
            template="phq-9",
            name="custom-name",
            title="My Custom Questionnaire",
        )

        # Name has dashes converted to underscores per FHIR conventions
        assert q["name"] == "custom_name"
        assert q["title"] == "My Custom Questionnaire"
        assert "custom-name" in q["url"]

    def test_generate_with_custom_status(self):
        """Test generating with custom status."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(status="draft")

        assert q["status"] == "draft"

    def test_generate_random_template(self):
        """Test generating with random template selection."""
        gen = QuestionnaireGenerator(seed=42)
        # Without specifying template, should pick randomly
        q1 = gen.generate()

        gen2 = QuestionnaireGenerator(seed=123)
        q2 = gen2.generate()

        # Different seeds should potentially produce different questionnaires
        # (though they could be the same by chance)
        assert q1["resourceType"] == "Questionnaire"
        assert q2["resourceType"] == "Questionnaire"

    def test_generate_has_required_fields(self):
        """Test that generated questionnaire has all required FHIR fields."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate()

        # Required fields per FHIR spec
        assert "resourceType" in q
        assert "status" in q

        # Common expected fields
        assert "meta" in q
        assert "url" in q
        assert "identifier" in q
        assert "version" in q
        assert "name" in q
        assert "title" in q
        assert "subjectType" in q
        assert "date" in q
        assert "publisher" in q
        assert "description" in q
        assert "purpose" in q
        assert "item" in q

    def test_generate_answer_options_with_integer(self):
        """Test answer options with integer values."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(template="phq-9")

        # PHQ-9 has integer answer options (0-3)
        first_item = q["item"][0]
        assert "answerOption" in first_item

        # Should have valueInteger
        option = first_item["answerOption"][0]
        assert "valueInteger" in option
        assert option["valueInteger"] == 0  # "Not at all"

    def test_generate_answer_options_with_string(self):
        """Test answer options with string values."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(template="pain-assessment")

        # Find the pain-type choice item
        pain_type = next(i for i in q["item"] if i["linkId"] == "pain-type")
        assert "answerOption" in pain_type

        # Should have valueString
        option = pain_type["answerOption"][0]
        assert "valueString" in option

    def test_generate_items_with_display_extension(self):
        """Test that answer options have display extensions."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(template="phq-9")

        first_item = q["item"][0]
        option = first_item["answerOption"][0]

        assert "extension" in option
        ext = option["extension"][0]
        assert ext["url"] == "http://hl7.org/fhir/StructureDefinition/questionnaire-optionDisplay"
        assert "valueString" in ext

    def test_invalid_template_uses_first(self):
        """Test that invalid template falls back to first template."""
        gen = QuestionnaireGenerator(seed=42)
        q = gen.generate(template="nonexistent-template")

        # Should fall back to first template (phq-9)
        assert q["title"] == "Patient Health Questionnaire (PHQ-9)"


class TestQuestionnaireResponseGenerator:
    """Tests for QuestionnaireResponseGenerator."""

    def test_generate_default(self):
        """Test generating a response with defaults."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate()

        assert r["resourceType"] == "QuestionnaireResponse"
        assert "id" in r
        assert r["status"] == "completed"
        assert "item" in r
        assert len(r["item"]) > 0

    def test_generate_with_id(self):
        """Test generating with specific ID."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(response_id="resp-123")

        assert r["id"] == "resp-123"

    def test_generate_with_template_phq9(self):
        """Test generating PHQ-9 response."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(questionnaire_template="phq-9")

        assert r["questionnaire"] == "http://example.org/Questionnaire/phq-9"
        assert len(r["item"]) == 9

        # PHQ-9 responses have integer values
        for item in r["item"]:
            assert "answer" in item
            assert len(item["answer"]) == 1
            assert "valueInteger" in item["answer"][0]
            # Values should be 0-3
            assert 0 <= item["answer"][0]["valueInteger"] <= 3

    def test_generate_with_template_gad7(self):
        """Test generating GAD-7 response."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(questionnaire_template="gad-7")

        assert r["questionnaire"] == "http://example.org/Questionnaire/gad-7"
        assert len(r["item"]) == 7

    def test_generate_with_template_pain_assessment(self):
        """Test generating pain assessment response."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(questionnaire_template="pain-assessment")

        assert r["questionnaire"] == "http://example.org/Questionnaire/pain-assessment"

        # Check various answer types
        pain_level = next(i for i in r["item"] if i["linkId"] == "pain-level")
        assert "valueInteger" in pain_level["answer"][0]
        assert 0 <= pain_level["answer"][0]["valueInteger"] <= 10

        pain_interferes = next(i for i in r["item"] if i["linkId"] == "pain-interferes")
        assert "valueBoolean" in pain_interferes["answer"][0]

    def test_generate_with_template_covid_screening(self):
        """Test generating COVID screening response."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(questionnaire_template="covid-screening")

        # All answers should be boolean
        for item in r["item"]:
            assert "valueBoolean" in item["answer"][0]

    def test_generate_with_template_health_intake(self):
        """Test generating health intake response."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(questionnaire_template="health-intake")

        # Has various types: date, string, boolean
        allergies = next(i for i in r["item"] if i["linkId"] == "allergies")
        assert "valueBoolean" in allergies["answer"][0]

        medications = next(i for i in r["item"] if i["linkId"] == "medications")
        assert "valueString" in medications["answer"][0]

    def test_generate_with_patient_ref(self):
        """Test generating with patient reference."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(patient_ref="Patient/123")

        assert r["subject"]["reference"] == "Patient/123"
        assert r["source"]["reference"] == "Patient/123"
        # Author defaults to patient if not specified
        assert r["author"]["reference"] == "Patient/123"

    def test_generate_with_encounter_ref(self):
        """Test generating with encounter reference."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(
            patient_ref="Patient/123",
            encounter_ref="Encounter/456",
        )

        assert r["encounter"]["reference"] == "Encounter/456"

    def test_generate_with_author_ref(self):
        """Test generating with author reference."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(
            patient_ref="Patient/123",
            author_ref="Practitioner/789",
        )

        # Author should be the practitioner, not the patient
        assert r["author"]["reference"] == "Practitioner/789"

    def test_generate_with_questionnaire_ref(self):
        """Test generating with custom questionnaire reference."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(questionnaire_ref="Questionnaire/my-custom")

        assert r["questionnaire"] == "Questionnaire/my-custom"

    def test_generate_with_custom_status(self):
        """Test generating with custom status."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(status="in-progress")

        assert r["status"] == "in-progress"

    def test_generate_has_required_fields(self):
        """Test that generated response has all required FHIR fields."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate()

        # Required fields per FHIR spec
        assert "resourceType" in r
        assert "status" in r

        # Common expected fields
        assert "meta" in r
        assert "identifier" in r
        assert "questionnaire" in r
        assert "authored" in r
        assert "item" in r

    def test_generate_random_template(self):
        """Test generating with random template selection."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r1 = gen.generate()

        gen2 = QuestionnaireResponseGenerator(seed=123)
        r2 = gen2.generate()

        assert r1["resourceType"] == "QuestionnaireResponse"
        assert r2["resourceType"] == "QuestionnaireResponse"

    def test_answer_types_integer(self):
        """Test integer answer generation."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(questionnaire_template="phq-9")

        for item in r["item"]:
            answer = item["answer"][0]
            assert "valueInteger" in answer
            assert isinstance(answer["valueInteger"], int)

    def test_answer_types_boolean(self):
        """Test boolean answer generation."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(questionnaire_template="covid-screening")

        for item in r["item"]:
            answer = item["answer"][0]
            assert "valueBoolean" in answer
            assert isinstance(answer["valueBoolean"], bool)

    def test_answer_types_string_from_values(self):
        """Test string answer generation from predefined values."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(questionnaire_template="pain-assessment")

        pain_location = next(i for i in r["item"] if i["linkId"] == "pain-location")
        answer = pain_location["answer"][0]
        assert "valueString" in answer
        # Should be one of the predefined values
        assert answer["valueString"] in ["Lower back", "Neck", "Knee", "Shoulder", "Head", "Abdomen"]

    def test_answer_types_date(self):
        """Test date answer generation."""
        gen = QuestionnaireResponseGenerator(seed=42)
        r = gen.generate(questionnaire_template="health-intake")

        d1_item = next(i for i in r["item"] if i["linkId"] == "d1")
        answer = d1_item["answer"][0]
        assert "valueDate" in answer


class TestGeneratorSeeding:
    """Tests for generator seeding behavior."""

    def test_questionnaire_generator_reproducible(self):
        """Test that seeded generators produce reproducible results."""
        gen1 = QuestionnaireGenerator(seed=42)
        gen2 = QuestionnaireGenerator(seed=42)

        q1 = gen1.generate(template="phq-9")
        q2 = gen2.generate(template="phq-9")

        # IDs might be UUIDs but structure should be identical
        assert q1["title"] == q2["title"]
        assert q1["name"] == q2["name"]
        assert len(q1["item"]) == len(q2["item"])

    def test_response_generator_reproducible(self):
        """Test that seeded response generators produce reproducible results."""
        gen1 = QuestionnaireResponseGenerator(seed=42)
        gen2 = QuestionnaireResponseGenerator(seed=42)

        r1 = gen1.generate(questionnaire_template="phq-9", response_id="test")
        r2 = gen2.generate(questionnaire_template="phq-9", response_id="test")

        # Values should be identical with same seed
        for i in range(len(r1["item"])):
            assert r1["item"][i]["answer"] == r2["item"][i]["answer"]
