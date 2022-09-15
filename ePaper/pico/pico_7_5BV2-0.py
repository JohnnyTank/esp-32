# *****************************************************************************
# * | File        :	  Pico_ePaper-7.5-B.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2021-05-27
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from machine import Pin, SPI
import framebuf
import utime
from math import sin, cos, pi

# Display resolution
EPD_WIDTH       = 800
EPD_HEIGHT      = 480

RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13

DRAW_WHITE = const(0)
DRAW_BLACK = const(1)
DRAW_RED = const(2)

WHITE = const(0xff)
BLACK = const(0x00)
RED = const(0xff)
NO_RED = const(0x00)

class EPD_7in5_B:
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        

        self.buffer_balck = bytearray(self.height * self.width // 8)
        self.buffer_red = bytearray(self.height * self.width // 8)
        self.imageblack = framebuf.FrameBuffer(self.buffer_balck, self.width, self.height, framebuf.MONO_HLSB)
        self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200)   

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)

    def WaitUntilIdle(self):
        print("e-Paper busy")
        while(self.digital_read(self.busy_pin) == 0):   # Wait until the busy_pin goes LOW
            self.delay_ms(20)
        self.delay_ms(20) 
        print("e-Paper busy release")  

    def TurnOnDisplay(self):
        self.send_command(0x12) # DISPLAY REFRESH
        self.delay_ms(100)      #!!!The delay here is necessary, 200uS at least!!!
        self.WaitUntilIdle()
        
    def init(self):
        # EPD hardware init start     
        self.reset()
        
        self.send_command(0x06)     # btst
        self.send_data(0x17)
        self.send_data(0x17)
        self.send_data(0x28)        # If an exception is displayed, try using 0x38
        self.send_data(0x17)
        
#         self.send_command(0x01)  # POWER SETTING
#         self.send_data(0x07)
#         self.send_data(0x07)     # VGH=20V,VGL=-20V
#         self.send_data(0x3f)     # VDH=15V
#         self.send_data(0x3f)     # VDL=-15V
        
        self.send_command(0x04)  # POWER ON
        self.delay_ms(100)
        self.WaitUntilIdle()

        self.send_command(0X00)   # PANNEL SETTING
        self.send_data(0x0F)      # KW-3f   KWR-2F	BWROTP 0f	BWOTP 1f

        self.send_command(0x61)     # tres
        self.send_data(0x03)     # source 800
        self.send_data(0x20)
        self.send_data(0x01)     # gate 480
        self.send_data(0xE0)

        self.send_command(0X15)
        self.send_data(0x00)

        self.send_command(0X50)     # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x11)
        self.send_data(0x07)

        self.send_command(0X60)     # TCON SETTING
        self.send_data(0x22)

        self.send_command(0x65)     # Resolution setting
        self.send_data(0x00)
        self.send_data(0x00)     # 800*480
        self.send_data(0x00)
        self.send_data(0x00)
        
        return 0;

    def Clear(self):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1
        
        self.send_command(0x10) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0xff)
                
        self.send_command(0x13) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0x00)
                
        self.TurnOnDisplay()
        
    def ClearRed(self):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1
        
        self.send_command(0x10) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0xff)
                
        self.send_command(0x13) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0xff)
                
        self.TurnOnDisplay()
        
    def ClearBlack(self):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1
        
        self.send_command(0x10) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0x00)
                
        self.send_command(0x13) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0x00)
                
        self.TurnOnDisplay()
        
    def display(self):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1
        
        # send black data
        self.send_command(0x10) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(self.buffer_balck[i + j * wide])
            
        # send red data
        self.send_command(0x13) 
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(self.buffer_red[i + j * wide])
                
        self.TurnOnDisplay()


    def sleep(self):
        self.send_command(0x02) # power off
        self.WaitUntilIdle()
        self.send_command(0x07) # deep sleep
        self.send_data(0xa5)
    
    def TextBox(self, text, x, y, textColor, boxColor, filled):
        if filled:
            if (boxColor == DRAW_WHITE) or (boxColor == DRAW_BLACK):
                if (boxColor == DRAW_BLACK):
                    self.imageblack.fill_rect(x-2, y-2, len(text)*8+4, 12, BLACK)
                else:
                    self.imageblack.fill_rect(x-2, y-2, len(text)*8+4, 12, WHITE)
            else:
                self.imagered.fill_rect(x-2, y-2, len(text)*8+4, 12, RED)
        else:
            if (boxColor == DRAW_WHITE) or (boxColor == DRAW_BLACK):
                if (boxColor == DRAW_BLACK):
                    self.imageblack.rect(x-2, y-2, len(text)*8+4, 12, BLACK)
                else:
                    self.imagered.rect(x-2, y-2, len(text)*8+4, 12, NO_RED)
            else:
                self.imagered.rect(x-2, y-2, len(text)*8+4, 12, RED)
            
        if (textColor == DRAW_BLACK) or (textColor == DRAW_WHITE):
            if (textColor == DRAW_BLACK):
                self.imageblack.text(text, x, y, BLACK)
                self.imagered.text(text, x, y, NO_RED)
            else:
                self.imagered.text(text, x, y, NO_RED)
                self.imageblack.text(text, x, y, WHITE)
        else:
            self.imagered.text(text, x, y, RED)    
    
    def circle(self, x0, y0, r, color):
        w = 0.0
        while (w <= 2 * pi):
            x = x0+int(r * cos(w))
            y = y0+int(r * sin(w))
            if (color == DRAW_BLACK):
                self.imageblack.pixel(x, y, BLACK)
            elif (color == DRAW_WHITE):
                self.imageblack.pixel(x, y, WHITE)
                self.imagered.pixel(x, y, NO_RED)
            elif (color == DRAW_RED):
                self.imagered.pixel(x, y, RED)
            w += 0.001
    
    def filled_circle(self, x0, y0, radius, color):
        for rr in range (1, radius):
            self.circle(x0, y0, rr, color)
            
    def read_char(self, char):
        f = open('font20/' + str(ord(char)) + '.bin', 'r')
        data = f.read()
        f.close()
        width = int(data[0] + data[1]) # hier könnte man auch über die '-' separatoren arbeiten...
        height = int(data[3] + data[4])
        bitMap = ''
        for i in range (6, len(data)):
            bitMap += data[i]
        return width, height, bitMap
    
    def draw_char(self, char, x, y, color):
        data = self.read_char(char)
        width = data[0]
        height = data [1]
        bitMap = data[2]
        # print(bitMap)
        x_off = x
        y_off = y
        i = 0
        for bit in bitMap:
            if (bit == '1'):
                if (color == DRAW_BLACK):
                    self.imageblack.pixel(x_off, y_off, BLACK)
                elif (color == DRAW_WHITE):
                    self.imageblack.pixel(x_off, y_off, WHITE)
                    self.imagered.pixel(x_off, y_off, NO_RED)
                elif (color == DRAW_RED):
                    self.imagered.pixel(x_off, y_off, RED)
            x_off += 1
            if (x_off >= (x + width)):
                x_off = x
                y_off += 1
                
    def draw_string(self, myStr, x, y, color):
        width = self.read_char(myStr[0])[0]
        i = 0
        for char in myStr:
            if (char != ' '):
                self.draw_char(char, x + i * width, y, color)
            i += 1
    

if __name__=='__main__':
    epd = EPD_7in5_B()
    epd.Clear()
    
    epd.imageblack.fill(WHITE)
    epd.imagered.fill(NO_RED)
    
    epd.TextBox('Bis in die Ewigkeit', 5, 5, DRAW_BLACK, DRAW_BLACK, False)
    epd.TextBox('und noch viel weiter', 170, 5, DRAW_WHITE, DRAW_RED, True)
    epd.TextBox('Bis in die Ewigkeit', 5, 20, DRAW_WHITE, DRAW_BLACK, True)
    epd.TextBox('und noch viel weiter', 170, 20, DRAW_BLACK, DRAW_RED, True)
    epd.circle(400,50,25, DRAW_BLACK)
    epd.circle(460,50,25, DRAW_RED)
    epd.filled_circle(400,110,25, DRAW_BLACK)
    epd.filled_circle(460,110,25, DRAW_RED)
    epd.filled_circle(400,110,20, DRAW_WHITE)
    epd.circle(460,110,20, DRAW_WHITE)
    epd.draw_string('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 5, 40, DRAW_BLACK)
    epd.draw_string('abcdefghijklmnopqrstuvwxyz', 5, 65, DRAW_RED)
    epd.draw_string('0123456789.-+:', 5, 85, DRAW_BLACK)
    
    #epd.imageblack.text("Waveshare", 5, 10, 0x00)
    #epd.imagered.text("Pico_ePaper-7.5-B", 5, 40, 0xff)
    #epd.imageblack.text("Raspberry Pico", 5, 70, 0x00)
    #epd.display()
    #epd.delay_ms(500)
    
    #epd.imageblack.vline(10, 90, 60, 0x00)
    #epd.imageblack.vline(120, 90, 60, 0x00)
    #epd.imagered.hline(10, 90, 110, 0xff)
    #epd.imagered.hline(10, 150, 110, 0xff)
    #epd.imagered.line(10, 90, 120, 150, 0xff)
    #epd.imagered.line(120, 90, 10, 150, 0xff)
    #epd.display()
    #epd.delay_ms(500)
    
    #epd.imageblack.rect(10, 180, 50, 80, 0x00 )
    #epd.imageblack.fill_rect(70, 180, 50, 80,0x00 )
    #epd.imagered.rect(10, 300, 50, 80, 0xff )
    #epd.imagered.fill_rect(70, 300, 50, 80,0xff )
    epd.display()
    epd.delay_ms(500)

    

    # epd.Clear()
    epd.delay_ms(2000)
    print("sleep")
    epd.sleep()

