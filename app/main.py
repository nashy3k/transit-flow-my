import os
import asyncio
import uuid
import firebase_admin
from firebase_admin import auth as firebase_auth
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
        ai_response = await process_query_adk(
            query=request.message,
            user_id=user_id,
            user_location={"lat": lat, "lng": lng} if lat and lng else None
        )
        
        return {
            "response": ai_response,
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

@app.get("/config")
async def get_config():
    """Returns the Firebase configuration for the frontend."""
    return {
        "apiKey": os.environ.get("GOOGLE_API_KEY", "MISSING_API_KEY"),
        "authDomain": "transit-flow-my.firebaseapp.com",
        "projectId": "transit-flow-my",
        "storageBucket": "transit-flow-my.firebasestorage.app",
        "messagingSenderId": "360411242286",
        "appId": "1:360411242286:web:3e6e37535bb8ec917aa4bf",
        "measurementId": "G-TSSWSTS21D"
    }

# Mount Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

if __name__ == "__main__":
    import uvicorn
    # Final production port sync for Cloud Run 🎬📈 🇲🇾🚆stack
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
