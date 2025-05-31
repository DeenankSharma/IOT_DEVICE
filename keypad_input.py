import RPi.GPIO as GPIO
import time

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define the GPIO pins for rows and columns
ROWS = [3,5,6,13]  # GPIO pins for rows
COLS = [19,26,21,20]   # GPIO pins for columns

# Define the keypad layout (what each button represents)
KEYPAD = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'], 
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

def setup_keypad():
    """Initialize the GPIO pins for the keypad"""
    # Set up row pins as outputs
    for row_pin in ROWS:
        GPIO.setup(row_pin, GPIO.OUT)
        GPIO.output(row_pin, GPIO.LOW)  # Start with all rows LOW
    
    # Set up column pins as inputs with pull-down resistors
    for col_pin in COLS:
        GPIO.setup(col_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def scan_keypad():
    """Scan the keypad and return the pressed key, or None if no key is pressed"""
    for row_index, row_pin in enumerate(ROWS):
        # Set current row to HIGH
        GPIO.output(row_pin, GPIO.HIGH)
        
        # Check each column
        for col_index, col_pin in enumerate(COLS):
            if GPIO.input(col_pin) == GPIO.HIGH:
                # Key is pressed - get the corresponding character
                key = KEYPAD[row_index][col_index]
                
                # Wait for key release to avoid multiple readings
                while GPIO.input(col_pin) == GPIO.HIGH:
                    time.sleep(0.01)
                
                # Set row back to LOW before returning
                GPIO.output(row_pin, GPIO.LOW)
                return key
        
        # Set current row back to LOW
        GPIO.output(row_pin, GPIO.LOW)
    
    return None  # No key pressed

def take_input():
    """Main program loop"""
    print("4x4 Matrix Keypad Reader")
    print("Press keys on the keypad. Press Ctrl+C to exit.")
    print("-" * 40)
    
    setup_keypad()
    
    try:
        while True:
            key = scan_keypad()
            if key:
                print(f"Key pressed: {key}")
                
                # Example: Do something based on which key was pressed
                if key == 'A':
                    print("  -> Button A pressed! Doing special action A")
                elif key == 'B':
                    print("  -> Button B pressed! Doing special action B")
                elif key == '*':
                    print("  -> Star key pressed!")
                elif key == '#':
                    print("  -> Hash key pressed!")
                elif key.isdigit():
                    print(f"  -> Number {key} pressed!")
            
            time.sleep(0.1)  # Small delay to prevent excessive CPU usage
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Clean up GPIO pins
        GPIO.cleanup()
take_input()
