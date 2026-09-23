"""Tests for bog_simulator.core.producer — external gas supply model."""

from bog_simulator.core.producer import Producer


class TestProducer:
    """Tests for the Producer class."""

    def test_init_with_int(self):
        p = Producer(100)
        assert p.rate == 100

    def test_init_with_float(self):
        p = Producer(55.5)
        assert p.rate == 55.5

    def test_init_zero(self):
        p = Producer(0)
        assert p.rate == 0
