import network
import time
import urequests
import uasyncio as asyncio
from microdot import Microdot

app = Microdot()

# --- CONFIGURATION ---
WIFI_SSID = "DancingCats"
WIFI_PASSWORD = "Sysk1ng*"

# The IP address of your Ubuntu laptop running FastAPI
BACKEND_URL = "http://*:5000/log-power" 
MY_CAT_ID = 4

# ==========================================
# 1. Connect to Wi-Fi
# ==========================================
wlan = network.WLAN(network.STA_IF)

# Force the Wi-Fi hardware to turn off and reset its state first
wlan.active(False) 
time.sleep(0.5) 
# ---------------

wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

print("Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(1)
print("Connected! My ESP32 IP is:", wlan.ifconfig()[0])
# NOTE: Put this IP address into the CAT_IPS list in your Python Backend!

# ==========================================
# 2. Microdot Endpoint: Listen for the Dance Command
# ==========================================
@app.route('/dance', methods=['POST'])
async def dance(request):
    print("!!! DANCE COMMAND RECEIVED FROM BACKEND !!!")
    # You will add your servo motor code here later!
    return {"status": "dancing"}, 200

# ==========================================
# 3. Background Task: Send Power Data
# ==========================================
async def send_power_data():
    while True:
        # Fake power reading for MVP testing
        payload = {"cat_id": MY_CAT_ID, "power": 150} 
        try:
            print("Sending power data to backend...")
            response = urequests.post(BACKEND_URL, json=payload)
            response.close()
        except Exception as e:
            print("Could not reach backend:", e)
            
        # Wait 1 second without blocking the web server
        await asyncio.sleep(1) 

# ==========================================
# 4. Start Everything Concurrently
# ==========================================
async def main():
    # Start the background power sender
    asyncio.create_task(send_power_data())
    # Start the Microdot web server on port 80
    await app.start_server(port=80, debug=True)

# Run the async event loop
asyncio.run(main())
