"""Patient resource generator with comprehensive FHIR R4 fields."""

from datetime import date, datetime, timedelta, timezone
from typing import Any

from faker import Faker

from .base import FHIRResourceGenerator
from .clinical_codes import (
    BIRTH_SEX_EXTENSION_URL,
    GENDER_IDENTITY_CODES,
    GENDER_IDENTITY_EXTENSION_URL,
    GENDER_IDENTITY_SYSTEM,
    NAME_SUFFIXES,
)


class PatientGenerator(FHIRResourceGenerator):
    """Generator for FHIR Patient resources with comprehensive fields."""

    def __init__(self, faker: Faker | None = None, seed: int | None = None):
        super().__init__(faker, seed)

    def generate(
        self,
        patient_id: str | None = None,
        gender: str | None = None,
        birth_date: str | None = None,
        practitioner_ref: str | None = None,
        organization_ref: str | None = None,
        include_deceased: bool = True,
        include_contacts: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a Patient resource.

        Args:
            patient_id: Patient ID (generates UUID if None)
            gender: Patient gender (random if None)
            birth_date: Birth date (random if None)
            practitioner_ref: Reference to general practitioner (e.g., "Practitioner/123")
            organization_ref: Reference to managing organization (e.g., "Organization/456")
            include_deceased: Whether to randomly include deceased patients (~3%)
            include_contacts: Whether to include emergency contacts

        Returns:
            Patient FHIR resource
        """
        if patient_id is None:
            patient_id = self._generate_id()

        if gender is None:
            gender = self.faker.random_element(["male", "female"])

        # Generate appropriate name based on gender
        if gender == "male":
            first_name = self.faker.first_name_male()
        else:
            first_name = self.faker.first_name_female()

        last_name = self.faker.last_name()

        # Generate birth date with realistic age distribution
        if birth_date is None:
            birth_date = self._generate_birth_date()

        # Calculate age for age-dependent fields
        birth_date_obj = date.fromisoformat(birth_date)
        age = self._calculate_age(birth_date_obj)
        is_adult = age >= 18
        is_working_age = 18 <= age <= 65

        # Generate marital status
        marital_status = self._generate_marital_status()
        is_married = marital_status["coding"][0]["code"] == "M"

        # Generate MRN
        mrn = self.faker.numerify("MRN########")

        patient: dict[str, Any] = {
            "resourceType": "Patient",
            "id": patient_id,
            "meta": self._generate_meta(),
            "identifier": self._generate_identifiers(mrn, is_adult, age),
            "active": True,
            "name": self._generate_names(first_name, last_name, gender, is_married),
            "telecom": self._generate_telecom(is_working_age),
            "gender": gender,
            "birthDate": birth_date,
            "address": self._generate_addresses(is_working_age),
            "maritalStatus": marital_status,
            "communication": [
                {
                    "language": {
                        "coding": [
                            {
                                "system": "urn:ietf:bcp:47",
                                "code": "en-US",
                                "display": "English (United States)",
                            }
                        ],
                        "text": "English",
                    },
                    "preferred": True,
                }
            ],
        }

        # Add extensions (race, ethnicity, birth sex, gender identity)
        patient["extension"] = self._generate_extensions(gender)

        # Deceased status (~3% of patients)
        if include_deceased and self._should_be_deceased():
            deceased_dt = self._generate_deceased_datetime(birth_date_obj)
            patient["deceasedBoolean"] = True
            patient["deceasedDateTime"] = deceased_dt

        # Emergency contacts
        if include_contacts:
            contacts = self._generate_contacts(is_married)
            if contacts:
                patient["contact"] = contacts

        # Multiple birth (~3% of patients)
        if self._is_multiple_birth():
            patient["multipleBirthInteger"] = self._generate_multiple_birth_order()

        # General practitioner reference
        if practitioner_ref:
            patient["generalPractitioner"] = [{"reference": practitioner_ref}]

        # Managing organization reference
        if organization_ref:
            patient["managingOrganization"] = {"reference": organization_ref}

        return patient

    def _generate_birth_date(self) -> str:
        """Generate birth date with realistic age distribution."""
        age_weights = [
            (0, 18, 0.15),  # Children: 15%
            (18, 40, 0.25),  # Young adults: 25%
            (40, 65, 0.35),  # Middle aged: 35%
            (65, 90, 0.25),  # Elderly: 25%
        ]

        roll = self.faker.random.random()
        cumulative = 0.0
        min_age, max_age = 18, 65

        for age_min, age_max, weight in age_weights:
            cumulative += weight
            if roll < cumulative:
                min_age, max_age = age_min, age_max
                break

        today = date.today()
        start_date = today - timedelta(days=max_age * 365)
        end_date = today - timedelta(days=min_age * 365)
        return self._generate_date(start_date, end_date)

    def _calculate_age(self, birth_date: date) -> int:
        """Calculate age from birth date."""
        today = date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    def _generate_identifiers(self, mrn: str, is_adult: bool, age: int) -> list[dict[str, Any]]:
        """Generate patient identifiers including MRN, SSN, DL, insurance."""
        identifiers = [
            # MRN (always)
            self._generate_identifier(
                system="http://hospital.example.org/mrn",
                value=mrn,
                type_code="MR",
                type_display="Medical Record Number",
            ),
            # SSN (always)
            self._generate_identifier(
                system="http://hl7.org/fhir/sid/us-ssn",
                value=self.faker.ssn(),
                type_code="SS",
                type_display="Social Security Number",
            ),
        ]

        # Driver's License (70% of adults)
        if is_adult and self.faker.random.random() < 0.70:
            state_code = self.faker.state_abbr()
            dl_number = self.faker.bothify(text="??######").upper()
            identifiers.append(
                self._generate_identifier(
                    system=f"urn:oid:2.16.840.1.113883.4.3.{self._state_to_oid(state_code)}",
                    value=dl_number,
                    type_code="DL",
                    type_display="Driver's license number",
                )
            )

        # Insurance Member ID (85% of patients)
        if self.faker.random.random() < 0.85:
            identifiers.append(
                self._generate_identifier(
                    system="http://insurance.example.org/member",
                    value=self.faker.bothify(text="INS#########"),
                    type_code="MB",
                    type_display="Member number",
                )
            )

        # Passport (20% of patients)
        if self.faker.random.random() < 0.20:
            identifiers.append(
                self._generate_identifier(
                    system="http://hl7.org/fhir/sid/passport-USA",
                    value=self.faker.bothify(text="#########"),
                    type_code="PPN",
                    type_display="Passport number",
                )
            )

        return identifiers

    def _state_to_oid(self, state_code: str) -> str:
        """Map state code to OID suffix (simplified)."""
        # Using state index as OID suffix for simplicity
        states = [
            "AL",
            "AK",
            "AZ",
            "AR",
            "CA",
            "CO",
            "CT",
            "DE",
            "FL",
            "GA",
            "HI",
            "ID",
            "IL",
            "IN",
            "IA",
            "KS",
            "KY",
            "LA",
            "ME",
            "MD",
            "MA",
            "MI",
            "MN",
            "MS",
            "MO",
            "MT",
            "NE",
            "NV",
            "NH",
            "NJ",
            "NM",
            "NY",
            "NC",
            "ND",
            "OH",
            "OK",
            "OR",
            "PA",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VT",
            "VA",
            "WA",
            "WV",
            "WI",
            "WY",
        ]
        try:
            return str(states.index(state_code) + 1)
        except ValueError:
            return "99"

    def _generate_names(
        self,
        first_name: str,
        last_name: str,
        gender: str,
        is_married: bool,
    ) -> list[dict[str, Any]]:
        """Generate patient names including official name and possibly maiden name."""
        names = []

        # Official name
        official_name: dict[str, Any] = {
            "use": "official",
            "family": last_name,
            "given": [first_name, self.faker.first_name()[0] + "."],
        }

        # Name suffix (5% of patients)
        if self.faker.random.random() < 0.05:
            official_name["suffix"] = [self.faker.random_element(NAME_SUFFIXES)]

        # Add period
        official_name["period"] = {
            "start": self._generate_date(
                date.today() - timedelta(days=365 * 50),
                date.today() - timedelta(days=365 * 5),
            )
        }

        names.append(official_name)

        # Maiden name for married women (~30% of married women)
        if gender == "female" and is_married and self.faker.random.random() < 0.30:
            maiden_name = self.faker.last_name()
            names.append(
                {
                    "use": "maiden",
                    "family": maiden_name,
                    "given": [first_name],
                    "period": {
                        "end": self._generate_date(
                            date.today() - timedelta(days=365 * 20),
                            date.today() - timedelta(days=365),
                        )
                    },
                }
            )

        return names

    def _generate_telecom(self, is_working_age: bool) -> list[dict[str, str]]:
        """Generate patient telecom contacts."""
        telecoms = [
            self._generate_contact_point("phone", use="home"),
            self._generate_contact_point("phone", use="mobile"),
            self._generate_contact_point("email"),
        ]

        # Work phone for working-age adults (60%)
        if is_working_age and self.faker.random.random() < 0.60:
            telecoms.append(self._generate_contact_point("phone", use="work"))

        # Work fax for 10% of patients
        if self.faker.random.random() < 0.10:
            telecoms.append(
                {
                    "system": "fax",
                    "value": self.faker.phone_number(),
                    "use": "work",
                }
            )

        return telecoms

    def _generate_addresses(self, is_working_age: bool) -> list[dict[str, Any]]:
        """Generate patient addresses including home and possibly work."""
        addresses = [self._generate_enhanced_address("home")]

        # Work address for working-age adults (60%)
        if is_working_age and self.faker.random.random() < 0.60:
            addresses.append(self._generate_enhanced_address("work"))

        # Separate mailing address (20%)
        if self.faker.random.random() < 0.20:
            mailing = self._generate_enhanced_address("home")
            mailing["type"] = "postal"
            addresses.append(mailing)

        return addresses

    def _generate_enhanced_address(self, use: str = "home") -> dict[str, Any]:
        """Generate an enhanced address with district and period."""
        address = self._generate_address(use=use)
        address["district"] = self.faker.city() + " County"
        address["period"] = {
            "start": self._generate_date(
                date.today() - timedelta(days=365 * 20),
                date.today() - timedelta(days=30),
            )
        }
        return address

    def _generate_marital_status(self) -> dict[str, Any]:
        """Generate marital status."""
        statuses = [
            ("S", "Never Married", 0.3),
            ("M", "Married", 0.5),
            ("D", "Divorced", 0.1),
            ("W", "Widowed", 0.1),
        ]

        roll = self.faker.random.random()
        cumulative = 0.0
        code, display = "S", "Never Married"

        for c, d, weight in statuses:
            cumulative += weight
            if roll < cumulative:
                code, display = c, d
                break

        return {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                    "code": code,
                    "display": display,
                }
            ],
            "text": display,
        }

    def _generate_extensions(self, gender: str) -> list[dict[str, Any]]:
        """Generate US Core extensions including race, ethnicity, birth sex, gender identity."""
        extensions = []

        # Race extension
        extensions.append(self._generate_race_extension())

        # Ethnicity extension
        extensions.append(self._generate_ethnicity_extension())

        # Birth sex extension
        extensions.append(self._generate_birth_sex_extension(gender))

        # Gender identity extension (smaller probability for non-matching)
        if self.faker.random.random() < 0.10:  # 10% have explicit gender identity
            extensions.append(self._generate_gender_identity_extension(gender))

        return extensions

    def _generate_race_extension(self) -> dict[str, Any]:
        """Generate US Core race extension."""
        races = [
            ("2106-3", "White", 0.6),
            ("2054-5", "Black or African American", 0.13),
            ("2028-9", "Asian", 0.06),
            ("1002-5", "American Indian or Alaska Native", 0.01),
            ("2076-8", "Native Hawaiian or Other Pacific Islander", 0.002),
            ("2131-1", "Other Race", 0.19),
        ]

        roll = self.faker.random.random()
        cumulative = 0.0
        race_code, race_display = "2106-3", "White"

        for code, display, weight in races:
            cumulative += weight
            if roll < cumulative:
                race_code, race_display = code, display
                break

        return {
            "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
            "extension": [
                {
                    "url": "ombCategory",
                    "valueCoding": {
                        "system": "urn:oid:2.16.840.1.113883.6.238",
                        "code": race_code,
                        "display": race_display,
                    },
                },
                {"url": "text", "valueString": race_display},
            ],
        }

    def _generate_ethnicity_extension(self) -> dict[str, Any]:
        """Generate US Core ethnicity extension."""
        is_hispanic = self.faker.random.random() < 0.18  # ~18% Hispanic

        if is_hispanic:
            eth_code, eth_display = "2135-2", "Hispanic or Latino"
        else:
            eth_code, eth_display = "2186-5", "Not Hispanic or Latino"

        return {
            "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
            "extension": [
                {
                    "url": "ombCategory",
                    "valueCoding": {
                        "system": "urn:oid:2.16.840.1.113883.6.238",
                        "code": eth_code,
                        "display": eth_display,
                    },
                },
                {"url": "text", "valueString": eth_display},
            ],
        }

    def _generate_birth_sex_extension(self, gender: str) -> dict[str, Any]:
        """Generate US Core birth sex extension."""
        # 98% match gender, 2% differ
        if self.faker.random.random() < 0.98:
            if gender == "male":
                birth_sex_code = "M"
            elif gender == "female":
                birth_sex_code = "F"
            else:
                birth_sex_code = "UNK"
        else:
            # Random different value
            birth_sex_code = self.faker.random_element(["M", "F", "UNK"])

        return {
            "url": BIRTH_SEX_EXTENSION_URL,
            "valueCode": birth_sex_code,
        }

    def _generate_gender_identity_extension(self, gender: str) -> dict[str, Any]:
        """Generate gender identity extension."""
        # Weighted distribution
        identity_weights = [
            ("male", 0.45),
            ("female", 0.45),
            ("non-binary", 0.03),
            ("transgender-male", 0.02),
            ("transgender-female", 0.02),
            ("other", 0.03),
        ]

        roll = self.faker.random.random()
        cumulative = 0.0
        identity_code = "male" if gender == "male" else "female"

        for code, weight in identity_weights:
            cumulative += weight
            if roll < cumulative:
                identity_code = code
                break

        # Find display from GENDER_IDENTITY_CODES
        identity_display = identity_code.replace("-", " ").title()
        for gi in GENDER_IDENTITY_CODES:
            if gi.get("code") == identity_code:
                identity_display = gi.get("display", identity_display)
                break

        return {
            "url": GENDER_IDENTITY_EXTENSION_URL,
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": GENDER_IDENTITY_SYSTEM,
                        "code": identity_code,
                        "display": identity_display,
                    }
                ],
                "text": identity_display,
            },
        }

    def _should_be_deceased(self) -> bool:
        """Determine if patient should be deceased (~3%)."""
        return self.faker.random.random() < 0.03

    def _generate_deceased_datetime(self, birth_date: date) -> str:
        """Generate deceased datetime."""
        # 70% recent (last 5 years), 30% older
        today = date.today()
        age_at_today = self._calculate_age(birth_date)

        if self.faker.random.random() < 0.70:
            # Recent death
            start = max(birth_date, today - timedelta(days=365 * 5))
            end = today - timedelta(days=1)
        else:
            # Older death
            min_death_age = min(age_at_today, 20)
            start = birth_date + timedelta(days=min_death_age * 365)
            end = today - timedelta(days=365 * 5)

        if start >= end:
            start = birth_date + timedelta(days=365)
            end = today - timedelta(days=1)

        death_date = self.faker.date_between(start_date=start, end_date=end)
        death_dt = datetime.combine(
            death_date,
            datetime.min.time().replace(
                hour=self.faker.random_int(0, 23),
                minute=self.faker.random_int(0, 59),
            ),
            tzinfo=timezone.utc,
        )
        return death_dt.isoformat()

    def _generate_contacts(self, is_married: bool) -> list[dict[str, Any]]:
        """Generate emergency contacts."""
        contacts = []

        # Number of contacts: 1 (70%) or 2 (30%)
        num_contacts = 2 if self.faker.random.random() < 0.30 else 1

        for _ in range(num_contacts):
            contact = self._generate_emergency_contact(is_married)
            contacts.append(contact)

        return contacts

    def _generate_emergency_contact(self, is_married: bool) -> dict[str, Any]:
        """Generate a single emergency contact."""
        # Relationship distribution
        if is_married:
            relationships = [
                ("SPS", "spouse", 0.50),
                ("PRN", "parent", 0.20),
                ("SIB", "sibling", 0.15),
                ("CHILD", "child", 0.10),
                ("FRND", "unrelated friend", 0.05),
            ]
        else:
            relationships = [
                ("PRN", "parent", 0.40),
                ("SIB", "sibling", 0.30),
                ("FRND", "unrelated friend", 0.20),
                ("CHILD", "child", 0.10),
            ]

        roll = self.faker.random.random()
        cumulative = 0.0
        rel_code, rel_display = "PRN", "parent"

        for code, display, weight in relationships:
            cumulative += weight
            if roll < cumulative:
                rel_code, rel_display = code, display
                break

        # Generate contact gender
        contact_gender = self.faker.random_element(["male", "female"])

        # Generate appropriate name
        if contact_gender == "male":
            contact_first = self.faker.first_name_male()
        else:
            contact_first = self.faker.first_name_female()

        contact_last = self.faker.last_name()

        return {
            "relationship": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0131",
                            "code": "C",
                            "display": "Emergency Contact",
                        },
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                            "code": rel_code,
                            "display": rel_display,
                        },
                    ],
                    "text": f"Emergency Contact ({rel_display})",
                }
            ],
            "name": {
                "family": contact_last,
                "given": [contact_first],
                "text": f"{contact_first} {contact_last}",
            },
            "telecom": [
                {
                    "system": "phone",
                    "value": self.faker.phone_number(),
                    "use": "mobile",
                }
            ],
            "address": self._generate_address(),
            "gender": contact_gender,
        }

    def _is_multiple_birth(self) -> bool:
        """Determine if patient is a multiple birth (~3%)."""
        return self.faker.random.random() < 0.03

    def _generate_multiple_birth_order(self) -> int:
        """Generate multiple birth order (birth position)."""
        # 2.5% twins, 0.5% triplets+
        if self.faker.random.random() < 0.83:  # ~2.5% of 3% = twins
            return self.faker.random_int(1, 2)
        else:
            return self.faker.random_int(1, 3)
