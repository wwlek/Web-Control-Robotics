import network
import socket
import ujson  # Use ujson for JSON parsing in MicroPython
from cat_controller import move, stop, dance

# Connect WiFi
nic = network.WLAN(network.WLAN.IF_STA)
nic.active(True)
nic.connect('cats-project', '###')

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
    
    # POST /stop to handle stop action
    elif "POST /stop" in request:
        stop()
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\": \"OK\"}")
    
    # POST /dance to handle dance action
    elif "POST /dance" in request:
        dance()
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\": \"OK\"}")
    
    else:
        # Default response for unsupported routes or methods (404 Not Found)
        cl.send("HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\n\r\n{\"error\": \"Route Not Found\"}")

    cl.close()
