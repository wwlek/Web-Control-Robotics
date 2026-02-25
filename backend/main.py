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

# --- TEMPORARY DATABASE (RAM) ---
# This list will hold our data while the Python script is running.
# If you restart the server, this data is erased!
power_logs_memory = []

# --- ESP32 CONFIGURATION ---
# IMPORTANT: Change this to the actual IP address your ESP32 gets when it connects to Wi-Fi!
CAT_IPS = ["http://192.168.1.104"] 

class PowerData(BaseModel):
    cat_id: int
    power: int

# ==========================================
# ENDPOINT 1: ESP32 sends power data here
# ==========================================
@app.post("/log-power")
def log_power(data: PowerData):
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    
    # Create a dictionary of the new data
    new_entry = {
        "timestamp": current_time,
        "cat_id": data.cat_id,
        "power_mA": data.power
    }
    
    # Add it to our temporary RAM list
    power_logs_memory.append(new_entry)
    
    # Keep the list from getting too huge and crashing the laptop
    if len(power_logs_memory) > 400:
        power_logs_memory.pop(0)
        
    print(f"[{current_time}] Cat {data.cat_id} is using {data.power}mA")
    return {"status": "success"}

# ==========================================
# ENDPOINT 2: Frontend reads data from here
# ==========================================
@app.get("/get-chart-data")
def get_chart_data():
    # Just return our temporary RAM list!
    # We reverse it so the newest data is at the top, just like the SQL query did.
    return list(reversed(power_logs_memory))[:80]

# ==========================================
# ENDPOINT 3: Frontend triggers a dance
# ==========================================
@app.post("/trigger-dance")
def trigger_dance():
    print("Sending DANCE command to cats...")
    success_count = 0
    
    for ip in CAT_IPS:
        try:
            print(f"Trying to reach {ip}/dance ...")
            # We use timeout=2 so we don't wait forever if the ESP32 is offline
            response = requests.post(f"{ip}/dance", timeout=2)
            if response.status_code == 200:
                print(f"Cat at {ip} received the command!")
                success_count += 1
        except requests.exceptions.RequestException as e:
            print(f"Failed to reach cat at {ip}: {e}")
            
    return {"status": "command_processed", "cats_reached": success_count}