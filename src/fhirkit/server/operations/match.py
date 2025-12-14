"""Patient $match operation implementation.

Provides patient matching/deduplication using weighted field comparison.
"""

from typing import Any

from ..storage.fhir_store import FHIRStore


class PatientMatcher:
    """Patient matcher using weighted field comparison.

    Implements the FHIR Patient $match operation per:
    https://hl7.org/fhir/R4/patient-operation-match.html
    """

    # Field weights for scoring (higher = more important)
    WEIGHTS: dict[str, float] = {
        "identifier": 100.0,  # Exact identifier match
        "name.family": 30.0,
        "name.given": 20.0,
        "birthDate": 25.0,
        "gender": 5.0,
        "telecom.phone": 15.0,
        "telecom.email": 15.0,
        "address.postalCode": 10.0,
        "address.line": 5.0,
    }

    # Match grade thresholds
    GRADE_THRESHOLDS = {
        "certain": 0.95,
        "probable": 0.80,
        "possible": 0.60,
    }

    def __init__(self, store: FHIRStore):
        """Initialize the matcher.

        Args:
            store: FHIR store containing Patient resources
        """
        self.store = store

    def match(
        self,
        input_patient: dict[str, Any],
        threshold: float = 0.5,
        count: int = 10,
        only_certain_matches: bool = False,
    ) -> dict[str, Any]:
        """Find patients matching the input patient.

        Args:
            input_patient: Patient resource to match against
            threshold: Minimum score threshold (0.0 - 1.0)
            count: Maximum number of results to return
            only_certain_matches: If True, only return certain matches

        Returns:
            Bundle with matching patients and scores
        """
        # Get all patients from store
        all_patients, _ = self.store.search("Patient", {})

        if not all_patients:
            return self._build_bundle([])

        # Score each patient
        scored_matches: list[tuple[dict[str, Any], float]] = []

        for candidate in all_patients:
            # Skip self-matching (same ID)
            if candidate.get("id") == input_patient.get("id"):
                continue

            score = self._calculate_score(input_patient, candidate)

            if score >= threshold:
                scored_matches.append((candidate, score))

        # Sort by score descending
        scored_matches.sort(key=lambda x: x[1], reverse=True)

        # Apply count limit
        scored_matches = scored_matches[:count]

        # Filter by certain matches if requested
        if only_certain_matches:
            scored_matches = [(p, s) for p, s in scored_matches if s >= self.GRADE_THRESHOLDS["certain"]]

        return self._build_bundle(scored_matches)

    def _calculate_score(self, input_patient: dict[str, Any], candidate: dict[str, Any]) -> float:
        """Calculate match score between two patients.

        Args:
            input_patient: Input patient to match
            candidate: Candidate patient from store

        Returns:
            Score between 0.0 and 1.0
        """
        total_weight = 0.0
        earned_weight = 0.0

        # Check identifier matches (exact match = 100% if any match)
        if self._identifiers_match(input_patient, candidate):
            return 1.0  # Exact identifier match

        # Name matching
        name_score, name_weight = self._score_names(input_patient, candidate)
        earned_weight += name_score
        total_weight += name_weight

        # Birth date matching
        if "birthDate" in input_patient:
            total_weight += self.WEIGHTS["birthDate"]
            if input_patient.get("birthDate") == candidate.get("birthDate"):
                earned_weight += self.WEIGHTS["birthDate"]

        # Gender matching
        if "gender" in input_patient:
            total_weight += self.WEIGHTS["gender"]
            if input_patient.get("gender") == candidate.get("gender"):
                earned_weight += self.WEIGHTS["gender"]

        # Telecom matching
        telecom_score, telecom_weight = self._score_telecom(input_patient, candidate)
        earned_weight += telecom_score
        total_weight += telecom_weight

        # Address matching
        address_score, address_weight = self._score_address(input_patient, candidate)
        earned_weight += address_score
        total_weight += address_weight

        # Calculate final score
        if total_weight == 0:
            return 0.0

        return earned_weight / total_weight

    def _identifiers_match(self, input_patient: dict[str, Any], candidate: dict[str, Any]) -> bool:
        """Check if any identifiers match exactly.

        Args:
            input_patient: Input patient
            candidate: Candidate patient

        Returns:
            True if any identifier matches
        """
        input_ids = input_patient.get("identifier", [])
        candidate_ids = candidate.get("identifier", [])

        for input_id in input_ids:
            input_system = input_id.get("system", "")
            input_value = input_id.get("value", "")

            if not input_value:
                continue

            for cand_id in candidate_ids:
                if cand_id.get("system") == input_system and cand_id.get("value") == input_value:
                    return True

        return False

    def _score_names(self, input_patient: dict[str, Any], candidate: dict[str, Any]) -> tuple[float, float]:
        """Score name matching.

        Args:
            input_patient: Input patient
            candidate: Candidate patient

        Returns:
            Tuple of (earned_weight, total_weight)
        """
        input_names = input_patient.get("name", [])
        candidate_names = candidate.get("name", [])

        if not input_names:
            return 0.0, 0.0

        total_weight = self.WEIGHTS["name.family"] + self.WEIGHTS["name.given"]
        earned_weight = 0.0

        # Find best matching name pair
        best_family_match = False
        best_given_match = False

        for input_name in input_names:
            input_family = (input_name.get("family") or "").lower()
            input_given = [g.lower() for g in input_name.get("given", [])]

            for cand_name in candidate_names:
                cand_family = (cand_name.get("family") or "").lower()
                cand_given = [g.lower() for g in cand_name.get("given", [])]

                # Family name matching
                if input_family and cand_family:
                    if input_family == cand_family:
                        best_family_match = True
                    elif self._fuzzy_match(input_family, cand_family):
                        best_family_match = True

                # Given name matching
                if input_given and cand_given:
                    if any(ig in cand_given for ig in input_given):
                        best_given_match = True
                    elif any(self._fuzzy_match(ig, cg) for ig in input_given for cg in cand_given):
                        best_given_match = True

        if best_family_match:
            earned_weight += self.WEIGHTS["name.family"]
        if best_given_match:
            earned_weight += self.WEIGHTS["name.given"]

        return earned_weight, total_weight

    def _score_telecom(self, input_patient: dict[str, Any], candidate: dict[str, Any]) -> tuple[float, float]:
        """Score telecom (phone/email) matching.

        Args:
            input_patient: Input patient
            candidate: Candidate patient

        Returns:
            Tuple of (earned_weight, total_weight)
        """
        input_telecom = input_patient.get("telecom", [])
        candidate_telecom = candidate.get("telecom", [])

        if not input_telecom:
            return 0.0, 0.0

        total_weight = 0.0
        earned_weight = 0.0

        # Extract phones and emails
        input_phones = {self._normalize_phone(t.get("value", "")) for t in input_telecom if t.get("system") == "phone"}
        input_emails = {(t.get("value") or "").lower() for t in input_telecom if t.get("system") == "email"}

        cand_phones = {
            self._normalize_phone(t.get("value", "")) for t in candidate_telecom if t.get("system") == "phone"
        }
        cand_emails = {(t.get("value") or "").lower() for t in candidate_telecom if t.get("system") == "email"}

        if input_phones:
            total_weight += self.WEIGHTS["telecom.phone"]
            if input_phones & cand_phones:
                earned_weight += self.WEIGHTS["telecom.phone"]

        if input_emails:
            total_weight += self.WEIGHTS["telecom.email"]
            if input_emails & cand_emails:
                earned_weight += self.WEIGHTS["telecom.email"]

        return earned_weight, total_weight

    def _score_address(self, input_patient: dict[str, Any], candidate: dict[str, Any]) -> tuple[float, float]:
        """Score address matching.

        Args:
            input_patient: Input patient
            candidate: Candidate patient

        Returns:
            Tuple of (earned_weight, total_weight)
        """
        input_addresses = input_patient.get("address", [])
        candidate_addresses = candidate.get("address", [])

        if not input_addresses:
            return 0.0, 0.0

        total_weight = self.WEIGHTS["address.postalCode"] + self.WEIGHTS["address.line"]
        earned_weight = 0.0

        # Check postal code and address line matches
        postal_match = False
        line_match = False

        for input_addr in input_addresses:
            input_postal = (input_addr.get("postalCode") or "").replace(" ", "").replace("-", "")
            input_lines = [line.lower() for line in input_addr.get("line", [])]

            for cand_addr in candidate_addresses:
                cand_postal = (cand_addr.get("postalCode") or "").replace(" ", "").replace("-", "")
                cand_lines = [line.lower() for line in cand_addr.get("line", [])]

                if input_postal and cand_postal and input_postal == cand_postal:
                    postal_match = True

                if input_lines and cand_lines:
                    if any(il in cand_lines for il in input_lines):
                        line_match = True

        if postal_match:
            earned_weight += self.WEIGHTS["address.postalCode"]
        if line_match:
            earned_weight += self.WEIGHTS["address.line"]

        return earned_weight, total_weight

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for comparison.

        Args:
            phone: Phone number string

        Returns:
            Normalized phone string (digits only)
        """
        return "".join(c for c in phone if c.isdigit())

    def _fuzzy_match(self, s1: str, s2: str, threshold: float = 0.85) -> bool:
        """Check if two strings match fuzzily (simple Jaro-like).

        Args:
            s1: First string
            s2: Second string
            threshold: Similarity threshold

        Returns:
            True if strings are similar enough
        """
        if not s1 or not s2:
            return False

        # Simple prefix matching for short strings
        if len(s1) <= 3 or len(s2) <= 3:
            return s1 == s2

        # Check if one is prefix of other (common for nicknames)
        if s1.startswith(s2) or s2.startswith(s1):
            return True

        # Simple character overlap ratio
        s1_set = set(s1)
        s2_set = set(s2)
        overlap = len(s1_set & s2_set)
        total = len(s1_set | s2_set)

        return overlap / total >= threshold if total > 0 else False

    def _get_match_grade(self, score: float) -> str:
        """Get match grade based on score.

        Args:
            score: Match score (0.0 - 1.0)

        Returns:
            Match grade string
        """
        if score >= self.GRADE_THRESHOLDS["certain"]:
            return "certain"
        elif score >= self.GRADE_THRESHOLDS["probable"]:
            return "probable"
        elif score >= self.GRADE_THRESHOLDS["possible"]:
            return "possible"
        else:
            return "certainly-not"

    def _build_bundle(self, matches: list[tuple[dict[str, Any], float]]) -> dict[str, Any]:
        """Build response Bundle with matches.

        Args:
            matches: List of (patient, score) tuples

        Returns:
            Bundle resource
        """
        entries = []

        for patient, score in matches:
            grade = self._get_match_grade(score)

            entry: dict[str, Any] = {
                "fullUrl": f"Patient/{patient['id']}",
                "resource": patient,
                "search": {
                    "mode": "match",
                    "score": round(score, 4),
                    "extension": [
                        {
                            "url": "http://hl7.org/fhir/StructureDefinition/match-grade",
                            "valueCode": grade,
                        }
                    ],
                },
            }
            entries.append(entry)

        return {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(entries),
            "entry": entries,
        }
