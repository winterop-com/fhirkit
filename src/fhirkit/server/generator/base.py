"""Base class for FHIR resource generators."""

import uuid
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta, timezone
from typing import Any

from faker import Faker


class FHIRResourceGenerator(ABC):
    """Abstract base class for FHIR resource generators using Faker."""

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        """Initialize the generator.

        Args:
            faker: Faker instance to use (creates new one if None)
            seed: Random seed for reproducibility
        """
        self.faker = faker or Faker()
        if seed is not None:
            Faker.seed(seed)
            self.faker.seed_instance(seed)

    @abstractmethod
    def generate(self, **kwargs: Any) -> dict[str, Any]:
        """Generate a single FHIR resource.

        Returns:
            FHIR resource as dictionary
        """
        pass

    def generate_batch(self, count: int, **kwargs: Any) -> list[dict[str, Any]]:
        """Generate multiple resources.

        Args:
            count: Number of resources to generate
            **kwargs: Additional arguments passed to generate()

        Returns:
            List of FHIR resources
        """
        return [self.generate(**kwargs) for _ in range(count)]

    def _generate_id(self) -> str:
        """Generate a unique resource ID."""
        return str(uuid.uuid4())

    def _generate_reference(self, resource_type: str, resource_id: str) -> dict[str, str]:
        """Generate a FHIR reference."""
        return {"reference": f"{resource_type}/{resource_id}"}

    def _generate_identifier(
        self,
        system: str,
        value: str | None = None,
        type_code: str | None = None,
        type_display: str | None = None,
    ) -> dict[str, Any]:
        """Generate a FHIR Identifier."""
        identifier: dict[str, Any] = {
            "system": system,
            "value": value or self.faker.uuid4(),
        }
        if type_code:
            identifier["type"] = {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": type_code,
                        "display": type_display or type_code,
                    }
                ]
            }
        return identifier

    def _generate_date(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> str:
        """Generate a random date string in FHIR format (YYYY-MM-DD).

        Args:
            start_date: Earliest possible date
            end_date: Latest possible date (defaults to today)

        Returns:
            Date string in FHIR format
        """
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=365 * 5)

        random_date = self.faker.date_between(start_date=start_date, end_date=end_date)
        return random_date.isoformat()

    def _generate_datetime(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> str:
        """Generate a random datetime string in FHIR format.

        Args:
            start_date: Earliest possible datetime
            end_date: Latest possible datetime (defaults to now)

        Returns:
            DateTime string in FHIR format with timezone
        """
        if end_date is None:
            end_date = datetime.now(timezone.utc)
        if start_date is None:
            start_date = end_date - timedelta(days=365)

        random_dt = self.faker.date_time_between(start_date=start_date, end_date=end_date, tzinfo=timezone.utc)
        return random_dt.isoformat()

    def _generate_period(
        self,
        start: datetime | str | None = None,
        duration_hours: int | None = None,
    ) -> dict[str, str]:
        """Generate a FHIR Period.

        Args:
            start: Start datetime (generates random if None)
            duration_hours: Duration in hours (random 1-8 if None)

        Returns:
            Period with start and end
        """
        if isinstance(start, str):
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        elif start is None:
            start_dt = self.faker.date_time_between(
                start_date="-1y",
                end_date="now",
                tzinfo=timezone.utc,
            )
        else:
            start_dt = start

        if duration_hours is None:
            duration_hours = self.faker.random_int(min=1, max=8)

        end_dt = start_dt + timedelta(hours=duration_hours)

        return {
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
        }

    def _generate_human_name(
        self,
        family: str | None = None,
        given: list[str] | None = None,
        prefix: str | None = None,
    ) -> dict[str, Any]:
        """Generate a FHIR HumanName.

        Args:
            family: Family name (generates random if None)
            given: Given names (generates random if None)
            prefix: Name prefix (e.g., "Dr.")

        Returns:
            HumanName dictionary
        """
        if family is None:
            family = self.faker.last_name()
        if given is None:
            given = [self.faker.first_name()]

        name: dict[str, Any] = {
            "family": family,
            "given": given,
        }

        if prefix:
            name["prefix"] = [prefix]

        # Generate text representation
        parts = []
        if prefix:
            parts.append(prefix)
        parts.extend(given)
        parts.append(family)
        name["text"] = " ".join(parts)

        return name

    def _generate_address(
        self,
        use: str = "home",
        city: str | None = None,
        state: str | None = None,
        postal_code: str | None = None,
        country: str = "US",
    ) -> dict[str, Any]:
        """Generate a FHIR Address.

        Args:
            use: Address use (home, work, temp, etc.)
            city: City name
            state: State/province
            postal_code: Postal/ZIP code
            country: Country code

        Returns:
            Address dictionary
        """
        return {
            "use": use,
            "type": "physical",
            "line": [self.faker.street_address()],
            "city": city or self.faker.city(),
            "state": state or self.faker.state_abbr(),
            "postalCode": postal_code or self.faker.postcode(),
            "country": country,
        }

    def _generate_contact_point(
        self,
        system: str,
        value: str | None = None,
        use: str = "home",
    ) -> dict[str, str]:
        """Generate a FHIR ContactPoint.

        Args:
            system: Contact system (phone, email, etc.)
            value: Contact value (generates random if None)
            use: Contact use (home, work, mobile, etc.)

        Returns:
            ContactPoint dictionary
        """
        if value is None:
            if system == "phone":
                value = self.faker.phone_number()
            elif system == "email":
                value = self.faker.email()
            else:
                value = self.faker.word()

        return {
            "system": system,
            "value": value,
            "use": use,
        }

    def _generate_quantity(
        self,
        value: float,
        unit: str,
        system: str = "http://unitsofmeasure.org",
        code: str | None = None,
    ) -> dict[str, Any]:
        """Generate a FHIR Quantity.

        Args:
            value: Numeric value
            unit: Display unit
            system: Unit system URI
            code: Unit code (defaults to unit)

        Returns:
            Quantity dictionary
        """
        return {
            "value": round(value, 2),
            "unit": unit,
            "system": system,
            "code": code or unit,
        }

    def _generate_meta(self, version_id: str = "1") -> dict[str, str]:
        """Generate a FHIR Meta element.

        Args:
            version_id: Resource version

        Returns:
            Meta dictionary
        """
        return {
            "versionId": version_id,
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
        }
