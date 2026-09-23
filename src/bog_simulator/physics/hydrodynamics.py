"""Hydrodynamics and cargo tank geometry module.

This module models the geometry of membrane containment tanks (including upper and
lower corner chamfers conforming to the double hull) to analytically compute wetted
contact surface areas with sea, atmospheric air, and cofferdams, as well as the
sloshing amplification scaling factor (SSF).
"""

import numpy as np

def cofferdam_subArea(level: float | int, geometry: dict[str, float]) -> float:
    """Calculates the submerged/wetted surface area of LNG contacting cofferdam bulkheads.

    Accounts for the polygonal cross-section of membrane tanks with upper (h1) and
    lower (h2) corner chamfers across fore and aft transverse bulkheads.

    Args:
        level (float | int): Instantaneous liquid LNG sounding height [m].
        geometry (dict): Tank geometric dimensions containing:
            - 'height': Total tank height [m]
            - 'breadth': Tank breadth [m]
            - 'h1': Upper hopper corner chamfer height [m]
            - 'h2': Lower bilge corner chamfer height [m]

    Returns:
        float: Total submerged bulkhead surface area in contact with cofferdam spaces [m^2].
    """
    if level > geometry["height"] - geometry["h1"]:
        return 2 * (level * geometry["breadth"] - pow(geometry["h2"],2) - (level - (geometry["height"] - geometry["h1"])))
    elif level > geometry["h2"]:
        return 2 * (level * geometry["breadth"] - pow(geometry["h2"], 2))
    else:
        return 2 * (pow(level, 2) + level * geometry["breadth"] - geometry["h2"])
    

def sea_subArea(level: float | int, draft: float | int, geometry: dict[str, float]) -> float:
    """Calculates the submerged cargo tank surface area in thermal contact with seawater.

    Considers whether the liquid level is below or above the effective waterline
    (draft minus double-bottom height offset of ~3.2m), including bilge hopper slopes.

    Args:
        level (float): Liquid sounding level in the tank [m].
        draft (float): Ship draft waterline [m].
        geometry (dict): Tank geometry dict ('length', 'breadth', 'h2', etc.).

    Returns:
        float: Wetted tank boundary area in contact with seawater [m^2].
    """
    if level > geometry["h2"]:
        if draft - 3.2 < level:
            return geometry["breadth"] * (2 * geometry["h2"] * (np.sqrt(2)-2) + geometry["breadth"] + 2 * (draft - 3.2))
        else:
            return geometry["length"] * (geometry["breadth"] + 2 * geometry["h2"] * (np.sqrt(2) - 2) + 2 * level)
    else:
        return geometry["length"] * (geometry["breadth"] - 2 * geometry["h2"]) + (4/np.sqrt(2)) * geometry["length"] * level
     
def air_subArea(level: float | int, draft: float | int, geometry: dict[str, float]) -> float:
    """Calculates the submerged cargo tank surface area in contact with ambient air.

    Evaluates wetted tank sides extending above the ship draft waterline into the
    atmospheric freeboard and top wing spaces.

    Args:
        level (float): Liquid sounding level in the tank [m].
        draft (float): Ship draft waterline [m].
        geometry (dict): Tank geometry dict ('length', 'height', 'h1', etc.).

    Returns:
        float: Wetted tank boundary area in contact with ambient air [m^2].
    """
    if level > geometry["height"] - geometry["h1"]:
        return 2 * geometry["length"] * ((geometry["height"] - geometry["h1"]) - (draft - 3.2)) + (4/np.sqrt(2)) * geometry["length"] * (
                level-(geometry["height"] - geometry["h1"]))
    elif level > (draft - 3.2):
        return 2 * geometry["length"] * ((geometry["height"] - geometry["h1"]) - (draft - 3.2))
    else:
        return 0.0

def submerged_area(l_level: float | int, draft: float | int, tank_geometry: dict[str, float]) -> dict[str, float]:
    """Calculates the complete breakdown of wetted surface areas across all boundaries.

    Args:
        l_level (float): Liquid LNG sounding level [m].
        draft (float): Ship draft waterline [m].
        tank_geometry (dict): Geometric dimension specifications of the tank.

    Returns:
        dict: Submerged areas {'A_coff': float, 'A_sea': float, 'A_air': float} in [m^2].
    """
    A_submerged = {"A_coff" : cofferdam_subArea(l_level, tank_geometry),
                   "A_sea" : sea_subArea(l_level, draft, tank_geometry),
                   "A_air" : air_subArea(l_level, draft, tank_geometry)}
        
    return A_submerged

def ssf(sea_state : int, voyage : str ) -> float:
    """Calculates the Sloshing Scaling Factor (SSF) based on sea state and voyage loading.

    Linear empirical scaling factor that accounts for fluid motion, destruction of
    thermal boundary layers, and sloshing splashing on warm upper insulation walls.
    Ballast voyages exhibit higher sloshing amplification due to lower liquid filling
    ratios and unrestricted free-surface wave development.

    Args:
        sea_state (int): Beaufort wind force / sea state number (BN 0 to 12).
        voyage (str): Voyage loading condition ('L' for Laden, 'B' for Ballast).

    Returns:
        float: Sloshing Scaling Factor (SSF >= 1.0) dimensionless multiplier.
    """
    if voyage == "L": #if is 'L'aden
        return 1.0 + 0.03 * sea_state
    else: # if is 'B'allast
        return 1.0 + 0.05 * sea_state