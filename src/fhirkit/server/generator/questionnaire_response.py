"""QuestionnaireResponse resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class QuestionnaireResponseGenerator(FHIRResourceGenerator):
    """Generator for FHIR QuestionnaireResponse resources."""

    # Response templates that match questionnaire templates
    RESPONSE_TEMPLATES: dict[str, dict[str, Any]] = {
        "phq-9": {
            "questionnaire_url": "http://example.org/Questionnaire/phq-9",
            "items": [
                {"linkId": "1", "type": "integer", "range": (0, 3)},
                {"linkId": "2", "type": "integer", "range": (0, 3)},
                {"linkId": "3", "type": "integer", "range": (0, 3)},
                {"linkId": "4", "type": "integer", "range": (0, 3)},
                {"linkId": "5", "type": "integer", "range": (0, 3)},
                {"linkId": "6", "type": "integer", "range": (0, 3)},
                {"linkId": "7", "type": "integer", "range": (0, 3)},
                {"linkId": "8", "type": "integer", "range": (0, 3)},
                {"linkId": "9", "type": "integer", "range": (0, 3)},
            ],
        },
        "gad-7": {
            "questionnaire_url": "http://example.org/Questionnaire/gad-7",
            "items": [
                {"linkId": "1", "type": "integer", "range": (0, 3)},
                {"linkId": "2", "type": "integer", "range": (0, 3)},
                {"linkId": "3", "type": "integer", "range": (0, 3)},
                {"linkId": "4", "type": "integer", "range": (0, 3)},
                {"linkId": "5", "type": "integer", "range": (0, 3)},
                {"linkId": "6", "type": "integer", "range": (0, 3)},
                {"linkId": "7", "type": "integer", "range": (0, 3)},
            ],
        },
        "pain-assessment": {
            "questionnaire_url": "http://example.org/Questionnaire/pain-assessment",
            "items": [
                {"linkId": "pain-level", "type": "integer", "range": (0, 10)},
                {
                    "linkId": "pain-location",
                    "type": "string",
                    "values": ["Lower back", "Neck", "Knee", "Shoulder", "Head", "Abdomen"],
                },
                {
                    "linkId": "pain-duration",
                    "type": "string",
                    "values": ["Less than 1 week", "1-4 weeks", "1-3 months", "More than 3 months"],
                },
                {
                    "linkId": "pain-type",
                    "type": "string",
                    "values": ["sharp", "dull", "burning", "aching", "throbbing"],
                },
                {
                    "linkId": "pain-worse",
                    "type": "string",
                    "values": ["Movement", "Standing", "Sitting", "Lying down", "Nothing specific"],
                },
                {
                    "linkId": "pain-better",
                    "type": "string",
                    "values": ["Rest", "Heat", "Ice", "Medication", "Nothing helps"],
                },
                {"linkId": "pain-interferes", "type": "boolean"},
            ],
        },
        "covid-screening": {
            "questionnaire_url": "http://example.org/Questionnaire/covid-screening",
            "items": [
                {"linkId": "fever", "type": "boolean"},
                {"linkId": "cough", "type": "boolean"},
                {"linkId": "breathing", "type": "boolean"},
                {"linkId": "taste-smell", "type": "boolean"},
                {"linkId": "contact", "type": "boolean"},
                {"linkId": "travel", "type": "boolean"},
            ],
        },
        "health-intake": {
            "questionnaire_url": "http://example.org/Questionnaire/health-intake",
            "items": [
                {"linkId": "d1", "type": "date"},
                {"linkId": "d2", "type": "string", "values": ["male", "female", "other"]},
                {"linkId": "d3", "type": "string", "values": ["English", "Spanish", "French", "Chinese", "Other"]},
                {
                    "linkId": "current-symptoms",
                    "type": "string",
                    "values": ["Headache and fatigue", "Chest pain", "Joint pain", "Nausea", "None"],
                },
                {
                    "linkId": "symptom-duration",
                    "type": "string",
                    "values": ["1-2 days", "3-7 days", "1-2 weeks", "More than 2 weeks"],
                },
                {
                    "linkId": "medications",
                    "type": "string",
                    "values": ["None", "Aspirin", "Lisinopril", "Metformin", "Multiple medications"],
                },
                {"linkId": "allergies", "type": "boolean"},
                {
                    "linkId": "allergy-list",
                    "type": "string",
                    "values": ["Penicillin", "Sulfa", "None", "Latex", "Shellfish"],
                },
                {"linkId": "smoking", "type": "boolean"},
                {"linkId": "alcohol", "type": "string", "values": ["Never", "Occasionally", "Weekly", "Daily"]},
            ],
        },
    }

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        response_id: str | None = None,
        questionnaire_ref: str | None = None,
        questionnaire_template: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        author_ref: str | None = None,
        status: str = "completed",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a QuestionnaireResponse resource.

        Args:
            response_id: Response ID (generates UUID if None)
            questionnaire_ref: Canonical reference to Questionnaire (e.g., "Questionnaire/123" or URL)
            questionnaire_template: Template name to generate responses for (phq-9, gad-7, etc.)
            patient_ref: Reference to Patient (subject)
            encounter_ref: Reference to Encounter
            author_ref: Reference to who completed the response (Patient, Practitioner, etc.)
            status: Response status (in-progress, completed, amended, entered-in-error, stopped)

        Returns:
            QuestionnaireResponse FHIR resource
        """
        if response_id is None:
            response_id = self._generate_id()

        # Select template for generating responses
        template: dict[str, Any]
        if questionnaire_template and questionnaire_template in self.RESPONSE_TEMPLATES:
            template = self.RESPONSE_TEMPLATES[questionnaire_template]
        else:
            # Pick a random template
            template_keys = list(self.RESPONSE_TEMPLATES.keys())
            template_name = template_keys[self.faker.random_int(0, len(template_keys) - 1)]
            template = self.RESPONSE_TEMPLATES[template_name]

        # Use provided questionnaire ref or template URL
        questionnaire_url = questionnaire_ref or str(template["questionnaire_url"])

        response: dict[str, Any] = {
            "resourceType": "QuestionnaireResponse",
            "id": response_id,
            "meta": self._generate_meta(),
            "identifier": self._generate_identifier(
                system="http://example.org/questionnaire-response-ids",
                value=f"QR-{self.faker.numerify('########')}",
            ),
            "questionnaire": questionnaire_url,
            "status": status,
            "authored": self._generate_datetime(),
            "item": self._generate_response_items(list(template["items"])),
        }

        if patient_ref:
            response["subject"] = {"reference": patient_ref}
            # Default author to patient if not specified
            if not author_ref:
                response["author"] = {"reference": patient_ref}

        if encounter_ref:
            response["encounter"] = {"reference": encounter_ref}

        if author_ref:
            response["author"] = {"reference": author_ref}

        # Add source if different from author
        if patient_ref:
            response["source"] = {"reference": patient_ref}

        return response

    def _generate_response_items(self, item_specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generate response items based on specifications."""
        items = []

        for spec in item_specs:
            item: dict[str, Any] = {
                "linkId": spec["linkId"],
                "answer": [self._generate_answer(spec)],
            }
            items.append(item)

        return items

    def _generate_answer(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Generate an answer based on the item specification."""
        answer_type = spec["type"]

        if answer_type == "integer":
            range_vals = spec.get("range", (0, 10))
            return {"valueInteger": self.faker.random_int(min=range_vals[0], max=range_vals[1])}

        elif answer_type == "decimal":
            range_vals = spec.get("range", (0.0, 100.0))
            return {"valueDecimal": round(self.faker.pyfloat(min_value=range_vals[0], max_value=range_vals[1]), 2)}

        elif answer_type == "boolean":
            # Weight towards False for symptom questions
            return {"valueBoolean": self.faker.boolean(chance_of_getting_true=30)}

        elif answer_type == "date":
            return {"valueDate": self._generate_date()}

        elif answer_type == "dateTime":
            return {"valueDateTime": self._generate_datetime()}

        elif answer_type == "string":
            if "values" in spec:
                return {"valueString": self.faker.random_element(spec["values"])}
            return {"valueString": self.faker.sentence(nb_words=5)}

        elif answer_type == "text":
            return {"valueString": self.faker.paragraph(nb_sentences=2)}

        elif answer_type == "coding":
            coding = spec.get("coding", {"system": "http://example.org", "code": "unknown", "display": "Unknown"})
            return {"valueCoding": coding}

        else:
            # Default to string
            return {"valueString": self.faker.word()}
