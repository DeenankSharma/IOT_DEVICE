import time
from gpiozero import OutputDevice, InputDevice
from time import sleep
import requests
from dotenv import load_dotenv 
import os

load_dotenv()

fu_url = os.getenv("FU_URL")
at_url = os.getenv("AT_URL")
key_url = os.getenv("KEY_URL")


ROWS = [3,5,6,13]  # rows ki GPIO pins
COLS = [19,26,21,20]   # cols ki GPIO pins
KEYPAD = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'], 
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

LCD_RS_PIN = 25
LCD_E_PIN = 24
LCD_D4_PIN = 23
LCD_D5_PIN = 18
LCD_D6_PIN = 15
LCD_D7_PIN = 14

LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

STATE_DISPLAY_NAMES = 0
STATE_MENU = 1
STATE_ENTER_ENR = 2
STATE_PROCESSING = 3

def update_attendance(enrollment_num):
    print(str(enrollment_num))
    response = requests.post(str(at_url),data={"rollno":str(enrollment_num)})
    sleep(5)
    
def update_key_holder(enrollment_num):
    print(str(enrollment_num))
    response = requests.post(str(key_url),data={"rollno":str(enrollment_num)})
    sleep(5)

class KeypadLCDSystem:
    def __init__(self):
        self.current_state = STATE_DISPLAY_NAMES
        self.selected_option = None
        self.enrollment_number = ""
        self.names = []
        self.current_name_index = 0
        self.last_name_display_time = 0
        self.name_display_interval = 6  # seconds
        
        self.row_pins = []
        self.col_pins = []
        self.lcd_rs = None
        self.lcd_e = None
        self.lcd_d4 = None
        self.lcd_d5 = None
        self.lcd_d6 = None
        self.lcd_d7 = None
        
    def setup_keypad(self):
        """Initialize the GPIO pins for the keypad"""

        for pin in ROWS:
            row_device = OutputDevice(pin, initial_value=False)
            self.row_pins.append(row_device)
        for pin in COLS:
            col_device = InputDevice(pin, pull_up=False)
            self.col_pins.append(col_device)

    def scan_keypad(self):
        """Scan the keypad and return the pressed key, or None if no key is pressed"""
        for row_index, row_pin in enumerate(self.row_pins):
            row_pin.on()
            time.sleep(0.001)
            for col_index, col_pin in enumerate(self.col_pins):
                if col_pin.is_active:
                    
                    key = KEYPAD[row_index][col_index]
                    
           
                    while col_pin.is_active:
                        time.sleep(0.01)
                    row_pin.off()
                    return key
            
           
            row_pin.off()
        
        return None 

    def setup_lcd(self):
        """Initialize LCD GPIO pins"""
        self.lcd_rs = OutputDevice(LCD_RS_PIN)
        self.lcd_e = OutputDevice(LCD_E_PIN)
        self.lcd_d4 = OutputDevice(LCD_D4_PIN)
        self.lcd_d5 = OutputDevice(LCD_D5_PIN)
        self.lcd_d6 = OutputDevice(LCD_D6_PIN)
        self.lcd_d7 = OutputDevice(LCD_D7_PIN)

    def lcd_init(self):
        """Initialize the LCD"""
        self.lcd_byte(0x33, LCD_CMD)
        self.lcd_byte(0x32, LCD_CMD)
        self.lcd_byte(0x28, LCD_CMD)
        self.lcd_byte(0x0C, LCD_CMD)
        self.lcd_byte(0x06, LCD_CMD)
        self.lcd_byte(0x01, LCD_CMD)
        sleep(E_DELAY)
        
    def lcd_byte(self, bits, mode):
        """Send byte to LCD"""
        self.lcd_rs.value = mode
        
        
        self.lcd_d4.off()
        self.lcd_d5.off()
        self.lcd_d6.off()
        self.lcd_d7.off()
        
        if bits & 0x10:
            self.lcd_d4.on()
        if bits & 0x20:
            self.lcd_d5.on()
        if bits & 0x40:
            self.lcd_d6.on()
        if bits & 0x80:
            self.lcd_d7.on()
            
        self.lcd_toggle_enable()
        
        
        self.lcd_d4.off()
        self.lcd_d5.off()
        self.lcd_d6.off()
        self.lcd_d7.off()
        
        if bits & 0x01:
            self.lcd_d4.on()
        if bits & 0x02:
            self.lcd_d5.on()
        if bits & 0x04:
            self.lcd_d6.on()
        if bits & 0x08:
            self.lcd_d7.on()
        
        self.lcd_toggle_enable()
        
    def lcd_toggle_enable(self):
        """Toggle enable pin"""
        sleep(E_DELAY)
        self.lcd_e.on()
        sleep(E_PULSE)
        self.lcd_e.off()
        sleep(E_DELAY)
        
    def lcd_string(self, message, line):
        """Display string on LCD"""
        message = message.ljust(LCD_WIDTH, " ")
        self.lcd_byte(line, LCD_CMD)
        
        for i in range(LCD_WIDTH):
            self.lcd_byte(ord(message[i]), LCD_CHR)

    def lcd_clear(self):
        """Clear LCD screen"""
        self.lcd_byte(0x01, LCD_CMD)
        sleep(E_DELAY)

    def fetch_names(self):
        """Fetch names from API"""
        try:
            url = str(fu_url)  # Add your URL here
            response = requests.get(url=url)
            sleep(3)
            data = response.json()
            return data["rows"]
        except Exception as e:
            print(f"Warning: Failed to fetch data from API. Error: {e}")
            print("Using sample data.")
            return [
                {"enrollment_num": "23115042", "slack_name": "satoshi", "bhawan": "JB"},
                #{"enrollment_num": "23116101", "slack_name": "rhapsody", "bhawan": "KB"},
                #{"enrollment_num": "24112044", "slack_name": "smurf", "bhawan": "SB"}
            ]

    def display_current_name(self):
        """Display current name from the list"""
        if self.names:
            current_person = self.names[self.current_name_index]
            
            # slack name ki display line
            name = current_person.get("slack_name", "Unknown")
            self.lcd_string(name, LCD_LINE_1)
            
            # bhawan + enrollment_num
            bhawan = current_person.get("bhawan", "")
            enrollment = current_person.get("enrollment_num", "")
            second_line = f"{bhawan} {enrollment}"
            self.lcd_string(second_line, LCD_LINE_2)

    def display_menu(self):
        """Display menu options"""
        self.lcd_string("Select option:", LCD_LINE_1)
        self.lcd_string("B:In/Out C:Keys D", LCD_LINE_2)

    def display_enrollment_input(self):
        """Display enrollment number input screen"""
        if self.selected_option == 'B':
            self.lcd_string("Enter enr no:", LCD_LINE_1)
        elif self.selected_option == 'C':
            self.lcd_string("Who has keys?", LCD_LINE_1)
        
        display_enr = self.enrollment_number[-16:] if len(self.enrollment_number) > 16 else self.enrollment_number
        self.lcd_string(display_enr, LCD_LINE_2)

    def handle_in_out_function(self, enrollment_number):
        """Handle the in/out functionality"""
        print(f"Processing in/out for enrollment: {enrollment_number}")
        self.lcd_string("Processing...", LCD_LINE_1)
        self.lcd_string("In/Out logged", LCD_LINE_2)
        update__attendance(enrollment_number)
        sleep(4)
        
        
    def handle_keys_function(self, enrollment_number):
        """Handle the keys functionality"""
        print(f"Processing keys for enrollment: {enrollment_number}")
        self.lcd_string("Processing...", LCD_LINE_1)
        self.lcd_string("Keys logged", LCD_LINE_2)
        update_key_holder(enrollment_number)
        sleep(4)
        self.names = self.fetch_names()
        sleep(2)
        
    def cleanup(self):
        """Clean up GPIO resources"""
        try:
            for pin in self.row_pins:
                pin.close()
            
            for pin in self.col_pins:
                pin.close()
            
            
            if self.lcd_rs:
                self.lcd_rs.close()
            if self.lcd_e:
                self.lcd_e.close()
            if self.lcd_d4:
                self.lcd_d4.close()
            if self.lcd_d5:
                self.lcd_d5.close()
            if self.lcd_d6:
                self.lcd_d6.close()
            if self.lcd_d7:
                self.lcd_d7.close()
        except Exception as e:
            print(f"Cleanup error: {e}")

    def run(self):
        """Main program loop"""
        print("Keypad LCD System Starting...")
        print("Press Ctrl+C to exit.")
        
        try:
            self.setup_keypad()
            self.setup_lcd()
            self.lcd_init()
            
            self.names = self.fetch_names()
            self.last_name_display_time = 0
            
            while True:
                current_time = time.time()
                key = self.scan_keypad()
                
                if self.current_state == STATE_DISPLAY_NAMES:
            
                    if current_time - self.last_name_display_time >= self.name_display_interval:
                        self.current_name_index = (self.current_name_index + 1) % len(self.names)
                        self.display_current_name()
                        self.last_name_display_time = current_time
                    elif self.last_name_display_time == 0:
                        self.display_current_name()
                        self.last_name_display_time = current_time
                    
                    if key == 'A':
                        self.current_state = STATE_MENU
                        self.display_menu()
                        print("Menu activated")
                
                elif self.current_state == STATE_MENU:
                    if key in ['B', 'C']:
                        self.selected_option = key
                        self.current_state = STATE_ENTER_ENR
                        self.enrollment_number = ""
                        self.display_enrollment_input()
                        print(f"Option {key} selected, waiting for enrollment number")
                    elif key == 'D':
                        self.current_state = STATE_DISPLAY_NAMES
                        self.current_name_index = 0
                        self.last_name_display_time = time.time()
                        self.display_current_name()
                        print("Returning to name display")
                
                elif self.current_state == STATE_ENTER_ENR:
                    if key and key.isdigit():
                        self.enrollment_number += key
                        self.display_enrollment_input()
                        print(f"Enrollment number: {self.enrollment_number}")
                    elif key == '#':  
                        if self.enrollment_number:
                            print(f"Processing enrollment: {self.enrollment_number}")
                            if self.selected_option == 'B':
                                self.handle_in_out_function(self.enrollment_number)
                            elif self.selected_option == 'C':
                                self.handle_keys_function(self.enrollment_number)
                            
                            self.current_state = STATE_DISPLAY_NAMES
                            self.current_name_index = 0
                            self.last_name_display_time = time.time()
                            self.display_current_name()
                            self.enrollment_number = ""
                            self.selected_option = None
                    elif key == '*': 
                        if self.enrollment_number:
                            self.enrollment_number = self.enrollment_number[:-1]
                            self.display_enrollment_input()
                        else:
                            self.current_state = STATE_MENU
                            self.display_menu()
                    elif key == 'D': 
                        self.current_state = STATE_DISPLAY_NAMES
                        self.current_name_index = 0
                        self.last_name_display_time = time.time()
                        self.display_current_name()
                        self.enrollment_number = ""
                        self.selected_option = None
                        print("Cancelled, returning to name display")
                
                time.sleep(0.05) 
                
        except KeyboardInterrupt:
            print("\nExiting...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.lcd_clear()
            self.cleanup()

if __name__ == '__main__':
    system = KeypadLCDSystem()
    system.run()
