from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from functools import lru_cache

# Single geolocator instance (do NOT recreate per request)
_geolocator = Nominatim(
    user_agent="is875_wind_design_app",
    timeout=5
)


@lru_cache(maxsize=1000)
def _geocode_cached(query: str):
    """
    Cached geocoding call.
    Prevents repeated external requests for same city.
    """
    try:
        return _geolocator.geocode(query)
    except (GeocoderTimedOut, GeocoderUnavailable):
        return None


def get_location(
    city: str | None = None,
    district: str | None = None,
    state: str | None = None,
    lat: float | None = None,
    lon: float | None = None
):
    """
    Production-safe location resolver.

    Priority:
    1. If lat & lon are provided → use directly (NO external calls)
    2. Else resolve city/district/state using geopy (cached)

    Returns:
    {
        "lat": float,
        "lon": float
    }
    """

    # --------------------------------
    # Path 1: Direct coordinates (BEST)
    # --------------------------------
    if lat is not None and lon is not None:
        return {
            "lat": float(lat),
            "lon": float(lon)
        }

    # --------------------------------
    # Path 2: City-based lookup
    # --------------------------------
    if not (city and district and state):
        raise ValueError(
            "Either provide lat/lon OR city, district, and state"
        )

    query = f"{city}, {district}, {state}, India"

    location = _geocode_cached(query)

    if location is None:
        raise ValueError(
            "Unable to resolve location. "
            "Geocoding service unavailable or invalid city. "
            "Provide lat/lon instead."
        )

    return {
        "lat": location.latitude,
        "lon": location.longitude
    }