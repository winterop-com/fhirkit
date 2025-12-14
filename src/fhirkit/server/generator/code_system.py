"""CodeSystem resource generator."""

from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator


class CodeSystemGenerator(FHIRResourceGenerator):
    """Generator for FHIR CodeSystem resources."""

    # Code system templates
    CODE_SYSTEM_TEMPLATES: list[dict[str, Any]] = [
        {
            "name": "PriorityCodes",
            "title": "Priority Codes",
            "description": "Priority levels for clinical tasks and requests",
            "concepts": [
                {"code": "stat", "display": "STAT", "definition": "Immediate priority"},
                {"code": "urgent", "display": "Urgent", "definition": "High priority"},
                {"code": "routine", "display": "Routine", "definition": "Normal priority"},
                {"code": "elective", "display": "Elective", "definition": "Low priority"},
            ],
        },
        {
            "name": "TaskStatus",
            "title": "Task Status",
            "description": "Status codes for workflow tasks",
            "concepts": [
                {"code": "draft", "display": "Draft", "definition": "Task is in draft state"},
                {"code": "requested", "display": "Requested", "definition": "Task has been requested"},
                {"code": "in-progress", "display": "In Progress", "definition": "Task is being worked on"},
                {"code": "completed", "display": "Completed", "definition": "Task is complete"},
                {"code": "cancelled", "display": "Cancelled", "definition": "Task was cancelled"},
            ],
        },
        {
            "name": "AlertType",
            "title": "Alert Type",
            "description": "Types of clinical alerts",
            "concepts": [
                {"code": "allergy", "display": "Allergy Alert", "definition": "Patient allergy warning"},
                {"code": "drug-interaction", "display": "Drug Interaction", "definition": "Potential drug interaction"},
                {"code": "duplicate", "display": "Duplicate Order", "definition": "Duplicate order detected"},
                {"code": "lab-critical", "display": "Critical Lab", "definition": "Critical laboratory value"},
            ],
        },
    ]

    # Content modes
    CONTENT_MODES = ["not-present", "example", "fragment", "complete", "supplement"]

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        code_system_id: str | None = None,
        name: str | None = None,
        version: str = "1.0.0",
        status: str = "active",
        content: str = "complete",
        template: dict | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a CodeSystem resource.

        Args:
            code_system_id: CodeSystem ID (generates UUID if None)
            name: CodeSystem name (random template if None)
            version: CodeSystem version
            status: Publication status (draft, active, retired, unknown)
            content: Content mode (not-present, example, fragment, complete, supplement)
            template: Custom template with name, title, description, concepts

        Returns:
            CodeSystem FHIR resource
        """
        if code_system_id is None:
            code_system_id = self._generate_id()

        # Use provided template or select random one
        selected: dict[str, Any]
        if template is None:
            selected = self.CODE_SYSTEM_TEMPLATES[self.faker.random_int(0, len(self.CODE_SYSTEM_TEMPLATES) - 1)]
        else:
            selected = template

        if name is None:
            name = str(selected["name"])

        concepts: list[dict[str, Any]] = list(selected["concepts"])
        code_system: dict[str, Any] = {
            "resourceType": "CodeSystem",
            "id": code_system_id,
            "meta": self._generate_meta(),
            "url": f"http://example.org/fhir/CodeSystem/{name}",
            "identifier": [
                self._generate_identifier(
                    system="http://example.org/codesystem-ids",
                    value=f"CS-{self.faker.numerify('######')}",
                ),
            ],
            "version": version,
            "name": name,
            "title": selected["title"],
            "status": status,
            "experimental": False,
            "date": self._generate_date(),
            "publisher": self.faker.company(),
            "description": selected["description"],
            "caseSensitive": True,
            "content": content,
            "count": len(concepts),
            "concept": [
                {
                    "code": c["code"],
                    "display": c["display"],
                    "definition": c.get("definition", c["display"]),
                }
                for c in concepts
            ],
        }

        return code_system
