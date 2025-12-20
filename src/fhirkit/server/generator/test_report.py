"""TestReport resource generator."""

from datetime import datetime, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class TestReportGenerator(FHIRResourceGenerator):
    """Generator for FHIR TestReport resources."""

    STATUS_CODES = ["completed", "in-progress", "waiting", "stopped", "entered-in-error"]

    RESULT_CODES = ["pass", "fail", "pending"]

    ACTION_RESULT_CODES = ["pass", "skip", "fail", "warning", "error"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        report_id: str | None = None,
        name: str | None = None,
        status: str = "completed",
        result: str | None = None,
        test_script_reference: str | None = None,
        tester: str | None = None,
        issued: str | None = None,
        setup: dict[str, Any] | None = None,
        tests: list[dict[str, Any]] | None = None,
        teardown: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a TestReport resource.

        Args:
            report_id: Resource ID (generates UUID if None)
            name: Name of the test report
            status: Report status
            result: Overall test result
            test_script_reference: Reference to TestScript
            tester: Name of tester
            issued: When the report was issued
            setup: Setup results
            tests: Test results
            teardown: Teardown results

        Returns:
            TestReport FHIR resource
        """
        if report_id is None:
            report_id = self._generate_id()

        if name is None:
            name = f"Test Report {self.faker.random_number(digits=4, fix_len=True)}"

        if result is None:
            result = self.faker.random_element(self.RESULT_CODES)

        if issued is None:
            issued = datetime.now(timezone.utc).isoformat()

        test_report: dict[str, Any] = {
            "resourceType": "TestReport",
            "id": report_id,
            "meta": self._generate_meta(),
            "identifier": {
                "system": "http://example.org/test-reports",
                "value": f"TR-{self.faker.random_number(digits=8, fix_len=True)}",
            },
            "name": name,
            "status": status,
            "result": result,
            "issued": issued,
        }

        # Add test script reference
        if test_script_reference:
            test_report["testScript"] = {"reference": test_script_reference}
        else:
            test_report["testScript"] = {"reference": f"TestScript/{self._generate_id()}"}

        # Add tester
        if tester:
            test_report["tester"] = tester
        else:
            test_report["tester"] = f"{self.faker.first_name()} {self.faker.last_name()}"

        # Add score if completed
        if status == "completed":
            if result == "pass":
                test_report["score"] = float(self.faker.random_int(95, 100))
            elif result == "fail":
                test_report["score"] = float(self.faker.random_int(0, 60))
            else:
                test_report["score"] = float(self.faker.random_int(60, 94))

        # Add setup results
        if setup:
            test_report["setup"] = setup
        elif self.faker.boolean(chance_of_getting_true=70):
            test_report["setup"] = self._generate_setup_results()

        # Add test results
        if tests:
            test_report["test"] = tests
        else:
            test_report["test"] = self._generate_test_results(result)

        # Add teardown results
        if teardown:
            test_report["teardown"] = teardown
        elif self.faker.boolean(chance_of_getting_true=50):
            test_report["teardown"] = self._generate_teardown_results()

        return test_report

    def _generate_setup_results(self) -> dict[str, Any]:
        """Generate setup action results."""
        return {
            "action": [
                {
                    "operation": {
                        "result": "pass",
                        "message": "Setup completed successfully",
                    }
                }
            ]
        }

    def _generate_test_results(self, overall_result: str) -> list[dict[str, Any]]:
        """Generate test action results."""
        tests = []

        num_tests = self.faker.random_int(2, 5)
        for i in range(num_tests):
            # Determine test result based on overall result
            if overall_result == "pass":
                test_result = "pass"
            elif overall_result == "fail" and i == num_tests - 1:
                test_result = "fail"
            else:
                test_result = self.faker.random_element(["pass", "pass", "pass", "fail"])

            test = {
                "name": f"Test {i + 1}",
                "description": f"Test case {i + 1} validation",
                "action": [
                    {
                        "operation": {
                            "result": "pass",
                            "message": "Operation executed successfully",
                        }
                    },
                    {
                        "assert": {
                            "result": test_result,
                            "message": "Passed" if test_result == "pass" else "Assertion failed",
                        }
                    },
                ],
            }
            tests.append(test)

        return tests

    def _generate_teardown_results(self) -> dict[str, Any]:
        """Generate teardown action results."""
        return {
            "action": [
                {
                    "operation": {
                        "result": "pass",
                        "message": "Teardown completed successfully",
                    }
                }
            ]
        }

    def generate_for_test_script(
        self,
        test_script_id: str,
        result: str = "pass",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a TestReport for a specific TestScript.

        Args:
            test_script_id: TestScript ID
            result: Test result

        Returns:
            TestReport FHIR resource
        """
        return self.generate(
            test_script_reference=f"TestScript/{test_script_id}",
            result=result,
            **kwargs,
        )
