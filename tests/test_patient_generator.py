"""Tests for enhanced Patient resource generator."""

import pytest

from fhirkit.server.generator.patient import PatientGenerator


class TestPatientGenerator:
    """Tests for PatientGenerator."""

    @pytest.fixture
    def generator(self) -> PatientGenerator:
        """Create a seeded generator for reproducible tests."""
        return PatientGenerator(seed=42)

    def test_generate_basic_patient(self, generator: PatientGenerator) -> None:
        """Test basic patient generation."""
        patient = generator.generate()

        assert patient["resourceType"] == "Patient"
        assert "id" in patient
        assert patient["active"] is True
        assert "gender" in patient
        assert patient["gender"] in ["male", "female"]
        assert "birthDate" in patient
        assert "name" in patient
        assert len(patient["name"]) >= 1
        assert "telecom" in patient
        assert "address" in patient
        assert "maritalStatus" in patient
        assert "extension" in patient

    def test_generate_with_specific_id(self, generator: PatientGenerator) -> None:
        """Test patient generation with specific ID."""
        patient = generator.generate(patient_id="test-123")
        assert patient["id"] == "test-123"

    def test_generate_with_specific_gender(self, generator: PatientGenerator) -> None:
        """Test patient generation with specific gender."""
        male = generator.generate(gender="male")
        assert male["gender"] == "male"

        female = generator.generate(gender="female")
        assert female["gender"] == "female"

    def test_generate_with_specific_birth_date(self, generator: PatientGenerator) -> None:
        """Test patient generation with specific birth date."""
        patient = generator.generate(birth_date="1990-05-15")
        assert patient["birthDate"] == "1990-05-15"

    def test_identifiers_structure(self, generator: PatientGenerator) -> None:
        """Test that identifiers are properly structured."""
        patient = generator.generate()

        assert "identifier" in patient
        identifiers = patient["identifier"]
        assert len(identifiers) >= 2  # At least MRN and SSN

        # Check MRN
        mrn = next((i for i in identifiers if "mrn" in i["system"]), None)
        assert mrn is not None
        assert mrn["value"].startswith("MRN")
        assert mrn["type"]["coding"][0]["code"] == "MR"

        # Check SSN
        ssn = next((i for i in identifiers if "ssn" in i["system"]), None)
        assert ssn is not None
        assert ssn["type"]["coding"][0]["code"] == "SS"

    def test_identifiers_adult_driver_license(self) -> None:
        """Test that adults can have driver's license."""
        # Generate many patients to find one with DL
        generator = PatientGenerator(seed=100)
        found_dl = False

        for _ in range(50):
            patient = generator.generate(birth_date="1990-01-01")  # Adult
            identifiers = patient["identifier"]
            dl = next((i for i in identifiers if i["type"]["coding"][0]["code"] == "DL"), None)
            if dl:
                found_dl = True
                assert "urn:oid:2.16.840.1.113883.4.3" in dl["system"]
                break

        assert found_dl, "Expected to find driver's license in 50 adult patients"

    def test_identifiers_insurance(self) -> None:
        """Test insurance member ID generation."""
        generator = PatientGenerator(seed=200)
        found_insurance = False

        for _ in range(20):
            patient = generator.generate()
            identifiers = patient["identifier"]
            ins = next((i for i in identifiers if i["type"]["coding"][0]["code"] == "MB"), None)
            if ins:
                found_insurance = True
                assert ins["value"].startswith("INS")
                break

        assert found_insurance, "Expected to find insurance ID in 20 patients"

    def test_name_structure(self, generator: PatientGenerator) -> None:
        """Test name structure with use and period."""
        patient = generator.generate()

        names = patient["name"]
        assert len(names) >= 1

        official = names[0]
        assert official["use"] == "official"
        assert "family" in official
        assert "given" in official
        assert len(official["given"]) >= 1
        assert "period" in official
        assert "start" in official["period"]

    def test_maiden_name_for_married_women(self) -> None:
        """Test maiden name generation for married women."""
        generator = PatientGenerator(seed=500)
        found_maiden = False

        for _ in range(100):
            patient = generator.generate(gender="female")
            if patient["maritalStatus"]["coding"][0]["code"] == "M":
                names = patient["name"]
                maiden = next((n for n in names if n.get("use") == "maiden"), None)
                if maiden:
                    found_maiden = True
                    assert "family" in maiden
                    assert "period" in maiden
                    assert "end" in maiden["period"]
                    break

        assert found_maiden, "Expected to find maiden name for married women"

    def test_name_suffix(self) -> None:
        """Test name suffix generation."""
        generator = PatientGenerator(seed=300)
        found_suffix = False

        for _ in range(100):
            patient = generator.generate()
            names = patient["name"]
            if "suffix" in names[0]:
                found_suffix = True
                assert names[0]["suffix"][0] in ["Jr.", "Sr.", "II", "III", "IV", "MD", "PhD", "Esq."]
                break

        assert found_suffix, "Expected to find name suffix in 100 patients"

    def test_telecom_structure(self, generator: PatientGenerator) -> None:
        """Test telecom contacts structure."""
        patient = generator.generate()

        telecoms = patient["telecom"]
        assert len(telecoms) >= 3  # At least home, mobile, email

        systems = [t["system"] for t in telecoms]
        assert "phone" in systems
        assert "email" in systems

    def test_work_telecom_for_working_age(self) -> None:
        """Test work phone for working-age adults."""
        generator = PatientGenerator(seed=400)
        found_work = False

        for _ in range(50):
            patient = generator.generate(birth_date="1990-01-01")  # Working age
            telecoms = patient["telecom"]
            work = next((t for t in telecoms if t.get("use") == "work"), None)
            if work:
                found_work = True
                break

        assert found_work, "Expected to find work phone for working-age patients"

    def test_address_structure(self, generator: PatientGenerator) -> None:
        """Test address structure with district and period."""
        patient = generator.generate()

        addresses = patient["address"]
        assert len(addresses) >= 1

        home = addresses[0]
        assert home["use"] == "home"
        assert "line" in home
        assert "city" in home
        assert "state" in home
        assert "postalCode" in home
        assert "district" in home
        assert "County" in home["district"]
        assert "period" in home
        assert "start" in home["period"]

    def test_work_address_for_working_age(self) -> None:
        """Test work address for working-age adults."""
        generator = PatientGenerator(seed=600)
        found_work = False

        for _ in range(50):
            patient = generator.generate(birth_date="1990-01-01")
            addresses = patient["address"]
            work = next((a for a in addresses if a.get("use") == "work"), None)
            if work:
                found_work = True
                break

        assert found_work, "Expected to find work address for working-age patients"

    def test_extensions_race_ethnicity(self, generator: PatientGenerator) -> None:
        """Test race and ethnicity extensions."""
        patient = generator.generate()

        extensions = patient["extension"]
        assert len(extensions) >= 3  # Race, ethnicity, birth sex

        race = next((e for e in extensions if "us-core-race" in e["url"]), None)
        assert race is not None
        assert "extension" in race

        ethnicity = next((e for e in extensions if "us-core-ethnicity" in e["url"]), None)
        assert ethnicity is not None
        assert "extension" in ethnicity

    def test_birth_sex_extension(self, generator: PatientGenerator) -> None:
        """Test birth sex extension."""
        patient = generator.generate()

        extensions = patient["extension"]
        birth_sex = next((e for e in extensions if "us-core-birthsex" in e["url"]), None)

        assert birth_sex is not None
        assert "valueCode" in birth_sex
        assert birth_sex["valueCode"] in ["M", "F", "UNK"]

    def test_birth_sex_matches_gender_mostly(self) -> None:
        """Test that birth sex matches gender most of the time."""
        generator = PatientGenerator(seed=700)
        matches = 0

        for _ in range(100):
            patient = generator.generate()
            gender = patient["gender"]
            extensions = patient["extension"]
            birth_sex = next((e for e in extensions if "us-core-birthsex" in e["url"]), None)

            if birth_sex:
                expected = "M" if gender == "male" else "F"
                if birth_sex["valueCode"] == expected:
                    matches += 1

        # Should match at least 90% of the time (98% expected)
        assert matches >= 90, f"Birth sex should match gender most of the time, got {matches}/100"

    def test_gender_identity_extension(self) -> None:
        """Test gender identity extension generation."""
        generator = PatientGenerator(seed=800)
        found_identity = False

        for _ in range(100):
            patient = generator.generate()
            extensions = patient["extension"]
            identity = next((e for e in extensions if "patient-genderIdentity" in e["url"]), None)
            if identity:
                found_identity = True
                assert "valueCodeableConcept" in identity
                coding = identity["valueCodeableConcept"]["coding"][0]
                assert "code" in coding
                assert "display" in coding
                break

        assert found_identity, "Expected to find gender identity extension in 100 patients"

    def test_deceased_patient(self) -> None:
        """Test deceased patient generation."""
        generator = PatientGenerator(seed=900)
        found_deceased = False

        for _ in range(100):
            patient = generator.generate()
            if patient.get("deceasedBoolean"):
                found_deceased = True
                assert patient["deceasedBoolean"] is True
                assert "deceasedDateTime" in patient
                break

        assert found_deceased, "Expected to find deceased patient in 100 generations"

    def test_deceased_exclude(self, generator: PatientGenerator) -> None:
        """Test excluding deceased patients."""
        for _ in range(50):
            patient = generator.generate(include_deceased=False)
            assert "deceasedBoolean" not in patient
            assert "deceasedDateTime" not in patient

    def test_emergency_contacts(self, generator: PatientGenerator) -> None:
        """Test emergency contact generation."""
        patient = generator.generate()

        assert "contact" in patient
        contacts = patient["contact"]
        assert len(contacts) >= 1

        contact = contacts[0]
        assert "relationship" in contact
        assert "name" in contact
        assert "telecom" in contact
        assert "address" in contact
        assert "gender" in contact

        # Check relationship coding
        rel = contact["relationship"][0]
        assert "coding" in rel
        codes = [c["code"] for c in rel["coding"]]
        assert "C" in codes  # Emergency Contact

    def test_contacts_exclude(self, generator: PatientGenerator) -> None:
        """Test excluding contacts."""
        patient = generator.generate(include_contacts=False)
        assert "contact" not in patient

    def test_multiple_birth(self) -> None:
        """Test multiple birth generation."""
        generator = PatientGenerator(seed=1000)
        found_multiple = False

        for _ in range(100):
            patient = generator.generate()
            if "multipleBirthInteger" in patient:
                found_multiple = True
                assert patient["multipleBirthInteger"] in [1, 2, 3]
                break

        assert found_multiple, "Expected to find multiple birth in 100 patients"

    def test_general_practitioner_reference(self, generator: PatientGenerator) -> None:
        """Test generalPractitioner reference."""
        patient = generator.generate(practitioner_ref="Practitioner/dr-smith-123")

        assert "generalPractitioner" in patient
        assert len(patient["generalPractitioner"]) == 1
        assert patient["generalPractitioner"][0]["reference"] == "Practitioner/dr-smith-123"

    def test_managing_organization_reference(self, generator: PatientGenerator) -> None:
        """Test managingOrganization reference."""
        patient = generator.generate(organization_ref="Organization/hospital-456")

        assert "managingOrganization" in patient
        assert patient["managingOrganization"]["reference"] == "Organization/hospital-456"

    def test_batch_generation(self, generator: PatientGenerator) -> None:
        """Test batch patient generation."""
        patients = generator.generate_batch(5)

        assert len(patients) == 5
        ids = [p["id"] for p in patients]
        assert len(set(ids)) == 5  # All unique IDs

    def test_marital_status_distribution(self) -> None:
        """Test marital status distribution is reasonable."""
        generator = PatientGenerator(seed=1100)
        statuses = {"S": 0, "M": 0, "D": 0, "W": 0}

        for _ in range(200):
            patient = generator.generate()
            code = patient["maritalStatus"]["coding"][0]["code"]
            statuses[code] = statuses.get(code, 0) + 1

        # Married should be most common (~50%)
        assert statuses["M"] > statuses["S"]
        assert statuses["M"] > statuses["D"]
        assert statuses["M"] > statuses["W"]

    def test_age_distribution(self) -> None:
        """Test age distribution is reasonable."""
        from datetime import date

        generator = PatientGenerator(seed=1200)
        age_groups = {"0-18": 0, "18-40": 0, "40-65": 0, "65+": 0}

        for _ in range(200):
            patient = generator.generate()
            birth_date = date.fromisoformat(patient["birthDate"])
            age = (date.today() - birth_date).days // 365

            if age < 18:
                age_groups["0-18"] += 1
            elif age < 40:
                age_groups["18-40"] += 1
            elif age < 65:
                age_groups["40-65"] += 1
            else:
                age_groups["65+"] += 1

        # Should have patients in all age groups
        assert age_groups["0-18"] > 0
        assert age_groups["18-40"] > 0
        assert age_groups["40-65"] > 0
        assert age_groups["65+"] > 0

        # Middle aged should be most common (~35%)
        assert age_groups["40-65"] >= age_groups["0-18"]

    def test_communication_language(self, generator: PatientGenerator) -> None:
        """Test communication/language is properly set."""
        patient = generator.generate()

        assert "communication" in patient
        comm = patient["communication"][0]
        assert comm["preferred"] is True
        assert "language" in comm
        lang = comm["language"]
        assert lang["coding"][0]["code"] == "en-US"

    def test_reproducibility_with_seed(self) -> None:
        """Test that same seed produces same patient."""
        gen1 = PatientGenerator(seed=42)
        gen2 = PatientGenerator(seed=42)

        patient1 = gen1.generate()
        patient2 = gen2.generate()

        # Key fields should match
        assert patient1["gender"] == patient2["gender"]
        assert patient1["birthDate"] == patient2["birthDate"]
        assert patient1["name"][0]["family"] == patient2["name"][0]["family"]
