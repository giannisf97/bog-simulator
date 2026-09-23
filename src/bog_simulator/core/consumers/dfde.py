"""Wärtsilä Dual-Fuel Diesel Engine (DFDE) auxiliary generator model module."""

from typing import Any

from bog_simulator.physics.thermodynamics import dfde_consumption
from bog_simulator.physics import per

class DFDE:
    """Models a Wärtsilä four-stroke Dual-Fuel Diesel Electric (DFDE) auxiliary generator.

    Supports W6L34DF and W8L34DF engine models with designated electrical output boundaries.

    Attributes:
        output_limits (dict): Min/max electrical power limits in kW per engine type.
        type (str): Engine model designation ('W6L34DF' or 'W8L34DF').
        max_output (float): Maximum continuous power rating [kW].
        min_output (float): Minimum operating power limit [kW].
        is_operational (bool): Generator operating status.
        output (float): Current electrical power output [kW].
        m_gas (float): Fuel gas consumption mass rate [kg/s].
    """
    output_limits: dict[str, dict[str, int]] = {
        "W8L34DF": {"min": 1400, "max": 4000},
        "W6L34DF": {"min": 1000, "max": 3000}
    }

    type: str
    max_output: int | float
    min_output: int | float
    is_operational: bool
    output: int | float
    m_gas: float

    def __init__(self, **genset_params: Any) -> None:
        """Initializes a DFDE generator instance.

        Args:
            **genset_params: Dict containing 'type', 'is_operating', and 'output'.
        """
        config = genset_params or {}

        self.type = config["type"]

        self.max_output = self.output_limits[self.type]["max"]
        self.min_output = self.output_limits[self.type]["min"]

        self.is_operational = config["is_operating"]
        self.update(config["output"])

    def start_dg(self) -> None:
        """Starts the diesel generator set."""
        self.is_operational = True

    def stop_dg(self) -> None:
        """Stops the diesel generator set."""
        self.is_operational = False

    def update(self, output: float | int) -> None:
        """Updates electrical power output and recalculates fuel gas consumption.

        Args:
            output (float | int): Generator electrical output [kW].
        """
        if  self.min_output <= output <= self.max_output: 
            self.output = output
            m_gas_new = self.is_operational * dfde_consumption(self.type, output)
            self.m_gas = per.sec(m_gas_new)



if __name__ == '__main__':
    generator_parameters = {
        "type": 'W8L34DF',
        "is_operating": False,
        "output": 3500
    }
    dfde = DFDE(**generator_parameters)
    print(per.hour(dfde.m_gas))