import json
from pathlib import Path
from shapely.geometry import shape, Point
from shapely.ops import nearest_points
from math import radians, sin, cos, sqrt, atan2

# -------------------------------------------------
# Configuration (LOCKED)
# -------------------------------------------------
DATA_PATH = Path(__file__).parent / "data" / "is875_wind_zones.geojson"
BOUNDARY_THRESHOLD_KM = 20.0
EARTH_RADIUS_KM = 6371.0


# -------------------------------------------------
# Utilities
# -------------------------------------------------
def haversine_km(lat1, lon1, lat2, lon2):
    """
    Great-circle distance between two points on Earth.
    """
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * atan2(sqrt(a), sqrt(1 - a))


# -------------------------------------------------
# Core Engine
# -------------------------------------------------
class WindZoneEngine:
    """
    IS 875 (Part 3):2015 Wind Zone Engine
    """

    def __init__(self):
        if not DATA_PATH.exists():
            raise RuntimeError("IS 875 wind zone GeoJSON file not found")

        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.zones = []

        for feature in data.get("features", []):
            props = feature.get("properties", {})

            # Hard validation (fail fast)
            if "Zone" not in props or "Vb" not in props:
                raise RuntimeError(
                    f"Invalid GeoJSON schema. Required fields: 'Zone', 'Vb'. "
                    f"Found: {props}"
                )

            self.zones.append({
                "zone": props["Zone"],      # II, III, IV, V
                "Vb": float(props["Vb"]),   # 39, 44, 47, 50
                "geometry": shape(feature["geometry"])
            })

        if not self.zones:
            raise RuntimeError("No wind zones loaded from GeoJSON")

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------
    def lookup(self, lat: float, lon: float):
        point = Point(lon, lat)

        containing_zone = None
        nearest_zone = None
        min_distance_km = None

        # ---------------------------------------------
        # Step 1: Find containing zone
        # ---------------------------------------------
        for z in self.zones:
            if z["geometry"].contains(point):
                containing_zone = z
                break

        if containing_zone is None:
            raise ValueError(
                "Location does not fall inside any IS 875 wind zone polygon"
            )

        # ---------------------------------------------
        # Step 2: Distance to nearest ADJACENT zone
        # ---------------------------------------------
        for z in self.zones:
            # Skip same zone
            if z["zone"] == containing_zone["zone"]:
                continue

            geom = z["geometry"]
            nearest_pt = nearest_points(point, geom)[1]

            dist_km = haversine_km(
                lat,
                lon,
                nearest_pt.y,
                nearest_pt.x
            )

            if min_distance_km is None or dist_km < min_distance_km:
                min_distance_km = dist_km
                nearest_zone = z

        # ---------------------------------------------
        # Step 3: IS 875 conservative rule
        # ---------------------------------------------
        adopted_zone = containing_zone
        decision_reason = "Point lies within wind zone."

        if (
            min_distance_km is not None
            and min_distance_km <= BOUNDARY_THRESHOLD_KM
            and nearest_zone["Vb"] > containing_zone["Vb"]
        ):
            adopted_zone = nearest_zone
            decision_reason = (
                f"Location lies within {BOUNDARY_THRESHOLD_KM:.0f} km of a "
                "higher wind-zone boundary. Higher basic wind speed adopted "
                "as per IS 875 (Part 3):2015."
            )

        return {
            "zone": adopted_zone["zone"],
            "Vb": adopted_zone["Vb"],
            "distance_to_boundary_km": round(min_distance_km, 2),
            "nearest_zone": nearest_zone["zone"] if nearest_zone else None,
            "decision_reason": decision_reason,
            "ref": "IS 875 (Part 3):2015, Fig. 1"
        }


# -------------------------------------------------
# Singleton Engine (NO reload issues)
# -------------------------------------------------
_ENGINE = WindZoneEngine()


def get_wind_zone(lat: float, lon: float):
    return _ENGINE.lookup(lat, lon)