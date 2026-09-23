"""Tests for bog_simulator.physics.heat_transfer — heat inflow and BOG."""

import pytest

from bog_simulator.physics import heat_transfer as ht
from bog_simulator.config import LANTENT_HEAT, THERMAL_CONDUCTIVITY as U


# ── q_rate ────────────────────────────────────────────────────────────

class TestQRate:
    """q_rate: Q = U * A * (T_hot - T_cold)."""

    def test_basic(self):
        assert ht.q_rate(0.1, 100, 300, 112) == pytest.approx(0.1 * 100 * 188)

    def test_zero_area(self):
        assert ht.q_rate(0.1, 0, 300, 112) == 0.0

    def test_equal_temperatures(self):
        """No heat transfer when hot == cold."""
        assert ht.q_rate(0.1, 100, 112, 112) == 0.0

    def test_negative_delta_t(self):
        """Cold side hotter → negative Q (heat out)."""
        assert ht.q_rate(0.1, 100, 100, 200) < 0


# ── mbog ──────────────────────────────────────────────────────────────

class TestMbog:
    """mbog: m_bog = Q / L."""

    def test_basic(self):
        q = 510_000  # W
        assert ht.mbog(q) == pytest.approx(1.0)

    def test_zero(self):
        assert ht.mbog(0) == 0.0

    def test_proportionality(self):
        """Double the heat → double the BOG."""
        assert ht.mbog(1_020_000) == pytest.approx(2.0)


# ── total_Q_rate ──────────────────────────────────────────────────────

class TestTotalQRate:
    """total_Q_rate: integrates Q across coff/sea/air boundaries × SSF."""

    @pytest.fixture
    def areas(self):
        return {"A_coff": 200.0, "A_sea": 500.0, "A_air": 300.0}

    def test_returns_positive(self, areas):
        Q = ht.total_Q_rate(areas, T_coff=293.0, T_sea=300.0,
                            T_air=303.0, ssf=1.0, avg_liquid_temp=112.0)
        assert Q > 0

    def test_ssf_amplifies(self, areas):
        """SSF > 1 should increase total Q proportionally."""
        Q1 = ht.total_Q_rate(areas, 293.0, 300.0, 303.0, 1.0, 112.0)
        Q2 = ht.total_Q_rate(areas, 293.0, 300.0, 303.0, 1.15, 112.0)
        assert Q2 == pytest.approx(Q1 * 1.15)

    def test_zero_air_area(self):
        """When A_air = 0, air contribution should be suppressed."""
        areas = {"A_coff": 200.0, "A_sea": 500.0, "A_air": 0.0}
        Q = ht.total_Q_rate(areas, 293.0, 300.0, 303.0, 1.0, 112.0)
        # Verify only coff + sea contribute
        Q_manual = (U["coff"] * 200 * (293.0 - 112.0)
                    + U["sea"] * 500 * (300.0 - 112.0))
        assert Q == pytest.approx(Q_manual)

    def test_all_zero_areas(self):
        areas = {"A_coff": 0.0, "A_sea": 0.0, "A_air": 0.0}
        Q = ht.total_Q_rate(areas, 293.0, 300.0, 303.0, 1.0, 112.0)
        assert Q == 0.0
