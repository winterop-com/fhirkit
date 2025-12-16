# ELM Expression Reference

A comprehensive reference for ELM (Expression Logical Model) expression types with examples.

## Table of Contents

1. [Literals](#literals)
2. [Arithmetic Operations](#arithmetic-operations)
3. [Comparison Operations](#comparison-operations)
4. [Boolean Operations](#boolean-operations)
5. [Conditional Operations](#conditional-operations)
6. [String Operations](#string-operations)
7. [Collection Operations](#collection-operations)
8. [Aggregate Operations](#aggregate-operations)
9. [Set Operations](#set-operations)
10. [Type Operations](#type-operations)
11. [Date/Time Operations](#datetime-operations)
12. [Interval Operations](#interval-operations)
13. [Reference Operations](#reference-operations)
14. [Query Operations](#query-operations)
15. [Clinical Operations](#clinical-operations)

---

## Literals

### Integer Literal

```json
{
    "type": "Literal",
    "valueType": "{urn:hl7-org:elm-types:r1}Integer",
    "value": "42"
}
```

CQL equivalent: `42`

### Decimal Literal

```json
{
    "type": "Literal",
    "valueType": "{urn:hl7-org:elm-types:r1}Decimal",
    "value": "3.14159"
}
```

CQL equivalent: `3.14159`

### String Literal

```json
{
    "type": "Literal",
    "valueType": "{urn:hl7-org:elm-types:r1}String",
    "value": "Hello, ELM!"
}
```

CQL equivalent: `'Hello, ELM!'`

### Boolean Literal

```json
{
    "type": "Literal",
    "valueType": "{urn:hl7-org:elm-types:r1}Boolean",
    "value": "true"
}
```

CQL equivalent: `true`

### Null

```json
{
    "type": "Null"
}
```

CQL equivalent: `null`

### List

```json
{
    "type": "List",
    "element": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
    ]
}
```

CQL equivalent: `{1, 2, 3}`

### Tuple

```json
{
    "type": "Tuple",
    "element": [
        {
            "name": "name",
            "value": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "John"}
        },
        {
            "name": "age",
            "value": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "30"}
        }
    ]
}
```

CQL equivalent: `Tuple { name: 'John', age: 30 }`

### Interval

```json
{
    "type": "Interval",
    "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
    "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"},
    "lowClosed": true,
    "highClosed": true
}
```

CQL equivalent: `Interval[1, 10]`

### Quantity

```json
{
    "type": "Quantity",
    "value": 100,
    "unit": "mg"
}
```

CQL equivalent: `100 'mg'`

### Code

```json
{
    "type": "Code",
    "code": "2339-0",
    "system": {"name": "LOINC"},
    "display": "Glucose"
}
```

CQL equivalent: `Code '2339-0' from "LOINC" display 'Glucose'`

### Concept

```json
{
    "type": "Concept",
    "code": [
        {"code": "44054006", "system": {"name": "SNOMED"}}
    ],
    "display": "Type 2 diabetes"
}
```

CQL equivalent: `Concept { Code '44054006' from "SNOMED" } display 'Type 2 diabetes'`

---

## Arithmetic Operations

### Add

```json
{
    "type": "Add",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
    ]
}
```

CQL equivalent: `5 + 3` (Result: 8)

### Subtract

```json
{
    "type": "Subtract",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "4"}
    ]
}
```

CQL equivalent: `10 - 4` (Result: 6)

### Multiply

```json
{
    "type": "Multiply",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "6"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "7"}
    ]
}
```

CQL equivalent: `6 * 7` (Result: 42)

### Divide

```json
{
    "type": "Divide",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Decimal", "value": "10.0"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Decimal", "value": "4.0"}
    ]
}
```

CQL equivalent: `10.0 / 4.0` (Result: 2.5)

### TruncatedDivide

```json
{
    "type": "TruncatedDivide",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
    ]
}
```

CQL equivalent: `10 div 3` (Result: 3)

### Modulo

```json
{
    "type": "Modulo",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
    ]
}
```

CQL equivalent: `10 mod 3` (Result: 1)

### Power

```json
{
    "type": "Power",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "8"}
    ]
}
```

CQL equivalent: `Power(2, 8)` (Result: 256)

### Negate

```json
{
    "type": "Negate",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"}
}
```

CQL equivalent: `-5` (Result: -5)

### Abs

```json
{
    "type": "Abs",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "-5"}
}
```

CQL equivalent: `Abs(-5)` (Result: 5)

### Ceiling

```json
{
    "type": "Ceiling",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Decimal", "value": "4.2"}
}
```

CQL equivalent: `Ceiling(4.2)` (Result: 5)

### Floor

```json
{
    "type": "Floor",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Decimal", "value": "4.8"}
}
```

CQL equivalent: `Floor(4.8)` (Result: 4)

### Truncate

```json
{
    "type": "Truncate",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Decimal", "value": "4.8"}
}
```

CQL equivalent: `Truncate(4.8)` (Result: 4)

### Round

```json
{
    "type": "Round",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Decimal", "value": "3.14159"},
    "precision": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"}
}
```

CQL equivalent: `Round(3.14159, 2)` (Result: 3.14)

### Ln (Natural Log)

```json
{
    "type": "Ln",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Decimal", "value": "2.71828"}
}
```

CQL equivalent: `Ln(2.71828)` (Result: ~1.0)

### Log

```json
{
    "type": "Log",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Decimal", "value": "100"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Decimal", "value": "10"}
    ]
}
```

CQL equivalent: `Log(100, 10)` (Result: 2)

### Exp

```json
{
    "type": "Exp",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Decimal", "value": "1"}
}
```

CQL equivalent: `Exp(1)` (Result: ~2.71828)

### Successor

```json
{
    "type": "Successor",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"}
}
```

CQL equivalent: `successor of 5` (Result: 6)

### Predecessor

```json
{
    "type": "Predecessor",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"}
}
```

CQL equivalent: `predecessor of 5` (Result: 4)

---

## Comparison Operations

### Equal

```json
{
    "type": "Equal",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"}
    ]
}
```

CQL equivalent: `5 = 5` (Result: true)

### NotEqual

```json
{
    "type": "NotEqual",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
    ]
}
```

CQL equivalent: `5 != 3` (Result: true)

### Less

```json
{
    "type": "Less",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"}
    ]
}
```

CQL equivalent: `3 < 5` (Result: true)

### LessOrEqual

```json
{
    "type": "LessOrEqual",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"}
    ]
}
```

CQL equivalent: `5 <= 5` (Result: true)

### Greater

```json
{
    "type": "Greater",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
    ]
}
```

CQL equivalent: `5 > 3` (Result: true)

### GreaterOrEqual

```json
{
    "type": "GreaterOrEqual",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"}
    ]
}
```

CQL equivalent: `5 >= 5` (Result: true)

### Equivalent

```json
{
    "type": "Equivalent",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "abc"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "ABC"}
    ]
}
```

CQL equivalent: `'abc' ~ 'ABC'` (Result: true - case-insensitive)

---

## Boolean Operations

### And

```json
{
    "type": "And",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"}
    ]
}
```

CQL equivalent: `true and true` (Result: true)

### Or

```json
{
    "type": "Or",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "false"}
    ]
}
```

CQL equivalent: `true or false` (Result: true)

### Not

```json
{
    "type": "Not",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "false"}
}
```

CQL equivalent: `not false` (Result: true)

### Xor

```json
{
    "type": "Xor",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "false"}
    ]
}
```

CQL equivalent: `true xor false` (Result: true)

### Implies

```json
{
    "type": "Implies",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"}
    ]
}
```

CQL equivalent: `true implies true` (Result: true)

### IsNull

```json
{
    "type": "IsNull",
    "operand": {"type": "Null"}
}
```

CQL equivalent: `null is null` (Result: true)

### IsTrue

```json
{
    "type": "IsTrue",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"}
}
```

CQL equivalent: `true is true` (Result: true)

### IsFalse

```json
{
    "type": "IsFalse",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "false"}
}
```

CQL equivalent: `false is false` (Result: true)

---

## Conditional Operations

### If

```json
{
    "type": "If",
    "condition": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"},
    "then": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "Yes"},
    "else": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "No"}
}
```

CQL equivalent: `if true then 'Yes' else 'No'` (Result: 'Yes')

### Case

```json
{
    "type": "Case",
    "caseItem": [
        {
            "when": {"type": "Equal", "operand": [
                {"type": "ExpressionRef", "name": "X"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"}
            ]},
            "then": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "One"}
        },
        {
            "when": {"type": "Equal", "operand": [
                {"type": "ExpressionRef", "name": "X"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"}
            ]},
            "then": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "Two"}
        }
    ],
    "else": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "Other"}
}
```

CQL equivalent:
```cql
case
    when X = 1 then 'One'
    when X = 2 then 'Two'
    else 'Other'
end
```

### Coalesce

```json
{
    "type": "Coalesce",
    "operand": [
        {"type": "Null"},
        {"type": "Null"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"}
    ]
}
```

CQL equivalent: `Coalesce(null, null, 5)` (Result: 5)

---

## String Operations

### Concatenate

```json
{
    "type": "Concatenate",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "Hello, "},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "World!"}
    ]
}
```

CQL equivalent: `'Hello, ' + 'World!'` (Result: 'Hello, World!')

### Combine

```json
{
    "type": "Combine",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "a"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "b"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "c"}
        ]
    },
    "separator": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": ","}
}
```

CQL equivalent: `Combine({'a', 'b', 'c'}, ',')` (Result: 'a,b,c')

### Split

```json
{
    "type": "Split",
    "stringToSplit": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "a,b,c"},
    "separator": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": ","}
}
```

CQL equivalent: `Split('a,b,c', ',')` (Result: {'a', 'b', 'c'})

### Length

```json
{
    "type": "Length",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "Hello"}
}
```

CQL equivalent: `Length('Hello')` (Result: 5)

### Upper

```json
{
    "type": "Upper",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "hello"}
}
```

CQL equivalent: `Upper('hello')` (Result: 'HELLO')

### Lower

```json
{
    "type": "Lower",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "HELLO"}
}
```

CQL equivalent: `Lower('HELLO')` (Result: 'hello')

### Substring

```json
{
    "type": "Substring",
    "stringToSub": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "Hello"},
    "startIndex": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "0"},
    "length": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"}
}
```

CQL equivalent: `Substring('Hello', 0, 2)` (Result: 'He')

### StartsWith

```json
{
    "type": "StartsWith",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "Hello"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "He"}
    ]
}
```

CQL equivalent: `StartsWith('Hello', 'He')` (Result: true)

### EndsWith

```json
{
    "type": "EndsWith",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "Hello"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "lo"}
    ]
}
```

CQL equivalent: `EndsWith('Hello', 'lo')` (Result: true)

### Matches

```json
{
    "type": "Matches",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "Hello123"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "^[A-Za-z]+[0-9]+$"}
    ]
}
```

CQL equivalent: `Matches('Hello123', '^[A-Za-z]+[0-9]+$')` (Result: true)

### ReplaceMatches

```json
{
    "type": "ReplaceMatches",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "Hello World"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "World"},
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "ELM"}
    ]
}
```

CQL equivalent: `ReplaceMatches('Hello World', 'World', 'ELM')` (Result: 'Hello ELM')

### PositionOf

```json
{
    "type": "PositionOf",
    "pattern": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "l"},
    "string": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "Hello"}
}
```

CQL equivalent: `PositionOf('l', 'Hello')` (Result: 2)

### LastPositionOf

```json
{
    "type": "LastPositionOf",
    "pattern": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "l"},
    "string": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "Hello"}
}
```

CQL equivalent: `LastPositionOf('l', 'Hello')` (Result: 3)

---

## Collection Operations

### First

```json
{
    "type": "First",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
        ]
    }
}
```

CQL equivalent: `First({1, 2, 3})` (Result: 1)

### Last

```json
{
    "type": "Last",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
        ]
    }
}
```

CQL equivalent: `Last({1, 2, 3})` (Result: 3)

### Indexer

```json
{
    "type": "Indexer",
    "operand": [
        {
            "type": "List",
            "element": [
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "a"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "b"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "c"}
            ]
        },
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"}
    ]
}
```

CQL equivalent: `{'a', 'b', 'c'}[1]` (Result: 'b')

### IndexOf

```json
{
    "type": "IndexOf",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "a"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "b"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "c"}
        ]
    },
    "element": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "b"}
}
```

CQL equivalent: `IndexOf({'a', 'b', 'c'}, 'b')` (Result: 1)

### Exists

```json
{
    "type": "Exists",
    "operand": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"}
        ]
    }
}
```

CQL equivalent: `exists({1})` (Result: true)

### In

```json
{
    "type": "In",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
        {
            "type": "List",
            "element": [
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
            ]
        }
    ]
}
```

CQL equivalent: `2 in {1, 2, 3}` (Result: true)

### Contains

```json
{
    "type": "Contains",
    "operand": [
        {
            "type": "List",
            "element": [
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
            ]
        },
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"}
    ]
}
```

CQL equivalent: `{1, 2, 3} contains 2` (Result: true)

### Distinct

```json
{
    "type": "Distinct",
    "operand": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"}
        ]
    }
}
```

CQL equivalent: `distinct {1, 1, 2}` (Result: {1, 2})

### Flatten

```json
{
    "type": "Flatten",
    "operand": {
        "type": "List",
        "element": [
            {
                "type": "List",
                "element": [
                    {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
                    {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"}
                ]
            },
            {
                "type": "List",
                "element": [
                    {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
                ]
            }
        ]
    }
}
```

CQL equivalent: `flatten {{1, 2}, {3}}` (Result: {1, 2, 3})

### SingletonFrom

```json
{
    "type": "SingletonFrom",
    "operand": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "42"}
        ]
    }
}
```

CQL equivalent: `singleton from {42}` (Result: 42)

### ToList

```json
{
    "type": "ToList",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"}
}
```

CQL equivalent: Converts a single element to a list (Result: {5})

---

## Aggregate Operations

### Count

```json
{
    "type": "Count",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
        ]
    }
}
```

CQL equivalent: `Count({1, 2, 3})` (Result: 3)

### Sum

```json
{
    "type": "Sum",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
        ]
    }
}
```

CQL equivalent: `Sum({1, 2, 3})` (Result: 6)

### Avg

```json
{
    "type": "Avg",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "4"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "6"}
        ]
    }
}
```

CQL equivalent: `Avg({2, 4, 6})` (Result: 4)

### Min

```json
{
    "type": "Min",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "8"}
        ]
    }
}
```

CQL equivalent: `Min({5, 2, 8})` (Result: 2)

### Max

```json
{
    "type": "Max",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "8"}
        ]
    }
}
```

CQL equivalent: `Max({5, 2, 8})` (Result: 8)

### Median

```json
{
    "type": "Median",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "9"}
        ]
    }
}
```

CQL equivalent: `Median({1, 2, 9})` (Result: 2)

### Mode

```json
{
    "type": "Mode",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
        ]
    }
}
```

CQL equivalent: `Mode({1, 2, 2, 3})` (Result: 2)

### StdDev

```json
{
    "type": "StdDev",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
        ]
    }
}
```

CQL equivalent: `StdDev({1, 2, 3})`

### Variance

```json
{
    "type": "Variance",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
        ]
    }
}
```

CQL equivalent: `Variance({1, 2, 3})`

### AllTrue

```json
{
    "type": "AllTrue",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"}
        ]
    }
}
```

CQL equivalent: `AllTrue({true, true})` (Result: true)

### AnyTrue

```json
{
    "type": "AnyTrue",
    "source": {
        "type": "List",
        "element": [
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "false"},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Boolean", "value": "true"}
        ]
    }
}
```

CQL equivalent: `AnyTrue({false, true})` (Result: true)

---

## Set Operations

### Union

```json
{
    "type": "Union",
    "operand": [
        {
            "type": "List",
            "element": [
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"}
            ]
        },
        {
            "type": "List",
            "element": [
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
            ]
        }
    ]
}
```

CQL equivalent: `{1, 2} union {2, 3}` (Result: {1, 2, 3})

### Intersect

```json
{
    "type": "Intersect",
    "operand": [
        {
            "type": "List",
            "element": [
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"}
            ]
        },
        {
            "type": "List",
            "element": [
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
            ]
        }
    ]
}
```

CQL equivalent: `{1, 2} intersect {2, 3}` (Result: {2})

### Except

```json
{
    "type": "Except",
    "operand": [
        {
            "type": "List",
            "element": [
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"},
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"}
            ]
        },
        {
            "type": "List",
            "element": [
                {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2"}
            ]
        }
    ]
}
```

CQL equivalent: `{1, 2, 3} except {2}` (Result: {1, 3})

---

## Type Operations

### As (Type Cast)

```json
{
    "type": "As",
    "operand": {"type": "ExpressionRef", "name": "SomeValue"},
    "asType": "{urn:hl7-org:elm-types:r1}Integer"
}
```

CQL equivalent: `SomeValue as Integer`

### Is (Type Check)

```json
{
    "type": "Is",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
    "isType": "{urn:hl7-org:elm-types:r1}Integer"
}
```

CQL equivalent: `5 is Integer` (Result: true)

### ToInteger

```json
{
    "type": "ToInteger",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "42"}
}
```

CQL equivalent: `ToInteger('42')` (Result: 42)

### ToDecimal

```json
{
    "type": "ToDecimal",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "3.14"}
}
```

CQL equivalent: `ToDecimal('3.14')` (Result: 3.14)

### ToString

```json
{
    "type": "ToString",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "42"}
}
```

CQL equivalent: `ToString(42)` (Result: '42')

### ToBoolean

```json
{
    "type": "ToBoolean",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "true"}
}
```

CQL equivalent: `ToBoolean('true')` (Result: true)

### ToDateTime

```json
{
    "type": "ToDateTime",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "2024-01-15T10:30:00"}
}
```

CQL equivalent: `ToDateTime('2024-01-15T10:30:00')`

### ToDate

```json
{
    "type": "ToDate",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "2024-01-15"}
}
```

CQL equivalent: `ToDate('2024-01-15')`

### ToTime

```json
{
    "type": "ToTime",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "10:30:00"}
}
```

CQL equivalent: `ToTime('10:30:00')`

### ToQuantity

```json
{
    "type": "ToQuantity",
    "operand": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "100 mg"}
}
```

CQL equivalent: `ToQuantity('100 mg')`

---

## Date/Time Operations

### Today

```json
{
    "type": "Today"
}
```

CQL equivalent: `Today()`

### Now

```json
{
    "type": "Now"
}
```

CQL equivalent: `Now()`

### TimeOfDay

```json
{
    "type": "TimeOfDay"
}
```

CQL equivalent: `TimeOfDay()`

### Date

```json
{
    "type": "Date",
    "year": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2024"},
    "month": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
    "day": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "15"}
}
```

CQL equivalent: `Date(2024, 1, 15)`

### DateTime

```json
{
    "type": "DateTime",
    "year": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2024"},
    "month": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
    "day": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "15"},
    "hour": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"},
    "minute": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "30"}
}
```

CQL equivalent: `DateTime(2024, 1, 15, 10, 30)`

### Time

```json
{
    "type": "Time",
    "hour": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"},
    "minute": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "30"},
    "second": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "0"}
}
```

CQL equivalent: `Time(10, 30, 0)`

### DurationBetween

```json
{
    "type": "DurationBetween",
    "precision": "Year",
    "operand": [
        {"type": "Date", "year": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1990"}},
        {"type": "Today"}
    ]
}
```

CQL equivalent: `years between @1990 and Today()`

### DifferenceBetween

```json
{
    "type": "DifferenceBetween",
    "precision": "Day",
    "operand": [
        {"type": "Date", "year": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2024"}, "month": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"}, "day": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"}},
        {"type": "Date", "year": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2024"}, "month": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"}, "day": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"}}
    ]
}
```

CQL equivalent: `difference in days between @2024-01-01 and @2024-01-10`

### DateFrom

```json
{
    "type": "DateFrom",
    "operand": {"type": "Now"}
}
```

CQL equivalent: `date from Now()`

### TimeFrom

```json
{
    "type": "TimeFrom",
    "operand": {"type": "Now"}
}
```

CQL equivalent: `time from Now()`

### DateTimeComponentFrom

```json
{
    "type": "DateTimeComponentFrom",
    "precision": "Year",
    "operand": {"type": "Today"}
}
```

CQL equivalent: `year from Today()`

### SameAs

```json
{
    "type": "SameAs",
    "precision": "Day",
    "operand": [
        {"type": "Today"},
        {"type": "Today"}
    ]
}
```

CQL equivalent: `Today() same day as Today()` (Result: true)

### SameOrBefore

```json
{
    "type": "SameOrBefore",
    "precision": "Day",
    "operand": [
        {"type": "Date", "year": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2024"}, "month": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"}, "day": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"}},
        {"type": "Today"}
    ]
}
```

CQL equivalent: `@2024-01-01 same day or before Today()`

### SameOrAfter

```json
{
    "type": "SameOrAfter",
    "precision": "Day",
    "operand": [
        {"type": "Today"},
        {"type": "Date", "year": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "2024"}, "month": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"}, "day": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"}}
    ]
}
```

CQL equivalent: `Today() same day or after @2024-01-01`

---

## Interval Operations

### Start

```json
{
    "type": "Start",
    "operand": {
        "type": "Interval",
        "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
        "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"},
        "lowClosed": true,
        "highClosed": true
    }
}
```

CQL equivalent: `start of Interval[1, 10]` (Result: 1)

### End

```json
{
    "type": "End",
    "operand": {
        "type": "Interval",
        "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
        "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"},
        "lowClosed": true,
        "highClosed": true
    }
}
```

CQL equivalent: `end of Interval[1, 10]` (Result: 10)

### Width

```json
{
    "type": "Width",
    "operand": {
        "type": "Interval",
        "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
        "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"},
        "lowClosed": true,
        "highClosed": true
    }
}
```

CQL equivalent: `width of Interval[1, 10]` (Result: 9)

### Overlaps

```json
{
    "type": "Overlaps",
    "operand": [
        {
            "type": "Interval",
            "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
            "lowClosed": true,
            "highClosed": true
        },
        {
            "type": "Interval",
            "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"},
            "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "8"},
            "lowClosed": true,
            "highClosed": true
        }
    ]
}
```

CQL equivalent: `Interval[1, 5] overlaps Interval[3, 8]` (Result: true)

### Before

```json
{
    "type": "Before",
    "operand": [
        {
            "type": "Interval",
            "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"},
            "lowClosed": true,
            "highClosed": true
        },
        {
            "type": "Interval",
            "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
            "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"},
            "lowClosed": true,
            "highClosed": true
        }
    ]
}
```

CQL equivalent: `Interval[1, 3] before Interval[5, 10]` (Result: true)

### After

```json
{
    "type": "After",
    "operand": [
        {
            "type": "Interval",
            "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
            "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"},
            "lowClosed": true,
            "highClosed": true
        },
        {
            "type": "Interval",
            "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"},
            "lowClosed": true,
            "highClosed": true
        }
    ]
}
```

CQL equivalent: `Interval[5, 10] after Interval[1, 3]` (Result: true)

### Meets

```json
{
    "type": "Meets",
    "operand": [
        {
            "type": "Interval",
            "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
            "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
            "lowClosed": true,
            "highClosed": true
        },
        {
            "type": "Interval",
            "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
            "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "10"},
            "lowClosed": true,
            "highClosed": true
        }
    ]
}
```

CQL equivalent: `Interval[1, 5] meets Interval[5, 10]` (Result: true)

### Collapse

```json
{
    "type": "Collapse",
    "operand": {
        "type": "List",
        "element": [
            {
                "type": "Interval",
                "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
                "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
                "lowClosed": true,
                "highClosed": true
            },
            {
                "type": "Interval",
                "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "3"},
                "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "8"},
                "lowClosed": true,
                "highClosed": true
            }
        ]
    }
}
```

CQL equivalent: `collapse {Interval[1, 5], Interval[3, 8]}` (Result: {Interval[1, 8]})

### Expand

```json
{
    "type": "Expand",
    "operand": {
        "type": "Interval",
        "low": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "1"},
        "high": {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"},
        "lowClosed": true,
        "highClosed": true
    }
}
```

CQL equivalent: `expand Interval[1, 5]` (Result: {1, 2, 3, 4, 5})

---

## Reference Operations

### ExpressionRef

```json
{
    "type": "ExpressionRef",
    "name": "MyDefinition"
}
```

CQL equivalent: `MyDefinition`

### FunctionRef

```json
{
    "type": "FunctionRef",
    "name": "MyFunction",
    "operand": [
        {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}Integer", "value": "5"}
    ]
}
```

CQL equivalent: `MyFunction(5)`

### ParameterRef

```json
{
    "type": "ParameterRef",
    "name": "MeasurementPeriod"
}
```

CQL equivalent: `"MeasurementPeriod"`

### Property

```json
{
    "type": "Property",
    "path": "birthDate",
    "source": {"type": "ExpressionRef", "name": "Patient"}
}
```

CQL equivalent: `Patient.birthDate`

### AliasRef

```json
{
    "type": "AliasRef",
    "name": "O"
}
```

CQL equivalent: Reference to query alias `O`

---

## Query Operations

### Query

```json
{
    "type": "Query",
    "source": [{
        "expression": {"type": "ExpressionRef", "name": "Observations"},
        "alias": "O"
    }],
    "where": {
        "type": "Equal",
        "operand": [
            {"type": "Property", "path": "status", "source": {"type": "AliasRef", "name": "O"}},
            {"type": "Literal", "valueType": "{urn:hl7-org:elm-types:r1}String", "value": "final"}
        ]
    },
    "return": {
        "expression": {"type": "Property", "path": "value", "source": {"type": "AliasRef", "name": "O"}}
    }
}
```

CQL equivalent:
```cql
(Observations) O
    where O.status = 'final'
    return O.value
```

### Retrieve

```json
{
    "type": "Retrieve",
    "dataType": "{http://hl7.org/fhir}Observation",
    "codeProperty": "code",
    "codes": {"type": "ValueSetRef", "name": "BloodPressure"}
}
```

CQL equivalent: `[Observation: code in "BloodPressure"]`

### Sort

```json
{
    "type": "Query",
    "source": [{
        "expression": {"type": "ExpressionRef", "name": "Numbers"},
        "alias": "N"
    }],
    "sort": {
        "by": [{
            "direction": "asc",
            "expression": {"type": "AliasRef", "name": "N"}
        }]
    }
}
```

CQL equivalent: `(Numbers) N return N sort asc`

---

## Clinical Operations

### InValueSet

```json
{
    "type": "InValueSet",
    "code": {"type": "Property", "path": "code"},
    "valueset": {"name": "DiabetesCodes"}
}
```

CQL equivalent: `code in "DiabetesCodes"`

### InCodeSystem

```json
{
    "type": "InCodeSystem",
    "code": {"type": "Property", "path": "code"},
    "codesystem": {"name": "SNOMED"}
}
```

CQL equivalent: `code in "SNOMED"`

### CalculateAge

```json
{
    "type": "CalculateAge",
    "precision": "Year",
    "operand": {"type": "Property", "path": "birthDate"}
}
```

CQL equivalent: `AgeInYears()`

### CalculateAgeAt

```json
{
    "type": "CalculateAgeAt",
    "precision": "Year",
    "operand": [
        {"type": "Property", "path": "birthDate"},
        {"type": "Today"}
    ]
}
```

CQL equivalent: `AgeInYearsAt(Today())`

---

## Summary: Supported Expression Types

| Category | Count | Types |
|----------|-------|-------|
| Literals | 10 | Literal, Null, List, Tuple, Instance, Interval, Quantity, Code, Concept, Ratio |
| Arithmetic | 15 | Add, Subtract, Multiply, Divide, TruncatedDivide, Modulo, Power, Negate, Abs, Ceiling, Floor, Truncate, Round, Ln, Log, Exp, Successor, Predecessor |
| Comparison | 7 | Equal, NotEqual, Equivalent, Less, LessOrEqual, Greater, GreaterOrEqual |
| Boolean | 8 | And, Or, Not, Xor, Implies, IsNull, IsTrue, IsFalse |
| Conditional | 3 | If, Case, Coalesce |
| String | 13 | Concatenate, Combine, Split, Length, Upper, Lower, Substring, StartsWith, EndsWith, Matches, ReplaceMatches, PositionOf, LastPositionOf |
| Collection | 15 | First, Last, Indexer, IndexOf, Exists, In, Contains, Includes, IncludedIn, ProperIncludes, ProperIncludedIn, Distinct, Flatten, SingletonFrom, ToList |
| Aggregate | 12 | Count, Sum, Avg, Min, Max, Median, Mode, StdDev, PopulationStdDev, Variance, PopulationVariance, AllTrue, AnyTrue |
| Set | 3 | Union, Intersect, Except |
| Type | 16 | As, Is, ToBoolean, ToInteger, ToLong, ToDecimal, ToString, ToDateTime, ToDate, ToTime, ToQuantity, ToConcept, ConvertsTo* |
| Date/Time | 12 | Today, Now, TimeOfDay, Date, DateTime, Time, DurationBetween, DifferenceBetween, DateFrom, TimeFrom, DateTimeComponentFrom, SameAs, SameOrBefore, SameOrAfter |
| Interval | 15 | Interval, Start, End, Width, Size, PointFrom, Overlaps, OverlapsBefore, OverlapsAfter, Meets, MeetsBefore, MeetsAfter, Before, After, Starts, Ends, Collapse, Expand |
| Reference | 8 | ExpressionRef, FunctionRef, ParameterRef, Property, AliasRef, QueryLetRef, IdentifierRef, OperandRef |
| Query | 6 | Query, Retrieve, ForEach, Repeat, Filter, Times |
| Clinical | 6 | CodeRef, CodeSystemRef, ValueSetRef, ConceptRef, InValueSet, InCodeSystem, CalculateAge, CalculateAgeAt |

**Total: 168 expression types**

---

## See Also

- [ELM Guide](elm-guide.md) - Overview and quick start
- [ELM API](elm-api.md) - Python API reference
- [CQL Tutorial](cql-tutorial.md) - CQL syntax guide
- [FHIRPath & CQL Reference](fhirpath-cql-tutorial.md) - Expression examples
