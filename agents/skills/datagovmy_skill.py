import httpx
import json
import os
from typing import Dict, Any, List

class DataGovMySkill:
    """
    A skill to interact with the Malaysia Open Data MCP server (mcp-datagovmy).
    Uses direct POST requests with JSON-RPC over SSE format.
    """
    def __init__(self, endpoint: str = "https://mcp.techmavie.digital/datagovmy/mcp"):
        self.endpoint = endpoint
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Any:
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
            # The response is in SSE format: "event: message\ndata: {JSON}\n\n"
            text = response.text
            if "data: " in text:
                data_json = text.split("data: ")[1].strip()
                # Remove trailing markers if any
                if data_json.endswith("event:"): data_json = data_json[:-6].strip()
                parsed = json.loads(data_json)
                if "error" in parsed:
                    return f"Error: {parsed['error'].get('message', 'Unknown error')}"
                return parsed["result"]["content"][0]["text"]
            return "No data received from server."

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
        Fetches the latest weekly fuel prices with Firestore caching (Budi95 Update).
        Checks if the last sync was within 7 days; otherwise fetches from Data.Gov.My.
        """
        from firebase_admin import firestore
        import datetime

        db = firestore.client()
        fuel_ref = db.collection('metadata').document('fuel')
        fuel_doc = fuel_ref.get()

        if fuel_doc.exists:
            data = fuel_doc.to_dict()
            last_sync = data.get('last_sync')
            if last_sync:
                # Firestore timestamps are datetime objects
                age = (datetime.datetime.now(datetime.timezone.utc) - last_sync).days
                if age < 7: # Weekly Cache logic
                    print(f"BudiProtocol: Using Weekly Cached Price (Age: {age} days)")
                    return data.get('rates', {"ron95": 2.05, "ron97": 3.47, "diesel": 3.35, "ron95_skps": 2.05})

        print("BudiProtocol: Cache Expired. Syncing with DataGovMy Registry...")
        
        # 1. Official parquet URL from data.gov.my
        parquet_url = "https://storage.data.gov.my/commodities/fuelprice.parquet"
        
        # 2. Tool call to parse parquet
        result_text = await self._call_tool("parse_parquet_file", {"url": parquet_url})
        
        latest_rates = {"ron95": 2.05, "ron97": 3.47, "diesel": 3.35, "ron95_skps": 2.05}
        try:
            # The tool returns a JSON string or raw text parse.
            data_list = json.loads(result_text)
            if isinstance(data_list, list) and len(data_list) > 0:
                latest = data_list[-1]
                latest_rates = {
                    "ron95": float(latest.get("ron95", 2.05)),
                    "ron97": float(latest.get("ron97", 3.47)),
                    "diesel": float(latest.get("diesel", 3.35)),
                    "ron95_skps": float(latest.get("ron95_skps", 2.05))
                }
                # 3. Update Firestore Cache
                fuel_ref.set({
                    'rates': latest_rates,
                    'last_sync': datetime.datetime.now(datetime.timezone.utc)
                })
        except Exception as e:
            print(f"Error parsing fuel price data: {e}")
            
        return latest_rates
