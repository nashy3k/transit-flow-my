import asyncio
import json
import os
from app.vector_service import VectorService
from dotenv import load_dotenv

load_dotenv()

HISTORICAL_DATA = [
    {
        "content": "Flash flood reported at LRT Glenmarie station area during heavy rain in November 2023. Water depth reached 0.5m in the parking lot. Significant risk for low-clearance vehicles.",
        "metadata": {"type": "flood", "location": "Glenmarie", "date": "2023-11-15", "lat": 3.095, "lng": 101.59}
    },
    {
        "content": "Severe flooding at Federal Highway near Batu Tiga. Traffic at a standstill for 4 hours. Historical data suggests avoiding this route during monsoon peaks (Oct-Jan).",
        "metadata": {"type": "flood", "location": "Batu Tiga", "date": "2023-12-20", "lat": 3.058, "lng": 101.556}
    },
    {
        "content": "LRT Kelana Jaya line experienced delays due to lightning strike near Taman Bahagia. Historical reliability: 98%. Generally faster than car during Friday evening peaks.",
        "metadata": {"type": "transit_info", "location": "Taman Bahagia", "date": "2024-01-10", "lat": 3.11, "lng": 101.61}
    }
]

async def ingest():
    vs = VectorService()
    pool = await vs.get_pool()
    
    # 1. Ingest Transit Hubs from JSON
    hub_data_path = os.path.join(os.path.dirname(__file__), "..", "app", "data", "malaysian_rail_nodes.json")
    with open(hub_data_path, "r") as f:
        hubs = json.load(f)
        for hub in hubs.get("stations", []):
            content = f"Transit Hub: {hub['name']} on the {hub['line']} line. Accessible facilities available. GPS: {hub['lat']}, {hub['lng']}"
            metadata = {"type": "station", "name": hub['name'], "line": hub['line'], "lat": hub['lat'], "lng": hub['lng']}
            embedding = await vs.get_embedding(content)
            
            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO transit_knowledge (content, metadata, embedding) VALUES ($1, $2, $3)",
                    content, json.dumps(metadata), embedding
                )
            print(f"Ingested station: {hub['name']}")

    # 2. Ingest Historical Events
    for event in HISTORICAL_DATA:
        embedding = await vs.get_embedding(event["content"])
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO transit_knowledge (content, metadata, embedding) VALUES ($1, $2, $3)",
                event["content"], json.dumps(event["metadata"]), embedding
            )
        print(f"Ingested event: {event['metadata']['location']}")

    print("Ingestion complete!")
    await pool.close()

if __name__ == "__main__":
    asyncio.run(ingest())
