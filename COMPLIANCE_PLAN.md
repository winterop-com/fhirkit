# Compliance Improvement Plan

## Current Status

**Overall: 1,611 / 2,246 tests passing (71.7%)**

| Component | Passed | Failed | Rate |
|-----------|--------|--------|------|
| CQL | 1,140 | 418 | 73% |
| FHIRPath | 471 | 217 | 68% |

---

## CQL Failures by Category

| Category | Failures | Priority | Effort |
|----------|----------|----------|--------|
| Interval Operations | 126 | High | Medium |
| List Operations | 121 | High | Medium |
| DateTime Operations | 105 | Medium | High |
| Value Literals | 66 | Low | Low |
| String Operations | 39 | Medium | Low |
| Arithmetic | 32 | Medium | Low |
| Comparison | 30 | Medium | Medium |
| Type Operations | 18 | Low | Medium |
| Types | 17 | Low | Medium |
| Nullological | 9 | Low | Low |
| Aggregate Functions | 8 | Low | Low |
| Errors/Messaging | 4 | Low | Low |
| Aggregate | 2 | Low | Medium |
| Logical | 1 | Low | Low |

---

## Recommended Fix Order

### Phase 1: High-Impact Quick Wins (Est. +50-80 tests)

1. **String Operations (39 failures)**
   - Missing string functions or edge cases
   - Likely: `Split`, `SplitOnMatches`, unicode handling
   - Fix: Review string_funcs.py, add missing functions

2. **Arithmetic (32 failures)**
   - Likely: Precision issues, overflow handling
   - Fix: Check decimal precision, modulo edge cases

3. **Comparison (30 failures)**
   - Likely: Null handling, type coercion
   - Fix: Review comparison operators in visitor.py

### Phase 2: Core Functionality (Est. +100-150 tests)

4. **List Operations (121 failures)**
   - Key functions: `Flatten`, `Sort`, `IndexOf`, `Slice`
   - Edge cases: Empty lists, null elements
   - Fix: Review list_funcs.py, add missing operations

5. **Interval Operations (126 failures)**
   - Remaining: `Expand`, Quantity intervals, null bounds
   - Fix: Implement expand, add Quantity comparison

### Phase 3: DateTime Completeness (Est. +50-70 tests)

6. **DateTime Operations (105 failures)**
   - Remaining: Timezone arithmetic, precision comparisons
   - "after X of", "before X of" operators
   - Duration/difference edge cases

### Phase 4: Type System (Est. +30-50 tests)

7. **Type Operations (18 + 17 failures)**
   - Type casting edge cases
   - `as`, `is` operators
   - Implicit conversions

### Phase 5: Low Priority (Est. +20-30 tests)

8. **Value Literals (66 failures)**
   - Large decimals (10^28) - may need arbitrary precision
   - Scientific notation parsing

9. **Remaining categories**
   - Nullological, Aggregate, Errors/Messaging

---

## FHIRPath Failures (216)

### Known Issues
- `aggregate()` function not implemented
- `conformsTo()` requires StructureDefinition loading
- Type operations edge cases

### Recommended Fixes
1. Implement `aggregate()` function
2. Review type checking functions
3. Add missing FHIR-specific functions

---

## Implementation Strategy

### For Each Category:

1. Run focused tests: `pytest -k "CategoryName" -v --tb=short`
2. Identify patterns in failures
3. Group by root cause
4. Fix in order of impact
5. Re-run and verify

### Quick Commands:

```bash
# Run specific category
uv run pytest tests/compliance/cql/ -k "CqlStringOperatorsTest" -v --tb=short

# See failure details
uv run pytest tests/compliance/cql/ -k "CategoryName" -v --tb=line 2>&1 | grep -A2 "AssertionError"

# Count remaining
uv run pytest tests/compliance/ --tb=no 2>&1 | tail -1
```

---

## Target Milestones

| Milestone | Tests Passing | Rate |
|-----------|---------------|------|
| Current | 1,452 | 64.6% |
| Phase 1 | ~1,530 | 68% |
| Phase 2 | ~1,680 | 75% |
| Phase 3 | ~1,750 | 78% |
| Phase 4 | ~1,800 | 80% |
| Phase 5 | ~1,850 | 82% |

---

## Notes

- Some failures may be test comparison issues, not evaluator bugs
- Value Literals (66) may require changes to parser/lexer
- Full 100% compliance requires significant timezone support
