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
fhir fhirpath eval "Patient.name.family" -r patient.json
# Result: 'Smith'

# Get the gender
fhir fhirpath eval "Patient.gender" -r patient.json
# Result: 'male'

# Check if patient is male
fhir fhirpath eval "Patient.gender = 'male'" -r patient.json
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
fhir fhirpath eval "Patient.name.where(use='official').given.join(' ') & ' ' & Patient.name.where(use='official').family" -r patient.json

# Age check (is adult)
fhir fhirpath eval "Patient.birthDate <= today() - 18 years" -r patient.json

# Contact info
fhir fhirpath eval "Patient.telecom.where(system='phone').value" -r patient.json
```

### Clinical Checks

```bash
# Is blood pressure high?
fhir fhirpath eval "Observation.component.where(code.coding.code='8480-6').valueQuantity.value > 140" -r observation_bp.json

# Get all high interpretations
fhir fhirpath eval "Observation.interpretation.coding.where(code='H').exists()" -r observation_bp.json
```

### Data Validation

```bash
# Patient has required fields
fhir fhirpath eval "Patient.name.exists() and Patient.birthDate.exists() and Patient.gender.exists()" -r patient.json

# All identifiers have systems
fhir fhirpath eval "Patient.identifier.all(system.exists())" -r patient.json

# No duplicate identifiers
fhir fhirpath eval "Patient.identifier.value.isDistinct()" -r patient.json
```

### Data Extraction

```bash
# All codes from an observation
fhir fhirpath eval "Observation.code.coding.code | Observation.component.code.coding.code" -r observation_bp.json

# All phone numbers
fhir fhirpath eval "Patient.telecom.where(system='phone').value" -r patient.json

# Contact emergency info
fhir fhirpath eval "Patient.contact.where(relationship.coding.code='N').telecom.value" -r patient.json
```

---

## Function Reference

---

### Existence Functions

#### exists()

Returns `true` if the collection has any elements, `false` if empty.

**Signature:** `collection.exists()` or `collection.exists(criteria)`

**Parameters:**
- `criteria` (optional): A FHIRPath expression evaluated for each item. Returns `true` if ANY item satisfies the criteria.

**Returns:** Boolean

**Examples:**

```fhirpath
# Basic existence check
Patient.name.exists()
# Returns: true (if patient has any names)

Patient.photo.exists()
# Returns: false (if no photos)

# With criteria - check if specific type exists
Patient.telecom.exists(system = 'email')
# Returns: true if patient has any email telecom

Patient.name.exists(use = 'official')
# Returns: true if patient has an official name

Patient.identifier.exists(system = 'http://hospital.org')
# Returns: true if patient has hospital identifier

# Complex criteria
Patient.telecom.exists(system = 'phone' and use = 'mobile')
# Returns: true if patient has a mobile phone
```

**Edge Cases:**

```fhirpath
{}.exists()           # false - empty collection
(1).exists()          # true - single value exists
(1 | 2 | 3).exists()  # true - multiple values exist
```

---

#### empty()

Returns `true` if the collection is empty, `false` otherwise. Opposite of `exists()`.

**Signature:** `collection.empty()`

**Returns:** Boolean

**Examples:**

```fhirpath
Patient.deceased.empty()
# Returns: true if no deceased value

Patient.name.empty()
# Returns: false (patient has names)

Patient.photo.empty()
# Returns: true (no photos)

# Useful for validation
Patient.identifier.empty().not()
# Returns: true if patient has at least one identifier
```

**Edge Cases:**

```fhirpath
{}.empty()           # true
(1).empty()          # false
''.empty()           # false - empty string is still a value!
```

---

#### count()

Returns the number of items in the collection.

**Signature:** `collection.count()`

**Returns:** Integer

**Examples:**

```fhirpath
Patient.name.count()
# Returns: 2 (if patient has 2 names)

Patient.telecom.count()
# Returns: 3 (if patient has 3 telecom entries)

Patient.address.count()
# Returns: 1 (if patient has 1 address)

# Combined with filtering
Patient.telecom.where(system = 'phone').count()
# Returns: number of phone entries only

# Validation: must have at least 2 identifiers
Patient.identifier.count() >= 2
# Returns: true/false
```

**Edge Cases:**

```fhirpath
{}.count()           # 0
(1).count()          # 1
(1 | 2 | 3).count()  # 3
```

---

#### hasValue()

Returns `true` if the collection contains a single item that is not null. Used primarily for primitive values.

**Signature:** `collection.hasValue()`

**Returns:** Boolean

**Examples:**

```fhirpath
Patient.gender.hasValue()
# Returns: true (gender is a single value)

Patient.birthDate.hasValue()
# Returns: true (birthDate exists)

Patient.deceased.hasValue()
# Returns: true if deceasedBoolean or deceasedDateTime exists

Patient.name.hasValue()
# Returns: false - name is a collection, not single value
```

**Edge Cases:**

```fhirpath
{}.hasValue()        # false - empty
(1).hasValue()       # true - single value
(1 | 2).hasValue()   # false - multiple values
```

---

#### all(criteria)

Returns `true` if ALL items in the collection satisfy the criteria. Returns `true` for empty collections.

**Signature:** `collection.all(criteria)`

**Parameters:**
- `criteria`: FHIRPath expression evaluated for each item

**Returns:** Boolean

**Examples:**

```fhirpath
# All telecoms must have a system
Patient.telecom.all(system.exists())
# Returns: true if every telecom has a system

# All names must have a family name
Patient.name.all(family.exists())
# Returns: true/false

# All identifiers must have both system and value
Patient.identifier.all(system.exists() and value.exists())
# Returns: true if all identifiers are complete

# Using $this for the current item
Patient.name.given.all($this.length() > 1)
# Returns: true if all given names are longer than 1 character

# Numeric validation
Observation.component.all(valueQuantity.value > 0)
# Returns: true if all component values are positive
```

**Edge Cases:**

```fhirpath
{}.all(false)              # true - vacuously true for empty
(1 | 2 | 3).all($this > 0) # true
(1 | -2 | 3).all($this > 0) # false
```

---

#### allTrue()

Returns `true` if all items in the collection are boolean `true`.

**Signature:** `collection.allTrue()`

**Returns:** Boolean

**Examples:**

```fhirpath
(true | true | true).allTrue()
# Returns: true

(true | false | true).allTrue()
# Returns: false

# Check if all communications are preferred
Patient.communication.preferred.allTrue()
# Returns: true if all are marked preferred

# Validation results
(Patient.name.exists() | Patient.birthDate.exists()).allTrue()
# Returns: true if both name and birthDate exist
```

**Edge Cases:**

```fhirpath
{}.allTrue()          # true - empty is vacuously true
(true).allTrue()      # true
```

---

#### anyTrue()

Returns `true` if ANY item in the collection is boolean `true`.

**Signature:** `collection.anyTrue()`

**Returns:** Boolean

**Examples:**

```fhirpath
(false | false | true).anyTrue()
# Returns: true

(false | false).anyTrue()
# Returns: false

# Check if any communication is preferred
Patient.communication.preferred.anyTrue()
# Returns: true if at least one is preferred

# Check multiple conditions
(Patient.active | Patient.deceased.not()).anyTrue()
# Returns: true if either active or not deceased
```

**Edge Cases:**

```fhirpath
{}.anyTrue()          # false - no true values
(true).anyTrue()      # true
```

---

#### allFalse()

Returns `true` if all items in the collection are boolean `false`.

**Signature:** `collection.allFalse()`

**Returns:** Boolean

**Examples:**

```fhirpath
(false | false).allFalse()
# Returns: true

(false | true).allFalse()
# Returns: false

# Check no communications are preferred
Patient.communication.preferred.allFalse()
# Returns: true if none are preferred
```

---

#### anyFalse()

Returns `true` if ANY item in the collection is boolean `false`.

**Signature:** `collection.anyFalse()`

**Returns:** Boolean

**Examples:**

```fhirpath
(true | false | true).anyFalse()
# Returns: true

(true | true).anyFalse()
# Returns: false
```

---

### Subsetting Functions

#### first()

Returns the first item in the collection, or empty if the collection is empty.

**Signature:** `collection.first()`

**Returns:** Single item or empty

**Examples:**

```fhirpath
Patient.name.first()
# Returns: first HumanName object

Patient.name.given.first()
# Returns: first given name string (e.g., "John")

Patient.telecom.first().value
# Returns: value of first telecom entry

# Chained navigation
Patient.address.first().city
# Returns: city of first address

Patient.identifier.first().value
# Returns: first identifier value

# Get primary phone
Patient.telecom.where(system = 'phone').first().value
# Returns: first phone number
```

**Edge Cases:**

```fhirpath
{}.first()           # empty (not an error)
(1).first()          # 1
(1 | 2 | 3).first()  # 1
```

---

#### last()

Returns the last item in the collection, or empty if the collection is empty.

**Signature:** `collection.last()`

**Returns:** Single item or empty

**Examples:**

```fhirpath
Patient.name.last()
# Returns: last HumanName object

Patient.name.given.last()
# Returns: last given name

Patient.address.last().city
# Returns: city of last address

# Most recent entry (if ordered)
Bundle.entry.last().resource
# Returns: last resource in bundle
```

**Edge Cases:**

```fhirpath
{}.last()            # empty
(1).last()           # 1
(1 | 2 | 3).last()   # 3
```

---

#### tail()

Returns all items except the first. Useful for processing "rest of list".

**Signature:** `collection.tail()`

**Returns:** Collection without first item

**Examples:**

```fhirpath
Patient.name.tail()
# Returns: all names except the first

Patient.name.given.tail()
# Returns: all given names except first (e.g., middle names)

(1 | 2 | 3 | 4 | 5).tail()
# Returns: [2, 3, 4, 5]

# Process remaining items
Patient.telecom.tail().value
# Returns: values of all telecoms except first
```

**Edge Cases:**

```fhirpath
{}.tail()            # empty
(1).tail()           # empty (nothing after first)
(1 | 2).tail()       # [2]
```

---

#### take(count)

Returns the first `count` items from the collection.

**Signature:** `collection.take(count)`

**Parameters:**
- `count`: Integer - number of items to take

**Returns:** Collection with at most `count` items

**Examples:**

```fhirpath
Patient.name.given.take(2)
# Returns: first 2 given names

Patient.telecom.take(3)
# Returns: first 3 telecom entries

(1 | 2 | 3 | 4 | 5).take(3)
# Returns: [1, 2, 3]

# Top N results
Bundle.entry.take(10).resource
# Returns: first 10 resources from bundle
```

**Edge Cases:**

```fhirpath
{}.take(5)                # empty
(1 | 2 | 3).take(0)       # empty
(1 | 2 | 3).take(10)      # [1, 2, 3] - takes all available
```

---

#### skip(count)

Returns all items except the first `count` items.

**Signature:** `collection.skip(count)`

**Parameters:**
- `count`: Integer - number of items to skip

**Returns:** Collection without first `count` items

**Examples:**

```fhirpath
Patient.name.given.skip(1)
# Returns: all given names except the first

Patient.address.skip(1)
# Returns: all addresses except the first

(1 | 2 | 3 | 4 | 5).skip(2)
# Returns: [3, 4, 5]

# Pagination
Bundle.entry.skip(20).take(10)
# Returns: entries 21-30 (page 3 with page size 10)
```

**Edge Cases:**

```fhirpath
{}.skip(5)                # empty
(1 | 2 | 3).skip(0)       # [1, 2, 3] - skips nothing
(1 | 2 | 3).skip(10)      # empty - skipped all
```

---

#### single()

Returns the single item in the collection. Throws an error if the collection doesn't have exactly one item.

**Signature:** `collection.single()`

**Returns:** Single item (or error)

**Examples:**

```fhirpath
Patient.gender.single()
# Returns: "male" (gender is always single)

Patient.birthDate.single()
# Returns: "1985-06-15"

Patient.id.single()
# Returns: the patient ID

# After filtering to single result
Patient.name.where(use = 'official').single()
# Returns: the official name (error if multiple officials!)
```

**Edge Cases:**

```fhirpath
{}.single()               # empty (no error for empty)
(1).single()              # 1
(1 | 2).single()          # ERROR: collection has more than one item
```

---

#### Indexer [index]

Access item at specific position (0-based indexing).

**Signature:** `collection[index]`

**Parameters:**
- `index`: Integer - 0-based position

**Returns:** Single item or empty

**Examples:**

```fhirpath
Patient.name[0]
# Returns: first name object

Patient.name[1]
# Returns: second name object

Patient.name[0].given[0]
# Returns: first given name of first name

Patient.address[0].line[0]
# Returns: first line of first address

Patient.address[0].line[1]
# Returns: second line of first address (e.g., "Apt 4B")

# Combined with other operations
Patient.telecom[0].value
# Returns: value of first telecom
```

**Edge Cases:**

```fhirpath
Patient.name[99]          # empty (out of bounds, NOT an error)
{}[0]                     # empty
(1 | 2 | 3)[1]            # 2
```

---

### String Functions

#### upper()

Converts string to uppercase.

**Signature:** `string.upper()`

**Returns:** Uppercase string

**Examples:**

```fhirpath
'hello'.upper()
# Returns: "HELLO"

Patient.name.family.upper()
# Returns: ["SMITH"] (uppercase family name)

Patient.gender.upper()
# Returns: "MALE"

# Case-insensitive comparison
Patient.gender.upper() = 'MALE'
# Returns: true regardless of original case
```

---

#### lower()

Converts string to lowercase.

**Signature:** `string.lower()`

**Returns:** Lowercase string

**Examples:**

```fhirpath
'HELLO'.lower()
# Returns: "hello"

Patient.name.family.lower()
# Returns: ["smith"]

# Normalization for comparison
Patient.gender.lower() = 'male'
# Returns: true
```

---

#### trim()

Removes leading and trailing whitespace.

**Signature:** `string.trim()`

**Returns:** Trimmed string

**Examples:**

```fhirpath
'  hello world  '.trim()
# Returns: "hello world"

'   '.trim()
# Returns: ""

# Clean up user input
Patient.name.given.first().trim()
# Returns: given name without extra spaces
```

---

#### length()

Returns the length of the string.

**Signature:** `string.length()`

**Returns:** Integer

**Examples:**

```fhirpath
'hello'.length()
# Returns: 5

Patient.name.family.length()
# Returns: [5] (e.g., "Smith" has 5 chars)

Patient.id.length()
# Returns: length of patient ID

# Validation
Patient.identifier.value.length() >= 5
# Returns: true if identifier is at least 5 chars
```

---

#### substring(start, length?)

Extracts a portion of the string.

**Signature:** `string.substring(start)` or `string.substring(start, length)`

**Parameters:**
- `start`: Integer - starting position (0-based)
- `length` (optional): Integer - number of characters to extract

**Returns:** Substring

**Examples:**

```fhirpath
'hello world'.substring(0, 5)
# Returns: "hello"

'hello world'.substring(6)
# Returns: "world" (from position 6 to end)

'hello world'.substring(6, 3)
# Returns: "wor"

Patient.birthDate.substring(0, 4)
# Returns: "1985" (year portion)

Patient.birthDate.substring(5, 2)
# Returns: "06" (month portion)

Patient.birthDate.substring(8, 2)
# Returns: "15" (day portion)

# Extract area code from phone
Patient.telecom.where(system = 'phone').value.first().substring(0, 3)
# Returns: first 3 chars
```

---

#### startsWith(prefix)

Returns `true` if string starts with the given prefix.

**Signature:** `string.startsWith(prefix)`

**Parameters:**
- `prefix`: String to check for

**Returns:** Boolean

**Examples:**

```fhirpath
'hello'.startsWith('hel')
# Returns: true

'hello'.startsWith('world')
# Returns: false

Patient.name.family.startsWith('Sm')
# Returns: [true] if family name starts with "Sm"

# Filter by prefix
Patient.identifier.where(value.startsWith('MRN'))
# Returns: identifiers starting with "MRN"

# Check reference type
Observation.subject.reference.startsWith('Patient/')
# Returns: true if reference is to a Patient
```

---

#### endsWith(suffix)

Returns `true` if string ends with the given suffix.

**Signature:** `string.endsWith(suffix)`

**Parameters:**
- `suffix`: String to check for

**Returns:** Boolean

**Examples:**

```fhirpath
'hello'.endsWith('llo')
# Returns: true

Patient.name.family.endsWith('son')
# Returns: true for names like "Johnson", "Peterson"

# Check email domain
Patient.telecom.where(system = 'email').value.endsWith('@hospital.org')
# Returns: true for hospital emails
```

---

#### contains(substring)

Returns `true` if string contains the given substring.

**Signature:** `string.contains(substring)`

**Parameters:**
- `substring`: String to search for

**Returns:** Boolean

**Examples:**

```fhirpath
'hello world'.contains('wor')
# Returns: true

Patient.name.family.contains('mit')
# Returns: [true] for "Smith"

# Search phone numbers
Patient.telecom.where(value.contains('555'))
# Returns: telecoms with "555" in value

# Check for specific code system
Observation.code.coding.system.contains('loinc')
# Returns: true if any coding uses LOINC
```

---

#### indexOf(substring)

Returns the position of substring, or -1 if not found.

**Signature:** `string.indexOf(substring)`

**Parameters:**
- `substring`: String to find

**Returns:** Integer (position or -1)

**Examples:**

```fhirpath
'hello world'.indexOf('world')
# Returns: 6

'hello world'.indexOf('xyz')
# Returns: -1 (not found)

Patient.name.family.indexOf('i')
# Returns: position of 'i' in family name

# Check if found
'hello'.indexOf('e') >= 0
# Returns: true (found)

'hello'.indexOf('x') >= 0
# Returns: false (not found)
```

---

#### matches(regex)

Returns `true` if string matches the regular expression.

**Signature:** `string.matches(regex)`

**Parameters:**
- `regex`: Regular expression pattern

**Returns:** Boolean

**Examples:**

```fhirpath
'test123'.matches('\\d+')
# Returns: true (contains digits)

'test123'.matches('^\\d+$')
# Returns: false (not ALL digits)

'12345'.matches('^\\d+$')
# Returns: true (all digits)

Patient.name.family.matches('^[A-Z][a-z]+$')
# Returns: true if properly capitalized

# Phone number validation
Patient.telecom.value.matches('^\\+?\\d[\\d\\-\\s]+$')
# Returns: true for valid phone format

# Email validation
Patient.telecom.where(system = 'email').value.matches('^[^@]+@[^@]+\\.[^@]+$')
# Returns: true for valid email format
```

---

#### replace(pattern, replacement)

Replaces all occurrences of pattern with replacement (simple string replacement).

**Signature:** `string.replace(pattern, replacement)`

**Parameters:**
- `pattern`: String to find
- `replacement`: String to substitute

**Returns:** String with replacements

**Examples:**

```fhirpath
'hello world'.replace('world', 'FHIR')
# Returns: "hello FHIR"

'hello'.replace('l', 'L')
# Returns: "heLLo" (replaces ALL occurrences)

# Clean phone number
'+1-555-123-4567'.replace('-', '')
# Returns: "+15551234567"

# Format name
Patient.name.family.replace(' ', '-')
# Returns: hyphenated family name
```

---

#### replaceMatches(regex, replacement)

Replaces all regex matches with replacement.

**Signature:** `string.replaceMatches(regex, replacement)`

**Parameters:**
- `regex`: Regular expression pattern
- `replacement`: Replacement string (can use `\1`, `\2` for groups)

**Returns:** String with replacements

**Examples:**

```fhirpath
'test123abc456'.replaceMatches('\\d+', 'X')
# Returns: "testXabcX"

'hello-world'.replaceMatches('-(\\w+)', '_\\1')
# Returns: "hello_world"

# Remove all non-digits
'+1-555-123-4567'.replaceMatches('[^\\d]', '')
# Returns: "15551234567"

# Mask sensitive data
'SSN: 123-45-6789'.replaceMatches('\\d', '*')
# Returns: "SSN: ***-**-****"
```

---

#### split(separator)

Splits string into a collection by separator.

**Signature:** `string.split(separator)`

**Parameters:**
- `separator`: String to split on

**Returns:** Collection of strings

**Examples:**

```fhirpath
'a,b,c'.split(',')
# Returns: ["a", "b", "c"]

'hello world'.split(' ')
# Returns: ["hello", "world"]

Patient.birthDate.split('-')
# Returns: ["1985", "06", "15"]

# Parse CSV-like data
'code1|code2|code3'.split('|')
# Returns: ["code1", "code2", "code3"]

# Get domain from email
Patient.telecom.where(system = 'email').value.first().split('@').last()
# Returns: domain part of email
```

---

#### join(separator)

Joins collection elements into a single string.

**Signature:** `collection.join(separator)`

**Parameters:**
- `separator`: String to insert between items (defaults to empty)

**Returns:** Single string

**Examples:**

```fhirpath
Patient.name.given.join(' ')
# Returns: "John William" (given names joined by space)

Patient.name.given.join(', ')
# Returns: "John, William"

('a' | 'b' | 'c').join('-')
# Returns: "a-b-c"

# Full name construction
Patient.name.first().given.join(' ') & ' ' & Patient.name.first().family
# Returns: "John William Smith"

Patient.address.line.join(', ')
# Returns: "123 Main St, Apt 4B"
```

---

#### toChars()

Converts string to collection of individual characters.

**Signature:** `string.toChars()`

**Returns:** Collection of single-character strings

**Examples:**

```fhirpath
'hello'.toChars()
# Returns: ["h", "e", "l", "l", "o"]

'ABC'.toChars()
# Returns: ["A", "B", "C"]

# Count specific character
'hello'.toChars().where($this = 'l').count()
# Returns: 2
```

---

### Math Functions

#### abs()

Returns the absolute value of a number.

**Signature:** `number.abs()`

**Returns:** Positive number

**Examples:**

```fhirpath
(-5).abs()
# Returns: 5

(5).abs()
# Returns: 5

(-3.14).abs()
# Returns: 3.14

# Difference between values (always positive)
(Observation.valueQuantity.value - 100).abs()
# Returns: absolute difference from 100
```

---

#### ceiling()

Rounds up to the nearest integer.

**Signature:** `number.ceiling()`

**Returns:** Integer (rounded up)

**Examples:**

```fhirpath
(3.1).ceiling()
# Returns: 4

(3.9).ceiling()
# Returns: 4

(3.0).ceiling()
# Returns: 3

(-3.1).ceiling()
# Returns: -3 (towards zero for negatives)

# Round up quantity
(Observation.valueQuantity.value / 10).ceiling()
# Returns: value divided by 10, rounded up
```

---

#### floor()

Rounds down to the nearest integer.

**Signature:** `number.floor()`

**Returns:** Integer (rounded down)

**Examples:**

```fhirpath
(3.9).floor()
# Returns: 3

(3.1).floor()
# Returns: 3

(-3.1).floor()
# Returns: -4 (away from zero for negatives)

# Calculate complete units
(Observation.valueQuantity.value / 10).floor()
# Returns: complete tens
```

---

#### truncate()

Removes the decimal portion (truncates towards zero).

**Signature:** `number.truncate()`

**Returns:** Integer (truncated)

**Examples:**

```fhirpath
(3.7).truncate()
# Returns: 3

(-3.7).truncate()
# Returns: -3 (towards zero, unlike floor)

(3.0).truncate()
# Returns: 3
```

---

#### round(precision?)

Rounds to specified decimal places.

**Signature:** `number.round()` or `number.round(precision)`

**Parameters:**
- `precision` (optional): Number of decimal places (default 0)

**Returns:** Rounded number

**Examples:**

```fhirpath
(3.5).round()
# Returns: 4

(3.4).round()
# Returns: 3

(3.14159).round(2)
# Returns: 3.14

(3.14159).round(4)
# Returns: 3.1416

(3.145).round(2)
# Returns: 3.15

# Round observation value
Observation.valueQuantity.value.round(1)
# Returns: value rounded to 1 decimal place
```

---

#### sqrt()

Returns the square root.

**Signature:** `number.sqrt()`

**Returns:** Square root (decimal)

**Examples:**

```fhirpath
(16).sqrt()
# Returns: 4.0

(9).sqrt()
# Returns: 3.0

(2).sqrt()
# Returns: 1.4142135...

# Calculate distance
((x1 - x2).power(2) + (y1 - y2).power(2)).sqrt()
# Returns: Euclidean distance
```

---

#### ln()

Returns the natural logarithm (base e).

**Signature:** `number.ln()`

**Returns:** Natural log

**Examples:**

```fhirpath
(1).ln()
# Returns: 0

(2.718281828).ln()
# Returns: ~1.0

(10).ln()
# Returns: 2.302585...
```

---

#### log(base)

Returns the logarithm with specified base.

**Signature:** `number.log(base)`

**Parameters:**
- `base`: Logarithm base

**Returns:** Logarithm

**Examples:**

```fhirpath
(100).log(10)
# Returns: 2

(8).log(2)
# Returns: 3

(1000).log(10)
# Returns: 3
```

---

#### power(exponent)

Raises number to a power.

**Signature:** `number.power(exponent)`

**Parameters:**
- `exponent`: The power to raise to

**Returns:** Result

**Examples:**

```fhirpath
(2).power(3)
# Returns: 8

(2).power(10)
# Returns: 1024

(10).power(2)
# Returns: 100

(4).power(0.5)
# Returns: 2 (square root)

# Calculate BMI component
(height / 100).power(2)
# Returns: height in meters, squared
```

---

#### exp()

Returns e raised to the power of the number.

**Signature:** `number.exp()`

**Returns:** e^number

**Examples:**

```fhirpath
(0).exp()
# Returns: 1

(1).exp()
# Returns: 2.718281828...

(2).exp()
# Returns: 7.389056...
```

---

### Collection Functions

#### distinct()

Returns collection with duplicate values removed.

**Signature:** `collection.distinct()`

**Returns:** Collection with unique values

**Examples:**

```fhirpath
(1 | 2 | 2 | 3 | 3 | 3).distinct()
# Returns: [1, 2, 3]

Patient.address.state.distinct()
# Returns: unique states (e.g., ["MA"] if all addresses in MA)

Patient.telecom.system.distinct()
# Returns: unique systems (e.g., ["phone", "email"])

# Count unique values
Patient.address.city.distinct().count()
# Returns: number of different cities
```

---

#### isDistinct()

Returns `true` if all values in collection are unique.

**Signature:** `collection.isDistinct()`

**Returns:** Boolean

**Examples:**

```fhirpath
(1 | 2 | 3).isDistinct()
# Returns: true

(1 | 2 | 2).isDistinct()
# Returns: false

Patient.identifier.value.isDistinct()
# Returns: true if no duplicate identifier values

# Validation: all codes must be unique
Observation.code.coding.code.isDistinct()
# Returns: true if no duplicate codes
```

---

#### where(criteria)

Filters collection to items matching criteria.

**Signature:** `collection.where(criteria)`

**Parameters:**
- `criteria`: FHIRPath expression evaluated for each item

**Returns:** Filtered collection

**Examples:**

```fhirpath
Patient.name.where(use = 'official')
# Returns: names with use = 'official'

Patient.telecom.where(system = 'phone')
# Returns: phone telecoms only

Patient.telecom.where(system = 'phone' and use = 'mobile')
# Returns: mobile phones only

Patient.address.where(use = 'home' or use = 'work')
# Returns: home or work addresses

# Using $this
Patient.name.given.where($this.startsWith('J'))
# Returns: given names starting with 'J'

(1 | 2 | 3 | 4 | 5).where($this > 2)
# Returns: [3, 4, 5]

# Complex criteria
Observation.component.where(code.coding.code = '8480-6')
# Returns: component with specific code
```

---

#### select(projection)

Projects/transforms each item using an expression.

**Signature:** `collection.select(projection)`

**Parameters:**
- `projection`: Expression to evaluate for each item

**Returns:** Collection of projected values

**Examples:**

```fhirpath
Patient.name.select(family)
# Returns: ["Smith", "Doe"] (just family names)

Patient.telecom.select(value)
# Returns: all telecom values

Patient.name.select(given.first() & ' ' & family)
# Returns: ["John Smith", "Johnny Doe"]

Patient.address.select(city & ', ' & state)
# Returns: ["Boston, MA", "Cambridge, MA"]

# Using $this and $index
(10 | 20 | 30).select($this + $index)
# Returns: [10, 21, 32] (value + 0-based index)

Patient.identifier.select(system & ': ' & value)
# Returns: formatted identifier strings
```

---

#### repeat(expression)

Recursively applies expression, collecting all results.

**Signature:** `collection.repeat(expression)`

**Parameters:**
- `expression`: Expression to apply recursively

**Returns:** All collected results

**Examples:**

```fhirpath
# Get all descendants by repeatedly getting children
Patient.repeat(children())
# Returns: all nested elements recursively

# Traverse linked list
item.repeat(next)
# Returns: all items in linked list

# Get all nested contained resources
Bundle.entry.resource.repeat(contained)
# Returns: all contained resources at any depth
```

---

#### ofType(type)

Filters to items of specified FHIR type.

**Signature:** `collection.ofType(type)`

**Parameters:**
- `type`: FHIR type name

**Returns:** Items of that type

**Examples:**

```fhirpath
Bundle.entry.resource.ofType(Patient)
# Returns: only Patient resources

Bundle.entry.resource.ofType(Observation)
# Returns: only Observation resources

# Get all patients from search results
Bundle.entry.resource.ofType(Patient).name
# Returns: names of all patients in bundle

# Type-safe value extraction
Observation.value.ofType(Quantity).value
# Returns: value only if it's a Quantity
```

---

#### union (|) and union()

Combines two collections, removing duplicates.

**Signature:** `collection1 | collection2` or `collection1.union(collection2)`

**Returns:** Combined collection without duplicates

**Examples:**

```fhirpath
(1 | 2 | 3) | (3 | 4 | 5)
# Returns: [1, 2, 3, 4, 5]

Patient.name.given | Patient.contact.name.given
# Returns: all given names from patient and contacts

# Combine codes
Observation.code.coding.code | Observation.component.code.coding.code
# Returns: all unique codes
```

---

#### combine()

Combines two collections, keeping duplicates.

**Signature:** `collection1.combine(collection2)`

**Returns:** Combined collection (duplicates kept)

**Examples:**

```fhirpath
(1 | 2).combine(2 | 3)
# Returns: [1, 2, 2, 3]

Patient.name.given.combine(Patient.contact.name.given)
# Returns: all given names including duplicates
```

---

#### intersect()

Returns items present in both collections.

**Signature:** `collection1.intersect(collection2)`

**Returns:** Common items

**Examples:**

```fhirpath
(1 | 2 | 3).intersect(2 | 3 | 4)
# Returns: [2, 3]

# Find common codes
Observation.code.coding.code.intersect(requiredCodes)
# Returns: codes that match required list
```

---

#### exclude()

Returns items in first collection but not in second.

**Signature:** `collection1.exclude(collection2)`

**Returns:** Items only in first collection

**Examples:**

```fhirpath
(1 | 2 | 3 | 4).exclude(2 | 4)
# Returns: [1, 3]

Patient.address.city.exclude('Boston')
# Returns: cities except Boston

# Find missing required fields
requiredFields.exclude(presentFields)
# Returns: fields that are missing
```

---

#### flatten()

Flattens nested collections by one level.

**Signature:** `collection.flatten()`

**Returns:** Flattened collection

**Examples:**

```fhirpath
Patient.name.given.flatten()
# Returns: all given names flattened

Bundle.entry.resource.name.flatten()
# Returns: all names from all resources, flattened
```

---

#### subsetOf()

Returns `true` if first collection is a subset of second.

**Signature:** `collection1.subsetOf(collection2)`

**Returns:** Boolean

**Examples:**

```fhirpath
(1 | 2).subsetOf(1 | 2 | 3)
# Returns: true

(1 | 4).subsetOf(1 | 2 | 3)
# Returns: false (4 not in second)

# Check if all patient codes are valid
Patient.identifier.system.subsetOf(validSystems)
# Returns: true if all systems are valid
```

---

#### supersetOf()

Returns `true` if first collection is a superset of second.

**Signature:** `collection1.supersetOf(collection2)`

**Returns:** Boolean

**Examples:**

```fhirpath
(1 | 2 | 3).supersetOf(1 | 2)
# Returns: true

(1 | 2).supersetOf(1 | 2 | 3)
# Returns: false

# Check if patient has all required fields
Patient.children().supersetOf(requiredFields)
# Returns: true if patient has all required fields
```

---

### Type Functions

#### is (type check)

Checks if value is of specified type.

**Signature:** `value is type`

**Returns:** Boolean

**Examples:**

```fhirpath
Patient is Patient
# Returns: true

Patient is Observation
# Returns: false

Observation.value is Quantity
# Returns: true if value is a Quantity

Patient.deceased is boolean
# Returns: true if deceasedBoolean

Patient.birthDate is date
# Returns: true
```

---

#### as (type cast)

Casts value to specified type, returns empty if not that type.

**Signature:** `value as type`

**Returns:** Value if type matches, empty otherwise

**Examples:**

```fhirpath
Observation.value as Quantity
# Returns: the Quantity if value is Quantity, empty otherwise

Patient.deceased as boolean
# Returns: the boolean value if deceasedBoolean

Patient.deceased as dateTime
# Returns: the dateTime if deceasedDateTime

Bundle.entry.resource as Patient
# Returns: only Patient resources
```

---

#### toBoolean()

Converts value to boolean.

**Signature:** `value.toBoolean()`

**Returns:** Boolean or empty

**Conversion rules:**
- `'true'`, `'t'`, `'yes'`, `'y'`, `'1'` → `true`
- `'false'`, `'f'`, `'no'`, `'n'`, `'0'` → `false`
- `1` → `true`, `0` → `false`
- `1.0` → `true`, `0.0` → `false`
- Other values → empty

**Examples:**

```fhirpath
'true'.toBoolean()
# Returns: true

'false'.toBoolean()
# Returns: false

'yes'.toBoolean()
# Returns: true

'1'.toBoolean()
# Returns: true

(1).toBoolean()
# Returns: true

(0).toBoolean()
# Returns: false

'invalid'.toBoolean()
# Returns: empty
```

---

#### toInteger()

Converts value to integer.

**Signature:** `value.toInteger()`

**Returns:** Integer or empty

**Examples:**

```fhirpath
'42'.toInteger()
# Returns: 42

'-123'.toInteger()
# Returns: -123

'3.0'.toInteger()
# Returns: 3 (whole number decimal OK)

'3.5'.toInteger()
# Returns: empty (not a whole number)

true.toInteger()
# Returns: 1

false.toInteger()
# Returns: 0

'abc'.toInteger()
# Returns: empty
```

---

#### toDecimal()

Converts value to decimal.

**Signature:** `value.toDecimal()`

**Returns:** Decimal or empty

**Examples:**

```fhirpath
'3.14'.toDecimal()
# Returns: 3.14

'42'.toDecimal()
# Returns: 42.0

(42).toDecimal()
# Returns: 42.0

true.toDecimal()
# Returns: 1.0

false.toDecimal()
# Returns: 0.0

'abc'.toDecimal()
# Returns: empty
```

---

#### toString()

Converts value to string.

**Signature:** `value.toString()`

**Returns:** String

**Examples:**

```fhirpath
(42).toString()
# Returns: "42"

(3.14).toString()
# Returns: "3.14"

true.toString()
# Returns: "true"

false.toString()
# Returns: "false"

@2024-06-15.toString()
# Returns: "2024-06-15"

# Build formatted string
Observation.valueQuantity.value.toString() & ' ' & Observation.valueQuantity.unit
# Returns: "142 mmHg"
```

---

#### toDate()

Converts string to date.

**Signature:** `value.toDate()`

**Returns:** Date or empty

**Examples:**

```fhirpath
'2024-06-15'.toDate()
# Returns: @2024-06-15

'2024-06'.toDate()
# Returns: @2024-06 (partial date)

'2024'.toDate()
# Returns: @2024 (year only)

'2024-06-15T10:30:00'.toDate()
# Returns: @2024-06-15 (date part only)

'invalid'.toDate()
# Returns: empty
```

---

#### toDateTime()

Converts string to datetime.

**Signature:** `value.toDateTime()`

**Returns:** DateTime or empty

**Examples:**

```fhirpath
'2024-06-15T10:30:00'.toDateTime()
# Returns: @2024-06-15T10:30:00

'2024-06-15T10:30:00Z'.toDateTime()
# Returns: @2024-06-15T10:30:00Z

'2024-06-15'.toDateTime()
# Returns: @2024-06-15T00:00:00 (with default time)
```

---

#### toTime()

Converts string to time.

**Signature:** `value.toTime()`

**Returns:** Time or empty

**Examples:**

```fhirpath
'10:30:00'.toTime()
# Returns: @T10:30:00

'T10:30:00'.toTime()
# Returns: @T10:30:00

'14:30'.toTime()
# Returns: @T14:30

'invalid'.toTime()
# Returns: empty
```

---

#### toQuantity()

Converts value to quantity.

**Signature:** `value.toQuantity()` or `value.toQuantity(unit)`

**Returns:** Quantity or empty

**Examples:**

```fhirpath
(42).toQuantity()
# Returns: 42 '1' (unitless)

'100 mg'.toQuantity()
# Returns: 100 'mg'

'5.5 kg'.toQuantity()
# Returns: 5.5 'kg'
```

---

#### convertsToBoolean(), convertsToInteger(), etc.

Check if conversion is possible without doing it.

**Signature:** `value.convertsTo<Type>()`

**Returns:** Boolean

**Examples:**

```fhirpath
'true'.convertsToBoolean()
# Returns: true

'invalid'.convertsToBoolean()
# Returns: false

'42'.convertsToInteger()
# Returns: true

'3.5'.convertsToInteger()
# Returns: false (not whole number)

'abc'.convertsToInteger()
# Returns: false

'2024-06-15'.convertsToDate()
# Returns: true

'not-a-date'.convertsToDate()
# Returns: false
```

---

### Date/Time Functions

#### today()

Returns the current date.

**Signature:** `today()`

**Returns:** Date

**Examples:**

```fhirpath
today()
# Returns: @2024-12-12 (current date)

Patient.birthDate < today()
# Returns: true (patient was born before today)

today() - 18 years
# Returns: date 18 years ago

# Check if adult
Patient.birthDate <= today() - 18 years
# Returns: true if patient is 18 or older
```

---

#### now()

Returns the current date and time.

**Signature:** `now()`

**Returns:** DateTime

**Examples:**

```fhirpath
now()
# Returns: @2024-12-12T15:30:00Z (current datetime)

Observation.effectiveDateTime < now()
# Returns: true if observation was in the past

now() - 24 hours
# Returns: datetime 24 hours ago
```

---

#### timeOfDay()

Returns the current time.

**Signature:** `timeOfDay()`

**Returns:** Time

**Examples:**

```fhirpath
timeOfDay()
# Returns: @T15:30:00 (current time)
```

---

### Utility Functions

#### iif(condition, true-result, false-result)

Conditional expression - returns one value or another based on condition.

**Signature:** `iif(condition, true-result, false-result)`

**Parameters:**
- `condition`: Boolean expression
- `true-result`: Value if condition is true
- `false-result`: Value if condition is false

**Returns:** Selected value

**Examples:**

```fhirpath
iif(true, 'yes', 'no')
# Returns: "yes"

iif(false, 'yes', 'no')
# Returns: "no"

iif(Patient.gender = 'male', 'Mr.', 'Ms.')
# Returns: appropriate title

iif(Patient.active, 'Active Patient', 'Inactive Patient')
# Returns: status description

iif(Observation.valueQuantity.value > 140, 'High', 'Normal')
# Returns: interpretation

# Nested iif for multiple conditions
iif(value > 140, 'High', iif(value < 90, 'Low', 'Normal'))
# Returns: three-way classification
```

---

#### not()

Negates a boolean value.

**Signature:** `boolean.not()`

**Returns:** Negated boolean

**Examples:**

```fhirpath
true.not()
# Returns: false

false.not()
# Returns: true

Patient.active.not()
# Returns: true if patient is NOT active

Patient.deceased.exists().not()
# Returns: true if no deceased value

(Patient.gender = 'male').not()
# Returns: true if patient is not male
```

---

#### trace(name)

Logs the value for debugging and returns it unchanged.

**Signature:** `value.trace(name)`

**Parameters:**
- `name`: Label for debug output

**Returns:** Same value (unchanged)

**Examples:**

```fhirpath
Patient.name.trace('patient-names')
# Logs the names, returns them unchanged

Patient.telecom.where(system = 'phone').trace('phones').value
# Logs filtered telecoms, then gets values

(1 | 2 | 3).trace('numbers').first()
# Logs [1, 2, 3], returns 1
```

---

### Navigation Functions

#### children()

Returns all direct child elements.

**Signature:** `element.children()`

**Returns:** All immediate children

**Examples:**

```fhirpath
Patient.children()
# Returns: all direct children of Patient (name, gender, birthDate, etc.)

Patient.name.first().children()
# Returns: children of first name (use, family, given, etc.)
```

---

#### descendants()

Returns all descendant elements recursively.

**Signature:** `element.descendants()`

**Returns:** All nested elements at any depth

**Examples:**

```fhirpath
Patient.descendants()
# Returns: ALL nested elements in Patient

Observation.code.descendants()
# Returns: all nested elements under code
```

---

### FHIR-Specific Functions

#### extension(url)

Returns extensions matching the specified URL.

**Signature:** `element.extension(url)`

**Parameters:**
- `url`: Extension URL to match

**Returns:** Matching extensions

**Examples:**

```fhirpath
Patient.extension('http://example.org/race')
# Returns: race extension if present

Patient.birthDate.extension('http://hl7.org/fhir/StructureDefinition/patient-birthTime')
# Returns: birth time extension
```

---

#### resolve()

Resolves a Reference to its target resource.

**Signature:** `reference.resolve()`

**Returns:** Referenced resource (if resolver available)

**Examples:**

```fhirpath
Observation.subject.resolve()
# Returns: the Patient resource (if resolver configured)

Observation.performer.resolve()
# Returns: the Practitioner resource
```

---

### Operators Reference

#### Arithmetic Operators

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `+` | Addition | `1 + 2` | `3` |
| `-` | Subtraction | `10 - 3` | `7` |
| `*` | Multiplication | `4 * 5` | `20` |
| `/` | Division | `10 / 4` | `2.5` |
| `div` | Integer division | `10 div 3` | `3` |
| `mod` | Modulo (remainder) | `10 mod 3` | `1` |
| `&` | String concatenation | `'a' & 'b'` | `"ab"` |

#### Comparison Operators

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `=` | Equals | `1 = 1` | `true` |
| `!=` | Not equals | `1 != 2` | `true` |
| `<` | Less than | `1 < 2` | `true` |
| `>` | Greater than | `2 > 1` | `true` |
| `<=` | Less or equal | `2 <= 2` | `true` |
| `>=` | Greater or equal | `2 >= 2` | `true` |
| `~` | Equivalent (case-insensitive) | `'A' ~ 'a'` | `true` |
| `!~` | Not equivalent | `'A' !~ 'b'` | `true` |

#### Boolean Operators

| Operator | Description | Example | Result |
|----------|-------------|---------|--------|
| `and` | Logical AND | `true and false` | `false` |
| `or` | Logical OR | `true or false` | `true` |
| `xor` | Exclusive OR | `true xor false` | `true` |
| `implies` | Implication | `false implies x` | `true` |

#### Type Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `is` | Type check | `value is Quantity` |
| `as` | Type cast | `value as Quantity` |

#### Collection Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `\|` | Union | `(1 \| 2) \| (2 \| 3)` → `[1,2,3]` |
| `in` | Membership | `2 in (1 \| 2 \| 3)` → `true` |
| `contains` | Contains | `(1 \| 2 \| 3) contains 2` → `true` |

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
    Test expressions interactively with `fhir fhirpath repl -r resource.json`

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
