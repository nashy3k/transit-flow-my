import asyncio
import os
import sys

# Ensure ASCII output for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from agents.supervisor import calculate_economics_impact
from agents.skills.datagovmy_skill import DataGovMySkill

async def diagnostic():
    print("Starting Live Economics Diagnostic...")
    
    # 1. Test Skill Directly
    skill = DataGovMySkill()
    print("Fetching Live Fuel Prices from DataGovMy...")
    try:
        rates = await skill.get_latest_fuel_prices()
        print(f"Skill Result: {rates}")
    except Exception as e:
        print(f"Skill Error: {e}")

    # 2. Test Supervisor Tool
    print("\nTesting Supervisor Tool (calculate_economics_impact)...")
    try:
        report = await calculate_economics_impact(distance_km=25.0)
        print("Supervisor Report Generated:")
        print("-" * 30)
        print(report)
        print("-" * 30)
    except Exception as e:
        print(f"Supervisor Tool Error: {e}")

if __name__ == "__main__":
    asyncio.run(diagnostic())
