# reducing the imports saves on performance
import time
import board
import digitalio
import neopixel
import displayio
import adafruit_displayio_ssd1306
import supervisor
from random import randint
from busio import I2C
from usb_hid import devices
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# Globals
LED_BLINK = 50
DEBOUCE_NUMBER = 2
LAYER = 0
LAYER_LOCK = 0
ANIMATION_MODE = 4
# oled timeout
TIMEOUT = 50.0

# display parameters
display_width = 128
display_height = 64
NUM_OF_COLOR = 2

# led stuffddd
PIXELS_OFF = 0

#RGB Stuff
ANIMATION_MODE_TIMEING = 0.0
MODES = [1,2,3,4]

class macro1():
    
    def __init__(self):
        print ("init macro1")
        self.lock = 0
    
    def run(self, value):
        if( (value == 1) and (self.lock == 0) ):
            # occurs on press, macro's can be single press activation
            self.lock = 1
            led.value = True
            keyboard.press(Keycode.P)
            time.sleep(.01)
            keyboard.release(Keycode.P)
            keyboard.press(Keycode.R)
            time.sleep(.01)
            keyboard.release(Keycode.R)
            keyboard.press(Keycode.E)
            time.sleep(.01)
            keyboard.release(Keycode.E)
            keyboard.press(Keycode.S)
            time.sleep(.01)
            keyboard.release(Keycode.S)
            keyboard.press(Keycode.S)
            time.sleep(.01)
            keyboard.release(Keycode.S)
            led.value = False
        elif( (value == 0) ):
            # occurs on release, macro's can also be full words / strings parsed to the driver.
            self.lock = 0
            keyboard_layout.write("Release")

class macro2():
    
    def __init__(self):
        print ("init macro2")
    
    def run(self):
        print ("Macro2 Running")
        keyboard_layout.write("this is a test")

class board_reload():

    def __init__(self):
        print("Board Reload init")

    def run(self, state):
        supervisor.reload() 

class lighting_mode():

    def __init__(self, direction):
        print("Next / Prev Lighting init")
        self.single_activation = 0
        self.direction = direction

    def run(self, state):
        global ANIMATION_MODE
        global MODES
        if(not self.single_activation):
            if(state):
                self.single_activation = 1
                try:
                    ANIMATION_MODE = MODES[(ANIMATION_MODE - 1) + self.direction]
                except:
                    ANIMATION_MODE = 1
                change_animation_timeing()
        else:
            if(not state):
                self.single_activation = 0

class lighting_toggle_on_off():

    def __init__(self):
        print("Enable / Disable Lighting init")
        self.single_activation = 0

    def run(self, state):
        global NEO_Pixel_status
        global pixels
        global PIXELS_OFF
        if(not self.single_activation):
            if(state):
                self.single_activation = 1
                if(NEO_Pixel_status == 1):
                    # clear all pixels...
                    pixels.fill((0, 0, 0))
                    pixels.show()
                    # set them to off
                    NEO_Pixel_status = 0
                    PIXELS_OFF = 1
                else:
                    NEO_Pixel_status = 1
        else:
            if(not state):
                self.single_activation = 0

class function_key_layer_hold():

    def __init__(self, layer):
        print("init function_key_layer_hold: " + str(layer))
        self.layer = layer

    def run(self, state):
        global LAYER
        global LAYER_LOCK
        if(state):
            LAYER_LOCK = 0
            if(LAYER != self.layer):
                LAYER = self.layer
        elif(not LAYER_LOCK):
            LAYER = 0

class function_key_layer_lock():
    
    def __init__(self, layer):
        print ("init function_key_layer_lock: " + str(layer))
        self.layer_lock = 0
        self.single_activation = 0
        self.layer = layer
    
    def run(self, state):
        global LAYER_LOCK
        if(not self.single_activation):
            # key has been pressed
            if( (self.layer_lock == 0) and (state) ):
                print("locking layer")
                # Lock the layer
                self.layer_lock = 1
                self.single_activation = 1
                self.toggle_layer(self.layer)
                LAYER_LOCK = self.layer
                group_lock_on.hidden = False
                display.refresh(target_frames_per_second=None)
            elif( (self.layer_lock == 1) and (state) ):
                print("unlocking layer")
                # unlock the layer
                self.layer_lock = 0
                self.toggle_layer(0)
                LAYER_LOCK = 0
                group_lock_on.hidden = True
                display.refresh(target_frames_per_second=None)
        else:
            if( (self.layer_lock == 1) and (not state) ):
                self.single_activation = 0
        
    def toggle_layer(self, layer):
        # set the global layer
        global LAYER
        LAYER = layer

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

def change_animation_timeing():

    global ANIMATION_MODE_TIMEING
    # set the timing
    if(ANIMATION_MODE == 4):
        ANIMATION_MODE_TIMEING = 0.05
    elif(ANIMATION_MODE == 1):
        ANIMATION_MODE_TIMEING = 10.0
    elif(ANIMATION_MODE == 2):
        ANIMATION_MODE_TIMEING = 0.5
    elif(ANIMATION_MODE == 3):
        ANIMATION_MODE_TIMEING = 0.5

# instance definition
MACRO_TYPE = (macro1, macro2)
FUNCTION_TYPE = (function_key_layer_hold, function_key_layer_lock, lighting_toggle_on_off, lighting_mode, board_reload)

print("disabling the auto reload")
supervisor.disable_autoreload()

print("Initialising the display")

# Release the display, this is super important!
displayio.release_displays()

# Use for I2C, use the max frequency possible
i2c = I2C(scl=board.GP5, sda=board.GP4, frequency=1000000)

# setup the I2C display, its an ssd1306 display
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=display_width, height=display_height, auto_refresh=False)

#Set the brightness (reduced brightness should help the burn in)
display.brightness = 0.0

# Create the base group
group = displayio.Group()

# Load the images
f = open("Images/cap_on.bmp", "rb")
pic = displayio.OnDiskBitmap(f)
group_cap_on = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
# offset the image, so its not on the border
group_cap_on.x = 2

del pic

f = open("Images/num_on.bmp", "rb")
pic = displayio.OnDiskBitmap(f)
group_num_on = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
group_num_on.x = 44

del pic

f = open("Images/scr_on.bmp", "rb")
pic = displayio.OnDiskBitmap(f)
group_scr_on = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
group_scr_on.x = 86

del pic

f = open("Images/lock_on.bmp", "rb")
pic = displayio.OnDiskBitmap(f)
group_lock_on = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
group_lock_on.x = 86
group_lock_on.hidden = True

del pic

f = open("Images/logo.bmp", "rb")
pic = displayio.OnDiskBitmap(f)
group_logo = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
# move the image down.
group_logo.x = 0
group_logo.y = 18

del pic

"""
### BONGO CAT ####
f = open("Images/logo2.bmp", "rb")
pic = displayio.OnDiskBitmap(f)
group_logo_1 = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
# move the image down.
group_logo_1.x = 0
group_logo_1.y = 18

f = open("Images/logo3.bmp", "rb")
pic = displayio.OnDiskBitmap(f)
group_logo_2 = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
# move the image down.
group_logo_2.x = 0
group_logo_2.y = 18

group.append(group_logo_1)
group.append(group_logo_2)
"""

# add the groups to the main group
group.append(group_logo)
group.append(group_cap_on)
group.append(group_num_on)
group.append(group_scr_on)
group.append(group_lock_on)

display.show(group)

print("Initing device PINS, Key Matrix, Etc...")

# Keyboard Layout

# [[ Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , None      , Keycode   , Keycode   ],
#  [ Keycode   , None      , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   ],
#  [ Keycode   , None      , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , None      , Keycode   ],
#  [ Keycode   , None      , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , Keycode   , None      , Keycode   , None      , Keycode   ],
#  [ Keycode   , Keycode   , Keycode   , None      , None      , None      , Keycode   , None      , None      , None      , Keycode   , Keycode   , None      , Keycode   , Keycode   , Keycode   ]]

Keyboard_Layout = [ [ [ Keycode.ESCAPE, Keycode.ONE, Keycode.TWO, Keycode.THREE, Keycode.FOUR, Keycode.FIVE, Keycode.SIX, Keycode.SEVEN, Keycode.EIGHT, Keycode.NINE, Keycode.ZERO, Keycode.MINUS, Keycode.EQUALS, None, Keycode.BACKSPACE, Keycode.HOME ],
                      [ Keycode.TAB, None, Keycode.Q, Keycode.W, Keycode.E, Keycode.R, Keycode.T, Keycode.Y, Keycode.U, Keycode.I, Keycode.O, Keycode.P, Keycode.LEFT_BRACKET, Keycode.RIGHT_BRACKET, Keycode.BACKSLASH, Keycode.END ],
                      [ Keycode.CAPS_LOCK , None, Keycode.A, Keycode.S, Keycode.D, Keycode.F, Keycode.G, Keycode.H, Keycode.J, Keycode.K, Keycode.L, Keycode.SEMICOLON, Keycode.QUOTE, Keycode.ENTER, None, Keycode.PAGE_UP ],
                      [ Keycode.LEFT_SHIFT, None, Keycode.Z, Keycode.X, Keycode.C, Keycode.V, Keycode.B, Keycode.N, Keycode.M, Keycode.COMMA, Keycode.PERIOD, Keycode.FORWARD_SLASH, None, Keycode.RIGHT_SHIFT, None, Keycode.PAGE_DOWN ],
                      [ Keycode.LEFT_CONTROL, Keycode.LEFT_GUI, Keycode.LEFT_ALT, None, None, None, Keycode.SPACEBAR, None, None, None, Keycode.RIGHT_ALT, function_key_layer_hold(2), None, Keycode.APPLICATION, Keycode.RIGHT_CONTROL, function_key_layer_hold(1) ] ],
                    
                    [ [ Keycode.GRAVE_ACCENT, Keycode.F1, Keycode.F2, Keycode.F3, Keycode.F4, Keycode.F5, Keycode.F6, Keycode.F7, Keycode.F8, Keycode.F9, Keycode.F10, Keycode.F11, Keycode.F12, None, None, Keycode.DELETE],
                      [ macro1(), None, None, Keycode.UP_ARROW, None, None, None, None, None, None, None, None, None, None, None, Keycode.PRINT_SCREEN ],
                      [ Keycode.KEYPAD_NUMLOCK, None, Keycode.LEFT_ARROW, Keycode.DOWN_ARROW, Keycode.RIGHT_ARROW, None, None, None, None, None, None, None, None, Keycode.INSERT, None, None],
                      [ Keycode.LEFT_SHIFT, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                      [ Keycode.LEFT_CONTROL, Keycode.SCROLL_LOCK, None, None, None, None, Keycode.SPACEBAR, None, None, None, Keycode.RIGHT_ALT, None, None, Keycode.APPLICATION, Keycode.RIGHT_CONTROL, function_key_layer_hold(1) ] ],
                      
                    [ [ board_reload(), None, None, None, None, None, None, None, None, None, None, None, None, None, None, ConsumerControlCode.SCAN_PREVIOUS_TRACK],
                      [ None, None, lighting_mode(-1), lighting_toggle_on_off(), lighting_mode(1), None, None, None, None, None, None, None, None, None, None, ConsumerControlCode.SCAN_NEXT_TRACK],
                      [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, ConsumerControlCode.VOLUME_INCREMENT],
                      [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, ConsumerControlCode.VOLUME_DECREMENT],
                      [ None, None, None, None, None, None, ConsumerControlCode.PLAY_PAUSE, None, None, None, None, function_key_layer_hold(2), None, None, None, ConsumerControlCode.MUTE] ] ]

# The Physical Pins
#                       COL0       COL1       COL2       COL3       COL4       COL5       COL6       COL7       COL8        COL9        COL10       COL11       COL12       COL13       COL14       COL15
keyboard_cols = [ board.GP0, board.GP1, board.GP2, board.GP3, board.GP6, board.GP7, board.GP8, board.GP9, board.GP10, board.GP11, board.GP12, board.GP14, board.GP15, board.GP16, board.GP17, board.GP18 ]
#                       ROW0        ROW1        ROW2        ROW3        ROW4
keyboard_rows = [ board.GP19, board.GP20, board.GP21, board.GP22, board.GP26 ]

# The Pin Matrix
keyboard_cols_array = []
keyboard_rows_array = []

# Make all col pin objects inputs with pullups.
for pin in keyboard_cols:
    key_pin = digitalio.DigitalInOut(pin)           
    key_pin.direction = digitalio.Direction.OUTPUT
    key_pin.value = False
    keyboard_cols_array.append(key_pin)
    
# Make all row pin objects inputs with pullups
for pin in keyboard_rows:
    key_pin = digitalio.DigitalInOut(pin)
    key_pin.direction = digitalio.Direction.INPUT
    key_pin.pull = digitalio.Pull.DOWN
    keyboard_rows_array.append(key_pin)

print(keyboard_cols_array)
print(keyboard_rows_array)

led = digitalio.DigitalInOut(board.LED)
led.switch_to_output()

pixel_pin = board.GP13

# The number of NeoPixels
num_pixels = 17

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=ORDER
)

# perform a file import, this is a test to see if it's possible to protect against failures.
try:
    import blank

    # Boot the keyboard, Flash green a few times
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(.1)
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(.1)
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(.1)
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(.1)
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(.1)

except (ImportError, SyntaxError):
    pixels.fill((255, 0, 0))
    pixels.show()
    time.sleep(.1)
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(.1)
    pixels.fill((255, 0, 0))
    pixels.show()
    time.sleep(.1)
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(.1)
    pixels.fill((255, 0, 0))
    pixels.show()
    time.sleep(.1)

print("Check Device Ready!")

while(True):

    # Debug LED ON
    led.value = True
    
    print("Starting USB_HID")

    try:
        # start the USB Driver
        keyboard = Keyboard(devices)
        keyboard_layout = KeyboardLayoutUS(keyboard)
        # start the CC
        cc = ConsumerControl(devices)
        # exit the loop
        break
    except:
        print("Error starting USB_HID")
        # Wait
        time.sleep(.5)
        # Debug LED OFF
        led.value = False
        pass

# Debug LED ON
led.value = False

print("Starting Main Loop")

# Debouncing Array
Debouncing_Array = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

# Status LED
LED_Count = 0

# Neopixel Status
NEO_Pixel_status = 1
Flip_flop = 1

# rainbow cycle
rainbow_range = 0

# Past Keyboard Report
Past_Report = list(keyboard.report)

# Past CC report
cc_lock = 0

# Past LED Report
current_leds = b'0x00'
past_current_leds = b'0x16'

# microcontroller timing
current_timeing = time.monotonic()
hid_check_timeing = 0.0
animation_timeing = 0.0
oled_refresh_timeing = 0.0
oled_timeout_setting = current_timeing + TIMEOUT 

#set timeing
change_animation_timeing()

# bongo_cat
bongo_cat_timeing = 0.0
display_logo = 0

# Keyboard Variables
col_pin_number = 0
row_pin_number = 0
state_change = False

#TODO 1) Stop error when more than 6 keys are pressed.
#TODO 5) Backup Load if error with original 
#TODO 6) Implement a new way of hanling excalated function key layers so they do not get stuck.
#           1) keep a list of keys that are pressed when escalated
#           2) When the function key is release, make sure that all keys are removed from the report
#           3) This tends to happen with things like print screen and ctrl keys most offten, reproduce.
#TODO 10) Improve Layer Lock functionality
#TODO 11) Keyboard managment functions 
#           2) disable the oled

# debug run counter (aiming for about 100 cycles per second)
runs = 0

# Main Loop
while True:

    #Update time
    current_timeing = time.monotonic()

    #HID Check loop
    if(current_timeing >= (hid_check_timeing + 5.0)):
        # try and send a report, if it fails disable the LED's
        print(runs)
        runs = 0
        try:
            keyboard._keyboard_device.send_report(keyboard.report)
            # set neopixels to on, resume animations, only if pixel lock isn't on
            if(not PIXELS_OFF):
                NEO_Pixel_status = 1

            # show the display (only if the timeout hasn't expired)
            if(current_timeing <= oled_timeout_setting):
                # the oled is still active
                group.hidden = False
            else:
                # only activate if the oled is timed out
                group.hidden = True
            # refresh the display, no target
            display.refresh(target_frames_per_second=None)
        except:
            # clear all pixels...
            pixels.fill((0, 0, 0))
            pixels.show()
            # set them to off
            NEO_Pixel_status = 0
            # clear the display, disable it.
            group.hidden = True
            # refresh the display, no target
            display.refresh(target_frames_per_second=None)
        
        # reset the timing
        hid_check_timeing = current_timeing

    #Animation loop
    if(current_timeing >= (animation_timeing + ANIMATION_MODE_TIMEING)):
        #rainbow update animation
        if((ANIMATION_MODE == 4) and (NEO_Pixel_status == 1)):
            for i in range(num_pixels):
                pixel_index = (i * 256 // num_pixels) + rainbow_range
                pixels[i] = wheel(pixel_index & 255)
            # show
            pixels.show()
            
            if(rainbow_range < 255):
                rainbow_range += 3
            else:
                rainbow_range = 0

        # blue flip
        elif((ANIMATION_MODE == 2) and (NEO_Pixel_status == 1)):
            # implement a nice periodic animation.
            for a in range(0, num_pixels, 1):
                if(((a + Flip_flop) % 2) == 0):
                    pixels[a] = (0, 0, 255)
                elif(((a + Flip_flop) % 3) == 0):
                    pixels[a] = (100, 100, 100)
                else:
                    pixels[a] = (20, 120, 255)

            # display
            Flip_flop += 1
            pixels.show()
        
        # neon flip
        elif((ANIMATION_MODE == 3) and (NEO_Pixel_status == 1)):
            # implement a nice periodic animation.
            for a in range(0, num_pixels, 1):
                if(((a + Flip_flop) % 2) == 0):
                    pixels[a] = (255, 0, 255)
                elif(((a + Flip_flop) % 3) == 0):
                    pixels[a] = (10, 150, 255)
                else:
                    pixels[a] = (255, 0, 0)

            # display
            Flip_flop += 1
            pixels.show()
        
        # reset the timing
        animation_timeing = current_timeing

    if(current_timeing >= (oled_refresh_timeing + 0.4)):
        # Debug LED ON
        led.value = True
        # Run done

        # check the hid status of the report
        current_leds = keyboard.led_status

        # check that there is a change between the past and current
        if(current_leds != past_current_leds):
        
            # check if the capslock is active
            if(current_leds[0] & Keyboard.LED_CAPS_LOCK):
                # show the caps on and hide the caps off.
                group_cap_on.hidden = False
            else:
                # show the caps off and hide the caps on.
                group_cap_on.hidden = True
            
            # Check if the numlock key is active
            if(current_leds[0] & Keyboard.LED_NUM_LOCK):
                # show the caps on and hide the caps off.
                group_num_on.hidden = False
            else:
                # show the num off and hide the num on.
                group_num_on.hidden = True

            # Check if the scrolllock key is active
            if(current_leds[0] & Keyboard.LED_SCROLL_LOCK):
                # show the caps on and hide the caps off.
                group_scr_on.hidden = False
            else:
                # show the scr off and hide the scr on.
                group_scr_on.hidden = True

            # update the past status
            past_current_leds = current_leds

            # refresh the display, no target
            display.refresh(target_frames_per_second=None)

    if(current_timeing >= (oled_refresh_timeing + 0.41)):
        # Debug LED OFF
        led.value = False

        # update timeing
        oled_refresh_timeing = current_timeing

    """
    if(current_timeing >= (bongo_cat_timeing + 2.0)):
        
        if(display_logo == 0):
            group_logo_1.hidden = True
            group_logo_2.hidden = False
            display_logo += 1
        else:
            group_logo_1.hidden = False
            group_logo_2.hidden = True
            display_logo = 0

        bongo_cat_timeing = current_timeing

        # refresh the display, no target
        display.refresh(target_frames_per_second=None)
    """

    # HID State change, reset at every refresh (save cycles)
    state_change = False

    # do something using direct access to the array of col and row....

    # Scan Rows
    col_pin_number = 0
    # Set all Rows
    for col in keyboard_cols_array: 
        # Set the pin to High
        col.value = True
        # Scan Cols
        row_pin_number = 0
        # Read all Cols
        for row in keyboard_rows_array:
            # Check if the col is low
            if ( row.value == True ):
                # If the pin is low, add to debouce array
                Debouncing_Array[row_pin_number][col_pin_number] += 1
                # check if debounce is > 2 and the keycode is not none (skip emtpy keys)
                if(Debouncing_Array[row_pin_number][col_pin_number] >= DEBOUCE_NUMBER):
                    # If it passes the debouce test
                    if ( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], int) ):
                        # Add the keycode to the HID report
                        if(LAYER != 2):
                            keyboard._add_keycode_to_report(Keyboard_Layout[LAYER][row_pin_number][col_pin_number])
                            # update state change only if there was a change 
                            if( list(keyboard.report) == Past_Report):
                                pass
                            else:
                                state_change = True
                        elif(cc_lock != 1):
                            # this is for the CC report
                            cc.send(Keyboard_Layout[LAYER][row_pin_number][col_pin_number])
                            # Update the oled timeout
                            oled_timeout_setting = current_timeing + TIMEOUT
                            cc_lock = 1
                    elif( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], FUNCTION_TYPE) ):
                        Keyboard_Layout[LAYER][row_pin_number][col_pin_number].run(1)
                    elif( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], MACRO_TYPE)):
                        Keyboard_Layout[LAYER][row_pin_number][col_pin_number].run(1)
                    else:
                        # unknwon type, pass
                        pass
            else:
                # check if this key was just released
                if(Debouncing_Array[row_pin_number][col_pin_number] != 0):
                    # If it doesn't pass the debouce test, or is no longer pressed
                    if ( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], int) ):
                        # Remove the keycode to the HID report
                        if(LAYER != 2):
                            keyboard._remove_keycode_from_report(Keyboard_Layout[LAYER][row_pin_number][col_pin_number])
                            # update state change
                            if( list(keyboard.report) == Past_Report):
                                pass
                            else:
                                state_change = True
                        else:
                            # this is for the CC report
                            cc_lock = 0
                    elif( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], FUNCTION_TYPE) ):
                        Keyboard_Layout[LAYER][row_pin_number][col_pin_number].run(0)
                    elif( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], MACRO_TYPE)):
                        Keyboard_Layout[LAYER][row_pin_number][col_pin_number].run(0)
                    else:
                        # unknwon type, pass
                        pass

                    # If the pin is high, set the debounce to zero
                    Debouncing_Array[row_pin_number][col_pin_number] = 0

            # Inc col_pin_number
            row_pin_number += 1
        
        # Inc row_pin_number
        col_pin_number += 1

        # Set col Low
        col.value = False   

    if(state_change == True):
        # Only if there is a HID Report change Send report
        try:
            keyboard._keyboard_device.send_report(keyboard.report)
            Past_Report = list(keyboard.report)

            # Update the oled timeout
            oled_timeout_setting = current_timeing + TIMEOUT
        except:
            pass

        # perform a dynamic typing animation
        if(ANIMATION_MODE == 1):
            pixels[randint(0, num_pixels-1)] = (randint(0,3)*80, randint(0,3)*80, randint(0,3)*80)
            pixels.show()

    runs += 1