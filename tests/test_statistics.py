"""Tests for bog_simulator.utils.statistics — telemetry collection."""

import pytest

from bog_simulator.utils.statistics import Statistics
from bog_simulator.physics import per


class TestStatisticsInit:
    """Tests for Statistics initialization."""

    def test_creates_instance(self):
        s = Statistics(press=100.0, consumption=0.5)
        assert isinstance(s, Statistics)

    def test_initial_data_point(self):
        s = Statistics(press=100.0, consumption=0.5)
        assert len(s.press) == 1
        assert len(s.consumption) == 1
        assert len(s.time) == 1

    def test_initial_values(self):
        s = Statistics(press=150.0, consumption=0.3)
        assert s.press[0] == 150.0
        assert s.consumption[0] == pytest.approx(per.hour(0.3))
        assert s.time[0] == 0.0


class TestStatisticsFetchData:
    """Tests for Statistics.fetch_data() time-series recording."""

    def test_appends_data(self):
        s = Statistics(press=100.0, consumption=0.5)
        s.fetch_data(110.0, 0.6, 3600)
        assert len(s.press) == 2
        assert len(s.consumption) == 2
        assert len(s.time) == 2

    def test_time_increments(self):
        s = Statistics(press=100.0, consumption=0.5)
        s.fetch_data(110.0, 0.6, 3600)
        assert s.time[-1] == pytest.approx(1.0)  # 3600s = 1 hour

    def test_multiple_appends(self):
        s = Statistics(press=100.0, consumption=0.5)
        for i in range(10):
            s.fetch_data(100.0 + i, 0.5, 3600)
        assert len(s.press) == 11  # 1 initial + 10 appends
        assert s.time[-1] == pytest.approx(10.0)

    def test_consumption_converted_to_per_hour(self):
        s = Statistics(press=100.0, consumption=0.5)
        s.fetch_data(110.0, 1.0, 3600)  # 1.0 kg/s
        assert s.consumption[-1] == pytest.approx(3600.0)  # 1 kg/s = 3600 kg/h
