"""Web UI routes for FHIR server."""

import json
from typing import Any

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from ..storage.fhir_store import FHIRStore
from ..ui.helpers import (
    RESOURCE_CATEGORIES,
    format_date,
    get_resource_display,
)
from .routes import SUPPORTED_TYPES
from .search import SEARCH_PARAMS


def create_ui_router(
    templates: Jinja2Templates,
    store: FHIRStore,
    settings: Any,
) -> APIRouter:
    """Create the UI router.

    Args:
        templates: Jinja2 templates instance
        store: FHIR data store
        settings: Server settings

    Returns:
        FastAPI router with UI routes
    """
    router = APIRouter(tags=["UI"])

    def get_context(request: Request, **kwargs: Any) -> dict[str, Any]:
        """Build template context with common values."""
        return {
            "request": request,
            "server_name": settings.server_name,
            "ui_mount_path": settings.ui_mount_path,
            "api_base_path": settings.api_base_path,
            "format_date": format_date,
            "get_resource_display": get_resource_display,
            "messages": [],
            **kwargs,
        }

    @router.get("/", response_class=HTMLResponse, name="ui_home")
    async def home(request: Request) -> HTMLResponse:
        """Dashboard home page."""
        # Get resource counts
        resource_counts: dict[str, int] = {}
        total_resources = 0

        for resource_type in SUPPORTED_TYPES:
            count = store.count(resource_type)
            if count > 0:
                resource_counts[resource_type] = count
                total_resources += count

        # Sort by count descending
        resource_counts = dict(sorted(resource_counts.items(), key=lambda x: x[1], reverse=True))

        context = get_context(
            request,
            total_resources=total_resources,
            active_types=len(resource_counts),
            patient_count=store.count("Patient"),
            supported_types=len(SUPPORTED_TYPES),
            resource_counts=resource_counts,
        )

        return templates.TemplateResponse("pages/home.html", context)

    @router.get("/resources", response_class=HTMLResponse, name="ui_resource_types")
    async def resource_types(request: Request) -> HTMLResponse:
        """List all resource types by category."""
        # Build categorized resource list with counts
        categories: dict[str, list[dict[str, Any]]] = {}

        for category, types in RESOURCE_CATEGORIES.items():
            category_types = []
            for resource_type in types:
                if resource_type in SUPPORTED_TYPES:
                    category_types.append(
                        {
                            "name": resource_type,
                            "count": store.count(resource_type),
                        }
                    )
            if category_types:
                categories[category] = category_types

        context = get_context(
            request,
            supported_types=SUPPORTED_TYPES,
            categories=categories,
        )

        return templates.TemplateResponse("pages/resource_types.html", context)

    # =========================================================================
    # FHIRPath, CQL, CDS Hooks, and Measures Routes
    # NOTE: These MUST be defined BEFORE /{resource_type} to avoid being caught
    # =========================================================================

    @router.get("/fhirpath", response_class=HTMLResponse, name="ui_fhirpath")
    async def fhirpath_playground(request: Request) -> HTMLResponse:
        """FHIRPath expression playground."""
        # Get sample resources for the dropdown
        sample_resources: list[dict[str, Any]] = []
        for resource_type in ["Patient", "Observation", "Condition"]:
            resources, _ = store.search(resource_type, {}, _count=5)
            for r in resources:
                sample_resources.append(
                    {
                        "type": resource_type,
                        "id": r.get("id"),
                        "display": f"{resource_type}/{r.get('id')}",
                    }
                )

        context = get_context(
            request,
            sample_resources=sample_resources,
        )
        return templates.TemplateResponse("pages/fhirpath.html", context)

    @router.get("/cql", response_class=HTMLResponse, name="ui_cql")
    async def cql_workbench(request: Request) -> HTMLResponse:
        """CQL workbench."""
        # Get available Library resources
        libraries, _ = store.search("Library", {}, _count=100)

        context = get_context(
            request,
            libraries=libraries,
        )
        return templates.TemplateResponse("pages/cql.html", context)

    @router.get("/cds-hooks", response_class=HTMLResponse, name="ui_cds_hooks")
    async def cds_hooks_tester(request: Request) -> HTMLResponse:
        """CDS Hooks testing interface."""
        context = get_context(request)
        return templates.TemplateResponse("pages/cds_hooks.html", context)

    @router.get("/measures", response_class=HTMLResponse, name="ui_measures")
    async def measures_dashboard(request: Request) -> HTMLResponse:
        """Measure evaluation dashboard."""
        # Get available Measure resources
        measures, _ = store.search("Measure", {}, _count=100)

        # Get patients for subject selection
        patients, patient_total = store.search("Patient", {}, _count=100)

        context = get_context(
            request,
            measures=measures,
            patients=patients,
            patient_total=patient_total,
        )
        return templates.TemplateResponse("pages/measures.html", context)

    # =========================================================================
    # Resource CRUD Routes (catch-all must come AFTER specific routes)
    # =========================================================================

    @router.get("/{resource_type}", response_class=HTMLResponse, name="ui_resource_list")
    async def resource_list(
        request: Request,
        resource_type: str,
        page: int = 1,
    ) -> Response:
        """List resources of a specific type."""
        if resource_type not in SUPPORTED_TYPES:
            return RedirectResponse(url=request.url_for("ui_resource_types"))

        per_page = settings.ui_resources_per_page

        # Build search parameters from query string
        search_params_dict: dict[str, str | list[str]] = {}
        for key, value in request.query_params.items():
            if key not in ["page"] and value:
                search_params_dict[key] = value

        # Get resources
        resources, total = store.search(
            resource_type,
            search_params_dict,
            _offset=(page - 1) * per_page,
            _count=per_page,
        )

        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        # Get available search params for this type
        type_search_params = SEARCH_PARAMS.get(resource_type, {})
        search_param_list = [
            {"name": name, "type": info.get("type", "string"), "description": name}
            for name, info in type_search_params.items()
            if not name.startswith("_") or name == "_id"
        ]

        context = get_context(
            request,
            resource_type=resource_type,
            resources=resources,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            search_params=search_param_list,
        )

        return templates.TemplateResponse("pages/resource_list.html", context)

    @router.get("/{resource_type}/new", response_class=HTMLResponse, name="ui_resource_new")
    async def resource_new(request: Request, resource_type: str) -> Response:
        """Create new resource form."""
        if resource_type not in SUPPORTED_TYPES:
            return RedirectResponse(url=request.url_for("ui_resource_types"))

        # Generate template JSON
        template_json = json.dumps({"resourceType": resource_type}, indent=2)

        context = get_context(
            request,
            resource_type=resource_type,
            resource_id=None,
            is_new=True,
            resource_json=template_json,
            validation_errors=[],
        )

        return templates.TemplateResponse("pages/resource_edit.html", context)

    @router.post("/{resource_type}/new", response_class=HTMLResponse, name="ui_resource_create")
    async def resource_create(
        request: Request,
        resource_type: str,
        resource_json: str = Form(...),
    ) -> Response:
        """Create a new resource."""
        if resource_type not in SUPPORTED_TYPES:
            return RedirectResponse(url=request.url_for("ui_resource_types"))

        validation_errors = []

        try:
            resource = json.loads(resource_json)

            # Validate resourceType
            if resource.get("resourceType") != resource_type:
                validation_errors.append(f"resourceType must be '{resource_type}'")
            else:
                # Create the resource
                created = store.create(resource)
                return RedirectResponse(
                    url=request.url_for(
                        "ui_resource_detail",
                        resource_type=resource_type,
                        resource_id=created["id"],
                    ),
                    status_code=303,
                )

        except json.JSONDecodeError as e:
            validation_errors.append(f"Invalid JSON: {e}")
        except Exception as e:
            validation_errors.append(str(e))

        context = get_context(
            request,
            resource_type=resource_type,
            resource_id=None,
            is_new=True,
            resource_json=resource_json,
            validation_errors=validation_errors,
        )

        return templates.TemplateResponse("pages/resource_edit.html", context)

    @router.get("/{resource_type}/{resource_id}", response_class=HTMLResponse, name="ui_resource_detail")
    async def resource_detail(
        request: Request,
        resource_type: str,
        resource_id: str,
    ) -> Response:
        """View a specific resource."""
        if resource_type not in SUPPORTED_TYPES:
            return RedirectResponse(url=request.url_for("ui_resource_types"))

        resource = store.read(resource_type, resource_id)
        if not resource:
            return RedirectResponse(url=request.url_for("ui_resource_list", resource_type=resource_type))

        # Extract references from resource
        references = _extract_references(resource)

        context = get_context(
            request,
            resource_type=resource_type,
            resource=resource,
            resource_json=json.dumps(resource, indent=2),
            references=references,
        )

        return templates.TemplateResponse("pages/resource_detail.html", context)

    @router.get("/{resource_type}/{resource_id}/edit", response_class=HTMLResponse, name="ui_resource_edit")
    async def resource_edit(
        request: Request,
        resource_type: str,
        resource_id: str,
    ) -> Response:
        """Edit resource form."""
        if resource_type not in SUPPORTED_TYPES:
            return RedirectResponse(url=request.url_for("ui_resource_types"))

        resource = store.read(resource_type, resource_id)
        if not resource:
            return RedirectResponse(url=request.url_for("ui_resource_list", resource_type=resource_type))

        context = get_context(
            request,
            resource_type=resource_type,
            resource_id=resource_id,
            is_new=False,
            resource_json=json.dumps(resource, indent=2),
            validation_errors=[],
        )

        return templates.TemplateResponse("pages/resource_edit.html", context)

    @router.post("/{resource_type}/{resource_id}/edit", response_class=HTMLResponse, name="ui_resource_update")
    async def resource_update(
        request: Request,
        resource_type: str,
        resource_id: str,
        resource_json: str = Form(...),
    ) -> Response:
        """Update a resource."""
        if resource_type not in SUPPORTED_TYPES:
            return RedirectResponse(url=request.url_for("ui_resource_types"))

        validation_errors = []

        try:
            resource = json.loads(resource_json)

            # Validate resourceType
            if resource.get("resourceType") != resource_type:
                validation_errors.append(f"resourceType must be '{resource_type}'")
            elif resource.get("id") != resource_id:
                validation_errors.append(f"Resource ID must be '{resource_id}'")
            else:
                # Update the resource
                store.update(resource_type, resource_id, resource)
                return RedirectResponse(
                    url=request.url_for(
                        "ui_resource_detail",
                        resource_type=resource_type,
                        resource_id=resource_id,
                    ),
                    status_code=303,
                )

        except json.JSONDecodeError as e:
            validation_errors.append(f"Invalid JSON: {e}")
        except Exception as e:
            validation_errors.append(str(e))

        context = get_context(
            request,
            resource_type=resource_type,
            resource_id=resource_id,
            is_new=False,
            resource_json=resource_json,
            validation_errors=validation_errors,
        )

        return templates.TemplateResponse("pages/resource_edit.html", context)

    @router.post("/{resource_type}/{resource_id}/delete", name="ui_resource_delete")
    async def resource_delete(
        request: Request,
        resource_type: str,
        resource_id: str,
    ) -> RedirectResponse:
        """Delete a resource."""
        if resource_type in SUPPORTED_TYPES:
            store.delete(resource_type, resource_id)

        return RedirectResponse(
            url=request.url_for("ui_resource_list", resource_type=resource_type),
            status_code=303,
        )

    @router.get("/{resource_type}/{resource_id}/history", response_class=HTMLResponse, name="ui_resource_history")
    async def resource_history(
        request: Request,
        resource_type: str,
        resource_id: str,
    ) -> Response:
        """View resource version history."""
        if resource_type not in SUPPORTED_TYPES:
            return RedirectResponse(url=request.url_for("ui_resource_types"))

        # Get history (returns list of resource versions)
        versions = store.history(resource_type, resource_id)

        context = get_context(
            request,
            resource_type=resource_type,
            resource_id=resource_id,
            versions=versions,
            versions_json=json.dumps(versions),
        )

        return templates.TemplateResponse("pages/resource_history.html", context)

    return router


def _extract_references(resource: dict[str, Any], path: str = "") -> list[dict[str, str]]:
    """Extract all references from a resource.

    Args:
        resource: FHIR resource dict
        path: Current path (for recursion)

    Returns:
        List of reference info dicts
    """
    references = []

    for key, value in resource.items():
        current_path = f"{path}.{key}" if path else key

        if key == "reference" and isinstance(value, str) and "/" in value:
            # Found a reference
            parts = value.split("/")
            if len(parts) >= 2:
                ref_type = parts[-2]
                ref_id = parts[-1]
                # Remove path suffix like ".subject" -> "subject"
                clean_path = current_path.replace(".reference", "")
                references.append(
                    {
                        "path": clean_path,
                        "type": ref_type,
                        "id": ref_id,
                        "reference": value,
                    }
                )

        elif isinstance(value, dict):
            references.extend(_extract_references(value, current_path))

        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    references.extend(_extract_references(item, f"{current_path}[{i}]"))

    return references
