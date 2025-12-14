"""CQL Library preloader.

Loads CQL files from a directory and creates FHIR Library resources.
"""

import base64
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def parse_cql_metadata(cql_content: str) -> dict[str, Any]:
    """Extract metadata from CQL library content.

    Args:
        cql_content: The CQL source code

    Returns:
        Dict with name, version, and other metadata
    """
    metadata: dict[str, Any] = {}

    # Extract library name and version
    # Pattern: library "Name" version '1.0.0'
    library_match = re.search(
        r"library\s+[\"']?(\w+)[\"']?\s+version\s+[\"']([^\"']+)[\"']",
        cql_content,
        re.IGNORECASE,
    )
    if library_match:
        metadata["name"] = library_match.group(1)
        metadata["version"] = library_match.group(2)
    else:
        # Try without version
        library_match = re.search(r"library\s+[\"']?(\w+)[\"']?", cql_content, re.IGNORECASE)
        if library_match:
            metadata["name"] = library_match.group(1)
            metadata["version"] = "1.0.0"

    # Extract using statements for dependencies
    using_matches = re.findall(
        r"using\s+(\w+)\s+version\s+[\"']([^\"']+)[\"']",
        cql_content,
        re.IGNORECASE,
    )
    if using_matches:
        metadata["using"] = [{"model": m[0], "version": m[1]} for m in using_matches]

    # Extract include statements for related libraries
    include_matches = re.findall(
        r"include\s+[\"']?(\w+)[\"']?\s+version\s+[\"']([^\"']+)[\"'](?:\s+called\s+(\w+))?",
        cql_content,
        re.IGNORECASE,
    )
    if include_matches:
        metadata["includes"] = [
            {"name": m[0], "version": m[1], "alias": m[2] if m[2] else m[0]} for m in include_matches
        ]

    # Extract valueset definitions
    valueset_matches = re.findall(
        r"valueset\s+[\"']([^\"']+)[\"']\s*:\s*[\"']([^\"']+)[\"']",
        cql_content,
        re.IGNORECASE,
    )
    if valueset_matches:
        metadata["valuesets"] = [{"name": m[0], "url": m[1]} for m in valueset_matches]

    # Extract codesystem definitions
    codesystem_matches = re.findall(
        r"codesystem\s+[\"']([^\"']+)[\"']\s*:\s*[\"']([^\"']+)[\"']",
        cql_content,
        re.IGNORECASE,
    )
    if codesystem_matches:
        metadata["codesystems"] = [{"name": m[0], "url": m[1]} for m in codesystem_matches]

    return metadata


def create_library_resource(
    cql_content: str,
    file_path: Path,
    base_url: str = "http://example.org/fhir/Library",
) -> dict[str, Any]:
    """Create a FHIR Library resource from CQL content.

    Args:
        cql_content: The CQL source code
        file_path: Path to the CQL file
        base_url: Base URL for library canonical URL

    Returns:
        FHIR Library resource dict
    """
    metadata = parse_cql_metadata(cql_content)

    name = metadata.get("name", file_path.stem)
    version = metadata.get("version", "1.0.0")
    library_id = f"{name}-{version}".replace(".", "-")

    # Create Library resource
    library: dict[str, Any] = {
        "resourceType": "Library",
        "id": library_id,
        "url": f"{base_url}/{name}",
        "version": version,
        "name": name,
        "title": name.replace("-", " ").replace("_", " ").title(),
        "status": "active",
        "type": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/library-type",
                    "code": "logic-library",
                    "display": "Logic Library",
                }
            ]
        },
        "content": [
            {
                "contentType": "text/cql",
                "data": base64.b64encode(cql_content.encode("utf-8")).decode("utf-8"),
            }
        ],
    }

    # Add data requirements for valuesets
    if metadata.get("valuesets"):
        library["dataRequirement"] = []
        for vs in metadata["valuesets"]:
            library["dataRequirement"].append(
                {
                    "type": "CodeableConcept",
                    "codeFilter": [{"path": "code", "valueSet": vs["url"]}],
                }
            )

    # Add related artifacts for includes
    if metadata.get("includes"):
        library["relatedArtifact"] = []
        for inc in metadata["includes"]:
            library["relatedArtifact"].append(
                {
                    "type": "depends-on",
                    "resource": f"{base_url}/{inc['name']}|{inc['version']}",
                }
            )

    return library


def load_cql_directory(
    directory: str | Path,
    base_url: str = "http://example.org/fhir/Library",
) -> list[dict[str, Any]]:
    """Load all CQL files from a directory as Library resources.

    Args:
        directory: Path to directory containing CQL files
        base_url: Base URL for library canonical URLs

    Returns:
        List of FHIR Library resources
    """
    directory = Path(directory)
    libraries: list[dict[str, Any]] = []

    if not directory.exists():
        logger.warning(f"CQL directory does not exist: {directory}")
        return libraries

    # Find all .cql files
    cql_files = list(directory.glob("**/*.cql"))
    logger.info(f"Found {len(cql_files)} CQL files in {directory}")

    for cql_file in cql_files:
        try:
            cql_content = cql_file.read_text(encoding="utf-8")
            library = create_library_resource(cql_content, cql_file, base_url)
            libraries.append(library)
            logger.debug(f"Loaded CQL library: {library['name']} v{library['version']}")
        except Exception as e:
            logger.error(f"Error loading CQL file {cql_file}: {e}")

    logger.info(f"Loaded {len(libraries)} CQL libraries")
    return libraries


def load_cql_file(
    file_path: str | Path,
    base_url: str = "http://example.org/fhir/Library",
) -> dict[str, Any]:
    """Load a single CQL file as a Library resource.

    Args:
        file_path: Path to the CQL file
        base_url: Base URL for library canonical URL

    Returns:
        FHIR Library resource
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"CQL file not found: {file_path}")

    cql_content = file_path.read_text(encoding="utf-8")
    return create_library_resource(cql_content, file_path, base_url)
