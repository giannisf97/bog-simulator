"""Fuel gas consumers aggregator module.

Collects and sums the instantaneous fuel gas consumption across all active propulsion
engines, electrical generators, and thermal combustion units.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bog_simulator.core.consumers.dfde import DFDE
    from bog_simulator.core.consumers.megi import MEGI
    from bog_simulator.core.consumers.gcu import GCU

class Consumers:
    """Aggregates all fuel gas consuming machinery on board the LNG carrier.

    Attributes:
        gensets (list[DFDE]): List of auxiliary diesel generator set models.
        mainEngines (list[MEGI]): List of main propulsion engine models.
        gcu (GCU): Gas Combustion Unit model instance.
    """
    gensets: list["DFDE"]
    mainEngines: list["MEGI"]
    gcu: "GCU"

    def __init__(self, genSets: list["DFDE"], mainEngines: list["MEGI"], gcu: "GCU") -> None:
        """Initializes the Consumers manager.

        Args:
            genSets (list): List of DFDE generator instances.
            mainEngines (list): List of MEGI main engine instances.
            gcu (GCU): Gas Combustion Unit instance.
        """
        self.gensets = genSets
        self.mainEngines = mainEngines
        self.gcu = gcu
    
    def total_consumption(self) -> float:
        """Calculates aggregate fuel gas consumption rate across all active machinery.

        Returns:
            float: Total fuel gas mass flow rate consumed [kg/s].
        """
        total_cons: float = 0.0
        for genset in self.gensets:
            total_cons += genset.m_gas
        for mainEngine in self.mainEngines:
            total_cons += mainEngine.m_gas
        total_cons += self.gcu.m_gas
        return total_cons