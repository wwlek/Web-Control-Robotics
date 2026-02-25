import requests
import time
import random

BACKEND_URL = "http://127.0.0.1:5000/log-power"

print("🐱 Multi-Cat Simulator Started!")
print("Simulating 4 cats sending data... Press Ctrl+C to stop.")

while True:
    # Loop through Cat 1, 2, 3, and 4
    for cat_id in range(1, 5):
        # Give each cat a slightly different power range so the graph looks cool
        base_power = cat_id * 50 
        fake_power = random.randint(base_power, base_power + 100)
        
        payload = {"cat_id": cat_id, "power": fake_power}
        
        try:
            requests.post(BACKEND_URL, json=payload)
            print(f"Sent: Cat {cat_id} used {fake_power}mA")
        except requests.exceptions.ConnectionError:
            print("Backend is down. Waiting...")
            
    # Wait 1 second before the next wave of data
    time.sleep(1)