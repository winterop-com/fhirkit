# Device

## Overview

The Device resource represents medical devices used in patient care. This includes implanted devices, durable medical equipment, and monitoring devices.

## FHIR R4 Specification

See the official HL7 specification: [https://hl7.org/fhir/R4/device.html](https://hl7.org/fhir/R4/device.html)

## Supported Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Logical ID of the resource |
| `meta` | Meta | Resource metadata |
| `identifier` | Identifier[] | Business identifiers |
| `definition` | Reference | Device definition |
| `udiCarrier` | BackboneElement[] | UDI barcode info |
| `status` | code | active, inactive, entered-in-error, unknown |
| `statusReason` | CodeableConcept[] | Why current status |
| `distinctIdentifier` | string | Instance identifier |
| `manufacturer` | string | Manufacturer name |
| `manufactureDate` | dateTime | Manufacturing date |
| `expirationDate` | dateTime | Expiration date |
| `lotNumber` | string | Lot number |
| `serialNumber` | string | Serial number |
| `deviceName` | BackboneElement[] | Device names |
| `modelNumber` | string | Model number |
| `partNumber` | string | Part number |
| `type` | CodeableConcept | Device type |
| `specialization` | BackboneElement[] | Device specializations |
| `version` | BackboneElement[] | Device versions |
| `property` | BackboneElement[] | Device properties |
| `patient` | Reference(Patient) | Patient using device |
| `owner` | Reference(Organization) | Device owner |
| `contact` | ContactPoint[] | Contact details |
| `location` | Reference(Location) | Device location |
| `url` | uri | Device network URL |
| `note` | Annotation[] | Notes |
| `safety` | CodeableConcept[] | Safety information |
| `parent` | Reference(Device) | Parent device |

## Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Resource ID | `_id=dev-001` |
| `identifier` | token | Business identifier | `identifier=DEV-12345` |
| `patient` | reference | Patient using device | `patient=Patient/123` |
| `status` | token | Device status | `status=active` |
| `type` | token | Device type | `type=43770009` |
| `manufacturer` | string | Manufacturer | `manufacturer=Acme` |
| `model` | string | Model number | `model=BPM-2000` |
| `udi-carrier` | string | UDI carrier HRF | `udi-carrier=01234` |
| `udi-di` | string | UDI device identifier | `udi-di=09876` |
| `device-name` | string | Device name | `device-name=Monitor` |
| `organization` | reference | Owner organization | `organization=Organization/456` |
| `location` | reference | Device location | `location=Location/789` |

## Examples

### Create a Device

```bash
curl -X POST http://localhost:8080/baseR4/Device \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Device",
    "status": "active",
    "udiCarrier": [{
      "deviceIdentifier": "09876543210987",
      "carrierHRF": "(01)09876543210987(17)240101(10)LOT123"
    }],
    "manufacturer": "Acme Medical Devices Inc.",
    "manufactureDate": "2023-06-15",
    "expirationDate": "2028-06-15",
    "lotNumber": "LOT-2023-456",
    "serialNumber": "SN-2023-12345",
    "deviceName": [{
      "name": "Acme Blood Pressure Monitor Pro",
      "type": "user-friendly-name"
    }],
    "modelNumber": "BPM-PRO-2000",
    "type": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "43770009",
        "display": "Sphygmomanometer"
      }],
      "text": "Blood Pressure Monitor"
    },
    "patient": {
      "reference": "Patient/patient-001"
    },
    "owner": {
      "reference": "Organization/organization-001"
    },
    "location": {
      "reference": "Location/location-001"
    },
    "note": [{
      "text": "Device assigned for home monitoring"
    }]
  }'
```

### Search Devices

```bash
# By patient
curl "http://localhost:8080/baseR4/Device?patient=Patient/123"

# By status
curl "http://localhost:8080/baseR4/Device?status=active"

# By type
curl "http://localhost:8080/baseR4/Device?type=43770009"

# By manufacturer
curl "http://localhost:8080/baseR4/Device?manufacturer=Acme"
```

### Patient Compartment

```bash
# Get all devices for a patient
curl "http://localhost:8080/baseR4/Patient/123/Device"
```

## Status Codes

| Code | Display | Description |
|------|---------|-------------|
| active | Active | Device is available for use |
| inactive | Inactive | Not currently available |
| entered-in-error | Entered in Error | Data entry error |
| unknown | Unknown | Status unknown |

## Device Types (SNOMED CT)

| Code | Display |
|------|---------|
| 43770009 | Sphygmomanometer |
| 19257004 | Defibrillator |
| 303607000 | Cochlear implant |
| 272265001 | Bone prosthesis |
| 417425009 | Artificial eye |
| 304070002 | Wheelchair |
| 37299003 | Glucose monitor |
| 53350007 | Pacemaker |
| 462894001 | Insulin pump |
| 360063003 | Continuous positive airway pressure unit |

## Device Name Types

| Code | Display |
|------|---------|
| udi-label-name | UDI Label Name |
| user-friendly-name | User Friendly Name |
| patient-reported-name | Patient Reported Name |
| manufacturer-name | Manufacturer Name |
| model-name | Model Name |
| other | Other |
