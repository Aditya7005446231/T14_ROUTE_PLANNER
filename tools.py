"""
tools.py - Mock Dataset and LangChain Tools for T14 Multi-Stop Route Planner.

This module provides mock distance lookup data for major Indian tourist cities
(Delhi, Agra, Jaipur, Chandigarh, Amritsar) and defines `@tool` decorated functions
for tool-calling agents to query distances and commit optimized travel itineraries into state.
"""

from typing import Union, List
from langchain_core.tools import tool

# Mock distance dictionary storing driving distances in kilometers between Indian cities
CITY_DISTANCES = {
    ("delhi", "agra"): 233,
    ("delhi", "jaipur"): 280,
    ("delhi", "chandigarh"): 244,
    ("delhi", "amritsar"): 450,
    ("agra", "jaipur"): 240,
    ("agra", "chandigarh"): 440,
    ("agra", "amritsar"): 650,
    ("jaipur", "chandigarh"): 510,
    ("jaipur", "amritsar"): 700,
    ("chandigarh", "amritsar"): 228,
}

# Global session state container to retain committed routes
SAVED_ROUTES: List[List[str]] = []


def _find_distance(city_a: str, city_b: str) -> Union[int, None]:
    """Helper to look up bidirectional distance between two cities in CITY_DISTANCES dictionary."""
    ca, cb = city_a.strip().lower(), city_b.strip().lower()
    if ca == cb:
        return 0
    return CITY_DISTANCES.get((ca, cb)) or CITY_DISTANCES.get((cb, ca))


@tool
def get_distance(a: str, b: str) -> str:
    """Look up driving distance (in kilometers) between two cities.

    Args:
        a: Name of the first city (e.g., 'Delhi').
        b: Name of the second city (e.g., 'Agra').

    Returns:
        A string message containing the distance in km, or error message if city pair is not in database.
    """
    distance = _find_distance(a, b)
    if distance is None:
        return f"Distance lookup failed: Unknown distance between '{a}' and '{b}'. Available cities: Delhi, Agra, Jaipur, Chandigarh, Amritsar."
    if distance == 0:
        return f"'{a}' and '{b}' are the same city (distance: 0 km)."
    
    return f"Driving distance between {a.strip().title()} and {b.strip().title()} is {distance} km."


@tool
def order_stops(route: Union[List[str], str]) -> str:
    """Commit and save an optimized visiting order of stops into session state.

    Args:
        route: A list of city names in visiting order (e.g., ['Delhi', 'Agra', 'Jaipur']), 
               or a comma-separated string of city names.

    Returns:
        Confirmation string indicating the route has been saved to session state.
    """
    if isinstance(route, str):
        # Handle cases where LLM passes comma/arrow separated string instead of list
        stops = [s.strip().title() for s in route.replace("->", ",").split(",") if s.strip()]
    elif isinstance(route, list):
        stops = [str(s).strip().title() for s in route if str(s).strip()]
    else:
        return "Error: Invalid route format. Route must be a list of city names or a string."

    if not stops:
        return "Error: Cannot commit an empty route."

    SAVED_ROUTES.append(stops)
    formatted_route = " -> ".join(stops)
    return f"Successfully committed optimized route to session state: [{formatted_route}]."


def get_saved_routes() -> List[List[str]]:
    """Helper function to retrieve all saved routes from session state."""
    return SAVED_ROUTES.copy()


def clear_saved_routes() -> None:
    """Helper function to reset session state."""
    SAVED_ROUTES.clear()
