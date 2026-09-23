"""Tests for bog_simulator.physics.thermodynamics — thermodynamic calculations."""

import pytest
import numpy as np
import pandas as pd

from bog_simulator.physics import thermodynamics as th


# ── Temperature conversions ────────────────────────────────────────────

class TestToKelvin:
    """to_Kelvin: °C → K (add 273)."""

    def test_zero_celsius(self):
        assert th.to_Kelvin(0) == 273

    def test_positive(self):
        assert th.to_Kelvin(25) == 298

    def test_negative(self):
        assert th.to_Kelvin(-163) == 110

    def test_type_float(self):
        assert th.to_Kelvin(25.5) == pytest.approx(298.5)


class TestToDegC:
    """to_degC: K → °C (subtract 273)."""

    def test_zero_kelvin(self):
        assert th.to_degC(273) == 0

    def test_round_trip(self):
        assert th.to_degC(th.to_Kelvin(37)) == pytest.approx(37)


# ── Mass-volume conversion ────────────────────────────────────────────

class TestKgToM3:
    """kg_to_m3: mass/density → volume."""

    def test_basic(self):
        assert th.kg_to_m3(434.8, 434.8) == pytest.approx(1.0)

    def test_zero_mass(self):
        assert th.kg_to_m3(434.8, 0) == 0.0

    def test_double_mass(self):
        assert th.kg_to_m3(434.8, 869.6) == pytest.approx(2.0)


# ── Boiling point interpolation ───────────────────────────────────────

class TestBoilingPoint:
    """boiling_point: interpolates T_boil from gauge pressure + atm."""

    def test_returns_float(self, boiling_df):
        result = th.boiling_point(100, 1013, boiling_df)
        assert isinstance(result, (float, np.floating))

    def test_higher_pressure_raises_temperature(self, boiling_df):
        t_low = th.boiling_point(50, 1013, boiling_df)
        t_high = th.boiling_point(200, 1013, boiling_df)
        assert t_high > t_low, "Higher pressure must yield higher boiling point"

    def test_typical_range(self, boiling_df):
        """At ~1113 mbar abs (100 gauge + 1013 atm), methane boils around 111-113 K."""
        t = th.boiling_point(100, 1013, boiling_df)
        assert 108 < t < 118


# ── Liquid level interpolation ────────────────────────────────────────

class TestLiquidLevel:
    """liquid_level: volume → gauge height via calibration table."""

    def test_zero_volume_gives_zero_level(self, calibration_table_1):
        level = th.liquid_level(0, calibration_table_1["Volume[m3]"],
                                calibration_table_1["Gauge[mm]"])
        assert level == pytest.approx(0.0, abs=0.01)

    def test_positive_volume_positive_level(self, calibration_table_1):
        level = th.liquid_level(10000, calibration_table_1["Volume[m3]"],
                                calibration_table_1["Gauge[mm]"])
        assert level > 0

    def test_level_monotonically_increases(self, calibration_table_1):
        vol_col = calibration_table_1["Volume[m3]"]
        gauge_col = calibration_table_1["Gauge[mm]"]
        l1 = th.liquid_level(5000, vol_col, gauge_col)
        l2 = th.liquid_level(15000, vol_col, gauge_col)
        assert l2 > l1


# ── Vapor temperature ─────────────────────────────────────────────────

class TestVaporTemp:
    """vapor_temp: ullage temperature stratification model."""

    def test_high_filling_small_offset(self):
        """At 95% filling, vapor temp ≈ liquid temp + ~4 K."""
        liquid_temp = 112.0
        capacity = 40_000
        liquid_volume = capacity * 0.95
        t_vapor = th.vapor_temp(capacity, liquid_volume, liquid_temp)
        offset = t_vapor - liquid_temp
        assert 2 <= offset <= 6

    def test_low_filling_large_offset(self):
        """At 2% filling (ballast heel), ΔT ≈ 45 K."""
        liquid_temp = 112.0
        capacity = 40_000
        liquid_volume = capacity * 0.02
        t_vapor = th.vapor_temp(capacity, liquid_volume, liquid_temp)
        offset = t_vapor - liquid_temp
        assert 40 <= offset <= 50

    def test_vapor_always_warmer_than_liquid(self):
        liquid_temp = 112.0
        for fr in [0.02, 0.1, 0.5, 0.8, 0.95, 0.98]:
            t_vapor = th.vapor_temp(40_000, 40_000 * fr, liquid_temp)
            assert t_vapor > liquid_temp


# ── ME-GI consumption ─────────────────────────────────────────────────

class TestMegiConsumption:
    """megi_consumption: 3rd-order polynomial fuel gas model."""

    def test_returns_positive(self):
        assert th.megi_consumption(65) > 0

    def test_higher_rpm_more_consumption(self):
        low = th.megi_consumption(45)
        high = th.megi_consumption(73)
        assert high > low

    def test_min_rpm(self):
        c = th.megi_consumption(45)
        assert c > 0

    def test_max_rpm(self):
        c = th.megi_consumption(73)
        assert c > 0

    def test_returns_float(self):
        assert isinstance(th.megi_consumption(60), float)


# ── DFDE consumption ──────────────────────────────────────────────────

class TestDfdeConsumption:
    """dfde_consumption: quadratic fuel gas model for W6L34DF / W8L34DF."""

    def test_w6_returns_positive(self):
        assert th.dfde_consumption("W6L34DF", 2000) > 0

    def test_w8_returns_positive(self):
        assert th.dfde_consumption("W8L34DF", 3000) > 0

    def test_w8_higher_than_w6_at_same_output(self):
        """W8L34DF has higher base consumption (132.3 vs 99.2)."""
        c6 = th.dfde_consumption("W6L34DF", 2000)
        c8 = th.dfde_consumption("W8L34DF", 2000)
        assert c8 > c6

    def test_higher_output_more_consumption(self):
        low = th.dfde_consumption("W8L34DF", 1400)
        high = th.dfde_consumption("W8L34DF", 4000)
        assert high > low

    def test_unknown_type_returns_zero(self):
        assert th.dfde_consumption("UNKNOWN", 2000) == 0.0
