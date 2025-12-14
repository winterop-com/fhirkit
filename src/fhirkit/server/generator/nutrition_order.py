"""NutritionOrder resource generator."""

from datetime import timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import make_codeable_concept


class NutritionOrderGenerator(FHIRResourceGenerator):
    """Generator for FHIR NutritionOrder resources.

    NutritionOrder represents diet orders for patients, including therapeutic
    diets, texture modifications, and enteral/parenteral nutrition orders.
    """

    # Diet types
    DIET_TYPES: list[dict[str, Any]] = [
        {
            "code": {"system": "http://snomed.info/sct", "code": "160670007", "display": "Diabetic diet"},
            "instruction": "Follow diabetic meal plan with controlled carbohydrates",
            "texture": None,
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "1055201009", "display": "Low sodium diet"},
            "instruction": "Limit sodium intake to less than 2g per day",
            "texture": None,
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "226208002", "display": "Cardiac diet"},
            "instruction": "Heart-healthy diet low in saturated fat and cholesterol",
            "texture": None,
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "226211001", "display": "Renal diet"},
            "instruction": "Restricted protein, sodium, potassium, and phosphorus",
            "texture": None,
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "226214009", "display": "Clear liquid diet"},
            "instruction": "Clear liquids only - broth, juice, gelatin, clear beverages",
            "texture": "liquid",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "226215005", "display": "Full liquid diet"},
            "instruction": "All liquids including milk, cream soups, and puddings",
            "texture": "liquid",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "226216006", "display": "Soft diet"},
            "instruction": "Soft, easy to chew foods - no hard or crunchy items",
            "texture": "soft",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "226227002", "display": "Pureed diet"},
            "instruction": "All foods pureed to smooth consistency",
            "texture": "pureed",
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "182922004", "display": "Regular diet"},
            "instruction": "Regular diet with no restrictions",
            "texture": None,
        },
        {
            "code": {"system": "http://snomed.info/sct", "code": "310244003", "display": "NPO (nothing by mouth)"},
            "instruction": "Nothing by mouth until further orders",
            "texture": None,
        },
    ]

    # Food texture modifiers
    TEXTURE_MODIFIERS: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "228049004", "display": "Chopped"},
        {"system": "http://snomed.info/sct", "code": "228053002", "display": "Ground"},
        {"system": "http://snomed.info/sct", "code": "441761000124107", "display": "Minced"},
        {"system": "http://snomed.info/sct", "code": "228055009", "display": "Pureed"},
        {"system": "http://snomed.info/sct", "code": "228054008", "display": "Moist"},
    ]

    # Fluid consistency
    FLUID_CONSISTENCY: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "439021000124105", "display": "Thin liquids"},
        {"system": "http://snomed.info/sct", "code": "439031000124108", "display": "Nectar thick liquids"},
        {"system": "http://snomed.info/sct", "code": "439041000124103", "display": "Honey thick liquids"},
        {"system": "http://snomed.info/sct", "code": "439051000124101", "display": "Pudding thick liquids"},
    ]

    # Allergen exclusions
    ALLERGEN_EXCLUSIONS: list[dict[str, str]] = [
        {"system": "http://snomed.info/sct", "code": "227493005", "display": "Gluten"},
        {"system": "http://snomed.info/sct", "code": "102263004", "display": "Eggs"},
        {"system": "http://snomed.info/sct", "code": "3718001", "display": "Cow milk"},
        {"system": "http://snomed.info/sct", "code": "256350002", "display": "Peanut"},
        {"system": "http://snomed.info/sct", "code": "227219009", "display": "Tree nuts"},
        {"system": "http://snomed.info/sct", "code": "67324005", "display": "Shellfish"},
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        order_id: str | None = None,
        patient_ref: str | None = None,
        encounter_ref: str | None = None,
        orderer_ref: str | None = None,
        status: str | None = None,
        diet_type: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a NutritionOrder resource.

        Args:
            order_id: Resource ID (generates UUID if None)
            patient_ref: Patient reference (e.g., "Patient/123")
            encounter_ref: Encounter reference
            orderer_ref: Practitioner who ordered the diet
            status: Order status
            diet_type: Specific diet type to use

        Returns:
            NutritionOrder FHIR resource
        """
        if order_id is None:
            order_id = self._generate_id()

        # Generate status (weighted towards active)
        if status is None:
            status_weights = [
                ("active", 0.60),
                ("completed", 0.25),
                ("on-hold", 0.05),
                ("draft", 0.05),
                ("revoked", 0.05),
            ]
            roll = self.faker.random.random()
            cumulative = 0.0
            status = "active"
            for s, weight in status_weights:
                cumulative += weight
                if roll < cumulative:
                    status = s
                    break

        # Select diet type
        if diet_type is None:
            diet_type = self.faker.random_element(self.DIET_TYPES)

        # Generate order datetime
        order_datetime = self.faker.date_time_between(
            start_date="-7d",
            end_date="now",
            tzinfo=timezone.utc,
        )

        order: dict[str, Any] = {
            "resourceType": "NutritionOrder",
            "id": order_id,
            "meta": self._generate_meta(),
            "status": status,
            "intent": "order",
            "dateTime": order_datetime.isoformat(),
            "oralDiet": {
                "type": [make_codeable_concept(diet_type["code"])],
                "instruction": diet_type["instruction"],
            },
        }

        # Add texture modifier if specified
        if diet_type.get("texture") == "pureed":
            order["oralDiet"]["texture"] = [
                {
                    "modifier": make_codeable_concept(
                        {"system": "http://snomed.info/sct", "code": "228055009", "display": "Pureed"}
                    ),
                }
            ]
        elif diet_type.get("texture") == "soft":
            order["oralDiet"]["texture"] = [
                {
                    "modifier": make_codeable_concept(
                        {"system": "http://snomed.info/sct", "code": "228054008", "display": "Moist"}
                    ),
                }
            ]

        # Randomly add fluid consistency for some diets
        if self.faker.boolean(chance_of_getting_true=30):
            order["oralDiet"]["fluidConsistencyType"] = [
                make_codeable_concept(self.faker.random_element(self.FLUID_CONSISTENCY))
            ]

        # Randomly add allergen exclusions
        if self.faker.boolean(chance_of_getting_true=40):
            num_exclusions = self.faker.random_int(1, 3)
            exclusions = self.faker.random_elements(
                elements=self.ALLERGEN_EXCLUSIONS,
                length=num_exclusions,
                unique=True,
            )
            order["excludeFoodModifier"] = [make_codeable_concept(e) for e in exclusions]

        if patient_ref:
            order["patient"] = {"reference": patient_ref}

        if encounter_ref:
            order["encounter"] = {"reference": encounter_ref}

        if orderer_ref:
            order["orderer"] = {"reference": orderer_ref}

        return order
