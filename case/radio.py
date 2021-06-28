#!/usr/bin/python3

import os
import cgitb; cgitb.enable()
import spidev
import busio
import digitalio
import board
from adafruit_bus_device.spi_device import SPIDevice
import RPi.GPIO as GPIO
import time
import adafruit_pcd8544
import requests
import _thread
import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
url = "http://iotessentialsr0800828.hub.ubeac.io/iotesslienhoudenaert"
uid = "iotesslienhoudenaert"

os.system("sudo systemctl start pifi")
os.system("mpc clear")
os.system("mpc load playlist")

#initialize SPI bus
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# initialize control pins for adc
cs0 = digitalio.DigitalInOut(board.CE0) #chip select
adc = SPIDevice(spi, cs0, baudrate= 1000000)

# Initialize display
dc = digitalio.DigitalInOut(board.D23)  # data/command
cs1 = digitalio.DigitalInOut(board.CE1)  # chip select CE1 for display
reset = digitalio.DigitalInOut(board.D24)  # reset
display = adafruit_pcd8544.PCD8544(spi, dc, cs1, reset, baudrate= 1000000)
display.bias = 4
display.contrast = 60
display.invert = True

#  Clear the display.  Always call show after changing pixels to make the display update visible!
display.fill(0)
display.show()
  
# Load default font
# font = ImageFont.load_default()
font=ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf", 10)
font2=ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf", 9)

#get drawing object to draw on image
nummer = 4

#text
image = Image.new('1', (display.width, display.height))
image2 = Image.new('1', (display.width, display.height))

# set max speed
spi.max_speed_hz=(1000000)

#read SPI data 8 possible adc's (0 thru 7)
def readadc(adcnum):
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    with adc:
        r = bytearray(3)
        spi.write_readinto([1,(8+adcnum)<<4,0], r)
        time.sleep(0.000005)
        adcout = ((r[1]&3) << 8) + r[2]
        return adcout
        
# to use raspberry PI GPIO numbers
GPIO.setmode(GPIO.BCM)
#GPIO.setup(17 , GPIO.IN)

def blink(pin1,pin2):
	GPIO.setup(pin1, GPIO.OUT)
	GPIO.setup(pin2, GPIO.OUT)
	GPIO.output(pin1,1)
	GPIO.output(pin2,1)
	
	time.sleep(0.01)
	GPIO.output(pin1,0)
	GPIO.output(pin2,0)
	time.sleep(0.0001)

#open and read the file:
txt = open("/home/pi/channel_count.txt", "r")
i = int(txt.read())

if (i == 1):
    os.system("mpc play 1")
elif (i == 2):
    os.system("mpc play 2")
elif (i == 3):
    os.system("mpc play 3")
elif (i == 4):
    os.system("mpc play 4")
elif (i == 5):
    os.system("mpc play 5")
elif (i == 6):
    os.system("mpc play 6")
    
oldChannel = 0
oldVolume = -1
volume = readadc(1) # read channel 1
vol = round((volume/10.23))
vol = vol - 100
vol = abs(vol)

def ubeac(): 
    
    while True:
        # read the mpc volume and store it in an int   
        disVol=os.popen("mpc volume",'r')

        disVol = disVol.readline()
        disVol = str(disVol)
        maxVol = "100"

        if maxVol in disVol:
            disVol = disVol.partition("volume:")[2]
        else: 
            disVol = disVol.partition("volume: ")[2]

        disVol = disVol.partition("%")[0]        
        disVol = int(disVol)
        
        chan = i  
        
        data= {
            "id": uid,
            "sensors":[{
                'id': 'adc kanaal0',
                'data': chan
            },
            {
                'id': 'adc kanaal1',
                'data': disVol
            }]
        }
        r = requests.post(url, verify=False,  json=data)
        #break

# initiate timer from 60 sec when volume is 0 for 10 seconds, until volume is changed
def countdown(): 
   
        sec = 0
        t = 60
        volume = readadc(1) # read channel 1
        oldVolume = volume
    
        # read the mpc volume and store it in an int   
        disVol=os.popen("mpc volume",'r')

        disVol = disVol.readline()
        disVol = str(disVol)
        maxVol = "100"

        if maxVol in disVol:
            disVol = disVol.partition("volume:")[2]
        else: 
            disVol = disVol.partition("volume: ")[2]

        disVol = disVol.partition("%")[0]
                
        disVol = int(disVol)         
        
        for x in range(10):
            
            volume = readadc(1) # read channel 1
            
            # keep volume steady when not turning on volume dail
            while (oldVolume != volume and oldVolume+1 != volume and oldVolume-1 != volume and oldVolume+2 != volume and oldVolume-2 != volume and oldVolume+3 != volume and oldVolume-3 != volume and oldVolume+4 != volume and oldVolume-4 != volume and oldVolume+5 != volume and oldVolume-5 != volume and oldVolume+6 != volume and oldVolume-6 != volume and oldVolume+7 != volume and oldVolume-7 != volume and oldVolume+8 != volume and oldVolume-8 != volume and oldVolume+9 != volume and oldVolume-9 != volume and oldVolume+10 != volume and oldVolume-10 != volume): 
            
                vol = round((volume/10.23))
                vol = vol - 100
                vol = abs(vol)
                os.system("mpc volume %s"%vol)
                oldVolume = volume
            
            # read the mpc volume and store it in an int   
            disVol=os.popen("mpc volume",'r')

            disVol = disVol.readline()
            disVol = str(disVol)
            maxVol = "100"

            if maxVol in disVol:
                disVol = disVol.partition("volume:")[2]
            else: 
                disVol = disVol.partition("volume: ")[2]

            disVol = disVol.partition("%")[0]
                    
            disVol = int(disVol)

            if (disVol == 0):   
                sec = sec + 1
                print(sec)
                time.sleep(1)       
            else:
                break            
                
        if (sec == 10):
            
            while (disVol == 0):            
            
                while t: # while t > 0 for clarity 
                
                    mins = t // 60
                    secs = t % 60
                    timer = '{:02d}:{:02d}'.format(mins, secs)
                    print(timer, end="\r") # overwrite previous line 
                    time.sleep(1)
                    t -= 1
                    
                    draw = ImageDraw.Draw(image)
                    draw.rectangle((0,0,display.width, display.height), outline = 255, fill=255)
                    
                    draw.text((1,2), (str("Shutting down")), font = font)
                    draw.text((1,12), (str("in %s"%timer)), font = font)
                    draw.text((1,26), (str("Turn volume up")), font = font2)
                    draw.text((1,34), (str("to stop shutdown")), font = font2)

                    display.image(image)
                    display.show()
                    
                    volume = readadc(1) # read channel 1
                    
                    # keep volume steady when not turning on volume dail
                    while (oldVolume != volume and oldVolume+1 != volume and oldVolume-1 != volume and oldVolume+2 != volume and oldVolume-2 != volume and oldVolume+3 != volume and oldVolume-3 != volume and oldVolume+4 != volume and oldVolume-4 != volume and oldVolume+5 != volume and oldVolume-5 != volume and oldVolume+6 != volume and oldVolume-6 != volume and oldVolume+7 != volume and oldVolume-7 != volume and oldVolume+8 != volume and oldVolume-8 != volume and oldVolume+9 != volume and oldVolume-9 != volume and oldVolume+10 != volume and oldVolume-10 != volume): 
                        vol = round((volume/10.23))
                        vol = vol - 100
                        vol = abs(vol)
                        os.system("mpc volume %s"%vol)
                        oldVolume = volume
                    
                    voltext = "volume = %s"%disVol
                    draw.text((1,24), (str(voltext)), font = font)
                    
                    break
                
                # read the mpc volume and store it in an int   
                disVol=os.popen("mpc volume",'r')

                disVol = disVol.readline()
                disVol = str(disVol)
                maxVol = "100"

                if maxVol in disVol:
                    disVol = disVol.partition("volume:")[2]
                else: 
                    disVol = disVol.partition("volume: ")[2]

                disVol = disVol.partition("%")[0]       
                disVol = int(disVol)
                
                if (t == 0):
                    os.system ("sudo shutdown now")
                    break
                
               
try:
    
    #start ubeac thread
    _thread.start_new_thread(ubeac, ())
     
    
    while True:
        
        channel = readadc(0) # read channel 0
        volume = readadc(1) # read channel 1
        
        # keep volume steady when not turning on volume dail
        while (oldVolume != volume and oldVolume+1 != volume and oldVolume-1 != volume and oldVolume+2 != volume and oldVolume-2 != volume and oldVolume+3 != volume and oldVolume-3 != volume and oldVolume+4 != volume and oldVolume-4 != volume and oldVolume+5 != volume and oldVolume-5 != volume and oldVolume+6 != volume and oldVolume-6 != volume and oldVolume+7 != volume and oldVolume-7 != volume and oldVolume+8 != volume and oldVolume-8 != volume and oldVolume+9 != volume and oldVolume-9 != volume and oldVolume+10 != volume and oldVolume-10 != volume):        
            vol = round((volume/10.23))
            vol = vol - 100
            vol = abs(vol)
            os.system("mpc volume %s"%vol)
            oldVolume = volume
            break
         
        # read the mpc volume and store it in an int        
        disVol=os.popen("mpc volume",'r')

        disVol = disVol.readline()
        disVol = str(disVol)
        maxVol = "100"

        if maxVol in disVol:
            disVol = disVol.partition("volume:")[2]
        else: 
            disVol = disVol.partition("volume: ")[2]

        disVol = disVol.partition("%")[0]         
        disVol = int(disVol)
        
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,display.width, display.height), outline = 255, fill=255)
        
        # read station that is currently playing
        f =os.popen("mpc current")
        station = " "
        for s in f.readlines():
            station += s 

        text = station.partition("http://playerservices.streamtheworld.com/api/livestream-redirect/")[2]
        text = text.partition(".mp3")[0]
        
        voltext = "volume = %s"%disVol
        chantext = "channel = %s"%channel
        ip = "192.168.0.10"
        
        draw.text((1,0), (str(text)), font=font)
        draw.text((1,24), (str(voltext)), font = font)
        draw.text((1,34), (str(ip)), font = font)
            
        display.image(image)
        display.show()
        
        # countdown function
        countdown()
        
        while (channel >= 492 and channel <= 532):
            oldChannel = 512
            break
        # check the i value when already on 6, you can't go a channel to the right anymore
        if (i < 6 and i >= 1):         
            if (channel == 0 and oldChannel == 512):
                for x in range(64):
                    blink(17,27),
                    blink(27,22),
                    blink(22,25),
                    blink(25,17)
                oldChannel = channel
                i = i + 1
                
                # clear the playlist from the webinterface and load the playlist again
                os.system("mpc clear")
                os.system("mpc load playlist")
                if (i==1):
                    os.system("mpc play 1")
                elif (i==2):
                    os.system("mpc play 2")
                elif (i==3):
                    os.system("mpc play 3")
                elif (i==4):
                    os.system("mpc play 4")
                elif (i==5):
                    os.system("mpc play 5")
                elif (i==6):
                    os.system("mpc play 6")
                
                # write i to .txt file, in order for the radio to remember the last played station before shutdown               
                stri = str(i)
                txt = open("/home/pi/channel_count.txt", "w")
                txt.write(stri)
                txt.close()
                
        # check the i value when already on 1, you can't go a channel to the left anymore
        if (i <= 6 and i > 1):
            if (channel == 1023 and oldChannel == 512):
                for x in range(64):
                    blink(25,17),
                    blink(22,25),
                    blink(27,22),
                    blink(17,27)
                oldChannel = channel
                i = i - 1
                
                # clear the playlist from the webinterface and load the playlist again
                oldChannel = channel
                os.system("mpc clear")
                os.system("mpc load playlist")
                if (i==1):
                    os.system("mpc play 1")
                elif (i==2):
                    os.system("mpc play 2")
                elif (i==3):
                    os.system("mpc play 3")
                elif (i==4):
                    os.system("mpc play 4")
                elif (i==5):
                    os.system("mpc play 5")
                elif (i==6):
                    os.system("mpc play 6")
                
                # write i to .txt file, in order for the radio to remember the last played station before shutdown                
                stri = str(i)
                txt = open("/home/pi/channel_count.txt", "w")
                txt.write(stri)
                txt.close()
        

except KeyboardInterrupt:
    stri = str(i)
    txt = open("/home/pi/channel_count.txt", "w")
    txt.write(stri)
    txt.close()
    os.system("mpc stop")	
    print("Program stopped")			
    GPIO.cleanup()
