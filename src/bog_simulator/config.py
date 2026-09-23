"""Global configuration, physical constants, and directory path definitions."""

from pathlib import Path

#-----Directories--------
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
DATA_DIR: Path = BASE_DIR / "data"
RESOURCE_DIR: Path = BASE_DIR / "resources"

#-----Constants----------
LANTENT_HEAT: float = 510_000.0 # J/kg
GAS_CONSTANT: float = 8.314 # J/mol*K
MOLECULAR_MASS_CH4: float = 0.016034 # kg/mol
DENSITY_LNG: float = 434.8 # kg/m^3

# Overall heat transfer coefficients (U-values) [W/(m^2*K)] calibrated to yield
# an overall daily Boil-Off Rate (BOR) of ~0.10% - 0.15% per day in accordance with
# international maritime standards for GTT Mark III / NO96 membrane containment systems.
THERMAL_CONDUCTIVITY: dict[str, float] = {
    "sea": 0.08,
    "air": 0.10,
    "coff": 0.12,
} # W/m^2*K