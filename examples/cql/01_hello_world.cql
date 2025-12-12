/*
 * Hello World - Basic CQL Example
 */
library HelloWorld version '1.0.0'

using FHIR version '4.0.1'

// Simple expression
define HelloMessage: 'Hello, World!'

// Basic arithmetic
define Sum: 1 + 2 + 3

// Boolean expression
define IsTrue: true and not false
