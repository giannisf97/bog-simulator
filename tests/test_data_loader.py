"""Tests for bog_simulator.utils.data_loader — data file loading."""

import pytest
import pandas as pd

from bog_simulator.utils import data_loader


class TestLoadCalibrationTable:
    """load_calibration_table: CSV → DataFrame with Gauge/Volume columns."""

    def test_returns_dataframe(self):
        df = data_loader.load_calibration_table(1)
        assert isinstance(df, pd.DataFrame)

    def test_columns_present(self):
        df = data_loader.load_calibration_table(1)
        assert "Gauge[mm]" in df.columns
        assert "Volume[m3]" in df.columns

    def test_non_empty(self):
        df = data_loader.load_calibration_table(1)
        assert len(df) > 0

    @pytest.mark.parametrize("tank_num", [1, 2, 3, 4])
    def test_all_four_tanks(self, tank_num):
        df = data_loader.load_calibration_table(tank_num)
        assert len(df) > 100  # each table has thousands of rows

    def test_invalid_tank_raises(self):
        with pytest.raises(FileNotFoundError):
            data_loader.load_calibration_table(99)

    def test_gauge_monotonically_increasing(self):
        df = data_loader.load_calibration_table(1)
        gauge = df["Gauge[mm]"].values
        assert all(gauge[i] <= gauge[i+1] for i in range(len(gauge) - 1))


class TestLoadBoilingPoints:
    """load_boiling_points: methane saturation curve CSV."""

    def test_returns_dataframe(self):
        df = data_loader.load_boiling_points()
        assert isinstance(df, pd.DataFrame)

    def test_columns(self):
        df = data_loader.load_boiling_points()
        assert "mbarA" in df.columns
        assert "Temp[K]" in df.columns

    def test_non_empty(self):
        df = data_loader.load_boiling_points()
        assert len(df) > 0


class TestLoadVesselData:
    """load_vessel_data: TOML configuration parser."""

    def test_returns_dict(self):
        data = data_loader.load_vessel_data()
        assert isinstance(data, dict)

    def test_has_tanks(self):
        data = data_loader.load_vessel_data()
        assert "tanks" in data
        assert len(data["tanks"]) == 4

    def test_has_vessel_section(self):
        data = data_loader.load_vessel_data()
        assert "vessel" in data

    def test_has_main_engines(self):
        data = data_loader.load_vessel_data()
        assert "Main_Engines" in data
        assert len(data["Main_Engines"]) == 2

    def test_has_diesel_generators(self):
        data = data_loader.load_vessel_data()
        assert "Diesel_Generators" in data
        assert len(data["Diesel_Generators"]) == 4

    def test_has_gcu(self):
        data = data_loader.load_vessel_data()
        assert "Gcu" in data

    def test_tank_has_geometry(self):
        data = data_loader.load_vessel_data()
        tank = data["tanks"][0]
        assert "Geometry" in tank
        geo = tank["Geometry"]
        for key in ["height", "breadth", "length", "h1", "h2"]:
            assert key in geo


class TestLoadWeatherVariables:
    """load_weather_variables: voyage weather CSV."""

    def test_returns_dataframe(self):
        df = data_loader.load_weather_variables()
        assert isinstance(df, pd.DataFrame)

    def test_required_columns(self):
        df = data_loader.load_weather_variables()
        for col in ["date", "apparent_temperature", "sea_surface_temperature",
                     "pressure_msl", "wind_speed_10m"]:
            assert col in df.columns, f"Missing column: {col}"

    def test_non_empty(self):
        df = data_loader.load_weather_variables()
        assert len(df) > 0
