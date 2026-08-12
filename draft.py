import tomllib
from src.bog_simulator.config import DATA_DIR 

file_path = DATA_DIR / "vessel_configs" / "vessel_174k_membrane.toml"
with open(file_path, "rb") as f:
    vessel_data = tomllib.load(f)
    print(vessel_data)