/*
 * Functions - User-defined functions in CQL
 */
library Functions version '1.0.0'

using FHIR version '4.0.1'

// Simple function
define function Add(a Integer, b Integer) returns Integer:
    a + b

// Function with null handling
define function SafeDivide(numerator Decimal, denominator Decimal) returns Decimal:
    if denominator = 0 then null
    else numerator / denominator

// String function
define function FormatName(given String, family String) returns String:
    given + ' ' + family

// Boolean function
define function IsAdult(birthDate Date) returns Boolean:
    years between birthDate and Today() >= 18

// Function using FHIR types
define function GetAge(patient FHIR.Patient) returns Integer:
    years between patient.birthDate and Today()

// Function with list
define function Average(values List<Decimal>) returns Decimal:
    Sum(values) / Count(values)

// Using the functions
define TestAdd: Add(5, 3)

define TestDivide: SafeDivide(10.0, 2.0)

define TestDivideByZero: SafeDivide(10.0, 0.0)

define TestFormat: FormatName('John', 'Doe')
