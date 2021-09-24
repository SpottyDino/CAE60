import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# Globals
LED_BLINK = 100
DEBOUCE_NUMBER = 2
MATRIX_SCAN = 0.0001
LAYER = 0

class macro1():
    
    def __init__(self):
        print ("init macro1")
    
    def run(self):
        print ("Macro1 Running")
        keyboard.press(Keycode.A)
        time.sleep(.01)
        keyboard.release(Keycode.A)
        keyboard.press(Keycode.B)
        time.sleep(.01)
        keyboard.release(Keycode.B)
        keyboard.press(Keycode.C)
        time.sleep(.01)
        keyboard.release(Keycode.C)
        keyboard.press(Keycode.D)
        time.sleep(.01)
        keyboard.release(Keycode.D)
        keyboard.press(Keycode.E)
        time.sleep(.01)
        keyboard.release(Keycode.E)

class macro2():
    
    def __init__(self):
        print ("init macro2")
    
    def run(self):
        print ("Macro2 Running")
        keyboard_layout.write("this is a test")

class function_key():

    layer_lock = 0

    def __init__(self):
        print ("init function_key")
    
    def run(self, value):
        if( self.layer_lock == 0 and value == 1):
            # Lcok the layer
            self.layer_lock = 1
            self.toggle_layer(value)
        elif( self.layer_lock == 1 and value == 0 ):
            # unlock the layer
            self.layer_lock = 0
            self.toggle_layer(value)

    def toggle_layer(self, layer):
        # set the global layer
        global LAYER
        LAYER = layer

    def switch_layer(self):
        print ("Switch")


MACRO_TYPE = (macro1, macro2)

print("Initing device PINS, Key Matrix, Etc...")

# Keyboard Layout
Keyboard_Layout = [ [ [ macro1(), function_key(), Keycode.K, Keycode.P, Keycode.U, Keycode.Z, Keycode.FIVE, Keycode.ZERO, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A ],
                      [ Keycode.B, Keycode.G, Keycode.L, Keycode.Q, Keycode.V, Keycode.ONE, Keycode.SIX, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A ],
                      [ Keycode.C, Keycode.H, Keycode.M, Keycode.R, Keycode.W, Keycode.TWO, Keycode.SEVEN, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A ],
                      [ Keycode.D, Keycode.I, Keycode.N, Keycode.S, Keycode.X, Keycode.THREE, Keycode.EIGHT, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A ],
                      [ Keycode.E, Keycode.J, Keycode.O, Keycode.T, Keycode.Y, Keycode.FOUR, Keycode.NINE, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, Keycode.A, macro2() ] ],
                    
                    [ [ None, function_key(), None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                      [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                      [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                      [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                      [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None] ] ]
# The Physical Pins
keyboard_cols = [ board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP8, board.GP9, board.GP10, board.GP11, board.GP12, board.GP16, board.GP17, board.GP18, board.GP19, board.GP20 ]
keyboard_rows = [ board.GP21, board.GP22, board.GP26, board.GP27, board.GP28 ]

# The Pin Matrix
keyboard_cols_array = []
keyboard_rows_array = []

# Make all col pin objects inputs with pullups
for pin in keyboard_cols:
    key_pin = digitalio.DigitalInOut(pin)
    key_pin.direction = digitalio.Direction.OUTPUT
    # key_pin.pull = digitalio.Pull.UP
    key_pin.value = False
    keyboard_cols_array.append(key_pin)
    
# Make all row pin objects inputs with pullups
for pin in keyboard_rows:
    key_pin = digitalio.DigitalInOut(pin)
    key_pin.direction = digitalio.Direction.INPUT
    key_pin.pull = digitalio.Pull.DOWN
    # key_pin.value = True
    keyboard_rows_array.append(key_pin)

print(keyboard_cols_array)
print(keyboard_rows_array)

led = digitalio.DigitalInOut(board.LED)
led.switch_to_output()

print(Keyboard_Layout)

print("Device ready HID")

# Debug LED ON
led.value = True
# Wait
time.sleep(1)
# Debug LED OFF
led.value = False
# Wait
time.sleep(1)
# Debug LED ON
led.value = True
# Wait
time.sleep(1)
# Debug LED OFF
led.value = False

print("Starting USB_HID")

keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

print("Starting Main Loop")

# Debouncing Array
Debouncing_Array = [[ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

# Status LED
LED_Count = 0
# Main Loop
while True:

    if(LED_Count == LED_BLINK):
        # Debug LED ON
        led.value = True
        LED_Count = 0

    # Scan Rows
    col_pin_number = 0
    # Set all Rows
    for col in keyboard_cols_array: 
        # Set the pin to High
        col.value = True
        # Wait for pin
        time.sleep(MATRIX_SCAN)
        # Scan Cols
        row_pin_number = 0
        # Read all Cols
        for row in keyboard_rows_array:
            # Check if the col is low
            if ( row.value == True ):
                # If the pin is low, add to debouce array
                Debouncing_Array[row_pin_number][col_pin_number] += 1
            else :
                # If the pin is high, set the debounce to zero
                Debouncing_Array[row_pin_number][col_pin_number] = 0
            # Inc col_pin_number
            row_pin_number += 1
        # Inc row_pin_number
        col_pin_number += 1
        # Set col Low
        col.value = False   

    # Debounce the Button
    for row in range(0, len(Debouncing_Array), 1):
        for col in range(0, len(Debouncing_Array[row]), 1):
            if( Debouncing_Array[row][col] >= DEBOUCE_NUMBER ):
                # If it passes the debouce test
                if ( isinstance(Keyboard_Layout[LAYER][row][col], int) ):
                    # Add the keycode to the HID report
                    keyboard._add_keycode_to_report(Keyboard_Layout[LAYER][row][col])
                elif( isinstance(Keyboard_Layout[LAYER][row][col], MACRO_TYPE) ):
                    # Fire off the macro
                    Keyboard_Layout[LAYER][row][col].run()
                elif( isinstance(Keyboard_Layout[LAYER][row][col], function_key) ):
                    # time to run the layer code.
                    Keyboard_Layout[LAYER][row][col].run(1)
                else:
                    # unknwon type, pass
                    pass
            else:
                # If it doesn't pass the debouce test, or is no longer pressed
                if ( isinstance(Keyboard_Layout[LAYER][row][col], int) ):
                    # Remove the keycode to the HID report
                    keyboard._remove_keycode_from_report(Keyboard_Layout[LAYER][row][col])
                elif( isinstance(Keyboard_Layout[LAYER][row][col], MACRO_TYPE) ):
                    # no need to fire off marco
                    pass
                elif( isinstance(Keyboard_Layout[LAYER][row][col], function_key) ):
                    Keyboard_Layout[LAYER][row][col].run(0)
                else:
                    # unknwon type, pass
                    pass

    # Debug LED OFF
    LED_Count += 1
    led.value = False

    # Send HID Report
    keyboard._keyboard_device.send_report(keyboard.report)