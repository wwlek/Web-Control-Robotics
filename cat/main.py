import network
import socket
import time
from cat_controller import move, stop, dance

SSID = "DancingCats"
PASSWORD = "Sysk1ng*"

# -----------------------
# WIFI CONNECTION
# -----------------------
def connect_wifi():
    nic = network.WLAN(network.WLAN.IF_STA)

    # Full reset (fixes Wifi Internal State Error)
    nic.active(False)
    time.sleep(1)
    nic.active(True)
    time.sleep(1)

    if not nic.isconnected():
        print("Connecting to WiFi...")
        nic.connect(SSID, PASSWORD)

        timeout = 15
        while not nic.isconnected() and timeout > 0:
            print("Waiting for connection...")
            time.sleep(1)
            timeout -= 1

    if not nic.isconnected():
        raise RuntimeError("WiFi connection failed")

    print("Connected!")
    print("IP address:", nic.ifconfig()[0])
    return nic.ifconfig()[0]


# -----------------------
# START SERVER
# -----------------------
def start_server(ip):
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)

    print("Server running at http://{}".format(ip))

    while True:
        try:
            cl, addr = s.accept()
            print("Client connected from", addr)

            request = cl.recv(1024).decode()
            print("Request:", request)

            # --- ROUTES ---
            if "GET /move/forward" in request:
                move("forward")

            elif "GET /move/backward" in request:
                move("backward")

            elif "GET /move/left" in request:
                move("left")

            elif "GET /move/right" in request:
                move("right")

            elif "GET /stop" in request:
                stop()

            elif "GET /dance" in request:
                dance()

            # --- RESPONSE ---
            response = """HTTP/1.1 200 OK
Content-Type: text/plain

OK
"""
            cl.send(response)

        except Exception as e:
            print("Error:", e)

        finally:
            cl.close()


# -----------------------
# MAIN
# -----------------------
ip_address = connect_wifi()
start_server(ip_address)
