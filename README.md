# README
## Git Repo
https://github.com/wwlek/Web-Control-Robotics

## Router
SSID: "DancingCats"
PASSWORD: "Sysk1ng*"

### IPs
Router = 192.168.1.1

Backend Server 1 = 192.168.1.10
Backend Server 2 = 192.168.1.20

Cat 1 = 192.168.1.101
Cat 2 = 192.168.1.102
Cat 3 = 192.168.1.103
Cat 4 = 192.168.1.104

## Commands
python3 fake-esp32.py
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
python3 -m http.server 8000