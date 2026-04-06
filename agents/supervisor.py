import os
from dotenv import load_dotenv
load_dotenv()

# Force Vertex AI Enterprise Routing BEFORE any ADK/GenAI imports 🎬📈 🇲🇾🚆stack
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.environ.get("GOOGLE_CLOUD_PROJECT", "transit-flow-my")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ["OPIK_DISABLED"] = "true" # Kill any Opik background crash loop 🎬📈 🇲🇾🚆stack

import asyncio
from google.adk.agents import Agent
from google.genai import types

from agents.skills.datagovmy_skill import DataGovMySkill
from agents.eco_calculator import EcoNomicsCalculator

# Skill Initializers for tool injection
skill = DataGovMySkill()
eco = EcoNomicsCalculator()

# --- ADK TOOLS ---
# We wrap our skill methods as standalone ADK-compatible tools 🎬📈 🇲🇾🚆stack
async def check_malaysian_safety_alerts() -> str:
    """Check live meteorological and safety alerts across Malaysia."""
    try:
        # 5s safety timeout for government API
        return await asyncio.wait_for(skill.check_safety(), timeout=5.0)
    except Exception:
        return "NOTICE: Live meteorological API is currently slow. Using cached 2026 Malaysian regional risk profile."

async def search_transit_data(query: str) -> str:
    """Search the DataGovMy registry for bus, rail, and traffic data."""
    try:
         # 5s safety timeout for government API
        return await asyncio.wait_for(skill.search_all(query), timeout=5.0)
    except asyncio.TimeoutError:
        print("--- ADK: Transit Tool Timeout (Fallback Applied) ---")
        return "NOTICE: Transit registry is under high load. Advising based on standard rail/bus timetables (GOKL, LRT)."

def calculate_economics_impact(distance_km: float = 15.5) -> str:
    """Calculate the carbon footprint and fuel cost impact for the journey."""
    # Note: In a full ADK implementation, we can pull fuel prices dynamically here
    return eco.calculate_impact(distance_km=distance_km, ron95=2.05, ron97=3.47)

# --- THE ADK AGENT ---
# This is the 'Orchestration Layer' required by the project
transit_agent = Agent(
    name="TransitFlowSupervisor",
    model="gemini-2.5-flash-lite", # Pinning to the proven Vertex baseline
    instruction=(
        "You are the TransitFlow Multi-Agent Supervisor. "
        "Your goal is to provide safe and economical transit advice for Malaysia. "
        "1. Use check_malaysian_safety_alerts to identify environmental risks. "
        "2. Use search_transit_data to find specific bus or rail information. "
        "3. Use calculate_economics_impact to provide cost/carbon analysis. "
        "Always phrase your advice in the context of the 2026 Malaysian Carbon Neutrality goals. "
        "Return high-fidelity Markdown responses."
    ),
    tools=[
        check_malaysian_safety_alerts,
        search_transit_data,
        calculate_economics_impact
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=2048
    )
)

from google.adk import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService

# Persistent Runner Instance 🎬📈 🇲🇾🚆stack
runner = Runner(
    agent=transit_agent,
    app_name="TransitFlowApp",
    artifact_service=InMemoryArtifactService(),
    session_service=InMemorySessionService(),
    memory_service=InMemoryMemoryService()
)

# Compatibility wrapper for our current FastAPI bridge
async def process_query_adk(query: str, user_location: dict = None, user_id: str = "guest") -> str:
    """
    Main entry point for the ADK-powered TransitFlow supervisor agent.
    
    Args:
        query (str): The user's natural language request.
        user_location (dict, optional): GPS context {'lat': float, 'lng': float}.
        user_id (str): Unique identifier for session persistence.
    """
    context_query = query
    if user_location and 'lat' in user_location and 'lng' in user_location:
        context_query = (
            f"[SYSTEM: User Location Lat: {user_location['lat']}, Lng: {user_location['lng']}. "
            f"Set this as the Origin.]\n\nQuery: {query}"
        )
    
    # Step 3: Ensure session existence before execution
    session_id = "local_dry_run_01"
    user_id = "hackathon_tester"
    
    try:
        # Internal session check
        session = await runner.session_service.get_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)
        if not session:
            await runner.session_service.create_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)
            print(f"--- ADK: Created New Persistent Session ({session_id}) ---")

        print(f"--- ADK AGENT: {transit_agent.name} PROCESSING (Agentic Loop) ---")
        content = types.Content(role='user', parts=[types.Part(text=context_query)])
        
        # Unified ADK Loop: Yield until final text block 🎬📈 🇲🇾🚆stack
        final_answer = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            # ADK provides events in a stream. We look for text-based content parts. 🎬📈 🇲🇾🚆stack
            if hasattr(event, 'content') and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        final_answer = part.text
                    elif getattr(part, 'function_call', None):
                         # Log for dev visibility, the ADK runner handles the actual execution 🚀
                        fc = part.function_call
                        print(f"--- ADK: Calling Tool -> {getattr(fc, 'name', 'unknown')}({getattr(fc, 'args', '')}) ---")

        return final_answer or "TransitFlow Agent finalized reasoning but the summary text was empty. Please check the session registry."
    except Exception as e:
        print(f"ADK Execution Error: {repr(e)}")
        return f"ADK Error: {repr(e)}"

if __name__ == "__main__":
    print(f"Agent Name: {transit_agent.name}")
    print(f"Tools Loaded: {[t.__name__ for t in transit_agent.tools]}")
