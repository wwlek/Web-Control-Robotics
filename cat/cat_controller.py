# cat_controller.py
import machine
from led_display import NeoPixelLED
from movements import walk, rotateRight, rotateLeft, smoothDance, sitUpAndWave

# temp, tbd movements
led = NeoPixelLED(pin=8, num_leds=1)

# ADC objects
Ucontroller = machine.ADC(0)  # Controller battery voltage
Uservo = machine.ADC(1)       # Servo motor voltage

def move(direction: str) -> None:
    if direction == "forward":
        walk()
    elif direction == "left":
        rotateLeft()
    elif direction == "right":
        rotateRight()
        
    print(f"[CAT PRD] Moving {direction}")

def dance() -> None:
    smoothDance()
    print("[CAT PRD] Dance")

def wave() -> None:
    sitUpAndWave()
    print("[CAT PRD] Wave")

def get_voltage():
    svoltage_raw = Uservo.read()
    svoltage = svoltage_raw / 100
    print(f"Returned servo voltage: {svoltage:.2f} V")
    return round(svoltage, 1)

def get_battery():
    bvoltage_raw = Ucontroller.read()
    percent = bvoltage_raw / 3.6
    print("Battery voltage percentage: ", min(100, round(percent, 2)))
    return min(100, round(percent))
