"""Data loading and configuration parser utility module.

Reads static vessel configuration (TOML), sounding calibration tables (CSV),
methane saturation pressure-temperature curves (CSV), and voyage weather records (CSV).
"""

from typing import Any
import tomllib
import pandas as pd
from bog_simulator.config import DATA_DIR

def load_calibration_table(tank_number: int) -> pd.DataFrame:
    """Loads the official sounding/gauge calibration table for a specified cargo tank.

    Maps gauge soundings [mm] to liquid cargo volume [m^3].

    Args:
        tank_number (int): Tank index number (1 to 4).

    Returns:
        pd.DataFrame: DataFrame containing 'Gauge[mm]' and 'Volume[m3]'.

    Raises:
        FileNotFoundError: If calibration CSV for the given tank does not exist.
    """
    file_path = DATA_DIR / "calibration_tables" / f"Table_{tank_number - 1}.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"Callibration table file doesn't exist: {file_path}")
    return pd.read_csv(file_path)

def load_boiling_points() -> pd.DataFrame:
    """Loads the pure methane saturation boiling curve dataset.

    Returns:
        pd.DataFrame: DataFrame containing 'mbarA' (absolute pressure) and 'Temp[K]'.
    """
    file_path = DATA_DIR / "thermodynamics" / "Boiling_points_CH4.csv"
    return pd.read_csv(file_path)

def load_vessel_data() -> dict[str, Any]:
    """Parses the static vessel and cargo tank configuration from TOML.

    Loads tank geometry, initial loading states, draft, cofferdam temperature,
    and initial main engine / generator settings.

    Returns:
        dict: Parsed vessel configuration dictionary.
    """
    file_path = DATA_DIR / "vessel_configs" / "vessel_174k_membrane.toml"
    with open(file_path, "rb") as f:
        vessel_data = tomllib.load(f)
        return vessel_data

def load_weather_variables() -> pd.DataFrame:
    """Loads historical hourly voyage weather and oceanographic logs.

    Contains timestamp, ambient air temperature, sea surface temperature,
    barometric pressure at mean sea level, and wind speed / Beaufort numbers.

    Returns:
        pd.DataFrame: Voyage weather time-series dataset.
    """
    file_path = DATA_DIR / "enviromental" / "weather.csv"
    weather_df = pd.read_csv(file_path)
    return weather_df