"""Tests for bog_simulator.config — physical constants and paths."""

from pathlib import Path

from bog_simulator import config


class TestPaths:
    """Verify that the configured project directories resolve correctly."""

    def test_base_dir_exists(self):
        assert config.BASE_DIR.exists()

    def test_data_dir_exists(self):
        assert config.DATA_DIR.exists()

    def test_resource_dir_exists(self):
        assert config.RESOURCE_DIR.exists()

    def test_base_dir_contains_src(self):
        assert (config.BASE_DIR / "src").is_dir()


class TestPhysicalConstants:
    """Verify that physical constants have expected magnitudes and types."""

    def test_latent_heat_type(self):
        assert isinstance(config.LANTENT_HEAT, float)

    def test_latent_heat_value(self):
        assert config.LANTENT_HEAT == 510_000.0

    def test_gas_constant_value(self):
        assert config.GAS_CONSTANT == 8.314

    def test_molecular_mass_ch4(self):
        assert config.MOLECULAR_MASS_CH4 == 0.016034

    def test_density_lng(self):
        assert config.DENSITY_LNG == 434.8


class TestThermalConductivity:
    """Verify thermal conductivity dictionary structure and values."""

    def test_keys(self):
        assert set(config.THERMAL_CONDUCTIVITY.keys()) == {"sea", "air", "coff"}

    def test_sea_value(self):
        assert config.THERMAL_CONDUCTIVITY["sea"] == 0.1

    def test_air_value(self):
        assert config.THERMAL_CONDUCTIVITY["air"] == 0.12

    def test_coff_value(self):
        assert config.THERMAL_CONDUCTIVITY["coff"] == 0.14

    def test_ordering_sea_le_air_le_coff(self):
        """Cofferdam should have the highest U, sea the lowest."""
        tc = config.THERMAL_CONDUCTIVITY
        assert tc["sea"] <= tc["air"] <= tc["coff"]
