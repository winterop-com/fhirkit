# Binary Resource

## Overview

Binary is a special FHIR resource for raw binary content like PDFs, images, and other files that don't fit the standard FHIR resource structure.

## FHIR Specification

- [Binary](https://hl7.org/fhir/R4/binary.html) - FHIR R4 Binary Resource

## Structure

| Element | Type | Description |
|---------|------|-------------|
| `contentType` | code | MIME type (required) |
| `data` | base64Binary | Base64-encoded content |
| `securityContext` | Reference | Security context for access control |

## Content Negotiation

The server supports content negotiation for Binary resources:

### FHIR JSON Response (default)

When requesting with `Accept: application/fhir+json`:

```bash
curl -H "Accept: application/fhir+json" http://localhost:8080/baseR4/Binary/123
```

Returns:
```json
{
  "resourceType": "Binary",
  "id": "123",
  "contentType": "application/pdf",
  "data": "JVBERi0xLjQKJ..."
}
```

### Raw Binary Response

When requesting with the content's MIME type:

```bash
curl -H "Accept: application/pdf" http://localhost:8080/baseR4/Binary/123 -o document.pdf
```

Returns the raw PDF bytes directly.

## Search Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `_id` | token | Resource ID |
| `contenttype` | token | Filter by MIME type |

### Search Examples

```bash
# Find all Binary resources
GET /Binary

# Find by content type
GET /Binary?contenttype=application/pdf

# Find images
GET /Binary?contenttype=image/png
```

## CRUD Operations

### Create Binary

```bash
curl -X POST http://localhost:8080/baseR4/Binary \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Binary",
    "contentType": "application/pdf",
    "data": "JVBERi0xLjQKJeLj..."
  }'
```

### Read Binary (JSON)

```bash
curl http://localhost:8080/baseR4/Binary/123
```

### Read Binary (Raw)

```bash
# Download PDF
curl -H "Accept: application/pdf" \
  http://localhost:8080/baseR4/Binary/123 \
  -o document.pdf

# Download image
curl -H "Accept: image/png" \
  http://localhost:8080/baseR4/Binary/123 \
  -o image.png
```

### Update Binary

```bash
curl -X PUT http://localhost:8080/baseR4/Binary/123 \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Binary",
    "id": "123",
    "contentType": "application/pdf",
    "data": "JVBERi0xLjQKJupdated..."
  }'
```

### Delete Binary

```bash
curl -X DELETE http://localhost:8080/baseR4/Binary/123
```

## Supported Content Types

The server supports any MIME type. Common types include:

| Category | MIME Types |
|----------|------------|
| Documents | `application/pdf`, `text/plain`, `text/html` |
| Images | `image/png`, `image/jpeg`, `image/gif` |
| Data | `application/json`, `application/xml`, `text/csv` |
| Healthcare | `application/hl7-v2`, `application/fhir+json`, `application/dicom` |

## Use Cases

### Storing PDF Reports

```bash
# Base64 encode and create
base64 report.pdf > report_b64.txt
curl -X POST http://localhost:8080/baseR4/Binary \
  -H "Content-Type: application/fhir+json" \
  -d "{
    \"resourceType\": \"Binary\",
    \"contentType\": \"application/pdf\",
    \"data\": \"$(cat report_b64.txt)\"
  }"
```

### Storing Images

```bash
# Create image Binary
curl -X POST http://localhost:8080/baseR4/Binary \
  -H "Content-Type: application/fhir+json" \
  -d "{
    \"resourceType\": \"Binary\",
    \"contentType\": \"image/png\",
    \"data\": \"$(base64 image.png)\"
  }"
```

### Linking to DocumentReference

Binary resources are often referenced from DocumentReference:

```json
{
  "resourceType": "DocumentReference",
  "content": [{
    "attachment": {
      "contentType": "application/pdf",
      "url": "Binary/123"
    }
  }]
}
```

## Generator

The server includes a BinaryGenerator for creating sample Binary resources:

```python
from fhirkit.server.generator import BinaryGenerator

gen = BinaryGenerator(seed=42)

# Generate random Binary
binary = gen.generate()

# Generate with specific content type
binary = gen.generate(content_type="application/pdf")

# Generate with custom data
binary = gen.generate(
    content_type="text/plain",
    data=b"Hello, World!"
)
```

## Notes

- Binary resources have limited search support (only `_id` and `contenttype`)
- Large files should consider using external storage with DocumentReference
- The `securityContext` field can reference another resource for access control
- Binary does not participate in patient compartments
