# Schreibe hier Deinen Code :-)
from machine import Pin, SoftSPI
import epaper4in2b_v2
import framebuf
import gc
from time import sleep_ms


# ---Main---
led=Pin(2,Pin.OUT)
led.on()
print(gc.mem_free())
busy = Pin(25)
rst = Pin(26)
dc = Pin(27)
cs = Pin(15)
miso = Pin(23)
sck = Pin(13)
mosi = Pin(14)
spi = SoftSPI(baudrate=40000000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)

e = epaper4in2b_v2.EPD(spi, cs, dc, rst, busy)
e.init()

w = 400
h = 300
x = 0
y = 0

# --------------------

# use a frame buffer
# 400 * 300 / 8 = 15000 - thats a lot of pixels


buf_black = bytearray(w * h // 8)
buf_red=bytearray(w*h//8)
fb_black = framebuf.FrameBuffer(buf_black, w, h, framebuf.MONO_HLSB)
fb_red = framebuf.FrameBuffer(buf_red, w, h, framebuf.MONO_HLSB)
white = 1
color = 0
while True:
    fb_black.fill(white)
    fb_red.fill(color)
    e.display_frame(buf_black, buf_red)
    sleep_ms(1000)
    e.clear()
    fb_black.fill(color)
    fb_red.fill(white)
    e.display_frame(buf_black, buf_red)
    sleep_ms(1000)
    e.clear()


