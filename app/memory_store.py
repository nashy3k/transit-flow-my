import json
import os
from typing import Dict, Optional

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "data", "session_memory.json")

def ensure_memory_dir():
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)

def save_user_memory(user_id: str, data: Dict):
    """Saves stateful user data to a local JSON store."""
    ensure_memory_dir()
    memory = {}
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                memory = json.load(f)
        except:
            memory = {}
            
    if user_id not in memory:
        memory[user_id] = {}
        
    memory[user_id].update(data)
    
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=4)

def get_user_memory(user_id: str) -> Dict:
    """Retrieves stateful user data."""
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, 'r') as f:
            memory = json.load(f)
            return memory.get(user_id, {})
    except:
        return {}
