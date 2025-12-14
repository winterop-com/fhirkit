"""ConceptMap $translate operation implementation.

Provides code translation between different code systems using ConceptMap resources.
"""

from typing import Any

from ..storage.fhir_store import FHIRStore


class ConceptMapTranslator:
    """Translator for codes using ConceptMap resources.

    Implements the FHIR $translate operation per:
    https://hl7.org/fhir/R4/conceptmap-operation-translate.html
    """

    def __init__(self, store: FHIRStore):
        """Initialize the translator.

        Args:
            store: FHIR store containing ConceptMap resources
        """
        self.store = store

    def translate(
        self,
        code: str,
        system: str,
        target: str | None = None,
        concept_map_url: str | None = None,
        concept_map_id: str | None = None,
        reverse: bool = False,
    ) -> dict[str, Any]:
        """Translate a code using ConceptMap resources.

        Args:
            code: The code to translate
            system: The source code system URI
            target: The target code system URI (optional)
            concept_map_url: Specific ConceptMap URL to use
            concept_map_id: Specific ConceptMap ID to use
            reverse: If True, translate in reverse direction

        Returns:
            Parameters resource with translation results
        """
        # Get relevant ConceptMaps
        concept_maps = self._get_concept_maps(system, target, concept_map_url, concept_map_id)

        if not concept_maps:
            return self._build_parameters(result=False, message="No suitable ConceptMap found")

        # Find all matches across concept maps
        matches: list[dict[str, Any]] = []

        for concept_map in concept_maps:
            map_matches = self._find_translations(concept_map, code, system, target, reverse)
            matches.extend(map_matches)

        if not matches:
            return self._build_parameters(
                result=False,
                message=f"No translation found for code '{code}' in system '{system}'",
            )

        return self._build_parameters(result=True, matches=matches)

    def _get_concept_maps(
        self,
        source_system: str,
        target_system: str | None,
        concept_map_url: str | None,
        concept_map_id: str | None,
    ) -> list[dict[str, Any]]:
        """Get ConceptMaps matching the criteria.

        Args:
            source_system: Source code system URI
            target_system: Target code system URI
            concept_map_url: Specific URL to match
            concept_map_id: Specific ID to match

        Returns:
            List of matching ConceptMap resources
        """
        # If specific ID provided, get that ConceptMap
        if concept_map_id:
            cm = self.store.read("ConceptMap", concept_map_id)
            if cm:
                return [cm]
            return []

        # Get all ConceptMaps
        all_maps, _ = self.store.search("ConceptMap", {})

        # Filter by criteria
        matches = []
        for cm in all_maps:
            # Check URL match
            if concept_map_url and cm.get("url") != concept_map_url:
                continue

            # Check source system match
            source_uri = cm.get("sourceUri", "")
            if source_uri and source_uri != source_system:
                # Also check groups
                groups = cm.get("group", [])
                source_match = any(g.get("source") == source_system for g in groups)
                if not source_match:
                    continue

            # Check target system match if specified
            if target_system:
                target_uri = cm.get("targetUri", "")
                if target_uri and target_uri != target_system:
                    groups = cm.get("group", [])
                    target_match = any(g.get("target") == target_system for g in groups)
                    if not target_match:
                        continue

            matches.append(cm)

        return matches

    def _find_translations(
        self,
        concept_map: dict[str, Any],
        code: str,
        system: str,
        target_system: str | None,
        reverse: bool,
    ) -> list[dict[str, Any]]:
        """Find translations for a code in a ConceptMap.

        Args:
            concept_map: ConceptMap resource
            code: Code to translate
            system: Source system
            target_system: Target system (optional)
            reverse: Whether to translate in reverse

        Returns:
            List of match dictionaries
        """
        matches = []

        for group in concept_map.get("group", []):
            group_source = group.get("source", "")
            group_target = group.get("target", "")

            # Handle reverse translation
            if reverse:
                if group_target != system:
                    continue
                if target_system and group_source != target_system:
                    continue
            else:
                if group_source != system:
                    continue
                if target_system and group_target != target_system:
                    continue

            # Search elements for the code
            for element in group.get("element", []):
                if reverse:
                    # Look in targets for the code
                    for target in element.get("target", []):
                        if target.get("code") == code:
                            matches.append(
                                {
                                    "equivalence": target.get("equivalence", "equivalent"),
                                    "concept": {
                                        "system": group_source,
                                        "code": element.get("code"),
                                        "display": element.get("display"),
                                    },
                                    "source": concept_map.get("url"),
                                }
                            )
                else:
                    if element.get("code") == code:
                        for target in element.get("target", []):
                            matches.append(
                                {
                                    "equivalence": target.get("equivalence", "equivalent"),
                                    "concept": {
                                        "system": group_target,
                                        "code": target.get("code"),
                                        "display": target.get("display"),
                                    },
                                    "source": concept_map.get("url"),
                                }
                            )

        return matches

    def _build_parameters(
        self,
        result: bool,
        matches: list[dict[str, Any]] | None = None,
        message: str | None = None,
    ) -> dict[str, Any]:
        """Build a Parameters response.

        Args:
            result: Whether translation was successful
            matches: List of translation matches
            message: Error/info message

        Returns:
            Parameters resource
        """
        parameters: dict[str, Any] = {
            "resourceType": "Parameters",
            "parameter": [
                {"name": "result", "valueBoolean": result},
            ],
        }

        if message:
            parameters["parameter"].append({"name": "message", "valueString": message})

        if matches:
            for match in matches:
                match_param: dict[str, Any] = {
                    "name": "match",
                    "part": [
                        {"name": "equivalence", "valueCode": match["equivalence"]},
                        {
                            "name": "concept",
                            "valueCoding": match["concept"],
                        },
                    ],
                }

                if match.get("source"):
                    match_param["part"].append({"name": "source", "valueUri": match["source"]})

                parameters["parameter"].append(match_param)

        return parameters
