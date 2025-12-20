# HL7 Specification Compliance

FHIRKit includes compliance testing against official HL7 test suites for CQL and FHIRPath.

## Running Compliance Tests

```bash
# Run all compliance tests
make compliance

# Run CQL compliance only
make compliance-cql

# Run FHIRPath compliance only
make compliance-fhirpath
```

## Current Compliance Status

### Summary

| Component | Tests | Passed | Failed | Pass Rate |
|-----------|-------|--------|--------|-----------|
| **CQL** | 1,557 | 685 | 872 | 44% |
| **FHIRPath** | 686 | 446 | 240 | 65% |
| **Total** | 2,243 | 1,131 | 1,112 | 50% |

### CQL Compliance by Category

| Category | Tests | Status |
|----------|-------|--------|
| CqlLogicalOperatorsTest | 39 | 38 pass, 1 fail (97%) |
| CqlConditionalOperatorsTest | 9 | Mostly passing |
| CqlNullologicalOperatorsTest | 22 | 12 pass, 10 fail (55%) |
| CqlArithmeticFunctionsTest | 192 | 150 pass, 42 fail (78%) |
| CqlComparisonOperatorsTest | 183 | 125 pass, 58 fail (68%) |
| CqlStringOperatorsTest | 81 | 42 pass, 39 fail (52%) |
| CqlTypeOperatorsTest | 32 | 6 pass, 26 fail (19%) |
| CqlTypesTest | 27 | 3 pass, 24 fail (11%) |
| CqlAggregateFunctionsTest | 39 | 28 pass, 11 fail (72%) |
| CqlAggregateTest | 2 | 0 pass, 2 fail (0%) |
| CqlListOperatorsTest | 207 | 82 pass, 125 fail (40%) |
| CqlIntervalOperatorsTest | 360 | 163 pass, 197 fail (45%) |
| CqlDateTimeOperatorsTest | 294 | 27 pass, 267 fail (9%) |
| CqlErrorsAndMessagingOperatorsTest | 4 | 0 pass, 4 fail (0%) |
| ValueLiteralsAndSelectors | 66 | 0 pass, 66 fail (0%) |

### Key Gap Areas

#### CQL

1. **DateTime Operations** (267 failures)
   - DateTime arithmetic with durations
   - Time zone handling
   - Precision-sensitive comparisons

2. **Interval Operations** (197 failures)
   - Complex interval relationships
   - Null handling in interval bounds
   - Precision handling

3. **List Operations** (125 failures)
   - Some aggregate operations
   - Complex filtering scenarios

4. **Value Literals** (66 failures)
   - Large decimal handling
   - Scientific notation
   - Edge case values

#### FHIRPath

1. **Type Operations** - Type checking and casting edge cases
2. **ConformsTo** - Profile validation requires StructureDefinition
3. **Aggregate** - `aggregate()` function not implemented
4. **Some FHIR-specific functions** - Require deeper FHIR model integration

## Test Suite Sources

- **CQL Tests**: https://cql.hl7.org/tests.html
- **FHIRPath Tests**: https://hl7.org/fhirpath/N1/tests.html

## Implementation Notes

The compliance tests use the official HL7 test XML format. The test runner:

1. Parses XML test files
2. Extracts expressions and expected outputs
3. Evaluates against FHIRKit evaluators
4. Compares results with type-aware comparison

Some tests require input FHIR resources (for FHIRPath) which are loaded from
the test data directory.

## Improving Compliance

To improve compliance:

1. Run `make compliance` to identify failing tests
2. Use `pytest -k "TestName" -v` to debug specific failures
3. Implement missing functionality
4. Re-run compliance to verify fixes

Priority areas for improvement:
- DateTime arithmetic and duration handling
- Interval edge cases
- Large decimal precision
- FHIRPath `aggregate()` function
