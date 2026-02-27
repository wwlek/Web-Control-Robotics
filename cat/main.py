import network
import socket
import ujson  # Use ujson for JSON parsing in MicroPython
from cat_controller import move, dance, get_voltage, get_battery

# Connect WiFi
nic = network.WLAN(network.WLAN.IF_STA)
nic.active(True)
nic.connect('DancingCats', 'Sysk1ng*')

while not nic.isconnected():
    pass

print("Connected:", nic.ifconfig())

# Simple HTTP server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Listening on", addr)

while True:
    cl, addr = s.accept()
    request = cl.recv(1024).decode()

    # POST /move to handle direction: forward, left, right
    if "POST /move" in request:
        try:
            # Extract JSON body (after '\r\n\r\n')
            body = request.split('\r\n\r\n')[1]
            data = ujson.loads(body)  # Parse JSON body

            # Get the direction from the JSON data
            direction = data.get("direction")

            # Call the move function based on the direction
            if direction == "forward":
                move("forward")
            elif direction == "left":
                move("left")
            elif direction == "right":
                move("right")
            else:
                # If direction is invalid, return JSON error response
                cl.send("HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\n\r\n{\"error\": \"Invalid direction\"}")
                cl.close()
                continue

            # Respond with OK after performing move
            cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\": \"OK\"}")
        except (ValueError, KeyError):
            # In case of error in JSON parsing or missing 'direction', return JSON error response
            cl.send("HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\n\r\n{\"error\": \"Invalid JSON or Missing 'direction'\"}")
    
    # POST /dance to handle dance action
    elif "POST /dance" in request:
        dance()
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\": \"OK\"}")
    
    # GET /status to return voltage and battery
    elif "GET /status" in request:
        try:
            # Prepare the status data
            status = {
                "voltage": get_voltage(),  # Replace with actual voltage reading function
                "battery": get_battery()   # Replace with actual battery level function
            }
            response = ujson.dumps(status)
            cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + response)
        except Exception:
            cl.send("HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\n\r\n{\"error\": \"Could not read status\"}")
            
    else:
        # Default response for unsupported routes or methods (404 Not Found)
        cl.send("HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\n\r\n{\"error\": \"Route Not Found\"}")

    cl.close()


