"""Public APIs: geocode US addresses and look up FEMA flood zones."""

from __future__ import annotations

import httpx

CENSUS_GEOCODER = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
NFHL_QUERY = (
    "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/28/query"
)


def geocode_us_address(location: str, timeout: float = 8.0) -> dict[str, float] | None:
    """Return lat/lon for a one-line US address via Census Geocoder."""
    params = {
        "address": location,
        "benchmark": "Public_AR_Current",
        "format": "json",
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.get(CENSUS_GEOCODER, params=params)
        resp.raise_for_status()
        matches = resp.json().get("result", {}).get("addressMatches", [])
    if not matches:
        return None
    coords = matches[0].get("coordinates", {})
    if "y" not in coords or "x" not in coords:
        return None
    return {"latitude": float(coords["y"]), "longitude": float(coords["x"])}


def lookup_flood_zone(latitude: float, longitude: float, timeout: float = 8.0) -> dict[str, str] | None:
    """Return FEMA NFHL flood zone code for a point (lon, lat)."""
    params = {
        "where": "1=1",
        "geometry": f"{longitude},{latitude}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "FLD_ZONE,ZONE_SUBTY",
        "returnGeometry": "false",
        "f": "json",
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.get(NFHL_QUERY, params=params)
        resp.raise_for_status()
        features = resp.json().get("features", [])
    if not features:
        return None
    attrs = features[0].get("attributes", {})
    zone = attrs.get("FLD_ZONE")
    if not zone:
        return None
    return {
        "flood_zone_code": str(zone),
        "flood_zone_subtype": str(attrs.get("ZONE_SUBTY") or ""),
    }


def enrich_location(location: str) -> dict:
    """
    Enrich a user location with coordinates and FEMA flood zone when APIs respond.

    Never raises — returns partial dict on failure so the workflow can continue.
    """
    result: dict = {"location_query": location}
    try:
        coords = geocode_us_address(location)
    except Exception as exc:
        result["enrichment_error"] = f"geocode: {exc}"
        return result

    if not coords:
        result["enrichment_error"] = "geocode: no match"
        return result

    result.update(coords)
    try:
        zone = lookup_flood_zone(coords["latitude"], coords["longitude"])
    except Exception as exc:
        result["enrichment_error"] = f"nfhl: {exc}"
        return result

    if zone:
        result.update(zone)
        code = zone["flood_zone_code"].upper()
        result["flood_zone_inferred"] = code not in ("X", "B", "C", "D")
    return result
