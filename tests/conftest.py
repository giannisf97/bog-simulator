"""Shared pytest fixtures for BOG Simulator test suite.

Provides reusable fixtures for Environment, MembraneTank, consumer models,
and the full LNGc vessel, all constructed from real project data files.
"""

import pytest
import pandas as pd

from bog_simulator.utils import data_loader
from bog_simulator.core.environment import Environment
from bog_simulator.core import tank as tnk
from bog_simulator.core.consumers.megi import MEGI
from bog_simulator.core.consumers.dfde import DFDE
from bog_simulator.core.consumers.gcu import GCU
from bog_simulator.core.consumers import consumer
from bog_simulator.core.vessel import LNGc


# ── Data Fixtures ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def vessel_config():
    """Loads the TOML vessel configuration once for the entire test session."""
    return data_loader.load_vessel_data()


@pytest.fixture(scope="session")
def weather_df():
    """Loads the weather CSV once for the entire test session."""
    return data_loader.load_weather_variables()


@pytest.fixture(scope="session")
def boiling_df():
    """Loads the methane saturation boiling curve once per session."""
    return data_loader.load_boiling_points()


@pytest.fixture(scope="session")
def calibration_table_1():
    """Loads the calibration table for Tank 1 once per session."""
    return data_loader.load_calibration_table(1)


# ── Model Fixtures ─────────────────────────────────────────────────────

@pytest.fixture
def environment(vessel_config, weather_df):
    """Creates a fresh Environment instance.

    Resets the class-level counter to 0 before each test to avoid
    cross-test pollution from the class variable `ic`.
    """
    Environment.ic = 0
    return Environment(vessel_config["vessel"], weather_df)


@pytest.fixture
def sample_tank(vessel_config, environment):
    """Creates a single MembraneTank (Tank 1) for unit testing."""
    tank_params = vessel_config["tanks"][0]
    return tnk.MembraneTank(tank_params, environment)


@pytest.fixture
def megi_engine():
    """Creates an operational ME-GI engine at 65 RPM."""
    return MEGI(type="5G70ME-C-GI Tier III", rpm=65, is_operational=True)


@pytest.fixture
def megi_engine_stopped():
    """Creates a stopped ME-GI engine at 65 RPM."""
    return MEGI(type="5G70ME-C-GI Tier III", rpm=65, is_operational=False)


@pytest.fixture
def dfde_w8():
    """Creates an operational W8L34DF DFDE generator at 3500 kW."""
    return DFDE(type="W8L34DF", is_operating=True, output=3500)


@pytest.fixture
def dfde_w6():
    """Creates an operational W6L34DF DFDE generator at 2000 kW."""
    return DFDE(type="W6L34DF", is_operating=True, output=2000)


@pytest.fixture
def gcu_unit():
    """Creates an operational GCU at 1000 kg/h."""
    return GCU(is_operational=True, rate=1000)


@pytest.fixture
def consumers_model(dfde_w8, dfde_w6, megi_engine, megi_engine_stopped, gcu_unit):
    """Creates a Consumers aggregator with mixed operational states."""
    return consumer.Consumers(
        genSets=[dfde_w8, dfde_w6],
        mainEngines=[megi_engine, megi_engine_stopped],
        gcu=gcu_unit,
    )


@pytest.fixture
def lngc_vessel(vessel_config, weather_df):
    """Creates a full LNGc vessel model from real configuration data.

    Resets class-level state to avoid pollution between tests.
    """
    from bog_simulator.core.consumers import megi as megi_mod, dfde as dfde_mod, gcu as gcu_mod

    Environment.ic = 0
    LNGc.internal_timer = 0

    megis = [megi_mod.MEGI(**p) for p in vessel_config["Main_Engines"]]
    dfdes = [dfde_mod.DFDE(**p) for p in vessel_config["Diesel_Generators"]]
    gcu_inst = gcu_mod.GCU(**vessel_config["Gcu"])
    env = Environment(vessel_config["vessel"], weather_df)
    cons = consumer.Consumers(dfdes, megis, gcu_inst)
    return LNGc(vessel_config["tanks"], env, cons, 0)
