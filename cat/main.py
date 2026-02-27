import network
import socket
import ujson
from cat_controller import move, dance, wave, get_voltage, get_battery

# Connect WiFi
nic = network.WLAN(network.WLAN.IF_STA)
nic.active(True)
nic.connect('DancingCats', 'Sysk1ng*')

while not nic.isconnected():
    pass

print("Connected:", nic.ifconfig())

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Listening on", addr)

while True:
    cl, addr = s.accept()
    request = cl.recv(1024).decode()

    if "POST /move" in request:
        try:
            body = request.split('\r\n\r\n')[1]
            data = ujson.loads(body)

            direction = data.get("direction")

            if direction == "forward":
                move("forward")
            elif direction == "left":
                move("left")
            elif direction == "right":
                move("right")
            else:
                cl.send("HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\n\r\n{\"error\": \"Invalid direction\"}")
                cl.close()
                continue

            cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\": \"OK\"}")
        except (ValueError, KeyError):
            cl.send("HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\n\r\n{\"error\": \"Invalid JSON or Missing 'direction'\"}")
    
    elif "POST /dance" in request:
        dance()
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\": \"OK\"}")
    
    elif "POST /wave" in request:
        wave()
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\": \"OK\"}")
    
    elif "GET /status" in request:
        try:
            status = {
                "voltage": get_voltage(),
                "battery": get_battery()
            }
            response = ujson.dumps(status)
            cl.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + response)
        except Exception:
            cl.send("HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\n\r\n{\"error\": \"Could not read status\"}")
            
    else:
        cl.send("HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\n\r\n{\"error\": \"Route Not Found\"}")

    cl.close()


