"""MAN B&W ME-GI main propulsion engine model module."""

from typing import Any

from bog_simulator.physics.thermodynamics import megi_consumption
from bog_simulator.physics import per

class MEGI:
    """Models a MAN B&W ME-GI two-stroke high-pressure dual-fuel main engine.

    Attributes:
        rpm_limit (dict): Operating shaft speed boundaries {"min": 45, "max": 73} [RPM].
        type (str): Specific engine designation string.
        is_operational (bool): Operating status (True if running, False if stopped).
        rpm (float | int): Current shaft speed [RPM].
        m_gas (float): Fuel gas consumption mass rate [kg/s].
    """
    rpm_limit: dict[str, int] = {
        "min": 45,
        "max": 73
    }

    type: str
    is_operational: bool
    rpm: float | int
    m_gas: float

    def __init__(self, **megi_config: Any) -> None:
        """Initializes the ME-GI engine model.

        Args:
            **megi_config: Keyword arguments containing 'type', 'is_operational', and 'rpm'.
        """
        config = megi_config or {}

        self.type = config["type"]
        self.is_operational = config["is_operational"]
        self.update(config["rpm"])

    def start_engine(self) -> None:
        """Starts the engine, enabling fuel gas consumption."""
        self.is_operational = True

    def stop_engine(self) -> None:
        """Stops the engine, setting effective consumption to zero."""
        self.is_operational = False

    def update(self, rpm: float | int) -> None:
        """Updates engine RPM and recalculates instantaneous fuel gas consumption.

        Args:
            rpm (float | int): Desired engine shaft speed [RPM].
        """
        if self.rpm_limit["max"] >= rpm >= self.rpm_limit["min"]:
            self.rpm = rpm
            m_gas_new = per.sec(megi_consumption(self.rpm))
            self.m_gas = self.is_operational * m_gas_new

#testing
if __name__ == "__main__":
    megi_test = MEGI(type="5G70ME-C-GI Tier III", rpm=65, is_operational=True)
    print(megi_test.m_gas)