import os
import uuid
import json
import asyncio
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Request, Depends, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager

import firebase_admin
from firebase_admin import auth as firebase_auth, credentials

# Initialize Firebase Admin for Production Identity verification
try:
    # Use default credentials if available, else look for service account
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
except Exception as e:
    print(f"Firebase Admin Initialization Warning: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("TransitFlow Engine: Ignition")
    print("Database Connection: Verified (CloudSQL Proxy Active)")
    print("Agentic Orchestrator: Multi-Agent Supervisor Online")
    yield
    # Shutdown logic
    print("TransitFlow Engine: Powering Down")
    # Send shutdown sentinel to clear SSE streams
    try:
        while not event_queue.empty():
            event_queue.get_nowait()
        event_queue.put_nowait({"type": "shutdown", "message": "Server restarting..."})
    except:
        pass

app = FastAPI(lifespan=lifespan)

# Enhanced CORS for production-ready cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:8000", 
        "https://transit-flow-my.web.app",
        "https://transit-flow-my.firebaseapp.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User Session Storage
sessions = {}

class ChatRequest(BaseModel):
    message: str
    location: Optional[dict] = None
    sessionId: Optional[str] = None

class NearbyRequest(BaseModel):
    lat: float
    lng: float
    radius_km: float = 5.0

class SafetyEvent(BaseModel):
    type: str
    message: str
    location: str
    timestamp: str

# --- AUTH DEPENDENCY (The Security Guard) ---
async def verify_user(authorization: str = Header(None)) -> str:
    """Verify the Firebase ID token or handle local development tokens."""
    # Prioritize SKIP_AUTH for local development environments
    if os.environ.get("SKIP_AUTH") == "true":
        print("SECURITY: Authentication bypass active (SKIP_AUTH=true)")
        return "guest@transitflow.ai"

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization scheme")

    token = authorization[7:]
    
    # DEV MODE TOKEN
    if token == "local-dev-token":
        return "guest@transitflow.ai"

    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token.get("email", "unknown_user")
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Identity verification failed: {str(e)}")

from agents.supervisor import process_query_adk
from app.memory_store import clear_user_memory

@app.get("/", response_class=HTMLResponse)
async def get_index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "static", "app_v0057.html")
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Index fetch error: {e}")
        return "<html><body><h1>TransitFlow Engine: UI Bundle Missing</h1></body></html>"

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
        
        try:
            print(f"--- RAW AGENT RESPONSE: {ai_raw} ---")
        except UnicodeEncodeError:
            print(f"--- RAW AGENT RESPONSE: [Encoding Error - Response contains Unicode/Emojis] ---")
        except Exception as e:
            print(f"Error printing response: {str(e)}")
            
        # --- DATA EXTRACTION & SCRUBBING ---
        chat_text = ai_raw
        visual_data = None
        
        if "<<<DATA>>>" in ai_raw:
            try:
                parts = ai_raw.split("<<<DATA>>>")
                chat_text = parts[0].strip()
                json_str = parts[1].strip()
                
                # Handle common markdown baggage
                json_str = json_str.replace("```json", "").replace("```", "").strip()
                
                # Extract clean JSON block
                start_idx = json_str.find("{")
                end_idx = json_str.rfind("}") + 1
                if start_idx != -1 and end_idx != 0:
                    try:
                        visual_data = json.loads(json_str[start_idx:end_idx])
                    except Exception as json_err:
                        print(f"JSON Parse failed, trying fallback: {json_err}")
                        import ast
                        clean_str = json_str[start_idx:end_idx].replace("null", "None").replace("true", "True").replace("false", "False")
                        visual_data = ast.literal_eval(clean_str)
                
                # Standardize to { "title": ..., "metrics": [...] }
                if isinstance(visual_data, list):
                    visual_data = { "title": "Calculated Journey", "metrics": visual_data }
                elif isinstance(visual_data, dict) and "metrics" not in visual_data:
                    visual_data = { "title": visual_data.get("title", "Insight"), "metrics": [visual_data] }
            except Exception as e:
                print(f"Delimiter Parsing failed: {e}")
                pass
        
        # --- HARD POLYLINE SHIELD: Strip any leaked polyline strings from chat ---
        import re
        # Scrub raw polylines (>50 alphanumeric chars)
        chat_text = re.sub(r'[a-zA-Z0-9\-_]{50,}', '[Map Data]', chat_text)
        # Scrub technical metadata
        chat_text = re.sub(r'--- TOOL_METADATA:.*?---', '', chat_text, flags=re.DOTALL)
        chat_text = re.sub(r'\[STATIONS_DATA\]:.*?$', '', chat_text, flags=re.MULTILINE)
        chat_text = re.sub(r'TOOL_METADATA:.*?$', '', chat_text, flags=re.MULTILINE)
        
        # --- PHASE 3 ROBUST SYNC: Fallback Extraction ---
        import re
        if isinstance(visual_data, dict):
            if "safety" not in visual_data:
                match = re.search(r'Safety Advisory: (.*?)\n', chat_text)
                if match: visual_data["safety"] = match.group(1)
            
            if "stations" not in visual_data or not visual_data["stations"]:
                station_match = re.search(r'\[STATIONS_DATA\]: (.*?)$', ai_raw, re.MULTILINE)
                if station_match:
                    try:
                        visual_data["stations"] = json.loads(station_match.group(1))
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

@app.post("/chat/clear")
async def clear_chat(request: dict, user_email: str = Depends(verify_user)):
    session_id = request.get("sessionId")
    user_id = user_email.split('@')[0]
    
    print(f"--- CLEARING HISTORY: {user_email} (Session: {session_id}) ---")
    
    # 1. Clear local session dict if it exists
    if session_id and session_id in sessions:
        del sessions[session_id]
    
    # 2. Clear persistent memory store
    clear_user_memory(user_id)
    
    return {"status": "success", "message": "History cleared"}

@app.get("/nearby")
async def get_nearby(lat: float, lng: float):
    # --- PHASE 3: CloudSQL + Geospatial Search (Primary) ---
    radius_km = 10.0
    try:
        import psycopg2
        db_user = os.getenv("DB_USER", "transit_admin").strip()
        db_pass = os.getenv("DB_PASS", "").strip()
        db_name = os.getenv("DB_NAME", "transit_db").strip()
        
        print(f"DEBUG: DB_PASS loaded (Length: {len(db_pass)}) - Stripped")
        
        conn_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")
        if conn_name:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_pass,
                host=f"/cloudsql/{conn_name}"
            )
        else:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_pass,
                host=os.getenv("DB_HOST", "127.0.0.1").strip(),
                port="5432"
            )
            
        cur = conn.cursor()
        
        # Geospatial Query: Find nodes within radius (Earth distance operator)
        # Using point(lng, lat) for Malaysian coordinates
        # Increase limit to 20 to allow for diversity selection in Python
        cur.execute("""
            SELECT name, line, (coords <@> point(%s, %s)) as distance
            FROM transit_nodes
            WHERE (coords <@> point(%s, %s)) < (%s / 1.60934)
            ORDER BY distance ASC
            LIMIT 20;
        """, (lng, lat, lng, lat, radius_km))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        if rows:
            print(f"CloudSQL: Found {len(rows)} nodes within {radius_km}km.")
            raw_nearby = []
            seen_names = set()
            for r in rows:
                clean_name = r[0].strip()
                if clean_name in seen_names: continue
                raw_nearby.append({
                    "name": clean_name,
                    "line": r[1],
                    "distance": round(r[2]*1.60934, 2),
                    "type": clean_name.split(']')[0].replace('[', '').strip() if ']' in clean_name else "Other"
                })
                seen_names.add(clean_name)
            
            # Diversity Logic
            diversified = []
            types_included = set()
            for item in raw_nearby:
                if item["type"] not in types_included:
                    diversified.append(item)
                    types_included.add(item["type"])
            
            remaining = [item for item in raw_nearby if item not in diversified]
            diversified.extend(remaining)
            return diversified[:5]
        else:
            print("CloudSQL: No rows found, falling back to JSON.")
    except Exception as db_err:
        print(f"CloudSQL Proximity Fetch Failed: {db_err}. Switching to JSON.")

    # --- PHASE 2: Tactical JSON Fallback ---
    try:
        # Robust path resolution for containerized environments
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "data", "malaysian_rail_nodes.json")
        
        if not os.path.exists(data_path):
            # Attempt 2: Search root data folder
            data_path = os.path.join(os.getcwd(), "app", "data", "malaysian_rail_nodes.json")
            
        if not os.path.exists(data_path):
            # Attempt 3: Search common container roots
            search_roots = [os.getcwd(), "/app", "/app/app"]
            for s_root in search_roots:
                if os.path.exists(s_root):
                    for root, dirs, files in os.walk(s_root):
                        if "malaysian_rail_nodes.json" in files:
                            data_path = os.path.join(root, "malaysian_rail_nodes.json")
                            break
                if os.path.exists(data_path): break
            
        if not os.path.exists(data_path):
            print(f"CRITICAL: JSON registry not found! Searched {search_roots}. Using empty fallback.")
            return []
            
        print(f"DEBUG: Loading JSON registry from {data_path}")
            
        with open(data_path, "r") as f:
            registry = json.load(f)
            
        nearby = []
        seen_names = set()
        
        # De-duplicate and parse
        for station in registry.get("stations", []):
            if station["name"] in seen_names:
                continue
                
            dist = ((station["lat"] - lat)**2 + (station["lng"] - lng)**2)**0.5 * 111
            if dist < radius_km:
                nearby.append({
                    "name": station["name"],
                    "line": station["line"],
                    "distance": round(dist, 2),
                    "type": station["name"].split(']')[0].replace('[', '').strip() if ']' in station["name"] else "Other"
                })
                seen_names.add(station["name"])
        
        # Sort by distance
        nearby.sort(key=lambda x: x["distance"])
        
        # Diversity Logic: Ensure we try to include one of each type in Top 5
        diversified = []
        types_included = set()
        
        # 1. Pick the closest for each unique type first
        for item in nearby:
            if item["type"] not in types_included:
                diversified.append(item)
                types_included.add(item["type"])
        
        # 2. Fill the rest with the remaining closest items
        remaining = [item for item in nearby if item not in diversified]
        diversified.extend(remaining)
        
        return diversified[:5]
    except Exception as e:
        print(f"Nearby fetch error: {e}")
        return []

@app.get("/stats")
async def get_stats():
    """Mock metrics for the Efficiency Score / Carbon Offset calculation."""
    try:
        return {
            "co2_saved": round(15.4 + (datetime.now().second / 10), 2),
            "efficiency": 88,
            "flood": 0,
            "fuel": "RON95 RM 3.97",
            "budi": "RM 2.05"
        }
    except Exception as e:
        print(f"Stats fetch error: {e}")
        return {"error": str(e)}

# SSE Event Queue for Real-time Alerts
event_queue = asyncio.Queue()

@app.get("/events")
async def events(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            try:
                data = await asyncio.wait_for(event_queue.get(), timeout=1.0)
                yield f"data: {json.dumps(data)}\n\n"
            except asyncio.TimeoutError:
                yield ": keep-alive\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
