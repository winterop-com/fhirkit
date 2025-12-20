# ChargeItemDefinition

## Overview

A ChargeItemDefinition provides the properties and rules for calculating the price of a billable service or product. It defines the pricing structure, applicable discounts, and conditions under which specific charges apply.

This resource enables dynamic pricing based on patient context, service type, payer rules, and other factors. It supports complex billing scenarios including tiered pricing, package deals, and payer-specific rates.

**Common use cases:**
- Defining service prices
- Managing fee schedules
- Configuring pricing rules
- Supporting payer negotiations
- Automating charge calculations

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/chargeitemdefinition.html](https://hl7.org/fhir/R4/chargeitemdefinition.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `url` | uri | Canonical identifier |
| `version` | string | Business version |
| `title` | string | Human-friendly title |
| `status` | code | draft, active, retired, unknown |
| `date` | date | Date last changed |
| `publisher` | string | Publisher name |
| `description` | markdown | Natural language description |
| `code` | CodeableConcept | Billing code |
| `applicability` | BackboneElement[] | Conditions for applicability |
| `propertyGroup` | BackboneElement[] | Property groups with pricing |
| `propertyGroup.priceComponent` | BackboneElement[] | Price components |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=def-001` |
| `url` | uri | Canonical URL | `url=http://example.org/fhir/ChargeItemDefinition/office-visit` |
| `status` | token | Publication status | `status=active` |

## Examples

### Create a ChargeItemDefinition

```bash
curl -X POST http://localhost:8080/baseR4/ChargeItemDefinition \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "ChargeItemDefinition",
    "url": "http://example.org/fhir/ChargeItemDefinition/office-visit",
    "version": "1.0.0",
    "title": "Office Visit Pricing",
    "status": "active",
    "date": "2024-01-15",
    "publisher": "ACME Health Systems",
    "description": "Pricing for standard office visits",
    "code": {
      "coding": [{
        "system": "http://www.ama-assn.org/go/cpt",
        "code": "99213",
        "display": "Office visit, established patient"
      }]
    },
    "propertyGroup": [{
      "priceComponent": [{
        "type": "base",
        "amount": {
          "value": 150.00,
          "currency": "USD"
        }
      }]
    }]
  }'
```

### Search ChargeItemDefinitions

```bash
# By status
curl "http://localhost:8080/baseR4/ChargeItemDefinition?status=active"

# By URL
curl "http://localhost:8080/baseR4/ChargeItemDefinition?url=http://example.org/fhir/ChargeItemDefinition/office-visit"
```

## Generator Usage

```python
from fhirkit.server.generator import ChargeItemDefinitionGenerator

generator = ChargeItemDefinitionGenerator(seed=42)

# Generate a random charge item definition
definition = generator.generate()

# Generate with specific pricing
pricing = generator.generate(
    title="Lab Test Pricing",
    status="active"
)

# Generate batch
definitions = generator.generate_batch(count=10)
```

## Status Codes

| Code | Description |
|------|-------------|
| draft | Definition is not yet active |
| active | Definition is currently active |
| retired | Definition is no longer active |
| unknown | Status is unknown |

## Related Resources

- [ChargeItem](./charge-item.md) - Charges using this definition
- [Account](./account.md) - Billing accounts
