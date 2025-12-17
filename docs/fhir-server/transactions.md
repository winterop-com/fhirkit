# Transactions

## Overview

The FHIR server supports both batch and transaction Bundle types with different processing semantics.

## FHIR Specification

- [Bundle](https://hl7.org/fhir/R4/bundle.html) - FHIR R4 Bundle Resource
- [HTTP Transactions](https://hl7.org/fhir/R4/http.html#transaction) - FHIR Transaction Processing

## Bundle Types

### Batch

A batch Bundle processes entries independently. Each entry is executed separately, and failures in one entry do not affect others.

```json
{
  "resourceType": "Bundle",
  "type": "batch",
  "entry": [
    {
      "resource": { "resourceType": "Patient", "name": [{"family": "Test"}] },
      "request": { "method": "POST", "url": "Patient" }
    },
    {
      "request": { "method": "GET", "url": "Patient/123" }
    }
  ]
}
```

**Behavior:**
- Each entry processed independently
- Failures do not affect other entries
- Response type: `batch-response`
- All entries return their individual status codes

### Transaction

A transaction Bundle processes entries atomically. All entries succeed together or all fail together (all-or-nothing semantics).

```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": { "resourceType": "Patient", "id": "p1", "name": [{"family": "Test1"}] },
      "request": { "method": "PUT", "url": "Patient/p1" }
    },
    {
      "resource": { "resourceType": "Patient", "id": "p2", "name": [{"family": "Test2"}] },
      "request": { "method": "PUT", "url": "Patient/p2" }
    }
  ]
}
```

**Behavior:**
- All entries processed atomically
- If any entry fails, ALL changes are rolled back
- Response type: `transaction-response`
- Either all succeed (200) or all fail (4xx/5xx)

## Transaction Atomicity

### How Rollback Works

The server implements transaction atomicity using a snapshot/rollback mechanism:

1. **Begin**: Before processing, a snapshot of the current state is taken
2. **Process**: Each entry in the transaction is processed sequentially
3. **Commit**: If all entries succeed, the snapshot is discarded
4. **Rollback**: If any entry fails, the state is restored from the snapshot

### What Gets Rolled Back

On failure, the following are restored to their pre-transaction state:

- All resources (creates, updates, deletes)
- Resource version history
- Deleted resource markers

### Example: Successful Transaction

```bash
curl -X POST http://localhost:8080/baseR4 \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Patient",
          "id": "patient-1",
          "name": [{"family": "Smith"}]
        },
        "request": {"method": "PUT", "url": "Patient/patient-1"}
      },
      {
        "resource": {
          "resourceType": "Observation",
          "id": "obs-1",
          "status": "final",
          "code": {"text": "Test"},
          "subject": {"reference": "Patient/patient-1"}
        },
        "request": {"method": "PUT", "url": "Observation/obs-1"}
      }
    ]
  }'
```

Response (200 OK):
```json
{
  "resourceType": "Bundle",
  "type": "transaction-response",
  "entry": [
    {
      "response": {
        "status": "201 Created",
        "location": "Patient/patient-1/_history/1",
        "etag": "W/\"1\""
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/obs-1/_history/1",
        "etag": "W/\"1\""
      }
    }
  ]
}
```

### Example: Failed Transaction (Rollback)

```bash
curl -X POST http://localhost:8080/baseR4 \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Patient",
          "id": "new-patient",
          "name": [{"family": "New"}]
        },
        "request": {"method": "PUT", "url": "Patient/new-patient"}
      },
      {
        "request": {"method": "GET", "url": "Patient/nonexistent"}
      }
    ]
  }'
```

Response (404 Not Found):
```json
{
  "resourceType": "OperationOutcome",
  "issue": [{
    "severity": "error",
    "code": "not-found",
    "diagnostics": "Transaction failed at entry 1: Resource not found"
  }]
}
```

In this case, `Patient/new-patient` is NOT created because the transaction failed.

## Batch vs Transaction Comparison

| Feature | Batch | Transaction |
|---------|-------|-------------|
| Atomicity | No | Yes |
| Rollback on failure | No | Yes |
| Independent entries | Yes | No |
| Response type | batch-response | transaction-response |
| Use case | Bulk operations | Related changes |

## Supported Methods

Both batch and transaction support these request methods:

| Method | Description |
|--------|-------------|
| `GET` | Read a resource |
| `POST` | Create a resource |
| `PUT` | Update/create a resource |
| `DELETE` | Delete a resource |

## Best Practices

### Use Transactions When

- Creating related resources (Patient + Observations)
- Updating multiple resources that must be consistent
- Performing operations that should all succeed or all fail

### Use Batches When

- Performing independent bulk operations
- Uploading large datasets where partial success is acceptable
- Running multiple read operations

## Error Handling

### Transaction Errors

When a transaction fails:

1. An OperationOutcome is returned with details about the failure
2. The entry index where the failure occurred is included
3. All changes from earlier entries are rolled back
4. The system state is restored to pre-transaction state

### Batch Errors

When a batch entry fails:

1. The batch continues processing remaining entries
2. The failed entry has an OperationOutcome in its response
3. Successful entries remain committed
4. The overall batch returns 200 with mixed entry statuses

## Python API

The FHIRStore provides a transaction context manager for programmatic use:

```python
from fhirkit.server.storage.fhir_store import FHIRStore

store = FHIRStore()

# Successful transaction
with store.transaction():
    store.create({"resourceType": "Patient", "name": [{"family": "Test"}]})
    store.create({"resourceType": "Observation", "status": "final"})
# Both resources are committed

# Failed transaction
try:
    with store.transaction():
        store.create({"resourceType": "Patient", "name": [{"family": "Temp"}]})
        raise ValueError("Something went wrong")
except Exception:
    pass
# Patient "Temp" is NOT created - rolled back
```
