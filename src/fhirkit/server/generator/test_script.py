"""TestScript resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class TestScriptGenerator(FHIRResourceGenerator):
    """Generator for FHIR TestScript resources."""

    STATUS_CODES = ["draft", "active", "retired", "unknown"]

    # Test script operations
    OPERATION_TYPES = [
        {"code": "read", "display": "Read"},
        {"code": "create", "display": "Create"},
        {"code": "update", "display": "Update"},
        {"code": "delete", "display": "Delete"},
        {"code": "search", "display": "Search"},
        {"code": "history", "display": "History"},
        {"code": "batch", "display": "Batch"},
        {"code": "transaction", "display": "Transaction"},
    ]

    # Assertion response codes
    RESPONSE_CODES = [
        "okay",
        "created",
        "noContent",
        "notModified",
        "bad",
        "forbidden",
        "notFound",
        "methodNotAllowed",
        "conflict",
        "gone",
        "unprocessableEntity",
    ]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        script_id: str | None = None,
        name: str | None = None,
        title: str | None = None,
        status: str = "active",
        description: str | None = None,
        purpose: str | None = None,
        fixtures: list[dict[str, Any]] | None = None,
        variables: list[dict[str, Any]] | None = None,
        setup: dict[str, Any] | None = None,
        tests: list[dict[str, Any]] | None = None,
        teardown: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a TestScript resource.

        Args:
            script_id: Resource ID (generates UUID if None)
            name: Computer-friendly name
            title: Human-friendly title
            status: Publication status
            description: Natural language description
            purpose: Why this test script exists
            fixtures: Test fixtures
            variables: Dynamic variables
            setup: Setup actions
            tests: Test definitions
            teardown: Teardown actions

        Returns:
            TestScript FHIR resource
        """
        if script_id is None:
            script_id = self._generate_id()

        if name is None:
            name = f"TestScript{self.faker.random_number(digits=4, fix_len=True)}"

        if title is None:
            title = f"Test Script for {self.faker.word().title()} {self.faker.word().title()}"

        test_script: dict[str, Any] = {
            "resourceType": "TestScript",
            "id": script_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/TestScript/{script_id}",
            "version": f"{self.faker.random_int(1, 3)}.0.0",
            "name": name,
            "title": title,
            "status": status,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "publisher": self.faker.company(),
        }

        if description:
            test_script["description"] = description
        else:
            test_script["description"] = "Automated test script for FHIR resource testing"

        if purpose:
            test_script["purpose"] = purpose
        else:
            test_script["purpose"] = "Verify FHIR server compliance and functionality"

        # Add fixtures
        if fixtures:
            test_script["fixture"] = fixtures
        else:
            test_script["fixture"] = self._generate_default_fixtures()

        # Add variables
        if variables:
            test_script["variable"] = variables
        else:
            test_script["variable"] = self._generate_default_variables()

        # Add setup
        if setup:
            test_script["setup"] = setup
        elif self.faker.boolean(chance_of_getting_true=70):
            test_script["setup"] = self._generate_setup()

        # Add test actions
        if tests:
            test_script["test"] = tests
        else:
            test_script["test"] = self._generate_tests()

        # Add teardown
        if teardown:
            test_script["teardown"] = teardown
        elif self.faker.boolean(chance_of_getting_true=50):
            test_script["teardown"] = self._generate_teardown()

        return test_script

    def _generate_default_fixtures(self) -> list[dict[str, Any]]:
        """Generate default test fixtures."""
        return [
            {
                "id": "patient-fixture",
                "autocreate": True,
                "autodelete": True,
                "resource": {
                    "reference": "Patient/example",
                    "display": "Test Patient",
                },
            },
        ]

    def _generate_default_variables(self) -> list[dict[str, Any]]:
        """Generate default test variables."""
        return [
            {
                "name": "patientId",
                "sourceId": "patient-fixture",
                "path": "Patient/id",
            },
            {
                "name": "searchUrl",
                "defaultValue": "Patient",
            },
        ]

    def _generate_setup(self) -> dict[str, Any]:
        """Generate setup actions."""
        return {
            "action": [
                {
                    "operation": {
                        "type": {"code": "read"},
                        "resource": "Patient",
                        "description": "Read patient resource for setup",
                        "accept": "application/fhir+json",
                        "encodeRequestUrl": True,
                        "params": "/${patientId}",
                    },
                },
            ],
        }

    def _generate_tests(self) -> list[dict[str, Any]]:
        """Generate test definitions."""
        return [
            {
                "name": "ReadPatient",
                "description": "Read Patient and validate response",
                "action": [
                    {
                        "operation": {
                            "type": {"code": "read"},
                            "resource": "Patient",
                            "description": "Read patient by ID",
                            "accept": "application/fhir+json",
                            "encodeRequestUrl": True,
                            "params": "/${patientId}",
                        },
                    },
                    {
                        "assert": {
                            "description": "Confirm response code is 200 OK",
                            "response": "okay",
                            "warningOnly": False,
                        },
                    },
                    {
                        "assert": {
                            "description": "Confirm resource type is Patient",
                            "resource": "Patient",
                            "warningOnly": False,
                        },
                    },
                ],
            },
            {
                "name": "SearchPatient",
                "description": "Search for patients",
                "action": [
                    {
                        "operation": {
                            "type": {"code": "search"},
                            "resource": "Patient",
                            "description": "Search for patients",
                            "accept": "application/fhir+json",
                            "encodeRequestUrl": True,
                        },
                    },
                    {
                        "assert": {
                            "description": "Confirm response code is 200 OK",
                            "response": "okay",
                            "warningOnly": False,
                        },
                    },
                    {
                        "assert": {
                            "description": "Confirm response is a Bundle",
                            "resource": "Bundle",
                            "warningOnly": False,
                        },
                    },
                ],
            },
        ]

    def _generate_teardown(self) -> dict[str, Any]:
        """Generate teardown actions."""
        return {
            "action": [
                {
                    "operation": {
                        "type": {"code": "delete"},
                        "resource": "Patient",
                        "description": "Delete test patient",
                        "encodeRequestUrl": True,
                        "targetId": "patient-fixture",
                    },
                },
            ],
        }

    def generate_for_resource_type(
        self,
        resource_type: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a TestScript for a specific resource type.

        Args:
            resource_type: The FHIR resource type to test

        Returns:
            TestScript FHIR resource
        """
        fixtures = [
            {
                "id": f"{resource_type.lower()}-fixture",
                "autocreate": True,
                "autodelete": True,
                "resource": {
                    "reference": f"{resource_type}/example",
                    "display": f"Test {resource_type}",
                },
            },
        ]

        tests = [
            {
                "name": f"Read{resource_type}",
                "description": f"Read {resource_type} and validate response",
                "action": [
                    {
                        "operation": {
                            "type": {"code": "read"},
                            "resource": resource_type,
                            "description": f"Read {resource_type} by ID",
                            "accept": "application/fhir+json",
                            "encodeRequestUrl": True,
                        },
                    },
                    {
                        "assert": {
                            "description": "Confirm response code is 200 OK",
                            "response": "okay",
                            "warningOnly": False,
                        },
                    },
                ],
            },
        ]

        return self.generate(
            name=f"{resource_type}Test",
            title=f"Test Script for {resource_type}",
            description=f"Automated tests for {resource_type} resource operations",
            fixtures=fixtures,
            tests=tests,
            **kwargs,
        )
