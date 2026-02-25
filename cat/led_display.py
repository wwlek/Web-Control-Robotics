import machine
import neopixel
import time

class NeoPixelLED:
    def __init__(self, pin=8, num_leds=1):
        self.np = neopixel.NeoPixel(machine.Pin(pin), num_leds)
        self.num_leds = num_leds

    def set_color(self, r, g, b):
        for i in range(self.num_leds):
            self.np[i] = (r, g, b)
        self.np.write()

    def off(self):
        self.set_color(0, 0, 0)

    def blink(self, r, g, b, delay=1):
        self.set_color(r, g, b)
        time.sleep(delay)
        self.off()
        time.sleep(delay)
