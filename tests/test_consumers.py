"""Tests for bog_simulator.core.consumers — MEGI, DFDE, GCU, Consumers."""

import pytest

from bog_simulator.core.consumers.megi import MEGI
from bog_simulator.core.consumers.dfde import DFDE
from bog_simulator.core.consumers.gcu import GCU
from bog_simulator.core.consumers.consumer import Consumers
from bog_simulator.physics import per


# ═══════════════════════════════════════════════════════════════════════
# ME-GI Main Engine
# ═══════════════════════════════════════════════════════════════════════

class TestMEGI:
    """Tests for the MAN B&W ME-GI two-stroke engine model."""

    def test_init_operational(self, megi_engine):
        assert megi_engine.is_operational is True
        assert megi_engine.rpm == 65
        assert megi_engine.m_gas > 0

    def test_init_stopped(self, megi_engine_stopped):
        """A stopped engine should have m_gas = 0 (multiplied by False)."""
        assert megi_engine_stopped.is_operational is False
        assert megi_engine_stopped.m_gas == 0.0

    def test_start_engine(self, megi_engine_stopped):
        megi_engine_stopped.start_engine()
        assert megi_engine_stopped.is_operational is True

    def test_stop_engine(self, megi_engine):
        megi_engine.stop_engine()
        assert megi_engine.is_operational is False

    def test_update_valid_rpm(self):
        eng = MEGI(type="5G70ME-C-GI Tier III", rpm=50, is_operational=True)
        old_gas = eng.m_gas
        eng.update(70)
        assert eng.rpm == 70
        assert eng.m_gas > old_gas

    def test_update_rpm_below_min_ignored(self):
        eng = MEGI(type="5G70ME-C-GI Tier III", rpm=50, is_operational=True)
        eng.update(30)  # below min of 45
        assert eng.rpm == 50  # unchanged

    def test_update_rpm_above_max_ignored(self):
        eng = MEGI(type="5G70ME-C-GI Tier III", rpm=50, is_operational=True)
        eng.update(80)  # above max of 73
        assert eng.rpm == 50  # unchanged

    def test_rpm_limits(self):
        assert MEGI.rpm_limit == {"min": 45, "max": 73}

    def test_consumption_in_kg_per_second(self, megi_engine):
        """m_gas should be in kg/s (i.e., relatively small number)."""
        assert 0 < megi_engine.m_gas < 5  # reasonable kg/s range


# ═══════════════════════════════════════════════════════════════════════
# DFDE Auxiliary Generator
# ═══════════════════════════════════════════════════════════════════════

class TestDFDE:
    """Tests for the Wärtsilä DFDE generator model."""

    def test_init_w8(self, dfde_w8):
        assert dfde_w8.type == "W8L34DF"
        assert dfde_w8.is_operational is True
        assert dfde_w8.output == 3500
        assert dfde_w8.m_gas > 0

    def test_init_w6(self, dfde_w6):
        assert dfde_w6.type == "W6L34DF"
        assert dfde_w6.output == 2000
        assert dfde_w6.m_gas > 0

    def test_output_limits_w8(self):
        assert DFDE.output_limits["W8L34DF"] == {"min": 1400, "max": 4000}

    def test_output_limits_w6(self):
        assert DFDE.output_limits["W6L34DF"] == {"min": 1000, "max": 3000}

    def test_start_stop(self, dfde_w8):
        dfde_w8.stop_dg()
        assert dfde_w8.is_operational is False
        dfde_w8.start_dg()
        assert dfde_w8.is_operational is True

    def test_update_within_limits(self):
        gen = DFDE(type="W8L34DF", is_operating=True, output=2000)
        gen.update(3000)
        assert gen.output == 3000

    def test_update_outside_limits_ignored(self):
        gen = DFDE(type="W8L34DF", is_operating=True, output=2000)
        gen.update(500)  # below min=1400
        assert gen.output == 2000  # unchanged

    def test_stopped_generator_zero_consumption(self):
        gen = DFDE(type="W8L34DF", is_operating=False, output=3000)
        assert gen.m_gas == 0.0


# ═══════════════════════════════════════════════════════════════════════
# GCU Gas Combustion Unit
# ═══════════════════════════════════════════════════════════════════════

class TestGCU:
    """Tests for the Gas Combustion Unit model."""

    def test_init(self, gcu_unit):
        assert gcu_unit.is_operational is True
        assert gcu_unit.m_gas > 0

    def test_capacity_range(self):
        assert GCU.capacity == {"min": 0, "max": 3300}

    def test_start_stop(self, gcu_unit):
        gcu_unit.stop_gcu()
        assert gcu_unit.is_operational is False
        gcu_unit.start_gcu()
        assert gcu_unit.is_operational is True

    def test_update_valid_rate(self):
        g = GCU(is_operational=True, rate=500)
        g.update(2000)
        expected = per.sec(2000) * True
        assert g.m_gas == pytest.approx(expected)

    def test_update_rate_too_high_ignored(self):
        g = GCU(is_operational=True, rate=500)
        old_gas = g.m_gas
        g.update(4000)  # above max=3300
        assert g.m_gas == pytest.approx(old_gas)  # unchanged

    def test_zero_rate(self):
        g = GCU(is_operational=True, rate=0)
        assert g.m_gas == 0.0

    def test_stopped_gcu_zero_consumption(self):
        g = GCU(is_operational=False, rate=2000)
        assert g.m_gas == 0.0


# ═══════════════════════════════════════════════════════════════════════
# Consumers Aggregator
# ═══════════════════════════════════════════════════════════════════════

class TestConsumers:
    """Tests for the Consumers aggregator."""

    def test_total_consumption_positive(self, consumers_model):
        total = consumers_model.total_consumption()
        assert total > 0

    def test_total_includes_all_machinery(self, consumers_model):
        """Total = sum of genset + main engine + GCU rates."""
        expected = (
            sum(g.m_gas for g in consumers_model.gensets)
            + sum(e.m_gas for e in consumers_model.mainEngines)
            + consumers_model.gcu.m_gas
        )
        assert consumers_model.total_consumption() == pytest.approx(expected)

    def test_all_stopped_zero_consumption(self):
        """If every unit is stopped, total consumption should be zero."""
        m1 = MEGI(type="5G70ME-C-GI Tier III", rpm=65, is_operational=False)
        m2 = MEGI(type="5G70ME-C-GI Tier III", rpm=65, is_operational=False)
        d1 = DFDE(type="W8L34DF", is_operating=False, output=3000)
        d2 = DFDE(type="W6L34DF", is_operating=False, output=2000)
        g = GCU(is_operational=False, rate=1000)
        cons = Consumers([d1, d2], [m1, m2], g)
        assert cons.total_consumption() == 0.0
