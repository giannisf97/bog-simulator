"""Gas Combustion Unit (GCU) model module."""

from typing import Any

from bog_simulator.physics import per

class GCU:
    """Models a marine Gas Combustion Unit (GCU) for thermal oxidation of excess BOG.

    Attributes:
        capacity (dict): Combustion capacity range {"min": 0, "max": 3300} [kg/h].
        is_operational (bool): Combustion unit operating state.
        m_gas (float): Mass burning rate of fuel gas [kg/s].
    """
    capacity: dict[str, int] = {"min": 0, "max": 3300}

    is_operational: bool
    m_gas: float
    
    def __init__(self, **gcu_parameters: Any) -> None:
        """Initializes a GCU model instance.

        Args:
            **gcu_parameters: Dict containing 'is_operational' and burning 'rate' in kg/h.
        """
        config = gcu_parameters or {}
        self.is_operational = config["is_operational"]
        self.update(config["rate"]) 

    def start_gcu(self) -> None:
        """Activates the gas combustion burner."""
        self.is_operational = True

    def stop_gcu(self) -> None:
        """Deactivates the gas combustion burner."""
        self.is_operational = False

    def update(self, rate: float | int) -> None:
        """Updates the gas combustion rate.

        Args:
            rate (float | int): Gas combustion mass flow rate [kg/h] (0 to 3,300 kg/h).
        """
        if self.capacity["max"] >= rate >= self.capacity["min"]:
            m_gas_new = per.sec(rate)
            self.m_gas = m_gas_new * self.is_operational