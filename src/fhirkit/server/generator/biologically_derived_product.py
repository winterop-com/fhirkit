"""BiologicallyDerivedProduct resource generator."""

from datetime import datetime, timedelta, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class BiologicallyDerivedProductGenerator(FHIRResourceGenerator):
    """Generator for FHIR BiologicallyDerivedProduct resources."""

    PRODUCT_CATEGORIES = ["organ", "tissue", "fluid", "cells", "biologicalAgent"]

    PRODUCT_CODES = [
        {
            "system": "http://snomed.info/sct",
            "code": "119297000",
            "display": "Blood product",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "256852006",
            "display": "Tissue sample",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "119347001",
            "display": "Whole blood",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "119351004",
            "display": "Platelets",
        },
        {
            "system": "http://snomed.info/sct",
            "code": "256909007",
            "display": "Plasma",
        },
    ]

    STATUS_CODES = ["available", "unavailable"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        product_id: str | None = None,
        product_category: str | None = None,
        product_code: dict[str, Any] | None = None,
        status: str | None = None,
        quantity: int | None = None,
        parent_references: list[str] | None = None,
        collection: dict[str, Any] | None = None,
        processing: list[dict[str, Any]] | None = None,
        storage: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a BiologicallyDerivedProduct resource.

        Args:
            product_id: Resource ID (generates UUID if None)
            product_category: Category of product
            product_code: Product code
            status: Availability status
            quantity: Number of items
            parent_references: References to parent products
            collection: Collection details
            processing: Processing details
            storage: Storage details

        Returns:
            BiologicallyDerivedProduct FHIR resource
        """
        if product_id is None:
            product_id = self._generate_id()

        if product_category is None:
            product_category = self.faker.random_element(self.PRODUCT_CATEGORIES)

        if product_code is None:
            product_code = self.faker.random_element(self.PRODUCT_CODES)

        if status is None:
            status = self.faker.random_element(self.STATUS_CODES)

        product: dict[str, Any] = {
            "resourceType": "BiologicallyDerivedProduct",
            "id": product_id,
            "meta": self._generate_meta(),
            "productCategory": product_category,
            "productCode": {"coding": [product_code], "text": product_code["display"]},
            "status": status,
        }

        # Add identifier
        product["identifier"] = [
            {
                "system": "http://example.org/bio-products",
                "value": f"BIO-{self.faker.random_number(digits=10, fix_len=True)}",
            }
        ]

        # Add quantity
        if quantity:
            product["quantity"] = quantity
        else:
            product["quantity"] = self.faker.random_int(1, 10)

        # Add parent references
        if parent_references:
            product["parent"] = [{"reference": ref} for ref in parent_references]

        # Add collection
        if collection:
            product["collection"] = collection
        else:
            product["collection"] = self._generate_collection()

        # Add processing
        if processing:
            product["processing"] = processing
        elif self.faker.boolean(chance_of_getting_true=60):
            product["processing"] = self._generate_processing()

        # Add storage
        if storage:
            product["storage"] = storage
        elif self.faker.boolean(chance_of_getting_true=70):
            product["storage"] = self._generate_storage()

        return product

    def _generate_collection(self) -> dict[str, Any]:
        """Generate collection information."""
        collected = datetime.now(timezone.utc) - timedelta(days=self.faker.random_int(1, 30))

        return {
            "collector": {"reference": f"Practitioner/{self._generate_id()}"},
            "source": {"reference": f"Patient/{self._generate_id()}"},
            "collectedDateTime": collected.isoformat(),
        }

    def _generate_processing(self) -> list[dict[str, Any]]:
        """Generate processing information."""
        return [
            {
                "description": "Standard processing procedure",
                "timeDateTime": datetime.now(timezone.utc).isoformat(),
            }
        ]

    def _generate_storage(self) -> list[dict[str, Any]]:
        """Generate storage information."""
        return [
            {
                "description": "Cold storage",
                "temperature": {
                    "value": float(self.faker.random_int(-80, 4)),
                    "unit": "degrees C",
                    "system": "http://unitsofmeasure.org",
                    "code": "Cel",
                },
                "scale": "celsius",
                "duration": {
                    "value": float(self.faker.random_int(1, 365)),
                    "unit": "days",
                    "system": "http://unitsofmeasure.org",
                    "code": "d",
                },
            }
        ]

    def generate_blood_product(
        self,
        product_type: str = "whole blood",
        donor_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a blood product.

        Args:
            product_type: Type of blood product
            donor_id: Patient ID of donor

        Returns:
            BiologicallyDerivedProduct FHIR resource
        """
        product_codes = {
            "whole blood": {"code": "119347001", "display": "Whole blood"},
            "platelets": {"code": "119351004", "display": "Platelets"},
            "plasma": {"code": "256909007", "display": "Plasma"},
        }

        code_info = product_codes.get(product_type, {"code": "119297000", "display": "Blood product"})
        product_code = {
            "system": "http://snomed.info/sct",
            "code": code_info["code"],
            "display": code_info["display"],
        }

        collection = self._generate_collection()
        if donor_id:
            collection["source"] = {"reference": f"Patient/{donor_id}"}

        return self.generate(
            product_category="fluid",
            product_code=product_code,
            collection=collection,
            **kwargs,
        )
