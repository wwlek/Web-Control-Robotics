from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import datetime

app = FastAPI(title="Cat Project API (No Database Mode)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

power_logs_memory = []
CAT_IPS = ["http://192.168.1.104"] 

class PowerData(BaseModel):
    cat_id: int
    power: int

# We need this to understand individual cat commands (arrows, stop, dance)
class CatCommand(BaseModel):
    cat_id: int
    action: str

# ==========================================
# 1. ESP32 Power Logging & Graph Data
# ==========================================
@app.post("/log-power")
def log_power(data: PowerData):
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    new_entry = {
        "timestamp": current_time,
        "cat_id": data.cat_id,
        "power_mA": data.power
    }
    power_logs_memory.append(new_entry)
    
    if len(power_logs_memory) > 400:
        power_logs_memory.pop(0)
        
    # (I commented this out so your terminal doesn't get spammed by the fake ESP32s while you test the buttons!)
    # print(f"[{current_time}] Cat {data.cat_id} is using {data.power}mA") 
    return {"status": "success"}

@app.get("/get-chart-data")
def get_chart_data():
    return list(reversed(power_logs_memory))[:80]

# ==========================================
# 2. Global Commands (Top of UI)
# ==========================================
@app.post("/trigger-dance")
def trigger_dance():
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
# 3. Individual Commands (Grid UI Arrows/Buttons)
# ==========================================
@app.post("/cat-command")
def cat_command(command: CatCommand):
    print(f"INDIVIDUAL: Telling Cat {command.cat_id} to do action: {command.action.upper()}")
    # Here you would eventually send a request to the specific cat's IP
    return {"status": "command_received", "cat": command.cat_id, "action": command.action}