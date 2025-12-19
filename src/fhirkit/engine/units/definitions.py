"""UCUM unit definitions for clinical calculations.

Based on the UCUM specification: https://ucum.org/ucum
Implements a subset of commonly used clinical units.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Dimension:
    """Represents dimensional analysis components."""

    length: int = 0  # L (meter)
    mass: int = 0  # M (gram - UCUM uses gram as base)
    time: int = 0  # T (second)
    temperature: int = 0  # K (Kelvin)
    amount: int = 0  # N (mole)
    current: int = 0  # I (Ampere)
    luminosity: int = 0  # J (candela)

    def __mul__(self, other: "Dimension") -> "Dimension":
        return Dimension(
            length=self.length + other.length,
            mass=self.mass + other.mass,
            time=self.time + other.time,
            temperature=self.temperature + other.temperature,
            amount=self.amount + other.amount,
            current=self.current + other.current,
            luminosity=self.luminosity + other.luminosity,
        )

    def __truediv__(self, other: "Dimension") -> "Dimension":
        return Dimension(
            length=self.length - other.length,
            mass=self.mass - other.mass,
            time=self.time - other.time,
            temperature=self.temperature - other.temperature,
            amount=self.amount - other.amount,
            current=self.current - other.current,
            luminosity=self.luminosity - other.luminosity,
        )

    def __pow__(self, power: int) -> "Dimension":
        return Dimension(
            length=self.length * power,
            mass=self.mass * power,
            time=self.time * power,
            temperature=self.temperature * power,
            amount=self.amount * power,
            current=self.current * power,
            luminosity=self.luminosity * power,
        )

    def is_dimensionless(self) -> bool:
        return all(
            v == 0
            for v in [
                self.length,
                self.mass,
                self.time,
                self.temperature,
                self.amount,
                self.current,
                self.luminosity,
            ]
        )


# Dimensionless
DIMENSIONLESS = Dimension()

# Base dimensions
LENGTH = Dimension(length=1)
MASS = Dimension(mass=1)
TIME = Dimension(time=1)
TEMPERATURE = Dimension(temperature=1)
AMOUNT = Dimension(amount=1)
CURRENT = Dimension(current=1)
LUMINOSITY = Dimension(luminosity=1)

# Derived dimensions
AREA = LENGTH**2
VOLUME = LENGTH**3
VELOCITY = LENGTH / TIME
ACCELERATION = VELOCITY / TIME
FORCE = MASS * ACCELERATION
ENERGY = FORCE * LENGTH
PRESSURE = FORCE / AREA
CONCENTRATION = MASS / VOLUME


@dataclass
class UnitDefinition:
    """Definition of a UCUM unit."""

    code: str  # UCUM code (e.g., "g", "mg", "[lb_av]")
    name: str  # Human-readable name
    dimension: Dimension  # Dimensional analysis
    factor: Decimal  # Conversion factor to base unit
    offset: Decimal = Decimal("0")  # Offset for temperature conversions
    is_metric: bool = True  # Whether metric prefixes apply
    is_special: bool = False  # Whether it's a special unit (like temperature)


# SI Prefixes with their factors
SI_PREFIXES: dict[str, Decimal] = {
    "Y": Decimal("1e24"),  # yotta
    "Z": Decimal("1e21"),  # zetta
    "E": Decimal("1e18"),  # exa
    "P": Decimal("1e15"),  # peta
    "T": Decimal("1e12"),  # tera
    "G": Decimal("1e9"),  # giga
    "M": Decimal("1e6"),  # mega
    "k": Decimal("1e3"),  # kilo
    "h": Decimal("1e2"),  # hecto
    "da": Decimal("1e1"),  # deca
    "d": Decimal("1e-1"),  # deci
    "c": Decimal("1e-2"),  # centi
    "m": Decimal("1e-3"),  # milli
    "u": Decimal("1e-6"),  # micro (UCUM uses 'u' not 'μ')
    "n": Decimal("1e-9"),  # nano
    "p": Decimal("1e-12"),  # pico
    "f": Decimal("1e-15"),  # femto
    "a": Decimal("1e-18"),  # atto
    "z": Decimal("1e-21"),  # zepto
    "y": Decimal("1e-24"),  # yocto
}

# Base units (factor = 1 relative to themselves)
BASE_UNITS: dict[str, UnitDefinition] = {
    # Length - meter is base
    "m": UnitDefinition("m", "meter", LENGTH, Decimal("1")),
    # Mass - gram is UCUM base (not kg!)
    "g": UnitDefinition("g", "gram", MASS, Decimal("1")),
    # Time - second is base
    "s": UnitDefinition("s", "second", TIME, Decimal("1")),
    # Temperature - Kelvin is base
    "K": UnitDefinition("K", "Kelvin", TEMPERATURE, Decimal("1")),
    # Amount - mole is base
    "mol": UnitDefinition("mol", "mole", AMOUNT, Decimal("1")),
    # Current - Ampere is base
    "A": UnitDefinition("A", "Ampere", CURRENT, Decimal("1")),
    # Luminosity - candela is base
    "cd": UnitDefinition("cd", "candela", LUMINOSITY, Decimal("1")),
    # Dimensionless
    "1": UnitDefinition("1", "unity", DIMENSIONLESS, Decimal("1"), is_metric=False),
    "%": UnitDefinition("%", "percent", DIMENSIONLESS, Decimal("0.01"), is_metric=False),
}

# Derived metric units
DERIVED_UNITS: dict[str, UnitDefinition] = {
    # Volume
    "L": UnitDefinition("L", "liter", VOLUME, Decimal("1e-3")),  # 1 L = 0.001 m^3
    "l": UnitDefinition("l", "liter", VOLUME, Decimal("1e-3")),  # alternate
    # Force
    "N": UnitDefinition("N", "Newton", FORCE, Decimal("1000")),  # 1 N = 1 kg*m/s^2 = 1000 g*m/s^2
    # Pressure
    "Pa": UnitDefinition("Pa", "Pascal", PRESSURE, Decimal("1000")),  # 1 Pa = 1 N/m^2
    "bar": UnitDefinition("bar", "bar", PRESSURE, Decimal("1e8")),  # 1 bar = 100000 Pa
    # Energy
    "J": UnitDefinition("J", "Joule", ENERGY, Decimal("1000")),  # 1 J = 1 N*m
    "cal": UnitDefinition("cal", "calorie", ENERGY, Decimal("4184")),  # thermochemical calorie
    # Frequency
    "Hz": UnitDefinition("Hz", "Hertz", TIME**-1, Decimal("1")),
    # Time
    "min": UnitDefinition("min", "minute", TIME, Decimal("60"), is_metric=False),
    "h": UnitDefinition("h", "hour", TIME, Decimal("3600"), is_metric=False),
    "d": UnitDefinition("d", "day", TIME, Decimal("86400"), is_metric=False),
    "wk": UnitDefinition("wk", "week", TIME, Decimal("604800"), is_metric=False),
    "mo": UnitDefinition("mo", "month", TIME, Decimal("2629746"), is_metric=False),  # avg month
    "a": UnitDefinition("a", "year", TIME, Decimal("31557600"), is_metric=False),  # Julian year
    # Angle
    "rad": UnitDefinition("rad", "radian", DIMENSIONLESS, Decimal("1")),
    "deg": UnitDefinition("deg", "degree", DIMENSIONLESS, Decimal("0.0174532925199433")),  # pi/180
}

# Special units (with square brackets in UCUM)
SPECIAL_UNITS: dict[str, UnitDefinition] = {
    # Temperature
    "Cel": UnitDefinition(
        "Cel", "degree Celsius", TEMPERATURE, Decimal("1"), Decimal("273.15"), is_metric=False, is_special=True
    ),
    "[degF]": UnitDefinition(
        "[degF]",
        "degree Fahrenheit",
        TEMPERATURE,
        Decimal("0.555555555555556"),  # 5/9
        Decimal("255.372222222222"),  # (459.67 * 5/9)
        is_metric=False,
        is_special=True,
    ),
    # US customary mass
    "[lb_av]": UnitDefinition("[lb_av]", "pound", MASS, Decimal("453.59237"), is_metric=False),
    "[oz_av]": UnitDefinition("[oz_av]", "ounce", MASS, Decimal("28.349523125"), is_metric=False),
    "[gr]": UnitDefinition("[gr]", "grain", MASS, Decimal("0.06479891"), is_metric=False),
    "[dr_av]": UnitDefinition("[dr_av]", "dram", MASS, Decimal("1.7718451953125"), is_metric=False),
    "[stone_av]": UnitDefinition("[stone_av]", "stone", MASS, Decimal("6350.29318"), is_metric=False),
    # US customary length
    "[in_i]": UnitDefinition("[in_i]", "inch", LENGTH, Decimal("0.0254"), is_metric=False),
    "[ft_i]": UnitDefinition("[ft_i]", "foot", LENGTH, Decimal("0.3048"), is_metric=False),
    "[yd_i]": UnitDefinition("[yd_i]", "yard", LENGTH, Decimal("0.9144"), is_metric=False),
    "[mi_i]": UnitDefinition("[mi_i]", "mile", LENGTH, Decimal("1609.344"), is_metric=False),
    # US customary volume
    "[gal_us]": UnitDefinition("[gal_us]", "US gallon", VOLUME, Decimal("0.003785411784"), is_metric=False),
    "[qt_us]": UnitDefinition("[qt_us]", "US quart", VOLUME, Decimal("0.000946352946"), is_metric=False),
    "[pt_us]": UnitDefinition("[pt_us]", "US pint", VOLUME, Decimal("0.000473176473"), is_metric=False),
    "[foz_us]": UnitDefinition("[foz_us]", "US fluid ounce", VOLUME, Decimal("0.0000295735295625"), is_metric=False),
    "[tbs_us]": UnitDefinition("[tbs_us]", "US tablespoon", VOLUME, Decimal("0.00001478676478125"), is_metric=False),
    "[tsp_us]": UnitDefinition("[tsp_us]", "US teaspoon", VOLUME, Decimal("0.00000492892159375"), is_metric=False),
    "[cup_us]": UnitDefinition("[cup_us]", "US cup", VOLUME, Decimal("0.0002365882365"), is_metric=False),
    # Clinical units
    "[IU]": UnitDefinition("[IU]", "international unit", DIMENSIONLESS, Decimal("1"), is_metric=False),
    "[iU]": UnitDefinition("[iU]", "international unit", DIMENSIONLESS, Decimal("1"), is_metric=False),
    "[arb'U]": UnitDefinition("[arb'U]", "arbitrary unit", DIMENSIONLESS, Decimal("1"), is_metric=False),
    "[USP'U]": UnitDefinition("[USP'U]", "USP unit", DIMENSIONLESS, Decimal("1"), is_metric=False),
    # Equivalents
    "eq": UnitDefinition("eq", "equivalent", AMOUNT, Decimal("1")),
    "osm": UnitDefinition("osm", "osmole", AMOUNT, Decimal("1")),
    # Pressure
    "mm[Hg]": UnitDefinition("mm[Hg]", "millimeter of mercury", PRESSURE, Decimal("133322.387415"), is_metric=False),
    "[psi]": UnitDefinition("[psi]", "pound per square inch", PRESSURE, Decimal("6894757.29"), is_metric=False),
    # pH and logarithmic
    "[pH]": UnitDefinition("[pH]", "pH", DIMENSIONLESS, Decimal("1"), is_metric=False),
}

# Build complete unit registry
UNIT_REGISTRY: dict[str, UnitDefinition] = {}
UNIT_REGISTRY.update(BASE_UNITS)
UNIT_REGISTRY.update(DERIVED_UNITS)
UNIT_REGISTRY.update(SPECIAL_UNITS)

# Common aliases
UNIT_ALIASES: dict[str, str] = {
    "mcg": "ug",  # microgram
    "sec": "s",
    "hr": "h",
    "yr": "a",
    "cc": "mL",  # cubic centimeter = milliliter
    "lbs": "[lb_av]",
    "lb": "[lb_av]",
    "oz": "[oz_av]",
    "in": "[in_i]",
    "ft": "[ft_i]",
    "mi": "[mi_i]",
    "gal": "[gal_us]",
    "degC": "Cel",
    "degF": "[degF]",
    "celsius": "Cel",
    "fahrenheit": "[degF]",
    "meter": "m",
    "gram": "g",
    "second": "s",
    "liter": "L",
    "litre": "L",
}


def get_unit(code: str) -> UnitDefinition | None:
    """Look up a unit by its UCUM code."""
    # Check aliases first
    if code in UNIT_ALIASES:
        code = UNIT_ALIASES[code]

    # Direct lookup
    if code in UNIT_REGISTRY:
        return UNIT_REGISTRY[code]

    return None


def get_prefixed_unit(code: str) -> tuple[UnitDefinition, Decimal] | None:
    """Try to parse a prefixed unit (e.g., 'mg' -> 'm' + 'g')."""
    # Check aliases first
    if code in UNIT_ALIASES:
        code = UNIT_ALIASES[code]

    # Direct lookup first
    if code in UNIT_REGISTRY:
        return UNIT_REGISTRY[code], Decimal("1")

    # Try prefix parsing (longest prefix first for 'da')
    for prefix in sorted(SI_PREFIXES.keys(), key=len, reverse=True):
        if code.startswith(prefix) and len(code) > len(prefix):
            base_code = code[len(prefix) :]
            if base_code in UNIT_REGISTRY:
                base_unit = UNIT_REGISTRY[base_code]
                if base_unit.is_metric:
                    return base_unit, SI_PREFIXES[prefix]

    return None
