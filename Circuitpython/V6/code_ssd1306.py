import os
import time
import busio
import board
import displayio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label

WIDTH = 128
HEIGHT = 48
CENTER_X = int(WIDTH/2)
CENTER_Y = int(HEIGHT/2)

displayio.release_displays()

SDA = board.GP2
SCL = board.GP3
i2c = busio.I2C(SCL, SDA)

if(i2c.try_lock()):
    print("i2c.scan(): " + str(i2c.scan()))
    i2c.unlock()
print()

display_bus = displayio.I2CDisplay(i2c, device_address=60)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=48)
"""
“displayio” drivers will also work with CircuitPython to display error messages
and other output to the display when the user code is not using it.
"""
print("Raspberry Pi Pico/CircuitPython ")
print("SSD1306 displayio (adafruit_displayio_ssd1306)")
time.sleep(0.5)

print()
print("os.uname():")
uname = os.uname()
for u in uname:
    print(u)
    time.sleep(1)

print()
print(adafruit_displayio_ssd1306.__name__ + " : " + adafruit_displayio_ssd1306.__version__)
print()
#================================================
# Make the display context
group = displayio.Group(max_size=10)

NUM_OF_COLOR = 2
bitmap = displayio.Bitmap(WIDTH, HEIGHT, NUM_OF_COLOR)
bitmap_palette = displayio.Palette(NUM_OF_COLOR)
bitmap_palette[0] = 0x000000
bitmap_palette[1] = 0xFFFFFF

tileGrid = displayio.TileGrid(bitmap,
                              pixel_shader=bitmap_palette,
                              x=0, y=0)
group.append(tileGrid)
display.show(group)

"""
print("bitmap: ")
print(type(bitmap))
print(dir(bitmap))
print("bitmap_palette")
print(type(bitmap_palette))
print(dir(bitmap_palette))
print("tileGrid")
print(type(tileGrid))
print(dir(tileGrid))
print("group")
print(type(group))
print(dir(group))
print("display")
print(type(display))
print(dir(display))
"""

time.sleep(1)
bitmap.fill(1)

def range_f(start, stop, step):
    f = start
    while f < stop:
        yield f
        f += step
        
time.sleep(1)
for y in range_f(0, HEIGHT-1, 2):
    for x in range_f(0, WIDTH-1, 2):
        #print(str(x) + " : " + str(y))
        bitmap[x, y] = 0

time.sleep(1)
#========================================================
# Draw a label
text_group1 = displayio.Group(max_size=10, scale=3, x=0, y=0)
text1 = "Hello"
text_area1 = label.Label(terminalio.FONT, text=text1, color=0xFFFFFF)
text_group1.append(text_area1)
group.append(text_group1)

"""
print("text_group1:")
print(type(text_group1))
print(dir(text_group1))
"""

for xy in range(20):
    time.sleep(0.1)
    text_group1.x=xy
    text_group1.y=xy
#========================================================
#invert palette
time.sleep(1)
bitmap_palette[1] = 0x000000
bitmap_palette[0] = 0xFFFFFF

time.sleep(1)
y = 0
for x in range_f(0, WIDTH-1, 1):
    bitmap[x, y] = 0
    time.sleep(0.01)
x = WIDTH-1
for y in range_f(0, HEIGHT-1, 1):
    bitmap[x, y] = 0
    time.sleep(0.01)

y = HEIGHT-1
for x in range_f(0, WIDTH-1, 1):
    bitmap[x, y] = 0
    time.sleep(0.01)
x = 0
for y in range_f(0, HEIGHT-1, 1):
    bitmap[x, y] = 0
    time.sleep(0.01)

#invert palette
time.sleep(1)
bitmap_palette[0] = 0x000000
bitmap_palette[1] = 0xFFFFFF
#invert palette
time.sleep(1)
bitmap_palette[1] = 0x000000
bitmap_palette[0] = 0xFFFFFF

time.sleep(1)
bitmap.fill(1)
time.sleep(1)
for xy in range(20):
    time.sleep(0.1)
    text_group1.x=xy+20
    text_group1.y=xy+20
time.sleep(1)
print("- bye -")