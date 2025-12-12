# FHIRPath Complete Guide

A comprehensive guide to FHIRPath - from beginner to expert.

## What is FHIRPath?

FHIRPath is a path-based navigation and extraction language designed for FHIR (Fast Healthcare Interoperability Resources). Think of it like:

- **XPath** for XML
- **JSONPath** for JSON
- **jq** for command-line JSON processing

But FHIRPath is specifically designed for healthcare data in FHIR format.

### Why Use FHIRPath?

- **Extract data** from FHIR resources (get patient name, lab values, etc.)
- **Validate constraints** (ensure required fields exist)
- **Filter collections** (find specific observations, conditions)
- **Transform data** (format strings, calculate values)

---

## Getting Started

### Your First Expression

Given this Patient resource:

```json
{
  "resourceType": "Patient",
  "name": [{"family": "Smith", "given": ["John"]}],
  "gender": "male",
  "birthDate": "1985-06-15"
}
```

Try these expressions:

```bash
# Get the family name
fhirpath eval "Patient.name.family" -r patient.json
# Result: 'Smith'

# Get the gender
fhirpath eval "Patient.gender" -r patient.json
# Result: 'male'

# Check if patient is male
fhirpath eval "Patient.gender = 'male'" -r patient.json
# Result: True
```

### Understanding the Basics

FHIRPath works by:

1. **Starting** at the resource root
2. **Navigating** through properties with `.`
3. **Returning** a collection (list) of values

```
Patient.name.family
   │     │     │
   │     │     └── Get 'family' from each name
   │     └── Get all 'name' entries (array)
   └── Start at Patient resource
```

!!! tip "Collections Everywhere"
    FHIRPath always works with collections (lists). Even single values are treated as a collection of one item. This is important to understand!

---

## Navigation

### Basic Path Navigation

Use `.` to navigate into nested properties:

```
Patient.name                    # All name entries
Patient.name.family             # All family names
Patient.address.city            # All cities from all addresses
Patient.contact.name.family     # Contact's family name
```

### Accessing Array Elements

FHIR resources often contain arrays. FHIRPath automatically flattens them:

```json
{
  "name": [
    {"family": "Smith", "given": ["John", "William"]},
    {"family": "Doe", "given": ["Johnny"]}
  ]
}
```

```
Patient.name.given
# Returns: ['John', 'William', 'Johnny'] (all given names, flattened)

Patient.name.family
# Returns: ['Smith', 'Doe'] (all family names)
```

### The Resource Type Prefix

You can optionally start with the resource type:

```
Patient.name.family      # Explicit - recommended
name.family              # Also works when context is clear
```

---

## Subsetting Functions

Get specific items from collections.

### first() and last()

```
Patient.name.first()           # First name entry
Patient.name.given.first()     # First given name overall
Patient.telecom.last()         # Last telecom entry
```

### take(n) and skip(n)

```
Patient.name.given.take(2)     # First 2 given names
Patient.address.skip(1)        # All addresses except first
```

### single()

Returns the single item, or error if not exactly one:

```
Patient.gender.single()        # Works - gender is single value
Patient.name.single()          # Error if multiple names!
```

### tail()

Everything except the first:

```
Patient.name.given.tail()      # All given names except first
```

### Indexing with [ ]

Access by position (0-based):

```
Patient.name[0]                # First name
Patient.name[0].given[1]       # Second given name of first name entry
Patient.address[0].line[0]     # First line of first address
```

---

## Filtering with where()

Filter collections based on conditions.

### Basic Filtering

```
Patient.name.where(use = 'official')
# Only names where use is 'official'

Patient.telecom.where(system = 'phone')
# Only phone telecoms

Patient.address.where(use = 'home')
# Only home addresses
```

### Combining with Navigation

```
Patient.name.where(use = 'official').family
# Family name from official name only

Patient.telecom.where(system = 'phone').value
# All phone numbers

Patient.telecom.where(system = 'email').value.first()
# First email address
```

### Multiple Conditions

```
Patient.telecom.where(system = 'phone' and use = 'mobile').value
# Mobile phone numbers only

Patient.address.where(city = 'Boston' or city = 'Cambridge')
# Addresses in Boston or Cambridge
```

### Using $this

Inside `where()`, `$this` refers to the current item:

```
Patient.name.where($this.use = 'official')
# Same as: Patient.name.where(use = 'official')

Patient.name.given.where($this.startsWith('J'))
# Given names starting with 'J'
```

---

## Existence Functions

Check if values exist or meet conditions.

### exists() and empty()

```
Patient.name.exists()          # True if has any names
Patient.deceased.empty()       # True if no deceased value
Patient.address.exists()       # True if has addresses
```

### exists() with Criteria

```
Patient.telecom.exists(system = 'email')
# True if has any email

Patient.name.exists(use = 'official')
# True if has official name
```

### count()

```
Patient.name.count()           # Number of names
Patient.telecom.count()        # Number of telecom entries
Patient.address.count()        # Number of addresses
```

### hasValue()

True if single item with actual value:

```
Patient.birthDate.hasValue()   # True if birthDate exists
Patient.gender.hasValue()      # True if gender exists
```

### all()

True if ALL items match:

```
Patient.telecom.all(system.exists())
# True if every telecom has a system

Patient.name.all(family.exists())
# True if every name has a family
```

### Boolean Aggregates

```
Patient.communication.preferred.allTrue()
# True if all preferred flags are true

Patient.communication.preferred.anyTrue()
# True if any preferred flag is true

Patient.active.allFalse()
# True if all active flags are false

Patient.contact.exists().anyFalse()
# True if any contact doesn't exist (always false here)
```

---

## Comparison Operators

### Equality

```
Patient.gender = 'male'        # Equals
Patient.gender != 'female'     # Not equals
```

### Equivalence (~)

Similar to `=` but handles nulls and case differently:

```
Patient.gender ~ 'MALE'        # Case-insensitive for strings
```

### Ordering

```
Observation.valueQuantity.value > 100
Observation.valueQuantity.value >= 100
Observation.valueQuantity.value < 200
Observation.valueQuantity.value <= 200
```

### Comparing Dates

```
Patient.birthDate < @1990-01-01
Patient.birthDate >= @1980-01-01
Observation.effectiveDateTime > @2024-01-01
```

---

## Boolean Logic

### and, or, not

```
Patient.gender = 'male' and Patient.active = true
Patient.gender = 'male' or Patient.gender = 'female'
Patient.active.not()
(Patient.deceased).not()
```

### implies

If A then B (true unless A is true and B is false):

```
Patient.active implies Patient.name.exists()
# If active, must have name
```

### xor

Exclusive or (exactly one is true):

```
Patient.deceasedBoolean xor Patient.deceasedDateTime.exists()
# Has one or the other, not both
```

---

## String Functions

### Case Conversion

```
Patient.name.family.upper()         # 'SMITH'
Patient.name.family.lower()         # 'smith'
```

### Searching

```
Patient.name.family.startsWith('Sm')    # true
Patient.name.family.endsWith('ith')     # true
Patient.name.family.contains('mit')     # true
Patient.name.family.matches('Sm.*')     # true (regex)
```

### Extraction

```
Patient.name.family.substring(0, 3)     # 'Smi'
Patient.name.family.substring(2)        # 'ith' (from index 2)
Patient.name.family.length()            # 5
```

### Finding

```
Patient.name.family.indexOf('i')        # 2 (position of 'i')
Patient.name.family.indexOf('x')        # -1 (not found)
```

### Transformation

```
'  hello  '.trim()                      # 'hello'
'hello world'.replace('world', 'FHIR')  # 'hello FHIR'
'a,b,c'.split(',')                      # ['a', 'b', 'c']
```

### Joining

```
Patient.name.given.join(' ')            # 'John William'
Patient.name.given.join(', ')           # 'John, William'
```

### Characters

```
'hello'.toChars()                       # ['h', 'e', 'l', 'l', 'o']
```

---

## Math Functions

### Basic Math Operators

```
1 + 2              # 3
10 - 3             # 7
4 * 5              # 20
10 / 3             # 3.333...
10 div 3           # 3 (integer division)
10 mod 3           # 1 (remainder)
```

### Numeric Functions

```
(-5).abs()         # 5
3.7.ceiling()      # 4
3.7.floor()        # 3
3.7.truncate()     # 3
3.567.round(2)     # 3.57
```

### Advanced Math

```
16.sqrt()          # 4
(2.718).ln()       # ~1 (natural log)
100.log(10)        # 2 (log base 10)
2.power(8)         # 256
2.exp()            # ~7.389 (e^2)
```

### Working with Quantities

Observations often have quantities with units:

```
Observation.valueQuantity.value
# Just the number: 142

Observation.valueQuantity.unit
# The unit: 'mmHg'

Observation.valueQuantity.value > 140
# Compare the value
```

---

## Collection Functions

### distinct()

Remove duplicates:

```
Patient.address.state.distinct()
# Unique states only
```

### isDistinct()

Check if all unique:

```
Patient.identifier.value.isDistinct()
# True if no duplicate identifier values
```

### union ( | )

Combine collections (removes duplicates):

```
Patient.name.given | Patient.contact.name.given
# All given names from patient and contacts
```

### combine()

Combine collections (keeps duplicates):

```
Patient.name.given.combine(Patient.contact.name.given)
```

### intersect()

Items in both collections:

```
collection1.intersect(collection2)
```

### exclude()

Items in first but not second:

```
Patient.address.city.exclude('Boston')
# All cities except Boston
```

### flatten()

Flatten nested collections:

```
Bundle.entry.resource.name.flatten()
```

### Set Operations

```
collection1.subsetOf(collection2)    # True if 1 is subset of 2
collection1.supersetOf(collection2)  # True if 1 is superset of 2
```

---

## Type Functions

### Type Checking with is

```
Patient.deceased is boolean
Observation.value is Quantity
Patient.birthDate is date
```

### Type Casting with as

```
Observation.value as Quantity
Patient.deceased as boolean
```

### ofType()

Filter by type:

```
Bundle.entry.resource.ofType(Patient)
# Only Patient resources from bundle

Bundle.entry.resource.ofType(Observation)
# Only Observation resources
```

---

## Type Conversion

### to*() Functions

```
'true'.toBoolean()          # true
'123'.toInteger()           # 123
'3.14'.toDecimal()          # 3.14
123.toString()              # '123'
true.toString()             # 'true'
```

### Date/Time Conversions

```
'2024-03-15'.toDate()
'2024-03-15T10:30:00Z'.toDateTime()
'10:30:00'.toTime()
```

### convertsTo*() Functions

Check if conversion is possible:

```
'123'.convertsToInteger()     # true
'abc'.convertsToInteger()     # false
'2024-03-15'.convertsToDate() # true
```

### Quantity Conversion

```
123.toQuantity()              # 123 '1' (unitless)
'100 mg'.toQuantity()         # 100 'mg'
```

---

## Date and Time

### Current Date/Time

```
today()                       # Current date
now()                         # Current datetime
timeOfDay()                   # Current time
```

### Date Literals

Use `@` prefix:

```
@2024-03-15                   # Date
@2024-03-15T10:30:00Z         # DateTime
@T10:30:00                    # Time
```

### Comparing Dates

```
Patient.birthDate < @1990-01-01
Patient.birthDate > today() - 18 years
Observation.effectiveDateTime > @2024-01-01
```

### Date Components

```
Patient.birthDate.year        # Birth year
Patient.birthDate.month       # Birth month
Patient.birthDate.day         # Birth day
```

---

## Working with FHIR Resources

### Navigating Complex Resources

**Observation with Components (Blood Pressure):**

```json
{
  "resourceType": "Observation",
  "code": {"coding": [{"code": "85354-9", "system": "http://loinc.org"}]},
  "component": [
    {"code": {"coding": [{"code": "8480-6"}]}, "valueQuantity": {"value": 142}},
    {"code": {"coding": [{"code": "8462-4"}]}, "valueQuantity": {"value": 88}}
  ]
}
```

```
# Get all component values
Observation.component.valueQuantity.value
# Returns: [142, 88]

# Get systolic (by LOINC code)
Observation.component.where(code.coding.code = '8480-6').valueQuantity.value
# Returns: 142

# Get diastolic
Observation.component.where(code.coding.code = '8462-4').valueQuantity.value
# Returns: 88
```

### Working with Codings

```
# Get LOINC code
Observation.code.coding.where(system = 'http://loinc.org').code

# Get SNOMED code
Condition.code.coding.where(system = 'http://snomed.info/sct').code

# Get any code display
Observation.code.coding.display.first()

# Check if has specific code
Observation.code.coding.exists(code = '85354-9')
```

### Bundle Navigation

```
# Count entries
Bundle.entry.count()

# Get all resources
Bundle.entry.resource

# Get specific resource types
Bundle.entry.resource.where(resourceType = 'Patient')
Bundle.entry.resource.ofType(Observation)

# Get patient names from bundle
Bundle.entry.resource.ofType(Patient).name.family
```

### References

```
# Get reference string
Observation.subject.reference
# Returns: 'Patient/example-patient-1'

# Get display
Observation.subject.display
# Returns: 'John Smith'
```

---

## Practical Examples

### Patient Demographics

```bash
# Full name
fhirpath eval "Patient.name.where(use='official').given.join(' ') & ' ' & Patient.name.where(use='official').family" -r patient.json

# Age check (is adult)
fhirpath eval "Patient.birthDate <= today() - 18 years" -r patient.json

# Contact info
fhirpath eval "Patient.telecom.where(system='phone').value" -r patient.json
```

### Clinical Checks

```bash
# Is blood pressure high?
fhirpath eval "Observation.component.where(code.coding.code='8480-6').valueQuantity.value > 140" -r observation_bp.json

# Get all high interpretations
fhirpath eval "Observation.interpretation.coding.where(code='H').exists()" -r observation_bp.json
```

### Data Validation

```bash
# Patient has required fields
fhirpath eval "Patient.name.exists() and Patient.birthDate.exists() and Patient.gender.exists()" -r patient.json

# All identifiers have systems
fhirpath eval "Patient.identifier.all(system.exists())" -r patient.json

# No duplicate identifiers
fhirpath eval "Patient.identifier.value.isDistinct()" -r patient.json
```

### Data Extraction

```bash
# All codes from an observation
fhirpath eval "Observation.code.coding.code | Observation.component.code.coding.code" -r observation_bp.json

# All phone numbers
fhirpath eval "Patient.telecom.where(system='phone').value" -r patient.json

# Contact emergency info
fhirpath eval "Patient.contact.where(relationship.coding.code='N').telecom.value" -r patient.json
```

---

## Function Reference

### Existence Functions

| Function | Description | Example |
|----------|-------------|---------|
| `exists()` | True if not empty | `name.exists()` |
| `exists(criteria)` | True if any match criteria | `telecom.exists(system='phone')` |
| `empty()` | True if empty | `deceased.empty()` |
| `count()` | Number of items | `name.count()` |
| `hasValue()` | Has single value | `gender.hasValue()` |
| `all(criteria)` | All items match | `name.all(family.exists())` |
| `allTrue()` | All are true | `active.allTrue()` |
| `anyTrue()` | Any is true | `preferred.anyTrue()` |
| `allFalse()` | All are false | `active.allFalse()` |
| `anyFalse()` | Any is false | `active.anyFalse()` |

### Subsetting Functions

| Function | Description | Example |
|----------|-------------|---------|
| `first()` | First item | `name.first()` |
| `last()` | Last item | `name.last()` |
| `tail()` | All except first | `name.tail()` |
| `take(n)` | First n items | `name.take(2)` |
| `skip(n)` | Skip first n | `name.skip(1)` |
| `single()` | Exactly one item | `gender.single()` |
| `[n]` | Item at index | `name[0]` |

### String Functions

| Function | Description | Example |
|----------|-------------|---------|
| `upper()` | Uppercase | `family.upper()` |
| `lower()` | Lowercase | `family.lower()` |
| `trim()` | Remove whitespace | `value.trim()` |
| `length()` | String length | `family.length()` |
| `substring(start, len)` | Extract substring | `family.substring(0,3)` |
| `startsWith(s)` | Starts with | `family.startsWith('Sm')` |
| `endsWith(s)` | Ends with | `family.endsWith('th')` |
| `contains(s)` | Contains | `family.contains('mit')` |
| `indexOf(s)` | Find position | `family.indexOf('i')` |
| `matches(regex)` | Regex match | `family.matches('S.*')` |
| `replace(old, new)` | Replace text | `family.replace('a','@')` |
| `split(sep)` | Split string | `value.split(',')` |
| `join(sep)` | Join collection | `given.join(' ')` |
| `toChars()` | To char array | `family.toChars()` |

### Math Functions

| Function | Description | Example |
|----------|-------------|---------|
| `abs()` | Absolute value | `(-5).abs()` |
| `ceiling()` | Round up | `3.2.ceiling()` |
| `floor()` | Round down | `3.8.floor()` |
| `truncate()` | Remove decimals | `3.8.truncate()` |
| `round(n)` | Round to n places | `3.567.round(2)` |
| `sqrt()` | Square root | `16.sqrt()` |
| `ln()` | Natural log | `value.ln()` |
| `log(base)` | Logarithm | `100.log(10)` |
| `power(exp)` | Exponentiation | `2.power(3)` |
| `exp()` | e^x | `2.exp()` |

### Collection Functions

| Function | Description | Example |
|----------|-------------|---------|
| `distinct()` | Remove duplicates | `state.distinct()` |
| `isDistinct()` | All unique? | `value.isDistinct()` |
| `where(criteria)` | Filter | `name.where(use='official')` |
| `select(expr)` | Project | `name.select(family)` |
| `repeat(expr)` | Recursive | `children().repeat(children())` |
| `ofType(type)` | Filter by type | `resource.ofType(Patient)` |
| `union(other)` | Combine unique | `a.union(b)` or `a \| b` |
| `combine(other)` | Combine all | `a.combine(b)` |
| `intersect(other)` | Common items | `a.intersect(b)` |
| `exclude(other)` | Remove items | `a.exclude(b)` |
| `flatten()` | Flatten nested | `nested.flatten()` |
| `subsetOf(other)` | Is subset? | `a.subsetOf(b)` |
| `supersetOf(other)` | Is superset? | `a.supersetOf(b)` |

### Type Functions

| Function | Description | Example |
|----------|-------------|---------|
| `is(type)` | Type check | `value is Quantity` |
| `as(type)` | Type cast | `value as Quantity` |
| `ofType(type)` | Filter by type | `ofType(Patient)` |
| `toBoolean()` | Convert to bool | `'true'.toBoolean()` |
| `toInteger()` | Convert to int | `'123'.toInteger()` |
| `toDecimal()` | Convert to decimal | `'3.14'.toDecimal()` |
| `toString()` | Convert to string | `123.toString()` |
| `toDate()` | Convert to date | `'2024-03-15'.toDate()` |
| `toDateTime()` | Convert to datetime | `value.toDateTime()` |
| `toTime()` | Convert to time | `'10:30'.toTime()` |
| `toQuantity()` | Convert to quantity | `'100 mg'.toQuantity()` |
| `convertsToBoolean()` | Can convert? | `value.convertsToBoolean()` |
| `convertsToInteger()` | Can convert? | `value.convertsToInteger()` |
| `convertsToDecimal()` | Can convert? | `value.convertsToDecimal()` |
| `convertsToDate()` | Can convert? | `value.convertsToDate()` |
| `convertsToDateTime()` | Can convert? | `value.convertsToDateTime()` |
| `convertsToTime()` | Can convert? | `value.convertsToTime()` |
| `convertsToQuantity()` | Can convert? | `value.convertsToQuantity()` |

### Date/Time Functions

| Function | Description | Example |
|----------|-------------|---------|
| `today()` | Current date | `today()` |
| `now()` | Current datetime | `now()` |
| `timeOfDay()` | Current time | `timeOfDay()` |

### Utility Functions

| Function | Description | Example |
|----------|-------------|---------|
| `iif(cond, t, f)` | Conditional | `iif(active, 'Yes', 'No')` |
| `not()` | Negate | `active.not()` |
| `trace(name)` | Debug output | `value.trace('debug')` |

### Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Add / concatenate | `1 + 2` or `'a' + 'b'` |
| `-` | Subtract | `10 - 3` |
| `*` | Multiply | `4 * 5` |
| `/` | Divide | `10 / 3` |
| `div` | Integer divide | `10 div 3` |
| `mod` | Modulo | `10 mod 3` |
| `&` | String concat | `family & ', ' & given` |
| `\|` | Union | `a \| b` |
| `=` | Equals | `gender = 'male'` |
| `!=` | Not equals | `gender != 'female'` |
| `~` | Equivalent | `gender ~ 'MALE'` |
| `!~` | Not equivalent | `gender !~ 'FEMALE'` |
| `<` | Less than | `value < 100` |
| `>` | Greater than | `value > 100` |
| `<=` | Less or equal | `value <= 100` |
| `>=` | Greater or equal | `value >= 100` |
| `and` | Logical AND | `a and b` |
| `or` | Logical OR | `a or b` |
| `xor` | Exclusive OR | `a xor b` |
| `implies` | Implication | `a implies b` |
| `is` | Type check | `value is Quantity` |
| `as` | Type cast | `value as Quantity` |

---

## Common Patterns

### Null-Safe Navigation

FHIRPath is null-safe by default - navigating into empty returns empty:

```
Patient.deceased.value     # Returns empty if deceased doesn't exist
Patient.address[5].city    # Returns empty if no 6th address
```

### String Concatenation

```
Patient.name.family & ', ' & Patient.name.given.first()
# Returns: 'Smith, John'
```

### Conditional Logic

```
iif(Patient.gender = 'male', 'Mr.', 'Ms.')
# Returns: 'Mr.' for male patients
```

### Default Values

```
Patient.nickname.first() | Patient.name.given.first()
# Returns nickname if exists, otherwise first given name
```

---

## Tips and Best Practices

!!! tip "Start Simple"
    Begin with basic navigation, then add filtering and functions as needed.

!!! tip "Use the REPL"
    Test expressions interactively with `fhirpath repl -r resource.json`

!!! tip "Remember Collections"
    Everything is a collection. Use `.first()` when you need a single value.

!!! warning "Index Bounds"
    `collection[n]` returns empty (not error) if index is out of bounds.

!!! warning "Type Sensitivity"
    `=` is type-sensitive. `1 = '1'` is false. Use conversions when comparing different types.

---

## Further Reading

- [FHIRPath Specification](http://hl7.org/fhirpath/) - Official HL7 specification
- [FHIR R4](https://hl7.org/fhir/R4/) - FHIR resource definitions
- [FHIRPath Tutorial](http://hl7.org/fhirpath/tutorial.html) - HL7 tutorial
