"""Tests for bog_simulator.physics.hydrodynamics — geometry and sloshing."""

import pytest
import numpy as np

from bog_simulator.physics import hydrodynamics as hyd


# ── Sloshing Scaling Factor (SSF) ─────────────────────────────────────

class TestSSF:
    """ssf(): linear sloshing factor based on Beaufort number and voyage."""

    def test_laden_calm_sea(self):
        assert hyd.ssf(0, "L") == pytest.approx(1.0)

    def test_laden_sea_state_5(self):
        assert hyd.ssf(5, "L") == pytest.approx(1.15)

    def test_ballast_calm_sea(self):
        assert hyd.ssf(0, "B") == pytest.approx(1.0)

    def test_ballast_sea_state_5(self):
        assert hyd.ssf(5, "B") == pytest.approx(1.25)

    def test_ballast_always_gte_laden(self):
        """Ballast SSF ≥ Laden SSF for any positive sea state."""
        for bn in range(1, 13):
            assert hyd.ssf(bn, "B") >= hyd.ssf(bn, "L")

    def test_ssf_monotonically_increases_laden(self):
        for bn in range(0, 11):
            assert hyd.ssf(bn + 1, "L") > hyd.ssf(bn, "L")

    def test_ssf_monotonically_increases_ballast(self):
        for bn in range(0, 11):
            assert hyd.ssf(bn + 1, "B") > hyd.ssf(bn, "B")


# ── Tank geometry for tests ────────────────────────────────────────────

@pytest.fixture
def geometry():
    """Typical membrane tank geometry based on a 174k LNGC."""
    return {
        "height": 27.0,
        "breadth": 38.0,
        "length": 45.0,
        "h1": 5.0,
        "h2": 3.0,
    }


# ── Cofferdam sub-area ────────────────────────────────────────────────

class TestCofferdamSubArea:
    """cofferdam_subArea: fore/aft bulkhead wetted area calc."""

    def test_positive_at_midlevel(self, geometry):
        area = hyd.cofferdam_subArea(15.0, geometry)
        assert area > 0

    def test_increases_with_level(self, geometry):
        a1 = hyd.cofferdam_subArea(5.0, geometry)
        a2 = hyd.cofferdam_subArea(15.0, geometry)
        assert a2 > a1

    def test_above_upper_chamfer(self, geometry):
        """Level above height - h1 triggers the upper chamfer branch."""
        level = geometry["height"] - geometry["h1"] + 1  # 23 m
        area = hyd.cofferdam_subArea(level, geometry)
        assert area > 0


# ── Sea sub-area ──────────────────────────────────────────────────────

class TestSeaSubArea:
    """sea_subArea: bottom/side hull contact with seawater."""

    def test_positive(self, geometry):
        area = hyd.sea_subArea(15.0, 12.0, geometry)
        assert area > 0

    def test_low_level_below_h2(self, geometry):
        """When level < h2, only the bilge hopper region is wetted."""
        area = hyd.sea_subArea(2.0, 12.0, geometry)
        assert area > 0

    def test_level_above_draft(self, geometry):
        """When level exceeds draft, the waterline caps the sea-contact area."""
        area = hyd.sea_subArea(20.0, 12.0, geometry)
        assert area > 0


# ── Air sub-area ──────────────────────────────────────────────────────

class TestAirSubArea:
    """air_subArea: freeboard-side contact with ambient air."""

    def test_zero_when_below_draft(self, geometry):
        """If liquid level ≤ draft - 3.2, no air contact."""
        area = hyd.air_subArea(5.0, 12.0, geometry)
        assert area == 0.0

    def test_positive_when_above_draft(self, geometry):
        area = hyd.air_subArea(20.0, 12.0, geometry)
        assert area > 0

    def test_above_upper_chamfer(self, geometry):
        level = geometry["height"] - geometry["h1"] + 1
        area = hyd.air_subArea(level, 12.0, geometry)
        assert area > 0


# ── Submerged area aggregate ──────────────────────────────────────────

class TestSubmergedArea:
    """submerged_area: returns dict with A_coff, A_sea, A_air."""

    def test_returns_dict(self, geometry):
        result = hyd.submerged_area(15.0, 12.0, geometry)
        assert isinstance(result, dict)

    def test_keys_present(self, geometry):
        result = hyd.submerged_area(15.0, 12.0, geometry)
        assert set(result.keys()) == {"A_coff", "A_sea", "A_air"}

    def test_all_values_non_negative(self, geometry):
        result = hyd.submerged_area(15.0, 12.0, geometry)
        for key, val in result.items():
            assert val >= 0, f"{key} is negative: {val}"
