import numpy as np

def cofferdam_subArea(level : type[float | int] , geometry : dict) -> float:
    '''Calculates the submerged area of LNG coming in contact with 
    cofferdam space.'''
    if level > geometry["height"] - geometry["h1"]:
        return 2 * (level * geometry["breadth"] - pow(geometry["h2"],2) - (level - (geometry["height"] - geometry["h1"])))
    elif level > geometry["h2"]:
        return 2 * (level * geometry["breadth"] - pow(geometry["h2"], 2))
    else:
        return 2 * (pow(level, 2) + level * geometry["breadth"] - geometry["h2"])
    

def sea_subArea(level : float, draft : float, geometry : dict) -> float:
    '''Calculates the submerged area of LNG coming in contact with the sea'''
    if level > geometry["h2"]:
        if draft - 3.2 < level:
            return geometry["breadth"] * (2 * geometry["h2"] * (np.sqrt(2)-2) + geometry["breadth"] + 2 * (draft - 3.2))
        else:
            return geometry["length"] * (geometry["breadth"] + 2 * geometry["h2"] * (np.sqrt(2) - 2) + 2 * level)
    else:
        return geometry["length"] * (geometry["breadth"] - 2 * geometry["h2"]) + (4/np.sqrt(2)) * geometry["length"] * level
     
def air_subArea(level : float, draft : float, geometry : dict) -> float:
    '''Calculates the submerged area of LNG coming in contact with air'''
    if level > geometry["height"] - geometry["h1"]:
        return 2 * geometry["length"] * ((geometry["height"] - geometry["h1"]) - (draft - 3.2)) + (4/np.sqrt(2)) * geometry["length"] * (
                level-(geometry["height"] - geometry["h1"]))
    elif level > (draft - 3.2):
        return 2 * geometry["length"] * ((geometry["height"] - geometry["h1"]) - (draft - 3.2))
    else:
        return 0.0

def submerged_area(l_level: float, draft: float, tank_geometry: dict) -> dict:
        '''Calculates the submerged area coming in contact with the enviroment'''
        A_submerged = {"A_coff" : cofferdam_subArea(l_level, tank_geometry),
                       "A_sea" : sea_subArea(l_level, draft, tank_geometry),
                       "A_air" : air_subArea(l_level, draft, tank_geometry)}
            
        return A_submerged

def ssf(sea_state : int, voyage : str ) -> float:
    '''Calculates the Sloshing Scaling Factor linearly based on BN'''
    if voyage == "L": #if is 'L'aden
        return 1.0 + 0.03 * sea_state
    else: # if is 'B'allast
        return 1.0 + 0.05 * sea_state