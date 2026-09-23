"""Tests for bog_simulator.core.environment — voyage weather model."""

import pytest
import pandas as pd

from bog_simulator.core.environment import Environment


class TestEnvironmentInit:
    """Tests for Environment initialization from vessel config + weather data."""

    def test_creates_instance(self, environment):
        assert isinstance(environment, Environment)

    def test_initial_temperatures_in_kelvin(self, environment):
        """All temperatures should be in Kelvin (> 200 K for typical conditions)."""
        assert environment.T_air > 200
        assert environment.T_sea > 200
        assert environment.T_coff > 200

    def test_atm_pressure_realistic(self, environment):
        """Atmospheric pressure should be around 950–1050 mbar."""
        assert 900 < environment.atm < 1100

    def test_draft_positive(self, environment):
        assert environment.draft > 0

    def test_ssf_gte_one(self, environment):
        assert environment.ssf >= 1.0

    def test_end_initially_false(self, environment):
        assert environment.end is False

    def test_voyage_is_L_or_B(self, environment):
        assert environment.voyage in ("L", "B")

    def test_date_is_string(self, environment):
        assert isinstance(environment.date, str)


class TestEnvironmentUpdate:
    """Tests for Environment.update() stepping through the weather dataset."""

    def test_update_advances_counter(self, environment):
        initial_ic = Environment.ic
        environment.update()
        assert Environment.ic == initial_ic + 1

    def test_update_changes_date(self, vessel_config, weather_df):
        Environment.ic = 0
        env = Environment(vessel_config["vessel"], weather_df)
        date_before = env.date
        env.update()
        assert env.date != date_before

    def test_update_to_end(self, vessel_config, weather_df):
        """Stepping past the dataset should set end=True."""
        Environment.ic = 0
        env = Environment(vessel_config["vessel"], weather_df)
        # Fast-forward to the end
        for _ in range(len(weather_df)):
            env.update()
            if env.end:
                break
        assert env.end is True
