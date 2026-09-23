"""Tests for bog_simulator.physics.per — time-rate conversion utilities."""

import pytest

from bog_simulator.physics.per import sec, hour


class TestSec:
    """per.sec(): converts per-hour → per-second (÷ 3600)."""

    def test_basic_conversion(self):
        assert sec(3600) == pytest.approx(1.0)

    def test_zero(self):
        assert sec(0) == 0.0

    def test_fractional(self):
        assert sec(7200) == pytest.approx(2.0)

    def test_negative(self):
        assert sec(-3600) == pytest.approx(-1.0)

    def test_small_value(self):
        assert sec(1) == pytest.approx(1 / 3600)


class TestHour:
    """per.hour(): converts per-second → per-hour (× 3600)."""

    def test_basic_conversion(self):
        assert hour(1) == pytest.approx(3600.0)

    def test_zero(self):
        assert hour(0) == 0.0

    def test_fractional(self):
        assert hour(0.5) == pytest.approx(1800.0)

    def test_negative(self):
        assert hour(-1) == pytest.approx(-3600.0)


class TestRoundTrip:
    """sec and hour should be exact inverses of each other."""

    @pytest.mark.parametrize("value", [0, 1, 100, 5432.1, -77])
    def test_roundtrip_hour_then_sec(self, value):
        assert sec(hour(value)) == pytest.approx(value)

    @pytest.mark.parametrize("value", [0, 1, 100, 5432.1, -77])
    def test_roundtrip_sec_then_hour(self, value):
        assert hour(sec(value)) == pytest.approx(value)
