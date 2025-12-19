# Web UI Guide

## Overview

The FHIR server includes a comprehensive web-based user interface for browsing, managing, and interacting with FHIR resources. The UI is built with Jinja2 templates and Tailwind CSS.

## Accessing the UI

Start the server and navigate to:

```
http://localhost:8080/
```

## Configuration

Enable/disable the UI via environment variables:

```bash
export FHIR_SERVER_ENABLE_UI=true
export FHIR_SERVER_UI_RESOURCES_PER_PAGE=20
```

Or in code:

```python
from fhirkit.server.config import FHIRServerSettings

settings = FHIRServerSettings(
    enable_ui=True,
    ui_resources_per_page=20,
)
```

## Main Pages

### Dashboard (Home)

**URL**: `/`

The dashboard provides an overview of your FHIR server:

- Total resource count
- Active resource types
- Patient count
- Resource breakdown by type

### Resource Browser

**URL**: `/resources`

Browse all supported resource types organized by category:

- Administrative (Patient, Practitioner, Organization, etc.)
- Clinical (Encounter, Condition, Observation, etc.)
- Medications (MedicationRequest, MedicationAdministration, etc.)
- Care Management (CarePlan, CareTeam, Goal, etc.)
- And more...

### Resource List

**URL**: `/{resource_type}`

View and search resources of a specific type:

- Paginated list with configurable page size
- Dynamic search filters based on resource type
- Quick links to view, edit, or delete
- Create new resource button

**Search Filters by Type**:
- Patient: name, family, given, gender, birthdate
- Condition: patient, code, clinical-status
- Observation: patient, code, category, date
- And type-specific filters for each resource

### Resource Detail

**URL**: `/{resource_type}/{id}`

View a single resource:

- Full JSON with syntax highlighting
- Copy to clipboard button
- Edit and delete actions
- Version history link
- Reference navigation

### Create/Edit Resource

**URL**: `/{resource_type}/new` or `/{resource_type}/{id}/edit`

Create or modify resources:

- JSON editor with template
- Validation feedback
- Save and cancel actions

### Version History

**URL**: `/{resource_type}/{id}/history`

View resource version history:

- List of all versions with timestamps
- Version comparison (diff)
- View any historical version

## Clinical Tools

### FHIRPath Evaluator

**URL**: `/fhirpath`

Evaluate FHIRPath expressions against resources:

- Expression editor with syntax highlighting
- Sample resource selector
- Example expressions by category
- Keyboard shortcut: Ctrl+Enter to evaluate

**Example Expressions**:
```
Patient.name.given
Observation.value.value > 100
Condition.where(clinicalStatus.coding.code = 'active')
```

### CQL Workbench

**URL**: `/cql`

Write and execute CQL (Clinical Quality Language):

- CQL code editor
- Example library browser
- Patient context selection
- Results panel

**Example CQL**:
```cql
define "Active Conditions":
  [Condition] C
    where C.clinicalStatus.coding.code = 'active'
```

### CDS Hooks Testing

**URL**: `/cds-hooks`

Test Clinical Decision Support services:

- Discover available CDS services
- Build service requests
- View prefetch data
- Execute hooks and view responses

**Built-in Services**:
- Patient Summary
- Drug Interaction Check

### Quality Measures

**URL**: `/measures`

Evaluate clinical quality measures:

- Browse available measures
- Select patient populations
- Run measure evaluation
- View measure reports

### Questionnaires

**URL**: `/questionnaires`

Work with FHIR Questionnaires:

- Browse available questionnaires
- View questionnaire structure
- Fill out forms
- Submit responses

### Hierarchy Explorer

**URL**: `/hierarchy`

Visualize organizational hierarchies:

- Organization tree view
- Location hierarchy
- Parent-child relationships
- Expand/collapse navigation

### IPS Generator

**URL**: `/ips`

Generate International Patient Summary documents:

- Select patient
- Generate IPS document
- View composition
- Export document

## Navigation

### Sidebar

The sidebar provides quick access to all sections:

| Section | Pages |
|---------|-------|
| Overview | Dashboard |
| Data | Resources, Hierarchy |
| Tools | FHIRPath, CQL, GraphQL |
| Clinical | CDS Hooks, Measures, Questionnaires, IPS |

### External Links

- **API Docs**: OpenAPI/Swagger documentation
- **GraphQL**: GraphiQL playground
- **Metadata**: Capability Statement

## Mobile Support

The UI is fully responsive:

- Hamburger menu on mobile
- Collapsible sidebar
- Touch-friendly controls
- Responsive tables and forms

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Enter | Execute (FHIRPath, CQL) |
| Escape | Close modals |

## Tips

1. **Search Filters**: Use the dynamic filters to narrow down resource lists
2. **JSON Copy**: Click the copy button to copy resource JSON to clipboard
3. **Reference Links**: Click references to navigate to related resources
4. **Version Compare**: Use the history page to diff resource versions
5. **Examples**: Check the example dropdowns in FHIRPath and CQL editors

## Troubleshooting

### UI Not Loading

1. Check that `enable_ui=True` in settings
2. Verify the server is running
3. Check browser console for errors

### Search Not Working

1. Verify the search parameter is supported for the resource type
2. Check the search value format (dates, tokens, etc.)

### Page Not Found

1. Verify the resource exists
2. Check the resource type spelling (case-sensitive)
