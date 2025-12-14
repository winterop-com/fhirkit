#!/usr/bin/env python3
"""Example usage of the Terminology Service.

This script demonstrates how to use the InMemoryTerminologyService
to validate codes, check membership, and work with value sets.
"""

from pathlib import Path

from fhirkit.terminology import (
    InMemoryTerminologyService,
    MemberOfRequest,
    SubsumesRequest,
    ValidateCodeRequest,
    ValueSet,
)


def main() -> None:
    """Demonstrate terminology service usage."""
    # Create an in-memory terminology service
    service = InMemoryTerminologyService()

    # Load value sets from the examples directory
    examples_dir = Path(__file__).parent
    loaded = service.load_value_sets_from_directory(examples_dir)
    print(f"Loaded {loaded} value sets from {examples_dir}\n")

    # =========================================
    # Example 1: Validate a code against a value set
    # =========================================
    print("=" * 60)
    print("Example 1: Validate Code")
    print("=" * 60)

    # Valid diabetes code
    request = ValidateCodeRequest(
        url="http://example.org/fhir/ValueSet/diabetes-codes",
        code="44054006",
        system="http://snomed.info/sct",
    )
    result = service.validate_code(request)
    print("Code: 44054006 (Type 2 diabetes mellitus)")
    print("System: http://snomed.info/sct")
    print(f"Valid: {result.result}")
    print()

    # Invalid code
    request = ValidateCodeRequest(
        url="http://example.org/fhir/ValueSet/diabetes-codes",
        code="12345",
        system="http://snomed.info/sct",
    )
    result = service.validate_code(request)
    print("Code: 12345 (invalid code)")
    print(f"Valid: {result.result}")
    print(f"Message: {result.message}")
    print()

    # =========================================
    # Example 2: Check membership in a value set
    # =========================================
    print("=" * 60)
    print("Example 2: Check Membership (memberOf)")
    print("=" * 60)

    # Check if HbA1c code is in lab results value set
    request = MemberOfRequest(
        valueSetUrl="http://example.org/fhir/ValueSet/lab-result-codes",
        code="4548-4",
        system="http://loinc.org",
    )
    result = service.member_of(request)
    print("Code: 4548-4 (HbA1c)")
    print("ValueSet: lab-result-codes")
    print(f"Is member: {result.result}")
    print()

    # Check vital signs
    request = MemberOfRequest(
        valueSetUrl="http://example.org/fhir/ValueSet/vital-signs-codes",
        code="8867-4",
        system="http://loinc.org",
    )
    result = service.member_of(request)
    print("Code: 8867-4 (Heart rate)")
    print("ValueSet: vital-signs-codes")
    print(f"Is member: {result.result}")
    print()

    # =========================================
    # Example 3: Check subsumption
    # =========================================
    print("=" * 60)
    print("Example 3: Check Subsumption")
    print("=" * 60)

    # Same codes should be equivalent
    request = SubsumesRequest(
        codeA="44054006",
        codeB="44054006",
        system="http://snomed.info/sct",
    )
    result = service.subsumes(request)
    print("Code A: 44054006")
    print("Code B: 44054006")
    print(f"Outcome: {result.outcome}")
    print()

    # Different codes
    request = SubsumesRequest(
        codeA="44054006",
        codeB="46635009",
        system="http://snomed.info/sct",
    )
    result = service.subsumes(request)
    print("Code A: 44054006 (Type 2 diabetes)")
    print("Code B: 46635009 (Type 1 diabetes)")
    print(f"Outcome: {result.outcome}")
    print()

    # =========================================
    # Example 4: Retrieve and inspect a ValueSet
    # =========================================
    print("=" * 60)
    print("Example 4: Get ValueSet")
    print("=" * 60)

    vs = service.get_value_set("http://example.org/fhir/ValueSet/vital-signs-codes")
    if vs:
        print(f"Name: {vs.name}")
        print(f"Title: {vs.title}")
        print(f"URL: {vs.url}")
        print(f"Status: {vs.status}")
        if vs.expansion and vs.expansion.contains:
            print(f"Contains {len(vs.expansion.contains)} codes:")
            for item in vs.expansion.contains[:5]:  # Show first 5
                print(f"  - {item.code}: {item.display}")
            if len(vs.expansion.contains) > 5:
                print(f"  ... and {len(vs.expansion.contains) - 5} more")
    print()

    # =========================================
    # Example 5: Create a ValueSet programmatically
    # =========================================
    print("=" * 60)
    print("Example 5: Create ValueSet Programmatically")
    print("=" * 60)

    # Create a simple value set using the model
    custom_vs = ValueSet.model_validate(
        {
            "resourceType": "ValueSet",
            "url": "http://example.org/fhir/ValueSet/my-custom-codes",
            "name": "MyCustomCodes",
            "status": "draft",
            "compose": {
                "include": [
                    {
                        "system": "http://example.org/codesystem",
                        "concept": [
                            {"code": "ABC", "display": "Alpha Beta Charlie"},
                            {"code": "XYZ", "display": "X-ray Yellow Zebra"},
                        ],
                    }
                ]
            },
        }
    )

    service.add_value_set(custom_vs)
    print(f"Added custom ValueSet: {custom_vs.name}")

    # Validate a code in the custom value set
    request = ValidateCodeRequest(
        url="http://example.org/fhir/ValueSet/my-custom-codes",
        code="ABC",
        system="http://example.org/codesystem",
    )
    result = service.validate_code(request)
    print(f"Code 'ABC' in custom ValueSet: {result.result}")
    print()

    print("=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
