"""Tests for CQL With/Without clauses.

Tests cover:
- Basic with clause filtering
- Basic without clause filtering
- With clause with FHIR Retrieve
- Without clause with FHIR Retrieve
- Multiple with/without clauses
- Complex conditions in such that
"""

from fhirkit.engine.cql import CQLEvaluator
from fhirkit.engine.cql.context import DataSource


class MockDataSource(DataSource):
    """Mock data source for testing."""

    def __init__(self, data: dict):
        self.data = data

    def retrieve(self, resource_type, codes=None, valueset=None, code_path=None, context=None):
        return self.data.get(resource_type, [])


class TestWithClause:
    """Test CQL with clause."""

    def setup_method(self):
        """Set up test fixtures."""
        self.evaluator = CQLEvaluator()

    def test_with_clause_basic(self):
        """Test basic with clause filtering."""
        cql = """
        define Orders: {
            Tuple { id: '1', patientId: 'P1' },
            Tuple { id: '2', patientId: 'P2' },
            Tuple { id: '3', patientId: 'P3' }
        }

        define Patients: {
            Tuple { id: 'P1', name: 'Alice' },
            Tuple { id: 'P2', name: 'Bob' }
        }

        define OrdersWithPatient:
            from Orders O
            with Patients P
            such that O.patientId = P.id
            return O.id
        """
        self.evaluator.compile(cql)
        result = self.evaluator.evaluate_definition("OrdersWithPatient", {})
        assert sorted(result) == ["1", "2"]

    def test_with_clause_no_matches(self):
        """Test with clause when no items match."""
        cql = """
        define Items: { Tuple { id: '1', ref: 'X' }, Tuple { id: '2', ref: 'Y' } }
        define Related: { Tuple { id: 'A' }, Tuple { id: 'B' } }

        define Filtered:
            from Items I
            with Related R
            such that I.ref = R.id
            return I.id
        """
        self.evaluator.compile(cql)
        result = self.evaluator.evaluate_definition("Filtered", {})
        assert result == []

    def test_with_clause_all_match(self):
        """Test with clause when all items match."""
        cql = """
        define Items: {
            Tuple { id: '1', category: 'A' },
            Tuple { id: '2', category: 'A' }
        }
        define Categories: { Tuple { code: 'A' }, Tuple { code: 'B' } }

        define Filtered:
            from Items I
            with Categories C
            such that I.category = C.code
            return I.id
        """
        self.evaluator.compile(cql)
        result = self.evaluator.evaluate_definition("Filtered", {})
        assert sorted(result) == ["1", "2"]

    def test_with_clause_complex_condition(self):
        """Test with clause with complex such that condition."""
        cql = """
        define Events: {
            Tuple { id: '1', start: 5, end: 10 },
            Tuple { id: '2', start: 15, end: 20 },
            Tuple { id: '3', start: 25, end: 30 }
        }
        define Windows: { Tuple { low: 1, high: 12 } }

        define EventsInWindow:
            from Events E
            with Windows W
            such that E.start >= W.low and E.end <= W.high
            return E.id
        """
        self.evaluator.compile(cql)
        result = self.evaluator.evaluate_definition("EventsInWindow", {})
        assert result == ["1"]


class TestWithoutClause:
    """Test CQL without clause."""

    def setup_method(self):
        """Set up test fixtures."""
        self.evaluator = CQLEvaluator()

    def test_without_clause_basic(self):
        """Test basic without clause filtering."""
        cql = """
        define Orders: {
            Tuple { id: '1', patientId: 'P1' },
            Tuple { id: '2', patientId: 'P2' },
            Tuple { id: '3', patientId: 'P3' }
        }

        define Patients: {
            Tuple { id: 'P1', name: 'Alice' },
            Tuple { id: 'P2', name: 'Bob' }
        }

        define OrdersWithoutPatient:
            from Orders O
            without Patients P
            such that O.patientId = P.id
            return O.id
        """
        self.evaluator.compile(cql)
        result = self.evaluator.evaluate_definition("OrdersWithoutPatient", {})
        assert result == ["3"]

    def test_without_clause_all_excluded(self):
        """Test without clause when all items have matches."""
        cql = """
        define Items: {
            Tuple { id: '1', ref: 'A' },
            Tuple { id: '2', ref: 'B' }
        }
        define Related: { Tuple { id: 'A' }, Tuple { id: 'B' } }

        define Filtered:
            from Items I
            without Related R
            such that I.ref = R.id
            return I.id
        """
        self.evaluator.compile(cql)
        result = self.evaluator.evaluate_definition("Filtered", {})
        assert result == []

    def test_without_clause_none_excluded(self):
        """Test without clause when no items have matches."""
        cql = """
        define Items: {
            Tuple { id: '1', ref: 'X' },
            Tuple { id: '2', ref: 'Y' }
        }
        define Related: { Tuple { id: 'A' }, Tuple { id: 'B' } }

        define Filtered:
            from Items I
            without Related R
            such that I.ref = R.id
            return I.id
        """
        self.evaluator.compile(cql)
        result = self.evaluator.evaluate_definition("Filtered", {})
        assert sorted(result) == ["1", "2"]


class TestWithClauseFHIR:
    """Test with clause with FHIR Retrieve expressions."""

    def test_encounters_with_conditions(self):
        """Test finding encounters that have associated conditions."""
        data = {
            "Encounter": [
                {"resourceType": "Encounter", "id": "E1", "subject": {"reference": "Patient/P1"}},
                {"resourceType": "Encounter", "id": "E2", "subject": {"reference": "Patient/P2"}},
                {"resourceType": "Encounter", "id": "E3", "subject": {"reference": "Patient/P3"}},
            ],
            "Condition": [
                {"resourceType": "Condition", "id": "C1", "encounter": {"reference": "Encounter/E1"}},
                {"resourceType": "Condition", "id": "C2", "encounter": {"reference": "Encounter/E1"}},
            ],
        }
        data_source = MockDataSource(data)
        evaluator = CQLEvaluator(data_source=data_source)

        cql = """
        library Test version '1.0.0'
        using FHIR version '4.0.1'

        define EncountersWithConditions:
            from [Encounter] E
            with [Condition] C
            such that C.encounter.reference = 'Encounter/' + E.id
            return E.id
        """
        evaluator.compile(cql)
        result = evaluator.evaluate_definition("EncountersWithConditions", {})
        assert result == ["E1"]

    def test_patients_with_observations(self):
        """Test finding patients that have observations."""
        data = {
            "Patient": [
                {"resourceType": "Patient", "id": "P1", "name": [{"family": "Smith"}]},
                {"resourceType": "Patient", "id": "P2", "name": [{"family": "Jones"}]},
            ],
            "Observation": [
                {"resourceType": "Observation", "id": "O1", "subject": {"reference": "Patient/P1"}},
            ],
        }
        data_source = MockDataSource(data)
        evaluator = CQLEvaluator(data_source=data_source)

        cql = """
        library Test version '1.0.0'
        using FHIR version '4.0.1'

        define PatientsWithObs:
            from [Patient] P
            with [Observation] O
            such that O.subject.reference = 'Patient/' + P.id
            return P.id
        """
        evaluator.compile(cql)
        result = evaluator.evaluate_definition("PatientsWithObs", {})
        assert result == ["P1"]


class TestWithoutClauseFHIR:
    """Test without clause with FHIR Retrieve expressions."""

    def test_encounters_without_conditions(self):
        """Test finding encounters that don't have conditions."""
        data = {
            "Encounter": [
                {"resourceType": "Encounter", "id": "E1"},
                {"resourceType": "Encounter", "id": "E2"},
                {"resourceType": "Encounter", "id": "E3"},
            ],
            "Condition": [
                {"resourceType": "Condition", "id": "C1", "encounter": {"reference": "Encounter/E1"}},
            ],
        }
        data_source = MockDataSource(data)
        evaluator = CQLEvaluator(data_source=data_source)

        cql = """
        library Test version '1.0.0'
        using FHIR version '4.0.1'

        define EncountersWithoutConditions:
            from [Encounter] E
            without [Condition] C
            such that C.encounter.reference = 'Encounter/' + E.id
            return E.id
        """
        evaluator.compile(cql)
        result = evaluator.evaluate_definition("EncountersWithoutConditions", {})
        assert sorted(result) == ["E2", "E3"]


class TestMultipleClauses:
    """Test multiple with/without clauses."""

    def setup_method(self):
        """Set up test fixtures."""
        self.evaluator = CQLEvaluator()

    def test_with_and_where(self):
        """Test combining with clause and where clause."""
        cql = """
        define Orders: {
            Tuple { id: '1', patientId: 'P1', status: 'active' },
            Tuple { id: '2', patientId: 'P1', status: 'completed' },
            Tuple { id: '3', patientId: 'P2', status: 'active' }
        }

        define Patients: { Tuple { id: 'P1' } }

        define ActiveOrdersWithPatient:
            from Orders O
            with Patients P
            such that O.patientId = P.id
            where O.status = 'active'
            return O.id
        """
        self.evaluator.compile(cql)
        result = self.evaluator.evaluate_definition("ActiveOrdersWithPatient", {})
        assert result == ["1"]

    def test_multiple_with_clauses(self):
        """Test multiple with clauses in same query."""
        cql = """
        define Items: {
            Tuple { id: '1', catA: 'A1', catB: 'B1' },
            Tuple { id: '2', catA: 'A1', catB: 'B2' },
            Tuple { id: '3', catA: 'A2', catB: 'B1' }
        }
        define CatA: { Tuple { code: 'A1' } }
        define CatB: { Tuple { code: 'B1' } }

        define FilteredItems:
            from Items I
            with CatA A such that I.catA = A.code
            with CatB B such that I.catB = B.code
            return I.id
        """
        self.evaluator.compile(cql)
        result = self.evaluator.evaluate_definition("FilteredItems", {})
        # Only item 1 matches both A1 and B1
        assert result == ["1"]

    def test_with_empty_related(self):
        """Test with clause when related source is empty."""
        cql = """
        define Items: { Tuple { id: '1' }, Tuple { id: '2' } }
        define Related: List<Tuple { id String }> { }

        define Filtered:
            from Items I
            with Related R
            such that I.id = R.id
            return I.id
        """
        self.evaluator.compile(cql)
        result = self.evaluator.evaluate_definition("Filtered", {})
        assert result == []

    def test_without_empty_related(self):
        """Test without clause when related source is empty."""
        cql = """
        define Items: { Tuple { id: '1' }, Tuple { id: '2' } }
        define Related: List<Tuple { id String }> { }

        define Filtered:
            from Items I
            without Related R
            such that I.id = R.id
            return I.id
        """
        self.evaluator.compile(cql)
        result = self.evaluator.evaluate_definition("Filtered", {})
        assert sorted(result) == ["1", "2"]
