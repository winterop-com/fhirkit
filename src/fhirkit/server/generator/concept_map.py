"""ConceptMap resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class ConceptMapGenerator(FHIRResourceGenerator):
    """Generator for FHIR ConceptMap resources.

    ConceptMap provides mappings between concepts in different code systems,
    enabling translation between terminologies like SNOMED CT, ICD-10, LOINC, etc.
    """

    # Pre-defined concept mappings for common translations
    SNOMED_TO_ICD10: list[dict[str, Any]] = [
        {
            "source": {"code": "73211009", "display": "Diabetes mellitus"},
            "target": {"code": "E11.9", "display": "Type 2 diabetes mellitus without complications"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "38341003", "display": "Hypertensive disorder"},
            "target": {"code": "I10", "display": "Essential (primary) hypertension"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "195967001", "display": "Asthma"},
            "target": {"code": "J45.909", "display": "Unspecified asthma, uncomplicated"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "13645005", "display": "Chronic obstructive lung disease"},
            "target": {"code": "J44.9", "display": "Chronic obstructive pulmonary disease, unspecified"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "84114007", "display": "Heart failure"},
            "target": {"code": "I50.9", "display": "Heart failure, unspecified"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "22298006", "display": "Myocardial infarction"},
            "target": {"code": "I21.9", "display": "Acute myocardial infarction, unspecified"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "40930008", "display": "Hypothyroidism"},
            "target": {"code": "E03.9", "display": "Hypothyroidism, unspecified"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "414545008", "display": "Ischemic heart disease"},
            "target": {"code": "I25.9", "display": "Chronic ischemic heart disease, unspecified"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "44054006", "display": "Diabetes mellitus type 2"},
            "target": {"code": "E11", "display": "Type 2 diabetes mellitus"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "46635009", "display": "Diabetes mellitus type 1"},
            "target": {"code": "E10", "display": "Type 1 diabetes mellitus"},
            "equivalence": "equivalent",
        },
    ]

    LOINC_TO_LOCAL: list[dict[str, Any]] = [
        {
            "source": {"code": "2339-0", "display": "Glucose [Mass/volume] in Blood"},
            "target": {"code": "GLU", "display": "Blood Glucose"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "4548-4", "display": "Hemoglobin A1c/Hemoglobin.total in Blood"},
            "target": {"code": "HBA1C", "display": "Hemoglobin A1c"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "2160-0", "display": "Creatinine [Mass/volume] in Serum or Plasma"},
            "target": {"code": "CREAT", "display": "Serum Creatinine"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "2951-2", "display": "Sodium [Moles/volume] in Serum or Plasma"},
            "target": {"code": "NA", "display": "Sodium"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "2823-3", "display": "Potassium [Moles/volume] in Serum or Plasma"},
            "target": {"code": "K", "display": "Potassium"},
            "equivalence": "equivalent",
        },
    ]

    RXNORM_TO_NDC: list[dict[str, Any]] = [
        {
            "source": {"code": "860975", "display": "Metformin hydrochloride 500 MG Oral Tablet"},
            "target": {"code": "0093-7212-01", "display": "Metformin 500mg Tablets"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "197361", "display": "Aspirin 81 MG Oral Tablet"},
            "target": {"code": "0536-3086-01", "display": "Aspirin 81mg EC Tablets"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "310965", "display": "Lisinopril 10 MG Oral Tablet"},
            "target": {"code": "0093-7339-01", "display": "Lisinopril 10mg Tablets"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "314076", "display": "Simvastatin 20 MG Oral Tablet"},
            "target": {"code": "0093-7155-01", "display": "Simvastatin 20mg Tablets"},
            "equivalence": "equivalent",
        },
        {
            "source": {"code": "309362", "display": "Atorvastatin 20 MG Oral Tablet"},
            "target": {"code": "0071-0157-23", "display": "Lipitor 20mg Tablets"},
            "equivalence": "equivalent",
        },
    ]

    # Map templates with metadata
    CONCEPT_MAP_TEMPLATES: list[dict[str, Any]] = [
        {
            "name": "snomed-to-icd10",
            "title": "SNOMED CT to ICD-10-CM Mapping",
            "source_system": "http://snomed.info/sct",
            "target_system": "http://hl7.org/fhir/sid/icd-10-cm",
            "mappings": SNOMED_TO_ICD10,
        },
        {
            "name": "loinc-to-local",
            "title": "LOINC to Local Lab Codes",
            "source_system": "http://loinc.org",
            "target_system": "http://example.org/local-lab-codes",
            "mappings": LOINC_TO_LOCAL,
        },
        {
            "name": "rxnorm-to-ndc",
            "title": "RxNorm to NDC Mapping",
            "source_system": "http://www.nlm.nih.gov/research/umls/rxnorm",
            "target_system": "http://hl7.org/fhir/sid/ndc",
            "mappings": RXNORM_TO_NDC,
        },
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        concept_map_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        source_system: str | None = None,
        target_system: str | None = None,
        template_name: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a ConceptMap resource.

        Args:
            concept_map_id: Resource ID (generates UUID if None)
            name: Machine-readable name
            title: Human-readable title
            source_system: Source code system URI
            target_system: Target code system URI
            template_name: Use pre-defined template (snomed-to-icd10, loinc-to-local, rxnorm-to-ndc)

        Returns:
            ConceptMap FHIR resource
        """
        if concept_map_id is None:
            concept_map_id = self._generate_id()

        # Use template if specified
        template = None
        if template_name:
            for t in self.CONCEPT_MAP_TEMPLATES:
                if t["name"] == template_name:
                    template = t
                    break

        if template is None:
            template = self.faker.random_element(self.CONCEPT_MAP_TEMPLATES)

        # Override template values if explicitly provided
        if name is None:
            name = template["name"]
        if title is None:
            title = template["title"]
        if source_system is None:
            source_system = template["source_system"]
        if target_system is None:
            target_system = template["target_system"]

        mappings = template["mappings"]

        # At this point, name/title/source_system/target_system are guaranteed to be set
        assert name is not None
        assert title is not None
        assert source_system is not None
        assert target_system is not None

        # Build date
        published = self.faker.date_time_between(
            start_date="-2y",
            end_date="now",
            tzinfo=timezone.utc,
        )

        concept_map: dict[str, Any] = {
            "resourceType": "ConceptMap",
            "id": concept_map_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/ConceptMap/{name}",
            "version": "1.0.0",
            "name": name.replace("-", "_"),
            "title": title,
            "status": "active",
            "experimental": False,
            "date": published.isoformat(),
            "publisher": "Example Organization",
            "description": f"Maps concepts from {source_system} to {target_system}",
            "purpose": "To enable translation between coding systems for interoperability",
            "sourceUri": source_system,
            "targetUri": target_system,
        }

        # Build group with elements
        elements = []
        for mapping in mappings:
            element: dict[str, Any] = {
                "code": mapping["source"]["code"],
                "display": mapping["source"]["display"],
                "target": [
                    {
                        "code": mapping["target"]["code"],
                        "display": mapping["target"]["display"],
                        "equivalence": mapping["equivalence"],
                    }
                ],
            }
            elements.append(element)

        concept_map["group"] = [
            {
                "source": source_system,
                "target": target_system,
                "element": elements,
            }
        ]

        return concept_map

    def generate_all_templates(self) -> list[dict[str, Any]]:
        """Generate ConceptMaps for all pre-defined templates.

        Returns:
            List of ConceptMap resources
        """
        return [self.generate(template_name=t["name"]) for t in self.CONCEPT_MAP_TEMPLATES]
