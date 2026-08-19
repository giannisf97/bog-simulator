import pandas as pd
from bog_simulator.config import DATA_DIR
import tomllib

def load_calibration_table(tank_number: int) -> pd.DataFrame:
    """Loads calibration table of the tank."""
    file_path = DATA_DIR / "calibration_tables" / f"Table_{tank_number - 1}.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"Callibration table file doesn't exist: {file_path}")
    return pd.read_csv(file_path)

def load_boiling_points() -> pd.DataFrame:
    """Loads boiling points of methane."""
    file_path = DATA_DIR / "thermodynamics" / "Boiling_points_CH4.csv"
    return pd.read_csv(file_path)

def load_vessel_data() -> dict:
    file_path = DATA_DIR / "vessel_configs" / "vessel_174k_membrane.toml"
    with open(file_path, "rb") as f:
        vessel_data = tomllib.load(f)
        return vessel_data

def load_weather_variables() -> pd.DataFrame:
    file_path = DATA_DIR / "enviromental" / "weather.csv"
    weather_df = pd.read_csv(file_path)
    return weather_df