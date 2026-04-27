from typing import Dict, Any, List
from app.vector_service import VectorService
import datetime
import httpx
import json

class DataGovMySkill:
    """
    A skill to interact with the Malaysia Open Data MCP server (mcp-datagovmy).
    Uses direct POST requests with JSON-RPC over SSE format.
    Unified Cloud SQL Caching enabled for Phase 3.
    """
    def __init__(self, endpoint: str = "https://mcp.techmavie.digital/datagovmy/mcp"):
        self.endpoint = endpoint
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        self.vector_service = VectorService()

    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Any:
        # 1. Try Cache First (Phase 3 Unified Caching)
        cache_key = {"tool": tool_name, "args": arguments or {}}
        try:
            cached = await self.vector_service.get_cached_api_response("datagovmy", cache_key)
            if cached:
                print(f"CloudCache: Hit for {tool_name}")
                return cached
        except Exception as e:
            print(f"CloudCache Error (Read): {e}")

        # 2. Fetch Live
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name if tool_name.startswith("datagovmy_") else f"datagovmy_{tool_name}",
                "arguments": arguments or {}
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.endpoint, headers=self.headers, json=payload)
            text = response.text
            result_text = "No data received from server."
            
            if "data: " in text:
                data_json = text.split("data: ")[1].strip()
                if data_json.endswith("event:"): data_json = data_json[:-6].strip()
                parsed = json.loads(data_json)
                if "error" in parsed:
                    result_text = f"Error: {parsed['error'].get('message', 'Unknown error')}"
                else:
                    result_text = parsed["result"]["content"][0]["text"]
            
            # 3. Save to Cache
            # Intelligent TTL Logic (Phase 3 Optimization)
            ttl = 3600 # Default 1 hour
            if "fuelprice" in str(arguments):
                ttl = 604800 # 7 Days (Weekly fuel cycle)
            elif "weather" in tool_name or "flood" in tool_name:
                ttl = 1800 # 30 Minutes (Safety critical)

            try:
                await self.vector_service.cache_api_response("datagovmy", cache_key, result_text, ttl_seconds=ttl)
            except Exception as e:
                print(f"CloudCache Error (Write): {e}")
                print(f"CloudCache Error (Write): {e}")
                
            return result_text

    async def search_all(self, query: str) -> str:
        """Searches across datasets and dashboards."""
        return await self._call_tool("search_all", {"query": query})

    async def check_weather(self, location: str) -> str:
        """Gets weather forecast and warnings."""
        return await self._call_tool("get_weather_forecast", {"location": location})

    async def check_safety(self, location: str = "") -> str:
        """Checks for current weather and flood warnings."""
        weather_warn = await self._call_tool("get_weather_warnings", {"location": location})
        flood_warn = await self._call_tool("get_flood_warnings", {"state": location})
        return f"Weather Alerts: {weather_warn}\nFlood Alerts: {flood_warn}"

    async def find_transit(self, location: str) -> str:
        """Finds nearby transit stops and arrivals."""
        return await self._call_tool("search_transit_stops_by_location", {"location": location, "provider": "lrt"})

    async def get_latest_fuel_prices(self) -> Dict[str, float]:
        """
        Fetches the latest weekly fuel prices with Cloud SQL caching.
        """
        parquet_url = "https://storage.data.gov.my/commodities/fuelprice.parquet"
        result_text = await self._call_tool("parse_parquet_file", {"url": parquet_url})
        
        latest_rates = {"ron95": 2.05, "ron97": 3.47, "diesel": 3.35, "ron95_skps": 2.05}
        try:
            data_list = json.loads(result_text)
            if isinstance(data_list, list) and len(data_list) > 0:
                latest = data_list[-1]
                latest_rates = {
                    "ron95": float(latest.get("ron95", 2.05)),
                    "ron97": float(latest.get("ron97", 3.47)),
                    "diesel": float(latest.get("diesel", 3.35)),
                    "ron95_skps": float(latest.get("ron95_skps", 2.05))
                }
        except Exception as e:
            print(f"Error parsing fuel price data: {e}")
            
        return latest_rates

