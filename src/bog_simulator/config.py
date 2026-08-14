from pathlib import Path

#-----Directories--------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RESOURCE_DIR = BASE_DIR / "resources"

#-----Constants----------
LANTENT_HEAT = 510_000.0 # J/kg
GAS_CONSTANT = 8.314 # J/mol*K
MOLECULAR_MASS_CH4 = 0.016034 # kg/mol
DENSITY_LNG = 434.8 # kg/m^3

#different thermal conductivity for different contact surfaces
THERMAL_CONDUCTIVITY= {
    "sea": 0.1,
    "air": 0.12,
    "coff": 0.14,
} # W/m^2*K