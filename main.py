from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from wind_calc import wind_calc
import os

app = FastAPI(
    title="IS 875 Wind Design App",
    description="Wind zone and design wind speed as per IS 875 (Part 3):2015",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# --------------------------------
# API: Wind calculation
# --------------------------------
@app.post("/wind-calc")
def calculate_wind(payload: dict):
    """
    Input:
    {
      "city": "Ahmedabad",
      "district": "Ahmedabad",
      "state": "Gujarat"
    }

    Output:
    - Latitude & Longitude
    - Wind Zone
    - Basic Wind Speed (Vb)
    - Boundary distance
    - IS 875 justification
    """
    try:
        return wind_calc(payload)

    except ValueError as e:
        # Input / data issue (safe to expose)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Internal error (do NOT expose stack trace)
        raise HTTPException(
            status_code=500,
            detail="Internal error while computing wind data"
        )


# --------------------------------
# API: Serve wind zone GeoJSON
# --------------------------------
@app.get("/wind-zones")
def get_wind_zones():
    """
    Returns IS 875 wind zone polygons (GeoJSON)
    Used by frontend map overlay
    """
    geojson_path = os.path.join(BASE_DIR, "data", "is875_wind_zones.geojson")

    if not os.path.exists(geojson_path):
        raise HTTPException(
            status_code=500,
            detail="Wind zone GeoJSON file not found"
        )

    return FileResponse(
        path=geojson_path,
        media_type="application/geo+json",
        filename="is875_wind_zones.geojson"
    )


# --------------------------------
# UI: Serve interactive map page
# --------------------------------
@app.get("/map", response_class=HTMLResponse)
def show_map():
    """
    Interactive map showing:
    - Location pin
    - IS 875 wind zones
    """
    map_path = os.path.join(BASE_DIR, "map.html")

    if not os.path.exists(map_path):
        raise HTTPException(
            status_code=500,
            detail="map.html not found"
        )

    return FileResponse(map_path)


# --------------------------------
# Root endpoint (health check)
# --------------------------------
@app.get("/")
def root():
    return {
        "status": "running",
        "app": "IS 875 Wind Design App",
        "standard": "IS 875 (Part 3):2015",
        "endpoints": {
            "POST /wind-calc": "Calculate wind zone & Vb",
            "GET /wind-zones": "IS 875 wind zone GeoJSON",
            "GET /map": "Interactive map view",
            "GET /docs": "Swagger API documentation"
        }
    }