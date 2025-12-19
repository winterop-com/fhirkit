"""Tests for UCUM unit conversion."""

from decimal import Decimal

import pytest

from fhirkit.engine.units import UCUMConverter, convert_quantity, parse_unit
from fhirkit.engine.units.definitions import (
    DIMENSIONLESS,
    LENGTH,
    MASS,
    TEMPERATURE,
    TIME,
    VOLUME,
    get_prefixed_unit,
)
from fhirkit.engine.units.ucum import (
    IncompatibleUnitsError,
    UnitParseError,
    is_compatible,
)


class TestDimension:
    """Tests for dimensional analysis."""

    def test_dimensionless(self):
        assert DIMENSIONLESS.is_dimensionless()
        assert not LENGTH.is_dimensionless()

    def test_dimension_multiplication(self):
        # Area = Length * Length
        area = LENGTH * LENGTH
        assert area.length == 2
        assert area.mass == 0

    def test_dimension_division(self):
        # Velocity = Length / Time
        velocity = LENGTH / TIME
        assert velocity.length == 1
        assert velocity.time == -1

    def test_dimension_power(self):
        # Volume = Length^3
        volume = LENGTH**3
        assert volume.length == 3


class TestUnitParsing:
    """Tests for unit string parsing."""

    def test_parse_simple_unit(self):
        parsed = parse_unit("g")
        assert parsed.dimension == MASS
        assert parsed.factor == Decimal("1")

    def test_parse_prefixed_unit(self):
        parsed = parse_unit("mg")
        assert parsed.dimension == MASS
        assert parsed.factor == Decimal("0.001")

    def test_parse_kilogram(self):
        parsed = parse_unit("kg")
        assert parsed.dimension == MASS
        assert parsed.factor == Decimal("1000")

    def test_parse_liter(self):
        parsed = parse_unit("L")
        assert parsed.dimension == VOLUME

    def test_parse_milliliter(self):
        parsed = parse_unit("mL")
        assert parsed.dimension == VOLUME

    def test_parse_special_unit(self):
        parsed = parse_unit("[lb_av]")
        assert parsed.dimension == MASS
        assert float(parsed.factor) == pytest.approx(453.59237)

    def test_parse_temperature_celsius(self):
        parsed = parse_unit("Cel")
        assert parsed.dimension == TEMPERATURE
        assert parsed.is_special

    def test_parse_temperature_fahrenheit(self):
        parsed = parse_unit("[degF]")
        assert parsed.dimension == TEMPERATURE
        assert parsed.is_special

    def test_parse_compound_unit(self):
        parsed = parse_unit("mg/dL")
        assert parsed.dimension == MASS / VOLUME

    def test_parse_alias(self):
        parsed = parse_unit("mcg")
        assert parsed.dimension == MASS
        assert parsed.factor == Decimal("1e-6")

    def test_parse_invalid_unit(self):
        with pytest.raises(UnitParseError):
            parse_unit("invalid_unit_xyz")

    def test_parse_empty_unit(self):
        with pytest.raises(UnitParseError):
            parse_unit("")

    def test_parse_unity(self):
        parsed = parse_unit("1")
        assert parsed.dimension.is_dimensionless()


class TestGetPrefixedUnit:
    """Tests for prefix parsing."""

    def test_milligram(self):
        result = get_prefixed_unit("mg")
        assert result is not None
        unit_def, prefix_factor = result
        assert unit_def.code == "g"
        assert prefix_factor == Decimal("0.001")

    def test_kilogram(self):
        result = get_prefixed_unit("kg")
        assert result is not None
        unit_def, prefix_factor = result
        assert unit_def.code == "g"
        assert prefix_factor == Decimal("1000")

    def test_microgram(self):
        result = get_prefixed_unit("ug")
        assert result is not None
        unit_def, prefix_factor = result
        assert prefix_factor == Decimal("1e-6")

    def test_milliliter(self):
        result = get_prefixed_unit("mL")
        assert result is not None
        unit_def, prefix_factor = result
        assert unit_def.code == "L"

    def test_no_prefix_for_special_units(self):
        # Special units don't take prefixes
        result = get_prefixed_unit("m[lb_av]")
        assert result is None


class TestBasicConversions:
    """Tests for basic unit conversions."""

    def test_gram_to_milligram(self):
        result = convert_quantity(1, "g", "mg")
        assert result == pytest.approx(1000)

    def test_milligram_to_gram(self):
        result = convert_quantity(1000, "mg", "g")
        assert result == pytest.approx(1)

    def test_kilogram_to_gram(self):
        result = convert_quantity(1, "kg", "g")
        assert result == pytest.approx(1000)

    def test_gram_to_kilogram(self):
        result = convert_quantity(1000, "g", "kg")
        assert result == pytest.approx(1)

    def test_microgram_to_milligram(self):
        result = convert_quantity(1000, "ug", "mg")
        assert result == pytest.approx(1)

    def test_liter_to_milliliter(self):
        result = convert_quantity(1, "L", "mL")
        assert result == pytest.approx(1000)

    def test_milliliter_to_liter(self):
        result = convert_quantity(500, "mL", "L")
        assert result == pytest.approx(0.5)

    def test_meter_to_centimeter(self):
        result = convert_quantity(1, "m", "cm")
        assert result == pytest.approx(100)

    def test_centimeter_to_meter(self):
        result = convert_quantity(100, "cm", "m")
        assert result == pytest.approx(1)

    def test_same_unit_conversion(self):
        result = convert_quantity(42, "mg", "mg")
        assert result == pytest.approx(42)


class TestUSCustomaryConversions:
    """Tests for US customary unit conversions."""

    def test_pound_to_kilogram(self):
        result = convert_quantity(1, "[lb_av]", "kg")
        assert result == pytest.approx(0.45359237)

    def test_kilogram_to_pound(self):
        result = convert_quantity(1, "kg", "[lb_av]")
        assert result == pytest.approx(2.20462, rel=1e-4)

    def test_ounce_to_gram(self):
        result = convert_quantity(1, "[oz_av]", "g")
        assert result == pytest.approx(28.349523125)

    def test_inch_to_centimeter(self):
        result = convert_quantity(1, "[in_i]", "cm")
        assert result == pytest.approx(2.54)

    def test_foot_to_meter(self):
        result = convert_quantity(1, "[ft_i]", "m")
        assert result == pytest.approx(0.3048)

    def test_gallon_to_liter(self):
        result = convert_quantity(1, "[gal_us]", "L")
        assert result == pytest.approx(3.785411784)

    def test_pound_alias(self):
        result = convert_quantity(1, "lb", "kg")
        assert result == pytest.approx(0.45359237)


class TestTemperatureConversions:
    """Tests for temperature conversions."""

    def test_celsius_to_fahrenheit(self):
        result = convert_quantity(0, "Cel", "[degF]")
        assert result == pytest.approx(32)

    def test_fahrenheit_to_celsius(self):
        result = convert_quantity(32, "[degF]", "Cel")
        assert result == pytest.approx(0)

    def test_body_temperature_f_to_c(self):
        result = convert_quantity(98.6, "[degF]", "Cel")
        assert result == pytest.approx(37, abs=0.1)

    def test_body_temperature_c_to_f(self):
        result = convert_quantity(37, "Cel", "[degF]")
        assert result == pytest.approx(98.6, abs=0.1)

    def test_celsius_to_kelvin(self):
        result = convert_quantity(0, "Cel", "K")
        assert result == pytest.approx(273.15)

    def test_kelvin_to_celsius(self):
        result = convert_quantity(273.15, "K", "Cel")
        assert result == pytest.approx(0)

    def test_boiling_point_c_to_f(self):
        result = convert_quantity(100, "Cel", "[degF]")
        assert result == pytest.approx(212)


class TestCompoundUnits:
    """Tests for compound unit conversions."""

    def test_mg_per_dl_to_mg_per_l(self):
        # 1 dL = 0.1 L, so mg/dL * 10 = mg/L
        result = convert_quantity(100, "mg/dL", "mg/L")
        assert result == pytest.approx(1000)

    def test_mg_per_l_to_mg_per_dl(self):
        result = convert_quantity(1000, "mg/L", "mg/dL")
        assert result == pytest.approx(100)

    def test_g_per_l_to_mg_per_dl(self):
        result = convert_quantity(1, "g/L", "mg/dL")
        assert result == pytest.approx(100)

    def test_mmol_per_l_concentration(self):
        # mmol/L should be compatible with mol/L
        assert is_compatible("mmol/L", "mol/L")


class TestTimeConversions:
    """Tests for time unit conversions."""

    def test_minute_to_second(self):
        result = convert_quantity(1, "min", "s")
        assert result == pytest.approx(60)

    def test_hour_to_minute(self):
        result = convert_quantity(1, "h", "min")
        assert result == pytest.approx(60)

    def test_day_to_hour(self):
        result = convert_quantity(1, "d", "h")
        assert result == pytest.approx(24)

    def test_week_to_day(self):
        result = convert_quantity(1, "wk", "d")
        assert result == pytest.approx(7)


class TestCompatibility:
    """Tests for unit compatibility checking."""

    def test_compatible_mass_units(self):
        assert is_compatible("g", "mg")
        assert is_compatible("kg", "[lb_av]")
        assert is_compatible("mg", "ug")

    def test_compatible_volume_units(self):
        assert is_compatible("L", "mL")
        assert is_compatible("dL", "[gal_us]")

    def test_compatible_temperature_units(self):
        assert is_compatible("Cel", "[degF]")
        assert is_compatible("K", "Cel")

    def test_incompatible_units(self):
        assert not is_compatible("g", "L")
        assert not is_compatible("m", "s")
        assert not is_compatible("kg", "Cel")

    def test_incompatible_conversion_raises(self):
        converter = UCUMConverter()
        with pytest.raises(IncompatibleUnitsError):
            converter.convert(1, "g", "L")


class TestClinicalScenarios:
    """Tests for real clinical calculation scenarios."""

    def test_medication_dose_conversion(self):
        # Convert 500mg to grams
        result = convert_quantity(500, "mg", "g")
        assert result == pytest.approx(0.5)

    def test_iv_fluid_rate(self):
        # 1000 mL over 8 hours = 125 mL/h
        # This tests mL conversion
        result = convert_quantity(1000, "mL", "L")
        assert result == pytest.approx(1)

    def test_patient_weight_conversion(self):
        # Convert 150 pounds to kg for drug dosing
        result = convert_quantity(150, "[lb_av]", "kg")
        assert result == pytest.approx(68.0388555, rel=1e-4)

    def test_height_conversion(self):
        # Convert 5'10" (70 inches) to cm
        result = convert_quantity(70, "[in_i]", "cm")
        assert result == pytest.approx(177.8)

    def test_glucose_unit_conversion(self):
        # Note: This is just unit conversion, not molar conversion
        # (would need molecular weight for true mmol/L conversion)
        result = convert_quantity(180, "mg/dL", "mg/L")
        assert result == pytest.approx(1800)


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_none_value(self):
        result = convert_quantity(None, "g", "mg")
        assert result is None

    def test_zero_value(self):
        result = convert_quantity(0, "g", "mg")
        assert result == pytest.approx(0)

    def test_negative_value(self):
        result = convert_quantity(-10, "Cel", "[degF]")
        assert result == pytest.approx(14)

    def test_decimal_input(self):
        result = convert_quantity(Decimal("1.5"), "g", "mg")
        assert result == pytest.approx(1500)

    def test_very_small_value(self):
        result = convert_quantity(0.001, "mg", "ug")
        assert result == pytest.approx(1)

    def test_very_large_value(self):
        result = convert_quantity(1000000, "ug", "g")
        assert result == pytest.approx(1)


class TestCQLIntegration:
    """Tests for CQL ConvertQuantity function integration."""

    def test_cql_convert_quantity(self):
        from fhirkit.engine.cql import CQLEvaluator

        evaluator = CQLEvaluator()

        # Test basic conversion
        result = evaluator.evaluate_expression("ConvertQuantity(1 'g', 'mg')")
        assert result is not None
        assert result.value == pytest.approx(1000)
        assert result.unit == "mg"

    def test_cql_convert_weight(self):
        from fhirkit.engine.cql import CQLEvaluator

        evaluator = CQLEvaluator()

        result = evaluator.evaluate_expression("ConvertQuantity(150 '[lb_av]', 'kg')")
        assert result is not None
        assert float(result.value) == pytest.approx(68.0388555, rel=1e-4)
        assert result.unit == "kg"

    def test_cql_convert_temperature(self):
        from fhirkit.engine.cql import CQLEvaluator

        evaluator = CQLEvaluator()

        result = evaluator.evaluate_expression("ConvertQuantity(98.6 '[degF]', 'Cel')")
        assert result is not None
        assert result.value == pytest.approx(37, abs=0.1)
        assert result.unit == "Cel"

    def test_cql_convert_volume(self):
        from fhirkit.engine.cql import CQLEvaluator

        evaluator = CQLEvaluator()

        result = evaluator.evaluate_expression("ConvertQuantity(500 'mL', 'L')")
        assert result is not None
        assert result.value == pytest.approx(0.5)
        assert result.unit == "L"
