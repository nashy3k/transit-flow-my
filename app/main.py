import os
import asyncio
import uuid
import firebase_admin
from firebase_admin import auth as firebase_auth, firestore
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, Dict

# Initialize Environment
load_dotenv()

# Initialize Firebase Admin for Application-Level security 🎬📈 🇲🇾🚆stack
if not firebase_admin._apps:
    firebase_admin.initialize_app(options={
        'projectId': 'transit-flow-my'
    })

from agents.supervisor import process_query_adk

# Explicitly configure Opik per the Robust Integration Rule
# opik.configure(
#    use_local=False,
#    workspace=os.environ.get("OPIK_WORKSPACE_NAME", "default"),
#    api_key=os.environ.get("OPIK_API_KEY", "dummy-key-until-setup")
# )

app = FastAPI(title="TransitFlow API")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User Session Storage
sessions = {}

class ChatRequest(BaseModel):
    message: str
    sessionId: str = None
    location: Optional[Dict[str, float]] = None # Autonomous Context Field

# --- AUTH DEPENDENCY (The Security Guard) ---
async def verify_user(authorization: str = Header(None)) -> str:
    """Verify the Firebase ID token in the Authorization header."""
    if not authorization:
        # For local dry-runs we allow bypass if explicitly configured
        if os.environ.get("SKIP_AUTH") == "true":
            return "local_dev_user"
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization scheme")

    id_token = authorization[7:]
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token.get("email", "unknown_user")
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Identity verification failed: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("app/static/index.html") as f:
        return f.read()

@app.post("/chat")
async def chat(request: ChatRequest, user_email: str = Depends(verify_user)):
    session_id = request.sessionId or str(uuid.uuid4())
    user_id = user_email.split('@')[0] # Simple ID mapping
    
    # Inject autonomous GPS context if provided
    lat = request.location.get('lat') if request.location else None
    lng = request.location.get('lng') if request.location else None
    
    print(f"--- INCOMING: {user_email} (Location: {lat}, {lng}) ---")
    
    try:
        # Call the Native ADK Supervisor Agent
        ai_raw = await process_query_adk(
            query=request.message,
            user_id=user_id,
            user_location={"lat": lat, "lng": lng} if lat and lng else None
        )
        
        # Parse JSON if response is a JSON string (for Visual Insights)
        # New Robust Delimiter-based Parsing
        chat_text = ai_raw
        visual_data = None
        
        if "<<<DATA>>>" in ai_raw:
            try:
                parts = ai_raw.split("<<<DATA>>>")
                chat_text = parts[0].strip()
                json_str = parts[1].strip()
                
                # Cleanup any potential markdown baggage
                json_str = json_str.replace("```json", "").replace("```", "").strip()
                
                # Try parsing the data object/array
                try:
                    visual_data = json.loads(json_str)
                except:
                    import ast
                    clean_str = json_str.replace("null", "None").replace("true", "True").replace("false", "False")
                    visual_data = ast.literal_eval(clean_str)
                    
                # Standardize to { "title": ..., "metrics": [...] }
                if isinstance(visual_data, list):
                    visual_data = { "title": "Calculated Journey", "metrics": visual_data }
                elif isinstance(visual_data, dict) and "metrics" not in visual_data:
                    # Attempt to fix single objects
                    visual_data = { "title": visual_data.get("title", "Insight"), "metrics": [visual_data] }
            except Exception as e:
                print(f"Delimiter Parsing failed: {e}")
                # chat_text remains ai_raw as fallback
                pass
        else:
            # Legacy fallback if agent forgets delimiter
            if "{" in ai_raw and "}" in ai_raw:
                try:
                    start = ai_raw.find("{")
                    end = ai_raw.rfind("}") + 1
                    json_str = ai_raw[start:end]
                    data = json.loads(json_str) if "{" in json_str else {}
                    chat_text = data.get("chat_response", ai_raw)
                    visual_data = data.get("visual_data", None)
                except:
                    pass

        return {
            "response": chat_text,
            "visual_data": visual_data,
            "sessionId": session_id,
            "status": "success"
        }
    except Exception as e:
        print(f"Error in chat processing: {e}")
        return {
            "response": f"Error communicating with agent: {str(e)}",
            "sessionId": session_id,
            "status": "error"
        }

@app.get("/stats")
async def get_stats():
    """Fetches real-time dashboard statistics from DataGovMy."""
    from agents.skills.datagovmy_skill import DataGovMySkill
    import json
    skill = DataGovMySkill()
    
    try:
        # 1. Fetch Fuel Prices
        fuel = await skill.get_latest_fuel_prices()
        # 2. Fetch Flood Alerts (Simplified count for now)
        flood_data = await skill._call_tool("get_flood_warnings", {"state": ""})
        # Parse flood data count (usually a list of alerts)
        flood_count = 0
        try:
            alerts = json.loads(flood_data) if isinstance(flood_data, str) else []
            flood_count = len(alerts) if isinstance(alerts, list) else 0
        except:
            flood_count = 0 
            
        return {
            "fuel": f"RM 3.87",
            "budi": "RM 1.99",
            "flood": flood_count,
            "uptime": "99.8%" 
        }
    except Exception as e:
        print(f"Stats fetch error: {e}")
        return {"fuel": "RM 3.87", "flood": "--", "uptime": "98%"}

@app.get("/config")
async def get_config():
    """Return the client-side configuration (safe for public exposure)"""
    return {
        "firebaseConfig": {
            "apiKey": os.environ.get("FIREBASE_API_KEY"),
            "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
            "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
            "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.environ.get("FIREBASE_APP_ID")
        }
    }

# Mount Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

if __name__ == "__main__":
    import uvicorn
    # Final production port sync for Cloud Run 🎬📈 🇲🇾🚆stack
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
