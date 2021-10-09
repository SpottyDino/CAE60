import time
import _hid
from micropython import const
from machine import Pin
from Keycode import Keycode

_MAX_KEYPRESS = 6

# Globals
LED_BLINK = 100
DEBOUCE_NUMBER = 3
MATRIX_SCAN = 0.0001
LAYER = 0

# keyboard class
class Keyboard:
    # init the class
    def __init__(self):
        # setup the hid report array
        self.hid_report = bytearray(8)
        
        # View onto byte 0 in report.
        #self.report_modifier = memoryview(self.hid_report)[0:1]
        self.report_modifier = [0]


        # List of regular keys currently pressed.
        # View onto bytes 2-7 in report.
        self.report_keys = [0,0,0,0,0,0]
        self.past_report_keys = [0,0,0,0,0,0]

        # Clear HID on start
        try:
            self.release_all()
        except OSError:
            time.sleep(1)
            self.release_all()
    
    def release_all(self):
        """Release all pressed keys."""
        for i in range(8):
            self.hid_report[i] = 0
        _hid.keypress(self.report_modifier[0],self.report_keys)
        
    def _add_keycode_to_report(self, keycode):
        """Add a single keycode to the USB HID report."""
        
        print("Adding: {0}".format(keycode))
        
        modifier = Keycode.modifier_bit(keycode)
        if modifier:
            # Set bit for this modifier.
            self.report_modifier[0] |= modifier
        else:
            # Don't press twice.
            for i in range(_MAX_KEYPRESS):
                if self.report_keys[i] == keycode:
                    # Already pressed.
                    return
            # Put keycode in first empty slot.
            for i in range(_MAX_KEYPRESS):
                if self.report_keys[i] == 0:
                    self.report_keys[i] = keycode
                    return
            # All slots are filled.
            raise ValueError("Trying to press more than six keys at once.")
    
    def _remove_keycode_from_report(self, keycode):
        """Remove a single keycode from the report."""
        
        print("Removing: {0}".format(keycode))
        
        modifier = Keycode.modifier_bit(keycode)
        if modifier:
            # Turn off the bit for this modifier.
            self.report_modifier[0] &= ~modifier
        else:
            # Check all the slots, just in case there's a duplicate. (There should not be.)
            for i in range(_MAX_KEYPRESS):
                if self.report_keys[i] == keycode:
                    self.report_keys[i] = 0

led_onboard = Pin(25, Pin.OUT)

keyboard_cols = [ 0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18 ]
keyboard_rows = [ 19, 20, 21, 22, 26 ]

# The Pin Matrix
keyboard_cols_array = []
keyboard_rows_array = []

# Make all col pin objects inputs with pullups
for pin in keyboard_cols:
    key_pin = Pin(pin, Pin.OUT)
    key_pin.value(0)
    keyboard_cols_array.append(key_pin)
    
# Make all row pin objects inputs with pullups
for pin in keyboard_rows:
    key_pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
    keyboard_rows_array.append(key_pin)

print(keyboard_cols_array)
print(keyboard_rows_array)

# Keyboard Layout
Keyboard_Layout = [ [ [ Keycode.GRAVE_ACCENT, Keycode.ONE, Keycode.TWO, Keycode.THREE, Keycode.FOUR, Keycode.FIVE, Keycode.SIX, Keycode.SEVEN, Keycode.EIGHT, Keycode.NINE, Keycode.ZERO, Keycode.MINUS, Keycode.EQUALS, None, Keycode.BACKSLASH, Keycode.ONE ],
                      [ Keycode.TAB, None, Keycode.Q, Keycode.W, Keycode.E, Keycode.R, Keycode.T, Keycode.Y, Keycode.U, Keycode.I, Keycode.O, Keycode.P, Keycode.LEFT_BRACKET, Keycode.RIGHT_BRACKET, Keycode.BACKSLASH, Keycode.TWO ],
                      [ Keycode.CAPS_LOCK , None, Keycode.A, Keycode.S, Keycode.D, Keycode.F, Keycode.G, Keycode.H, Keycode.J, Keycode.K, Keycode.L, Keycode.SEMICOLON, Keycode.QUOTE, Keycode.ENTER, None, Keycode.THREE ],
                      [ Keycode.LEFT_SHIFT, None, Keycode.Z, Keycode.X, Keycode.C, Keycode.V, Keycode.B, Keycode.N, Keycode.M, Keycode.COMMA, Keycode.PERIOD, Keycode.FORWARD_SLASH, None, Keycode.RIGHT_SHIFT, None, Keycode.FOUR ],
                      [ Keycode.LEFT_CONTROL, Keycode.LEFT_GUI, Keycode.LEFT_ALT, None, None, None, Keycode.SPACEBAR, None, None, None, Keycode.RIGHT_ALT, Keycode.RIGHT_GUI, None, Keycode.APPLICATION, Keycode.RIGHT_CONTROL, None ] ],
                    
                    [ [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                      [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                      [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                      [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                      [ None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None] ] ]

# Debouncing Array
Debouncing_Array = [[ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

# create the Keyboard
keyboard = Keyboard()

# Status LED
LED_Count = 0
# Main Loop
while True:

    if(LED_Count == LED_BLINK):
        # Debug LED ON
        led_onboard.value(1)
        LED_Count = 0

    state_change = False

    # Scan Rows
    col_pin_number = 0
    # Set all Rows
    for col in keyboard_cols_array: 
        # Set the pin to High
        col.value(1)
        # Scan Cols
        row_pin_number = 0
        # Read all Cols
        for row in keyboard_rows_array:
            # Check if the col is low
            if ( row.value() == 1 ):
                # If the pin is low, add to debouce array
                Debouncing_Array[row_pin_number][col_pin_number] += 1
                # check if debounce is > 2
                if (Debouncing_Array[row_pin_number][col_pin_number] >= DEBOUCE_NUMBER):
                    # If it passes the debouce test
                    if ( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], int) ):
                        # Add the keycode to the HID report
                        keyboard._add_keycode_to_report(Keyboard_Layout[LAYER][row_pin_number][col_pin_number])
                    elif( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], MACRO_TYPE) ):
                        # Fire off the macro
                        Keyboard_Layout[LAYER][row_pin_number][col_pin_number].run()
                    elif( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], function_key) ):
                        # time to run the layer code.
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
                        keyboard._remove_keycode_from_report(Keyboard_Layout[LAYER][row_pin_number][col_pin_number])
                    elif( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], MACRO_TYPE) ):
                        # no need to fire off marco
                        pass
                    elif( isinstance(Keyboard_Layout[LAYER][row_pin_number][col_pin_number], function_key) ):
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
        col.value(0)   


    #if(keyboard.past_report_keys != keyboard.report_keys):
    # Only if there is a HID Report change Send report
    print("sending: {0}".format(keyboard.report_keys))
    _hid.keypress(keyboard.report_modifier[0],keyboard.report_keys)
    keyboard.past_report_keys = keyboard.report_keys

    # Debug LED OFF
    LED_Count += 1
    led_onboard.value(0)