from location_lookup import get_location
from wind_zone_lookup import get_wind_zone
from clauses import calc_design_wind


def wind_calc(payload: dict):
    # -------------------------------
    # Location resolution (SAFE)
    # -------------------------------
    location = get_location(
        city=payload.get("city"),
        district=payload.get("district"),
        state=payload.get("state"),
        lat=payload.get("lat"),
        lon=payload.get("lon")
    )

    # -------------------------------
    # Wind zone lookup
    # -------------------------------
    wind_zone = get_wind_zone(
        location["lat"],
        location["lon"]
    )

    # -------------------------------
    # Design wind calculation
    # -------------------------------
    wind_result = calc_design_wind(
        Vb=wind_zone["Vb"],
        k1=payload.get("k1", 1.0),
        k2=payload.get("k2", 1.0),
        k3=payload.get("k3", 1.0),
        k4=payload.get("k4", 1.0)
    )

    return {
        "location": {
            "latitude": location["lat"],
            "longitude": location["lon"]
        },
        "wind_zone": wind_zone,
        "wind": wind_result
    }