from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import datetime

app = FastAPI(title="Cat Project API (MVP Mode)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

power_logs_memory = []
CAT_IPS = ["http://192.168.1.100"] # Your ESP32 IP

# --- Data Models ---
class PowerData(BaseModel):
    cat_id: int
    power: int

class CatCommand(BaseModel):
    cat_id: int
    action: str  # e.g., "dance", "stop", "up", "left"

# ==========================================
# 1. ESP32 Power Logging & Graph Data
# ==========================================
@app.post("/log-power")
def log_power(data: PowerData):
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    power_logs_memory.append({"timestamp": current_time, "cat_id": data.cat_id, "power_mA": data.power})
    if len(power_logs_memory) > 50: power_logs_memory.pop(0) 
    return {"status": "success"}

@app.get("/get-chart-data")
def get_chart_data():
    return list(reversed(power_logs_memory))[:20]

# ==========================================
# 2. Global Commands (All Cats)
# ==========================================
@app.post("/trigger-sync")
def trigger_sync():
    print("GLOBAL: Make ALL cats dance!")
    for ip in CAT_IPS:
        try: requests.post(f"{ip}/dance", timeout=1)
        except: pass
    return {"status": "sync_sent"}

@app.post("/trigger-stop-all")
def trigger_stop_all():
    print("GLOBAL: Stop ALL cats instantly!")
    for ip in CAT_IPS:
        try: requests.post(f"{ip}/stop", timeout=1)
        except: pass
    return {"status": "stop_sent"}

# ==========================================
# 3. Individual Cat Commands (From the Grid UI)
# ==========================================
@app.post("/cat-command")
def cat_command(command: CatCommand):
    print(f"INDIVIDUAL: Telling Cat {command.cat_id} to do action: {command.action.upper()}")
    
    # In a real setup, you would look up the specific IP for command.cat_id
    # For now, we just print it to prove the UI works!
    
    return {"status": "command_received", "cat": command.cat_id, "action": command.action}