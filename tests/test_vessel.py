"""Tests for bog_simulator.core.vessel — LNGc integration model."""

import pytest

from bog_simulator.core.vessel import LNGc
from bog_simulator.core.environment import Environment


class TestLNGcInit:
    """Tests for LNGc vessel initialization."""

    def test_creates_instance(self, lngc_vessel):
        assert isinstance(lngc_vessel, LNGc)

    def test_four_tanks(self, lngc_vessel):
        assert len(lngc_vessel.tanks) == 4

    def test_vapor_header_positive(self, lngc_vessel):
        assert lngc_vessel.vapor_header > 0

    def test_vapor_header_is_mean_of_tanks(self, lngc_vessel):
        import numpy as np
        expected = float(np.mean([t.P_tank for t in lngc_vessel.tanks]))
        assert lngc_vessel.vapor_header == pytest.approx(expected)

    def test_stats_initialized(self, lngc_vessel):
        assert len(lngc_vessel.stats.press) >= 1
        assert len(lngc_vessel.stats.time) >= 1


class TestLNGcUpdateTanks:
    """Tests for the full simulation update cycle."""

    def test_update_tanks_runs(self, lngc_vessel):
        """update_tanks(3600) should complete without error."""
        lngc_vessel.update_tanks(3600)

    def test_pressure_recorded(self, lngc_vessel):
        initial_len = len(lngc_vessel.stats.press)
        lngc_vessel.update_tanks(3600)
        assert len(lngc_vessel.stats.press) == initial_len + 1

    def test_vapor_header_clamped(self, lngc_vessel):
        """Vapor header should never exceed 330 mbar or go below 0."""
        for _ in range(5):
            lngc_vessel.update_tanks(3600)
        for tank in lngc_vessel.tanks:
            assert 0 <= tank.P_tank <= 330

    def test_internal_timer_advances(self, vessel_config, weather_df):
        """Class-level timer should increment by dt per update step."""
        Environment.ic = 0
        LNGc.internal_timer = 0

        from bog_simulator.core.consumers import megi, dfde, gcu, consumer
        megis = [megi.MEGI(**p) for p in vessel_config["Main_Engines"]]
        dfdes = [dfde.DFDE(**p) for p in vessel_config["Diesel_Generators"]]
        gcu_inst = gcu.GCU(**vessel_config["Gcu"])
        env = Environment(vessel_config["vessel"], weather_df)
        cons = consumer.Consumers(dfdes, megis, gcu_inst)
        ship = LNGc(vessel_config["tanks"], env, cons, 0)

        ship.update_tanks(3600)
        assert LNGc.internal_timer == 3600
        ship.update_tanks(3600)
        assert LNGc.internal_timer == 7200


class TestLNGcUpdatePressure:
    """Tests for the pressure update mechanism."""

    def test_pressure_changes_after_update(self, lngc_vessel):
        p_before = lngc_vessel.vapor_header
        new_p = lngc_vessel.update_pressure(3600)
        # Pressure should change (BOG generation vs consumption imbalance)
        assert new_p != pytest.approx(p_before, abs=0.001)

    def test_returns_float(self, lngc_vessel):
        p = lngc_vessel.update_pressure(3600)
        assert isinstance(p, float)
