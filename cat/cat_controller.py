# cat_controller.py
from led_display import NeoPixelLED

led = NeoPixelLED(pin=8, num_leds=1)

def move(direction: str) -> None:
    led.set_color(0, 255, 0)  # Green
    led.off()                 # Turn off
    led.blink(0, 0, 255, 0.5) # Blue blink
    print(f"[CAT MOCK] Moving {direction}")

def stop() -> None:
    # Mock stop
    print("[CAT MOCK] Stop")

def dance() -> None:
    # Mock dance
    print("[CAT MOCK] Dance")
