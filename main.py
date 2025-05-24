from gpiozero import OutputDevice
from time import sleep

LCD_RS=OutputDevice(25)
LCD_E=OutputDevice(24)
LCD_D4=OutputDevice(23)
LCD_D5=OutputDevice(18)
LCD_D6=OutputDevice(15)
LCD_D7=OutputDevice(14)

LCD_WIDTH=16
LCD_CHR=True
LCD_CMD=False
LCD_LINE_1=0x80
LCD_LINE_2=0xC0

E_PULSE=0.0005
E_DELAY=0.0005

def lcd_init():
    lcd_byte(0x33,LCD_CMD)
    lcd_byte(0x32,LCD_CMD)
    lcd_byte(0x28,LCD_CMD)
    lcd_byte(0x0C,LCD_CMD)
    lcd_byte(0x06,LCD_CMD)
    lcd_byte(0x01,LCD_CMD)
    sleep(E_DELAY)
    
def lcd_byte(bits,mode):
    LCD_RS.value = mode
    
    LCD_D4.off()
    LCD_D5.off()
    LCD_D6.off()
    LCD_D7.off()
    
    if bits & 0x10:
        LCD_D4.on()
    if bits & 0x20:
        LCD_D5.on()
    if bits & 0x40:
        LCD_D6.on()
    if bits & 0x80:
        LCD_D7.on()
        
    lcd_toggle_enable()
    
    LCD_D4.off()
    LCD_D5.off()
    LCD_D6.off()
    LCD_D7.off()
    
    
    if bits & 0x01:
        LCD_D4.on()
    if bits & 0x02:
        LCD_D5.on()
    if bits & 0x04:
        LCD_D6.on()
    if bits & 0x08:
        LCD_D7.on()
    
    lcd_toggle_enable()
    
def lcd_toggle_enable():
    sleep(E_DELAY)
    LCD_E.on()
    sleep(E_PULSE)
    LCD_E.off()
    sleep(E_DELAY)
    
def lcd_string(message,line):
    message = message.ljust(LCD_WIDTH," ")
    lcd_byte(line,LCD_CMD)
    
    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]),LCD_CHR)

def read_file(filepath):
    with open(filepath,'r') as file:
        content = file.read()
    return content.split(",")


if __name__=='__main__':
    lcd_init()
    c = read_file("./names.txt")
    while True:
        for i in range(len(c)):
            lcd_string(c[i].split(" ")[0],LCD_LINE_1)
            lcd_string(c[i].split(" ")[1]+" "+c[i].split(" ")[2],LCD_LINE_2)
            sleep(3)
            
    
