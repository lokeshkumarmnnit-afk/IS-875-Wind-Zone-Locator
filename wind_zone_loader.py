import json
from pathlib import Path
from shapely.geometry import shape

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "is875_wind_zones.geojson"

class WindZoneEngine:
    def __init__(self):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            geojson = json.load(f)

        self.zones = []
        for feature in geojson["features"]:
            props = feature["properties"]

            self.zones.append({
                "geometry": shape(feature["geometry"]),
                "zone": props["Zone"],   # <-- matches QGIS
                "Vb": props["Vb"]        # <-- matches QGIS
            })