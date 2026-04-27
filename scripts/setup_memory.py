import os
import vertexai
from vertexai.preview import reasoning_engines
from vertexai.agent_engines import AdkApp
from google.adk.agents import Agent

# Project Config
PROJECT_ID = "transit-flow-my"
LOCATION = "us-central1"
STAGING_BUCKET = f"gs://{PROJECT_ID}-staging"

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

# Define a minimal dummy agent for the engine
dummy_agent = Agent(
    name="MemoryBankHost",
    model="gemini-2.5-flash-lite",
    instruction="Host for Memory Bank.",
    tools=[]
)

adk_app = AdkApp(agent=dummy_agent)

print("--- Initializing Reasoning Engine (Memory Bank Host) ---")
try:
    # Using the preview reasoning_engines module
    agent_engine = reasoning_engines.ReasoningEngine.create(
        adk_app,
        display_name="TransitFlowMemoryBank",
        description="Persistent memory host for TransitFlow journeys.",
    )
    
    engine_id = agent_engine.resource_name.split("/")[-1]
    print(f"\nSUCCESS! Agent Engine ID: {engine_id}")
    print(f"Add this to your .env: AGENT_ENGINE_ID={engine_id}")
    
except Exception as e:
    print(f"\nFAILED to create Reasoning Engine: {e}")
    print("\nFallback: If you cannot create an engine, we will continue using InMemoryMemoryService for this session.")
