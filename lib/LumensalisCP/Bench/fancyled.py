
import gc
import board
import microcontroller
import neopixel

import adafruit_fancyled.adafruit_fancyled as fancy

num_leds = 20

# Declare a 6-element RGB rainbow palette
palette = [
    fancy.CRGB(1.0, 0.0, 0.0),  # Red
    fancy.CRGB(0.5, 0.5, 0.0),  # Yellow
    fancy.CRGB(0.0, 1.0, 0.0),  # Green
    fancy.CRGB(0.0, 0.5, 0.5),  # Cyan
    fancy.CRGB(0.0, 0.0, 1.0),  # Blue
    fancy.CRGB(0.5, 0.0, 0.5),
]  # Magenta

# Declare a NeoPixel object on pin D6 with num_leds pixels, no auto-write.
# Set brightness to max because we'll be using FancyLED's brightness control.
pixels = neopixel.NeoPixel(
    microcontroller.pin.GPIO18,
    #board.D6,
     num_leds, brightness=1.0, auto_write=False)

offset = 0  # Positional offset into color palette to get it to 'spin'

gc.collect()
gc.disable()
before = ( gc.mem_free(), gc.mem_alloc() )
loopCount = 100
for loopX in range( loopCount ):
    for i in range(num_leds):
        # Load each pixel's color from the palette using an offset, run it
        # through the gamma function, pack RGB value and assign to pixel.
        color = fancy.palette_lookup(palette, offset + i / num_leds)
        color = fancy.gamma_adjust(color, brightness=0.25)
        pixels[i] = color.pack()
    pixels.show()

    offset += 0.02  # Bigger number = faster spin
after = ( gc.mem_free(), gc.mem_alloc() )
print(f"Memory before: {before}, after: {after}")
gc.enable()
gc.collect()

usedPerLoop = (before[1] - after[1]) / loopCount
print(f"Memory used per loop: {usedPerLoop} bytes")
print("Garbage collection enabled and collected.")