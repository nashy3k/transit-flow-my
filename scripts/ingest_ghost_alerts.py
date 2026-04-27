import asyncio
import os
import json
from app.vector_service import VectorService

# --- ENHANCED GHOST ALERT DATASET (Structured Metadata) ---
GHOST_ALERTS = [
    {
        "content": "Flash flood reported on Federal Highway near Mid Valley Megamall during extreme downpour in May 2024. Traffic halted for 3 hours. Water depth reached 0.5 meters.",
        "metadata": {
            "location": "Federal Highway", 
            "type": "Flood", 
            "date": "2024-05", 
            "depth_cm": 50, 
            "severity": "CRITICAL",
            "icon": "flood"
        }
    },
    {
        "content": "Kelana Jaya LRT line experienced a major signal fault between KLCC and Ampang Park in January 2024. Service suspended for 2 hours during evening rush hour.",
        "metadata": {
            "location": "KLCC-Ampang Park", 
            "type": "Signal Fault", 
            "date": "2024-01", 
            "severity": "HIGH",
            "icon": "warning"
        }
    },
    {
        "content": "KTM Komuter service at Subang Jaya station delayed by 45 minutes due to track maintenance and signaling upgrades in March 2024.",
        "metadata": {
            "location": "Subang Jaya KTM", 
            "type": "Maintenance", 
            "date": "2024-03", 
            "severity": "MEDIUM",
            "icon": "timer"
        }
    },
    {
        "content": "SMART Tunnel closed to traffic for flood diversion during a massive thunderstorm in KL City Center, December 2023. Drivers diverted to Jalan Tun Razak.",
        "metadata": {
            "location": "SMART Tunnel", 
            "type": "Flood Diversion", 
            "date": "2023-12", 
            "severity": "HIGH",
            "icon": "closed"
        }
    },
    {
        "content": "Flash flood at Jalan Tuanku Abdul Rahman near LRT Masjid Jamek in February 2024. Commuters advised to use upper levels of the station. Street level water reached 0.3 meters.",
        "metadata": {
            "location": "Masjid Jamek", 
            "type": "Flood", 
            "date": "2024-02", 
            "depth_cm": 30, 
            "severity": "HIGH",
            "icon": "flood"
        }
    },
    {
        "content": "Extreme congestion reported on KESAS highway near Shah Alam exit during a multi-vehicle accident in April 2024. Delay estimated at 90 minutes.",
        "metadata": {
            "location": "KESAS Shah Alam", 
            "type": "Accident", 
            "date": "2024-04", 
            "severity": "HIGH",
            "icon": "car"
        }
    },
    {
        "content": "LRT Bangsar station experienced a temporary power outage affecting ticket gates and escalators in June 2024. Trains continued to run with manual signaling.",
        "metadata": {
            "location": "Bangsar LRT", 
            "type": "Power Outage", 
            "date": "2024-06", 
            "severity": "MEDIUM",
            "icon": "bolt"
        }
    },
    {
        "content": "Heavy rain caused visibility issues and slow traffic at Jalan Pudu near the old prison site in October 2023. Localized ponding reported.",
        "metadata": {
            "location": "Jalan Pudu", 
            "type": "Weather", 
            "date": "2023-10", 
            "depth_cm": 10, 
            "severity": "MEDIUM",
            "icon": "rainy"
        }
    }
]

async def main():
    print("STARTING ENHANCED GHOST ALERT INGESTION...")
    vector_service = VectorService()
    
    pool = await vector_service.get_pool()
    if pool:
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM transit_knowledge")
            print("CLEARED EXISTING KNOWLEDGE BANK.")

    for alert in GHOST_ALERTS:
        await vector_service.add_transit_knowledge(alert["content"], alert["metadata"])
    
    print("\nSUCCESS: Memory Bank updated with structured Metadata (Depth/Severity).")

if __name__ == "__main__":
    asyncio.run(main())
