# cat_controller.py
import machine
import tft_config
import st7789py as st7789
from movements import walk, rotateRight, rotateLeft, smoothDance, sitUpAndWave

# ADC objects
Ucontroller = machine.ADC(0)  # Controller battery voltage
Uservo = machine.ADC(1)       # Servo motor voltage

display = tft_config.config()
display.fill(st7789.BLACK)

def draw_simple_cat(x=100, y=100, scale=2):
    # Head (white)
    display.fill_rect(x + 12*scale, y + 8*scale, 12*scale, 16*scale, st7789.WHITE)
    
    # Ears (white)
    display.fill_rect(x + 8*scale, y + 6*scale, 6*scale, 6*scale, st7789.WHITE)
    display.fill_rect(x + 8*scale, y + 20*scale, 6*scale, 6*scale, st7789.WHITE)
    
    # Eyes (black)
    display.fill_rect(x + 14*scale, y + 10*scale, 3*scale, 3*scale, st7789.BLACK)
    display.fill_rect(x + 14*scale, y + 19*scale, 3*scale, 3*scale, st7789.BLACK)
    
    # Nose (red)
    display.fill_rect(x + 18*scale, y + 15*scale, 2*scale, 2*scale, st7789.RED)
    
    # Whiskers (black)
    display.vline(x + 20*scale, y + 8*scale, 5*scale, st7789.BLACK)
    display.vline(x + 22*scale, y + 8*scale, 5*scale, st7789.BLACK)
    display.vline(x + 20*scale, y + 19*scale, 5*scale, st7789.BLACK)
    display.vline(x + 22*scale, y + 19*scale, 5*scale, st7789.BLACK)
    
def move(direction: str) -> None:
    draw_simple_cat(5, 90, scale=5)
    if direction == "forward":
        walk()
    elif direction == "left":
        rotateLeft()
    elif direction == "right":
        rotateRight()
        
    print(f"[CAT PRD] Moving {direction}")

def dance() -> None:
    draw_simple_cat(5, 90, scale=5)
    smoothDance()
    print("[CAT PRD] Dance")

def wave() -> None:
    draw_simple_cat(5, 90, scale=5)
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

