"""Tests for bog_simulator.core.tank — MembraneTank model."""

import pytest

from bog_simulator.core.environment import Environment
from bog_simulator.core.tank import MembraneTank


class TestMembraneTankInit:
    """Tests for MembraneTank construction from config + environment."""

    def test_creates_instance(self, sample_tank):
        assert isinstance(sample_tank, MembraneTank)

    def test_tank_number(self, sample_tank):
        assert sample_tank.tank_num >= 1

    def test_liquid_volume_positive(self, sample_tank):
        assert sample_tank.liquid_vol > 0

    def test_vapor_volume_positive(self, sample_tank):
        assert sample_tank.vapor_vol > 0

    def test_volumes_sum_to_capacity(self, sample_tank):
        total = sample_tank.liquid_vol + sample_tank.vapor_vol
        assert total == pytest.approx(sample_tank.tank_capacity)

    def test_pressure_positive(self, sample_tank):
        assert sample_tank.P_tank > 0

    def test_liquid_temp_cryogenic(self, sample_tank):
        """LNG boiling temp should be around 110-115 K."""
        assert 100 < sample_tank.avg_liquid_temp < 125

    def test_vapor_temp_above_liquid(self, sample_tank):
        assert sample_tank.avg_vapor_temp > sample_tank.avg_liquid_temp

    def test_liquid_level_positive(self, sample_tank):
        assert sample_tank.liquid_level > 0

    def test_heat_rate_positive(self, sample_tank):
        assert sample_tank.Q_rate > 0

    def test_bog_rate_positive(self, sample_tank):
        assert sample_tank.m_bog > 0

    def test_access_tank_true(self, sample_tank):
        assert sample_tank.access_tank is True

    def test_submerged_areas_dict(self, sample_tank):
        assert isinstance(sample_tank.A_submerged, dict)
        for key in ["A_coff", "A_sea", "A_air"]:
            assert key in sample_tank.A_submerged

    def test_geometry_has_required_keys(self, sample_tank):
        for key in ["height", "breadth", "length", "h1", "h2"]:
            assert key in sample_tank.tank_geometry


class TestMembraneTankUpdate:
    """Tests for MembraneTank.update() and update_parameters()."""

    def test_update_reduces_liquid_volume(self, sample_tank, environment):
        vol_before = sample_tank.liquid_vol
        sample_tank.update(3600, environment)  # 1 hour
        assert sample_tank.liquid_vol < vol_before

    def test_update_increases_vapor_volume(self, sample_tank, environment):
        vap_before = sample_tank.vapor_vol
        sample_tank.update(3600, environment)
        assert sample_tank.vapor_vol > vap_before

    def test_volumes_still_sum_to_capacity(self, sample_tank, environment):
        sample_tank.update(3600, environment)
        total = sample_tank.liquid_vol + sample_tank.vapor_vol
        assert total == pytest.approx(sample_tank.tank_capacity)

    def test_bog_rate_still_positive(self, sample_tank, environment):
        sample_tank.update(3600, environment)
        assert sample_tank.m_bog > 0

    def test_depleted_tank_locked(self, vessel_config, environment):
        """A tank with nearly zero LNG should lock (access_tank=False) after update."""
        tank_params = vessel_config["tanks"][0].copy()
        tank_params["Liquid_Volume"] = 0.01  # nearly empty
        tank = MembraneTank(tank_params, environment)
        # Force enough time to deplete the tiny amount
        tank.update(86400 * 365, environment)  # 1 year
        assert tank.access_tank is False
        assert tank.liquid_vol == 0

    def test_locked_tank_no_further_update(self, vessel_config, environment):
        """Once access_tank is False, update() should be a no-op."""
        tank_params = vessel_config["tanks"][0].copy()
        tank_params["Liquid_Volume"] = 0.001
        tank = MembraneTank(tank_params, environment)
        tank.update(86400 * 365, environment)
        assert tank.access_tank is False
        vol_after_lock = tank.liquid_vol
        tank.update(3600, environment)
        assert tank.liquid_vol == vol_after_lock  # unchanged
