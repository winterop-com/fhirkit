# Plugins Guide

This guide covers the CQL plugin system for extending CQL functionality with custom functions. Plugins allow you to add organization-specific or domain-specific operations that can be called directly from CQL expressions.

## Introduction

### Why Extend CQL?

While CQL provides a comprehensive set of built-in operators and functions, you may need custom functionality for:

- **Organization-specific calculations** (risk scores, proprietary algorithms)
- **Domain-specific operations** (specialized medical calculations)
- **Integration functions** (calling external services, data transformations)
- **Utility functions** (additional math, string, or date operations)

### Plugin Architecture

The plugin system consists of:

| Component | Description |
|-----------|-------------|
| `CQLPluginRegistry` | Container for registered functions |
| `register_function` | Decorator for easy function registration |
| Built-in plugins | Pre-built registries (math, string) |
| Global registry | Shared registry for decorator registration |

---

## Quick Start

### Using the Decorator

The simplest way to register a custom function:

```python
from fhirkit.engine.cql.plugins import register_function
from fhirkit.engine.cql import CQLEvaluator

# Register a custom function
@register_function("MyOrg.Double", description="Doubles a number")
def double(x: int) -> int:
    return x * 2

# Use with evaluator
evaluator = CQLEvaluator()
evaluator.compile("""
    library Test
    define Result: "MyOrg.Double"(21)
""")

result = evaluator.evaluate_definition("Result")
print(result)  # 42
```

### Using the Registry Directly

```python
from fhirkit.engine.cql import CQLEvaluator
from fhirkit.engine.cql.plugins import CQLPluginRegistry

# Create a registry
registry = CQLPluginRegistry()

# Register functions
registry.register("Triple", lambda x: x * 3)
registry.register(
    "Calculate",
    lambda a, b: a + b * 2,
    description="Custom calculation",
    param_types=["Integer", "Integer"],
    return_type="Integer"
)

# Use with evaluator
evaluator = CQLEvaluator(plugin_registry=registry)
evaluator.compile("""
    library Test
    define MyTriple: Triple(7)
""")

result = evaluator.evaluate_definition("MyTriple")
print(result)  # 21
```

---

## CQLPluginRegistry Class

The central class for managing custom functions.

### Creating a Registry

```python
from fhirkit.engine.cql.plugins import CQLPluginRegistry

# Create empty registry
registry = CQLPluginRegistry()
```

### Registering Functions

```python
# Basic registration
registry.register("MyFunc", lambda x: x * 2)

# With full metadata
registry.register(
    "MyOrg.Calculate",
    lambda a, b, c: a + b * c,
    description="Custom calculation: a + b * c",
    param_types=["Integer", "Integer", "Integer"],
    return_type="Integer"
)

# With a regular function
def calculate_risk(age: int, bp: int) -> str:
    if age > 65 and bp > 140:
        return "High"
    elif age > 50 or bp > 130:
        return "Medium"
    return "Low"

registry.register(
    "Clinical.RiskLevel",
    calculate_risk,
    description="Calculate patient risk level",
    param_types=["Integer", "Integer"],
    return_type="String"
)
```

### Checking and Retrieving Functions

```python
# Check if registered
if registry.has("MyFunc"):
    print("Function exists")

# Check with 'in' operator
if "MyFunc" in registry:
    print("Function exists")

# Get the function object
func = registry.get("MyFunc")
if func:
    result = func(10)

# Get function (returns None if not found)
func = registry.get("NonExistent")  # None
```

### Calling Functions

```python
# Direct call through registry
result = registry.call("MyFunc", 21)
print(result)  # 42

# With multiple arguments
result = registry.call("MyOrg.Calculate", 10, 5, 2)
print(result)  # 20

# Raises KeyError if not found
try:
    registry.call("NonExistent")
except KeyError as e:
    print(f"Function not found: {e}")
```

### Function Metadata

```python
# Get metadata
metadata = registry.get_metadata("MyOrg.Calculate")
print(metadata)
# {
#     "description": "Custom calculation: a + b * c",
#     "param_types": ["Integer", "Integer", "Integer"],
#     "return_type": "Integer"
# }

# Access specific fields
print(metadata["description"])
print(metadata["param_types"])
print(metadata["return_type"])
```

### Listing Functions

```python
# Get all function names
functions = registry.list_functions()
print(functions)  # ["MyFunc", "MyOrg.Calculate", "Clinical.RiskLevel"]

# Count functions
print(len(registry))  # 3
```

### Removing Functions

```python
# Unregister a function
removed = registry.unregister("MyFunc")
print(removed)  # True

# Returns False if not found
removed = registry.unregister("NonExistent")
print(removed)  # False

# Clear all functions
registry.clear()
print(len(registry))  # 0
```

### Merging Registries

```python
# Create two registries
registry1 = CQLPluginRegistry()
registry1.register("Func1", lambda: 1)

registry2 = CQLPluginRegistry()
registry2.register("Func2", lambda: 2)

# Merge registry2 into registry1
registry1.merge(registry2)

print(registry1.list_functions())  # ["Func1", "Func2"]

# Note: If same name exists, the merged function overwrites
```

---

## Decorator Registration

Use the `@register_function` decorator for convenient registration.

### Basic Usage

```python
from fhirkit.engine.cql.plugins import register_function

@register_function("MyFunc")
def my_func(x):
    return x * 2

# The function works normally
print(my_func(10))  # 20

# And is registered in the global registry
```

### With Metadata

```python
@register_function(
    "Clinical.BMI",
    description="Calculate Body Mass Index",
    param_types=["Decimal", "Decimal"],
    return_type="Decimal"
)
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI from weight (kg) and height (m)."""
    if height_m <= 0:
        return None
    return round(weight_kg / (height_m ** 2), 1)

# Use it
print(calculate_bmi(70, 1.75))  # 22.9
```

### Namespaced Functions

Use namespaces to organize functions:

```python
@register_function("MyOrg.Cardio.FraminghamScore")
def framingham_score(age, total_chol, hdl, sbp, smoker, diabetic):
    # Complex calculation...
    return score

@register_function("MyOrg.Renal.eGFR")
def egfr(creatinine, age, is_female, is_african_american):
    # CKD-EPI formula...
    return result
```

---

## Global Registry

The decorator uses a global registry shared across the application.

### Accessing the Global Registry

```python
from fhirkit.engine.cql.plugins import get_global_registry

registry = get_global_registry()

# List all globally registered functions
print(registry.list_functions())

# Access a function
if registry.has("MyOrg.Calculate"):
    result = registry.call("MyOrg.Calculate", 1, 2)
```

### Using with Evaluator

```python
from fhirkit.engine.cql import CQLEvaluator
from fhirkit.engine.cql.plugins import get_global_registry

# Register functions with decorator (uses global registry)
@register_function("Double")
def double(x):
    return x * 2

# Get global registry and pass to evaluator
registry = get_global_registry()
evaluator = CQLEvaluator(plugin_registry=registry)
```

---

## Built-in Plugins

The library includes pre-built plugin registries for common operations.

### Math Plugins

```python
from fhirkit.engine.cql.plugins import create_math_plugins

registry = create_math_plugins()

# Available functions
print(registry.list_functions())
# ["Math.Sin", "Math.Cos", "Math.Tan", "Math.Sqrt", "Math.Log", "Math.Log10"]

# Usage
import math

print(registry.call("Math.Sin", 0))        # 0.0
print(registry.call("Math.Cos", 0))        # 1.0
print(registry.call("Math.Sqrt", 16))      # 4.0
print(registry.call("Math.Log", math.e))   # 1.0
print(registry.call("Math.Log10", 100))    # 2.0

# Null handling
print(registry.call("Math.Sin", None))     # None
print(registry.call("Math.Sqrt", -1))      # None (invalid input)
```

### String Plugins

```python
from fhirkit.engine.cql.plugins import create_string_plugins

registry = create_string_plugins()

# Available functions
print(registry.list_functions())
# ["String.Reverse", "String.Trim", "String.IsBlank", "String.PadLeft", "String.PadRight"]

# Usage
print(registry.call("String.Reverse", "hello"))      # "olleh"
print(registry.call("String.Trim", "  hello  "))     # "hello"
print(registry.call("String.IsBlank", ""))           # True
print(registry.call("String.IsBlank", "hi"))         # False
print(registry.call("String.PadLeft", "42", 5, "0")) # "00042"
print(registry.call("String.PadRight", "hi", 5))     # "hi   "

# Null handling
print(registry.call("String.Reverse", None))         # None
print(registry.call("String.IsBlank", None))         # True
```

### Combining Built-in Plugins

```python
from fhirkit.engine.cql.plugins import (
    CQLPluginRegistry,
    create_math_plugins,
    create_string_plugins
)

# Create combined registry
registry = CQLPluginRegistry()
registry.merge(create_math_plugins())
registry.merge(create_string_plugins())

# Add your own functions
registry.register("MyOrg.Custom", lambda x: x)

# Use with evaluator
evaluator = CQLEvaluator(plugin_registry=registry)
```

---

## Integration with CQL Evaluator

### Setting Plugin Registry

```python
from fhirkit.engine.cql import CQLEvaluator
from fhirkit.engine.cql.plugins import CQLPluginRegistry

# Method 1: Constructor
registry = CQLPluginRegistry()
registry.register("Double", lambda x: x * 2)
evaluator = CQLEvaluator(plugin_registry=registry)

# Method 2: Property setter
evaluator = CQLEvaluator()
evaluator.plugin_registry = registry

# Method 3: Access existing registry
print(evaluator.plugin_registry)  # CQLPluginRegistry or None
```

### Calling Plugin Functions from CQL

```python
registry = CQLPluginRegistry()
registry.register("Triple", lambda x: x * 3)

evaluator = CQLEvaluator(plugin_registry=registry)
evaluator.compile("""
    library Test
    define MyResult: Triple(7)
""")

result = evaluator.evaluate_definition("MyResult")
print(result)  # 21
```

### Namespaced Function Calls

For namespaced functions (containing dots), use quoted syntax:

```python
registry = CQLPluginRegistry()
registry.register("MyOrg.Calculate", lambda a, b: a + b)

evaluator = CQLEvaluator(plugin_registry=registry)
evaluator.compile("""
    library Test
    define MyResult: "MyOrg.Calculate"(10, 5)
""")

result = evaluator.evaluate_definition("MyResult")
print(result)  # 15
```

---

## Creating Custom Plugins

### Single Function Plugin

```python
from fhirkit.engine.cql.plugins import CQLPluginRegistry

def create_bmi_plugin() -> CQLPluginRegistry:
    """Create a plugin for BMI calculation."""
    registry = CQLPluginRegistry()

    def calculate_bmi(weight_kg, height_m):
        if weight_kg is None or height_m is None or height_m <= 0:
            return None
        return round(weight_kg / (height_m ** 2), 1)

    def bmi_category(bmi):
        if bmi is None:
            return None
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    registry.register(
        "Clinical.BMI",
        calculate_bmi,
        description="Calculate BMI from weight and height",
        param_types=["Decimal", "Decimal"],
        return_type="Decimal"
    )

    registry.register(
        "Clinical.BMICategory",
        bmi_category,
        description="Get BMI category",
        param_types=["Decimal"],
        return_type="String"
    )

    return registry
```

### Multi-Function Plugin Module

```python
# my_plugins.py
from fhirkit.engine.cql.plugins import CQLPluginRegistry

def create_cardio_plugins() -> CQLPluginRegistry:
    """Create cardiovascular risk calculation plugins."""
    registry = CQLPluginRegistry()

    def ldl_goal(risk_level: str) -> int:
        """Get LDL goal based on risk level."""
        goals = {
            "Very High": 55,
            "High": 70,
            "Moderate": 100,
            "Low": 116
        }
        return goals.get(risk_level, 116)

    def framingham_risk(age, total_chol, hdl, systolic_bp, is_treated, is_smoker, is_diabetic):
        """Calculate 10-year cardiovascular risk."""
        # Simplified calculation
        score = 0
        if age >= 60:
            score += 2
        elif age >= 50:
            score += 1
        if total_chol > 240:
            score += 1
        if hdl < 40:
            score += 2
        if systolic_bp > 160:
            score += 2
        if is_smoker:
            score += 2
        if is_diabetic:
            score += 2
        return score * 2  # Simplified percentage

    registry.register(
        "Cardio.LDLGoal",
        ldl_goal,
        description="Get target LDL based on risk category",
        param_types=["String"],
        return_type="Integer"
    )

    registry.register(
        "Cardio.FraminghamRisk",
        framingham_risk,
        description="Calculate 10-year cardiovascular risk percentage",
        param_types=["Integer", "Integer", "Integer", "Integer", "Boolean", "Boolean", "Boolean"],
        return_type="Integer"
    )

    return registry
```

### Using Your Custom Plugins

```python
from fhirkit.engine.cql import CQLEvaluator
from fhirkit.engine.cql.plugins import CQLPluginRegistry
from my_plugins import create_cardio_plugins, create_bmi_plugin

# Combine plugins
registry = CQLPluginRegistry()
registry.merge(create_cardio_plugins())
registry.merge(create_bmi_plugin())

# Use with evaluator
evaluator = CQLEvaluator(plugin_registry=registry)
evaluator.compile("""
    library CardioRisk
    using FHIR version '4.0.1'

    context Patient

    define BMI: "Clinical.BMI"(80, 1.75)
    define BMICategory: "Clinical.BMICategory"(BMI)
    define LDLGoal: "Cardio.LDLGoal"('High')
""")
```

---

## Null Handling

Always handle null values in your plugin functions:

```python
# Good: Explicit null check
registry.register(
    "SafeDivide",
    lambda a, b: a / b if a is not None and b is not None and b != 0 else None
)

# Good: Using guard clause
def safe_sqrt(x):
    if x is None or x < 0:
        return None
    import math
    return math.sqrt(x)

registry.register("SafeSqrt", safe_sqrt)

# Good: Optional parameter handling
def format_name(first, last, middle=None):
    if first is None or last is None:
        return None
    if middle:
        return f"{last}, {first} {middle}"
    return f"{last}, {first}"

registry.register("FormatName", format_name)
```

---

## Error Handling

### In Plugin Functions

```python
def safe_parse_date(date_string):
    """Parse date with error handling."""
    if date_string is None:
        return None
    try:
        from datetime import datetime
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        return None  # Return None for invalid dates

registry.register("ParseDate", safe_parse_date)
```

### Raising Errors

```python
def strict_divide(a, b):
    """Division that raises on error."""
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

registry.register("StrictDivide", strict_divide)

# Errors will propagate to the CQL evaluator
```

---

## Testing Plugins

### Unit Testing Registry

```python
import pytest
from fhirkit.engine.cql.plugins import CQLPluginRegistry

def test_custom_function():
    registry = CQLPluginRegistry()
    registry.register("Double", lambda x: x * 2)

    assert registry.has("Double")
    assert registry.call("Double", 21) == 42

def test_null_handling():
    registry = CQLPluginRegistry()
    registry.register("SafeDouble", lambda x: x * 2 if x is not None else None)

    assert registry.call("SafeDouble", 5) == 10
    assert registry.call("SafeDouble", None) is None

def test_metadata():
    registry = CQLPluginRegistry()
    registry.register(
        "Calc",
        lambda x: x,
        description="Test function",
        param_types=["Integer"],
        return_type="Integer"
    )

    metadata = registry.get_metadata("Calc")
    assert metadata["description"] == "Test function"
    assert metadata["param_types"] == ["Integer"]
```

### Integration Testing with Evaluator

```python
from fhirkit.engine.cql import CQLEvaluator
from fhirkit.engine.cql.plugins import CQLPluginRegistry

def test_plugin_in_cql():
    registry = CQLPluginRegistry()
    registry.register("Triple", lambda x: x * 3)

    evaluator = CQLEvaluator(plugin_registry=registry)
    evaluator.compile("""
        library Test
        define Result: Triple(7)
    """)

    result = evaluator.evaluate_definition("Result")
    assert result == 21
```

---

## Best Practices

### Naming Conventions

```python
# Good: Use namespaces for organization
registry.register("MyOrg.Clinical.CalculateRisk", func)
registry.register("MyOrg.Financial.CalculateCost", func)

# Good: Clear, descriptive names
registry.register("Clinical.BMI", calculate_bmi)
registry.register("Clinical.eGFR", calculate_egfr)

# Avoid: Generic names without namespace
registry.register("Calculate", func)  # Too vague
registry.register("Func1", func)  # Meaningless
```

### Documentation

```python
# Always provide metadata
registry.register(
    "Clinical.CHA2DS2VASc",
    cha2ds2_vasc_score,
    description="Calculate CHA2DS2-VASc stroke risk score for atrial fibrillation",
    param_types=["Integer", "Boolean", "Boolean", "Boolean", "Boolean", "Boolean", "Boolean"],
    return_type="Integer"
)
```

### Function Design

```python
# Good: Pure functions without side effects
def double(x):
    return x * 2 if x is not None else None

# Avoid: Functions with side effects
def bad_function(x):
    print(f"Processing {x}")  # Side effect
    some_global.counter += 1   # Side effect
    return x * 2
```

### Registry Organization

```python
# Organize related functions into separate factory functions
def create_cardio_plugins() -> CQLPluginRegistry:
    """Cardiovascular calculation plugins."""
    registry = CQLPluginRegistry()
    # ... register cardio functions
    return registry

def create_renal_plugins() -> CQLPluginRegistry:
    """Renal function calculation plugins."""
    registry = CQLPluginRegistry()
    # ... register renal functions
    return registry

# Combine as needed
def create_clinical_plugins() -> CQLPluginRegistry:
    """All clinical plugins."""
    registry = CQLPluginRegistry()
    registry.merge(create_cardio_plugins())
    registry.merge(create_renal_plugins())
    return registry
```

---

## Examples

### Clinical Risk Score Plugin

```python
from fhirkit.engine.cql.plugins import CQLPluginRegistry

def create_risk_score_plugins() -> CQLPluginRegistry:
    """Create clinical risk score calculation plugins."""
    registry = CQLPluginRegistry()

    def cha2ds2_vasc(
        age: int,
        is_female: bool,
        has_chf: bool,
        has_hypertension: bool,
        has_stroke_tia: bool,
        has_vascular_disease: bool,
        has_diabetes: bool
    ) -> int:
        """Calculate CHA2DS2-VASc score for stroke risk in A-fib."""
        if age is None:
            return None

        score = 0
        if has_chf: score += 1
        if has_hypertension: score += 1
        if age >= 75: score += 2
        elif age >= 65: score += 1
        if has_diabetes: score += 1
        if has_stroke_tia: score += 2
        if has_vascular_disease: score += 1
        if is_female: score += 1

        return score

    def wells_score_dvt(
        active_cancer: bool,
        paralysis_paresis: bool,
        bedridden: bool,
        localized_tenderness: bool,
        entire_leg_swollen: bool,
        calf_swelling_3cm: bool,
        pitting_edema: bool,
        collateral_veins: bool,
        previous_dvt: bool,
        alternative_diagnosis: bool
    ) -> int:
        """Calculate Wells score for DVT probability."""
        score = 0
        if active_cancer: score += 1
        if paralysis_paresis: score += 1
        if bedridden: score += 1
        if localized_tenderness: score += 1
        if entire_leg_swollen: score += 1
        if calf_swelling_3cm: score += 1
        if pitting_edema: score += 1
        if collateral_veins: score += 1
        if previous_dvt: score += 1
        if alternative_diagnosis: score -= 2

        return max(score, 0)

    registry.register(
        "Risk.CHA2DS2VASc",
        cha2ds2_vasc,
        description="CHA2DS2-VASc stroke risk score for atrial fibrillation"
    )

    registry.register(
        "Risk.WellsDVT",
        wells_score_dvt,
        description="Wells score for DVT probability assessment"
    )

    return registry
```

### Data Transformation Plugin

```python
from fhirkit.engine.cql.plugins import CQLPluginRegistry

def create_transform_plugins() -> CQLPluginRegistry:
    """Create data transformation plugins."""
    registry = CQLPluginRegistry()

    def format_phone(phone: str) -> str:
        """Format phone number as (XXX) XXX-XXXX."""
        if phone is None:
            return None
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return phone

    def parse_mrn(mrn: str, prefix: str = "MRN-") -> int:
        """Parse MRN string to integer ID."""
        if mrn is None:
            return None
        if mrn.startswith(prefix):
            mrn = mrn[len(prefix):]
        try:
            return int(mrn)
        except ValueError:
            return None

    def age_in_months(birth_date, reference_date=None):
        """Calculate age in months."""
        from datetime import date
        if birth_date is None:
            return None
        if reference_date is None:
            reference_date = date.today()
        months = (reference_date.year - birth_date.year) * 12
        months += reference_date.month - birth_date.month
        if reference_date.day < birth_date.day:
            months -= 1
        return max(months, 0)

    registry.register("Transform.FormatPhone", format_phone)
    registry.register("Transform.ParseMRN", parse_mrn)
    registry.register("Transform.AgeInMonths", age_in_months)

    return registry
```

---

## See Also

- [CQL Tutorial](cql-tutorial.md) - CQL language basics
- [CQL Python API](cql-api.md) - CQL evaluator reference
- [Measure Evaluation Guide](measure-guide.md) - Quality measures
