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
| **CQL** | 1,558 | 973 | 585 | 62% |
| **FHIRPath** | 688 | 471 | 217 | 68% |
| **Total** | 2,246 | 1,444 | 802 | 64% |

### CQL Compliance by Category

| Category | Failures | Notes |
|----------|----------|-------|
| CqlLogicalOperatorsTest | 1 | 97% passing |
| CqlConditionalOperatorsTest | 0 | Fully passing |
| CqlNullologicalOperatorsTest | 9 | Some null edge cases |
| CqlArithmeticFunctionsTest | 32 | Large decimal edge cases |
| CqlComparisonOperatorsTest | 30 | Precision comparisons |
| CqlStringOperatorsTest | 39 | Some string functions |
| CqlTypeOperatorsTest | 18 | Type conversions |
| CqlTypesTest | 17 | Type handling |
| CqlAggregateFunctionsTest | 8 | Most aggregates work |
| CqlAggregateTest | 2 | `aggregate()` function |
| CqlListOperatorsTest | 121 | List operations |
| CqlIntervalOperatorsTest | 134 | Interval relationships |
| CqlDateTimeOperatorsTest | 104 | Timezone, precision |
| CqlErrorsAndMessagingOperatorsTest | 4 | Error handling |
| ValueLiteralsAndSelectors | 66 | Large decimals |

### Key Gap Areas

#### CQL

1. **Interval Operations** (134 failures)
   - Complex interval relationships
   - Null handling in interval bounds
   - Precision handling

2. **List Operations** (121 failures)
   - Some aggregate operations
   - Complex filtering scenarios

3. **DateTime Operations** (104 failures)
   - Timezone-aware comparisons
   - Precision-sensitive operations
   - Some edge cases

4. **Value Literals** (66 failures)
   - Large decimal handling (10^28)
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
- Interval edge cases and relationships
- List operation edge cases
- Large decimal precision
- FHIRPath `aggregate()` function
