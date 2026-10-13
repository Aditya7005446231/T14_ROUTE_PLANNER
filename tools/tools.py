"""
tools.py - Geoapify API Integration & LangChain Tools for T14 Multi-Stop Route Planner.

This module provides live geocoding & routing distance lookup via Geoapify API,
with a fallback mock dataset for offline usage. It defines `@tool` functions
for tool-calling agents to query distances and commit itineraries into session state.
"""

import os
from typing import Union, List, Optional, Dict
import requests
from langchain_core.tools import tool

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY", "f34e70b761bc4aec93741d15dc543138")

# Mock distance dictionary storing driving distances in kilometers between Indian cities (fallback)
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


def geocode_location(location_name: str) -> Optional[Dict]:
    """Geocode a address/city string using Geoapify API to obtain coordinates (lat, lon)."""
    api_key = os.getenv("GEOAPIFY_API_KEY", GEOAPIFY_API_KEY)
    if not api_key:
        return None
    
    url = f"https://api.geoapify.com/v1/geocode/search?text={requests.utils.quote(location_name)}&apiKey={api_key}"
    headers = {"Accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            features = data.get("features", [])
            if features:
                coords = features[0]["geometry"]["coordinates"]  # [lon, lat]
                formatted = features[0]["properties"].get("formatted", location_name)
                return {
                    "lat": coords[1],
                    "lon": coords[0],
                    "formatted": formatted
                }
    except Exception:
        pass
    return None


def get_geoapify_distance(location_a: str, location_b: str) -> Optional[Dict]:
    """Calculate real-world driving distance (in km) and travel time between two locations using Geoapify Routing API."""
    loc_a = geocode_location(location_a)
    loc_b = geocode_location(location_b)
    
    if not loc_a or not loc_b:
        return None
    
    api_key = os.getenv("GEOAPIFY_API_KEY", GEOAPIFY_API_KEY)
    waypoints = f"{loc_a['lat']},{loc_a['lon']}|{loc_b['lat']},{loc_b['lon']}"
    url = f"https://api.geoapify.com/v1/routing?waypoints={waypoints}&mode=drive&apiKey={api_key}"
    
    try:
        resp = requests.get(url, headers={"Accept": "application/json"}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            features = data.get("features", [])
            if features:
                props = features[0].get("properties", {})
                distance_meters = props.get("distance", 0)
                time_seconds = props.get("time", 0)
                
                distance_km = round(distance_meters / 1000, 1)
                hours = int(time_seconds // 3600)
                minutes = int((time_seconds % 3600) // 60)
                duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes} mins"
                
                return {
                    "distance_km": distance_km,
                    "duration": duration_str,
                    "loc_a": loc_a["formatted"],
                    "loc_b": loc_b["formatted"]
                }
    except Exception:
        pass
    return None


def _find_distance(city_a: str, city_b: str) -> Union[int, None]:
    """Helper to look up bidirectional distance between two cities in fallback CITY_DISTANCES dictionary."""
    ca, cb = city_a.strip().lower(), city_b.strip().lower()
    if ca == cb:
        return 0
    return CITY_DISTANCES.get((ca, cb)) or CITY_DISTANCES.get((cb, ca))


@tool
def geocode_address(address: str) -> str:
    """Geocode any address or city name worldwide using Geoapify API to get latitude, longitude, and formatted location.

    Args:
        address: Full or partial location/address string (e.g., '38 Upper Montagu Street, Westminster W1H 1LJ, UK').

    Returns:
        String with coordinates and formatted location details.
    """
    res = geocode_location(address)
    if not res:
        return f"Geocoding lookup failed for address: '{address}'."
    return f"Location: {res['formatted']} | Coordinates: ({res['lat']}, {res['lon']}) [via Geoapify]"


@tool
def get_distance(a: str, b: str) -> str:
    """Look up driving distance (in kilometers) between two locations or cities.

    Args:
        a: Name of the first location/city (e.g., 'Delhi' or '38 Upper Montagu Street, London').
        b: Name of the second location/city (e.g., 'Agra' or 'Oxford').

    Returns:
        A string message containing driving distance in km and travel duration.
    """
    ca, cb = a.strip(), b.strip()
    if ca.lower() == cb.lower():
        return f"'{a}' and '{b}' are the same location (distance: 0 km)."

    # 1. Try real-time Geoapify API distance & routing
    geo_res = get_geoapify_distance(ca, cb)
    if geo_res:
        return (
            f"Driving distance between '{geo_res['loc_a']}' and '{geo_res['loc_b']}' "
            f"is {geo_res['distance_km']} km (Est. driving time: {geo_res['duration']}) [via Geoapify]."
        )
    
    # 2. Fallback to mock dataset if Geoapify lookup fails or offline
    distance = _find_distance(ca, cb)
    if distance is None:
        return f"Distance lookup failed: Could not determine distance between '{a}' and '{b}'."
    if distance == 0:
        return f"'{a}' and '{b}' are the same city (distance: 0 km)."
    
    return f"Driving distance between {ca.title()} and {cb.title()} is {distance} km (Mock Data)."


def _save_route(route: Union[List[str], str]) -> str:
    """Helper to commit and save a visiting route sequence into session state."""
    if isinstance(route, str):
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


@tool
def order_stops(route: Union[List[str], str]) -> str:
    """Commit and save an optimized visiting order of stops into session state.

    Args:
        route: A list of city names in visiting order (e.g., ['Delhi', 'Agra', 'Jaipur']), 
               or a comma-separated string of city names.

    Returns:
        Confirmation string indicating the route has been saved to session state.
    """
    return _save_route(route)


def get_saved_routes() -> List[List[str]]:
    """Helper function to retrieve all saved routes from session state."""
    return SAVED_ROUTES.copy()


def clear_saved_routes() -> None:
    """Helper function to reset session state."""
    SAVED_ROUTES.clear()


def compute_optimal_route(origin: str, stops: List[str]) -> Dict:
    """Compute road distances and durations for a multi-stop route starting from origin.

    Args:
        origin: Starting city/location.
        stops: List of destination stops.

    Returns:
        Dict with route legs, total km, and formatted route sequence.
    """
    cleaned_origin = origin.strip()
    cleaned_stops = [s.strip() for s in stops if s.strip()]
    all_locations = [cleaned_origin] + cleaned_stops

    if len(all_locations) < 2:
        return {"legs": [], "total_km": 0, "route_str": cleaned_origin}

    legs = []
    total_km = 0.0

    for i in range(len(all_locations) - 1):
        loc_a = all_locations[i]
        loc_b = all_locations[i + 1]
        geo_info = get_geoapify_distance(loc_a, loc_b)

        if geo_info:
            dist_km = geo_info["distance_km"]
            duration = geo_info["duration"]
            name_a = geo_info["loc_a"]
            name_b = geo_info["loc_b"]
        else:
            dist = _find_distance(loc_a, loc_b) or 0
            dist_km = float(dist)
            duration = "N/A"
            name_a = loc_a.title()
            name_b = loc_b.title()

        legs.append({
            "from": name_a,
            "to": name_b,
            "distance_km": dist_km,
            "duration": duration,
        })
        total_km += dist_km

    _save_route(all_locations)

    return {
        "legs": legs,
        "total_km": round(total_km, 1),
        "route_str": " ➔ ".join([loc.title() for loc in all_locations]),
    }


