import os
import httpx
import json
from typing import Dict, Any, Optional
from google.cloud import secretmanager
from app.vector_service import VectorService

class RoutesService:
    def __init__(self, vector_service: VectorService):
        self.vector_service = vector_service
        self.project_id = os.getenv("PROJECT_ID", "transit-flow-my")
        self._api_key = None
        self.routes_url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        self.geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"

    async def get_api_key(self) -> str:
        if not self._api_key:
            try:
                client = secretmanager.SecretManagerServiceClient()
                name = f"projects/{self.project_id}/secrets/GOOGLE_MAPS_API_KEY/versions/latest"
                response = client.access_secret_version(request={"name": name})
                self._api_key = response.payload.data.decode("UTF-8").strip()
            except Exception as e:
                print(f"Error fetching API Key from Secret Manager: {e}")
                # Fallback to env if Secret Manager fails locally
                self._api_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
        return self._api_key

    async def geocode(self, address: str) -> Optional[Dict[str, float]]:
        """Resolves an address string to Lat/Lng coordinates using Google Geocoding API."""
        params = {"address": f"{address}, Malaysia", "key": await self.get_api_key()}
        
        # Check cache first
        cached = await self.vector_service.get_cached_api_response("geocoding", {"address": address})
        if cached:
            return cached

        async with httpx.AsyncClient() as client:
            resp = await client.get(self.geocode_url, params=params)
            data = resp.json()
            if data["status"] == "OK":
                location = data["results"][0]["geometry"]["location"]
                await self.vector_service.cache_api_response("geocoding", {"address": address}, location, ttl_seconds=86400 * 30) # 30 days
                return location
        return None

    async def get_route(self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Dict[str, Any]:
        """Calculates road distance and duration using Google Routes API v2."""
        
        # Round to 4 decimal places (~11m precision) to maximize cache hits while maintaining accuracy
        params = {
            "origin": {"lat": round(origin_lat, 4), "lng": round(origin_lng, 4)},
            "destination": {"lat": round(dest_lat, 4), "lng": round(dest_lng, 4)},
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE"
        }

        # Check cache
        cached = await self.vector_service.get_cached_api_response("google_routes_v2", params)
        if cached:
            print(f"Cloud SQL Cache: Hit for Route {origin_lat},{origin_lng} -> {dest_lat},{dest_lng}")
            return cached

        key = await self.get_api_key()
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": key,
            "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.staticDuration,routes.polyline.encodedPolyline"
        }
        
        body = {
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": params["origin"]["lat"],
                        "longitude": params["origin"]["lng"]
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": params["destination"]["lat"],
                        "longitude": params["destination"]["lng"]
                    }
                }
            },
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "units": "METRIC"
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.routes_url, headers=headers, json=body)
            if resp.status_code != 200:
                print(f"Routes API Error: {resp.text}")
                return {"error": "API Failure"}
            
            data = resp.json()
            if "routes" in data and len(data["routes"]) > 0:
                route = data["routes"][0]
                live_dur = int(route.get("duration", "0s").replace("s", ""))
                static_dur = int(route.get("staticDuration", "0s").replace("s", ""))
                
                result = {
                    "distance_km": route.get("distanceMeters", 0) / 1000,
                    "duration_seconds": live_dur,
                    "static_duration_seconds": static_dur,
                    "traffic_delay_minutes": max(0, (live_dur - static_dur) // 60),
                    "polyline": route.get("polyline", {}).get("encodedPolyline", "")
                }
                # Cache for 1 hour (traffic awareness)
                await self.vector_service.cache_api_response("google_routes_v2", params, result, ttl_seconds=3600)
                return result
        
        return {"error": "No routes found"}
