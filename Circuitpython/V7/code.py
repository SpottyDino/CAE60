import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode

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

    def hold_layer(self, toggle):
        global LAYER
        if(LAYER != toggle):
            LAYER = toggle


MACRO_TYPE = (macro1, macro2)

print("Initing device PINS, Key Matrix, Etc...")

# Keyboard Layout
Keyboard_Layout = [ [ [ Keycode.ESCAPE, Keycode.ONE, Keycode.TWO, Keycode.THREE, Keycode.FOUR, Keycode.FIVE, Keycode.SIX, Keycode.SEVEN, Keycode.EIGHT, Keycode.NINE, Keycode.ZERO, Keycode.MINUS, Keycode.EQUALS, None, Keycode.BACKSPACE, Keycode.HOME ],
                      [ Keycode.TAB, None, Keycode.Q, Keycode.W, Keycode.E, Keycode.R, Keycode.T, Keycode.Y, Keycode.U, Keycode.I, Keycode.O, Keycode.P, Keycode.LEFT_BRACKET, Keycode.RIGHT_BRACKET, Keycode.BACKSLASH, Keycode.END ],
                      [ Keycode.CAPS_LOCK , None, Keycode.A, Keycode.S, Keycode.D, Keycode.F, Keycode.G, Keycode.H, Keycode.J, Keycode.K, Keycode.L, Keycode.SEMICOLON, Keycode.QUOTE, Keycode.ENTER, None, Keycode.PAGE_UP ],
                      [ Keycode.LEFT_SHIFT, None, Keycode.Z, Keycode.X, Keycode.C, Keycode.V, Keycode.B, Keycode.N, Keycode.M, Keycode.COMMA, Keycode.PERIOD, Keycode.FORWARD_SLASH, None, Keycode.RIGHT_SHIFT, None, Keycode.PAGE_DOWN ],
                      [ Keycode.LEFT_CONTROL, Keycode.LEFT_GUI, Keycode.LEFT_ALT, None, None, None, Keycode.SPACEBAR, None, None, None, Keycode.RIGHT_ALT, Keycode.RIGHT_GUI, None, Keycode.APPLICATION, Keycode.RIGHT_CONTROL, function_key() ] ],
                    
                    [ [ Keycode.GRAVE_ACCENT, None, None, None, None, None, None, None, None, None, None, None, None, None, None, Keycode.DELETE],
                      [ None, None, None, Keycode.UP_ARROW, None, None, None, None, None, None, None, None, None, None, None, Keycode.PRINT_SCREEN ],
                      [ None, None, Keycode.LEFT_ARROW, Keycode.DOWN_ARROW, Keycode.RIGHT_ARROW, None, None, None, None, None, None, None, None, None, None, ConsumerControlCode.VOLUME_INCREMENT],
                      [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, Keycode.UP_ARROW, ConsumerControlCode.VOLUME_DECREMENT],
                      [ Keycode.LEFT_CONTROL, None, None, None, None, None, Keycode.SPACEBAR, None, None, None, None, None, Keycode.LEFT_ARROW, Keycode.DOWN_ARROW, Keycode.RIGHT_ARROW, function_key() ] ] ]
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

print(Keyboard_Layout)

print("Check Device Ready!")

while(True):

    # Debug LED ON
    led.value = True
    
    print("Starting USB_HID")

    try:
        # start the USB Driver
        keyboard = Keyboard(usb_hid.devices)
        keyboard_layout = KeyboardLayoutUS(keyboard)
        # exit the loop
        break
    except:
        print("Error starting USB_HID")
        # Wait
        time.sleep(.5)
        # Debug LED OFF
        led.value = False
        pass

# Wait
time.sleep(.5)
# Debug LED ON
led.value = False

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

    state_change = False

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
                # check if debounce is > 2
                if (Debouncing_Array[row_pin_number][col_pin_number] >= DEBOUCE_NUMBER):
                    # If it passes the debouce test
                    if ( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], int) ):
                        # Add the keycode to the HID report
                        keyboard._add_keycode_to_report(Keyboard_Layout[LAYER][row_pin_number][col_pin_number])
                        # update state change
                        state_change = True
                    elif( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], MACRO_TYPE) ):
                        # Fire off the macro
                        Keyboard_Layout[LAYER][row_pin_number][col_pin_number].run()
                    elif( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], function_key) ):
                        # time to run the layer code.
                        Keyboard_Layout[LAYER][row_pin_number][col_pin_number].hold_layer(1)
                    else:
                        # unknwon type, pass
                        pass
            else:
                # check if this key was just released
                if(Debouncing_Array[row_pin_number][col_pin_number] != 0):
                    # If it doesn't pass the debouce test, or is no longer pressed
                    if ( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], int) ):
                        # Remove the keycode to the HID report
                        keyboard._remove_keycode_from_report(Keyboard_Layout[LAYER][row_pin_number][col_pin_number])
                        # update state change
                        state_change = True

                    elif( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], MACRO_TYPE) ):
                        # no need to fire off marco
                        pass
                    elif( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], function_key) ):
                        Keyboard_Layout[LAYER][row_pin_number][col_pin_number].hold_layer(0)
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
        except:
            pass

    # Debug LED OFF
    LED_Count += 1
    led.value = False