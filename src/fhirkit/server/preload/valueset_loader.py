"""ValueSet and CodeSystem preloader.

Loads FHIR ValueSet and CodeSystem resources from JSON files.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Supported resource types for loading
TERMINOLOGY_TYPES = {"ValueSet", "CodeSystem", "ConceptMap", "NamingSystem"}


def load_json_resource(file_path: Path) -> dict[str, Any] | None:
    """Load a FHIR resource from a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        The FHIR resource dict, or None if not a valid resource
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            resource = json.load(f)

        # Validate it's a FHIR resource
        if not isinstance(resource, dict):
            logger.warning(f"File is not a JSON object: {file_path}")
            return None

        resource_type = resource.get("resourceType")
        if not resource_type:
            logger.warning(f"File does not have resourceType: {file_path}")
            return None

        return resource

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return None


def load_bundle(file_path: Path) -> list[dict[str, Any]]:
    """Load resources from a FHIR Bundle file.

    Args:
        file_path: Path to the Bundle JSON file

    Returns:
        List of resources from the bundle
    """
    resource = load_json_resource(file_path)
    if resource is None:
        return []

    if resource.get("resourceType") != "Bundle":
        # Single resource, not a bundle
        return [resource] if resource.get("resourceType") in TERMINOLOGY_TYPES else []

    # Extract resources from bundle entries
    resources = []
    for entry in resource.get("entry", []):
        entry_resource = entry.get("resource")
        if entry_resource and entry_resource.get("resourceType") in TERMINOLOGY_TYPES:
            resources.append(entry_resource)

    return resources


def load_valueset_directory(
    directory: str | Path,
    include_codesystems: bool = True,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Load all ValueSets and CodeSystems from a directory.

    Args:
        directory: Path to directory containing JSON files
        include_codesystems: Whether to also load CodeSystem resources

    Returns:
        Tuple of (valuesets, codesystems)
    """
    directory = Path(directory)
    valuesets: list[dict[str, Any]] = []
    codesystems: list[dict[str, Any]] = []

    if not directory.exists():
        logger.warning(f"Terminology directory does not exist: {directory}")
        return valuesets, codesystems

    # Find all JSON files
    json_files = list(directory.glob("**/*.json"))
    logger.info(f"Found {len(json_files)} JSON files in {directory}")

    for json_file in json_files:
        try:
            resources = load_bundle(json_file)
            for resource in resources:
                resource_type = resource.get("resourceType")
                if resource_type == "ValueSet":
                    valuesets.append(resource)
                    logger.debug(f"Loaded ValueSet: {resource.get('url', resource.get('id'))}")
                elif resource_type == "CodeSystem" and include_codesystems:
                    codesystems.append(resource)
                    logger.debug(f"Loaded CodeSystem: {resource.get('url', resource.get('id'))}")
        except Exception as e:
            logger.error(f"Error loading {json_file}: {e}")

    logger.info(f"Loaded {len(valuesets)} ValueSets and {len(codesystems)} CodeSystems")
    return valuesets, codesystems


def load_fhir_directory(
    directory: str | Path,
) -> dict[str, list[dict[str, Any]]]:
    """Load all FHIR resources from a directory.

    Supports any FHIR resource type, organizing by resourceType.

    Args:
        directory: Path to directory containing JSON files

    Returns:
        Dict mapping resource type to list of resources
    """
    directory = Path(directory)
    resources_by_type: dict[str, list[dict[str, Any]]] = {}

    if not directory.exists():
        logger.warning(f"FHIR directory does not exist: {directory}")
        return resources_by_type

    # Find all JSON files
    json_files = list(directory.glob("**/*.json"))
    logger.info(f"Found {len(json_files)} JSON files in {directory}")

    for json_file in json_files:
        try:
            resource = load_json_resource(json_file)
            if resource is None:
                continue

            resource_type = resource.get("resourceType")
            if not resource_type:
                continue

            # Handle bundles specially
            if resource_type == "Bundle":
                for entry in resource.get("entry", []):
                    entry_resource = entry.get("resource")
                    if entry_resource:
                        entry_type = entry_resource.get("resourceType")
                        if entry_type:
                            if entry_type not in resources_by_type:
                                resources_by_type[entry_type] = []
                            resources_by_type[entry_type].append(entry_resource)
            else:
                if resource_type not in resources_by_type:
                    resources_by_type[resource_type] = []
                resources_by_type[resource_type].append(resource)

        except Exception as e:
            logger.error(f"Error loading {json_file}: {e}")

    # Log summary
    total = sum(len(resources) for resources in resources_by_type.values())
    logger.info(f"Loaded {total} resources of {len(resources_by_type)} types")
    for resource_type, resources in resources_by_type.items():
        logger.debug(f"  {resource_type}: {len(resources)}")

    return resources_by_type


def load_single_file(file_path: str | Path) -> list[dict[str, Any]]:
    """Load FHIR resources from a single JSON file.

    Handles both single resources and bundles.

    Args:
        file_path: Path to the JSON file

    Returns:
        List of FHIR resources
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    resource = load_json_resource(file_path)
    if resource is None:
        return []

    # Handle bundles
    if resource.get("resourceType") == "Bundle":
        resources = []
        for entry in resource.get("entry", []):
            entry_resource = entry.get("resource")
            if entry_resource:
                resources.append(entry_resource)
        return resources

    return [resource]
