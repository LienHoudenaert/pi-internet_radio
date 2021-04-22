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
#uid = "0749a8fc-a841-44ef-8dce-741dfaa367e8"

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
font2=ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf", 11)

#get drawing object to draw on image
nummer = 4

#text
image = Image.new('1', (display.width, display.height))

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
f = open("channel_count.txt", "r")
i = int(f.read())

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

def ubeac(): 
    
        while True:
            #channel = readadc(0) # read channel 0
            volume = readadc(1) # read channel 1
            
            chan = i  
            vol = round((volume/10.23))
            
            data= {
                "id": uid,
                "sensors":[{
                    'id': 'adc kanaal0',
                    'data': chan
                },
                {
                    'id': 'adc kanaal1',
                    'data': vol
                }]
            }
            r = requests.post(url, verify=False,  json=data)
            #break
t = 60
sec = 0

def countdown():
           
    if (sec >= 10):
    
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        #print(timer, end="\r")
        time.sleep(1)
        t = t - 1
        
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,display.width, display.height), outline = 255, fill=255)
        
        draw.text((1,20), (str(timer, end="\r")), font = font)

        display.image(image)
        display.show()

try:
    
    _thread.start_new_thread(ubeac, ())
        
    while True:
    
        channel = readadc(0) # read channel 0
        volume = readadc(1) # read channel 1
        
        while (oldVolume != volume and oldVolume+1 != volume and oldVolume-1 != volume and oldVolume+2 != volume and oldVolume-2 != volume and oldVolume+3 != volume and oldVolume-3 != volume and oldVolume+4 != volume and oldVolume-4 != volume and oldVolume+5 != volume and oldVolume-5 != volume and oldVolume+6 != volume and oldVolume-6 != volume):        
            vol = round((volume/10.23))
            os.system("mpc volume %s"%vol)
            oldVolume = volume
            break
        
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
        
        f =os.popen("mpc current")
        station = " "
        for s in f.readlines():
            station += s 

        text = station.partition("http://playerservices.streamtheworld.com/api/livestream-redirect/")[2]
        text = text.partition(".mp3")[0]
        
        length = len(text)
        voltext = "volume = %s"%disVol
        chantext = "channel = %s"%channel
        ip = "192.168.0.10"
        
        if (length > 12): 
            a,b = text.split(" ",1)
            draw.text((1,0), (str(a)), font=font)
            draw.text((1,8), (str(b)), font=font)
            draw.text((1,24), (str(voltext)), font = font)
            draw.text((1,34), (str(ip)), font = font)
            
        else:
            draw.text((1,0), (str(text)), font=font)
            draw.text((1,24), (str(voltext)), font = font)
            draw.text((1,34), (str(ip)), font = font)
            
        display.image(image)
        display.show()
         
        while (channel >= 492 and channel <= 532):
            oldChannel = 512
            break
        if (i < 6 and i >= 1):         
            if (channel == 0 and oldChannel == 512):
                for x in range(64):
                    blink(17,27),
                    blink(27,22),
                    blink(22,25),
                    blink(25,17)
                oldChannel = channel
                os.system("mpc clear")
                os.system("mpc load playlist")
                i = i + 1
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
                    
                stri = str(i)
                f = open("channel_count.txt", "w")
                f.write(stri)
                f.close()
                
        
        if (i <= 6 and i > 1):
            if (channel == 1023 and oldChannel == 512):
                for x in range(64):
                    blink(25,17),
                    blink(22,25),
                    blink(27,22),
                    blink(17,27)
                oldChannel = channel
                i = i - 1
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
                    
                stri = str(i)
                f = open("channel_count.txt", "w")
                f.write(stri)
                f.close()
        
        
        while (vol == 0):
        
            time.sleep(1)
            sec = sec + 1      
            _thread.start_new_thread(countdown, ())

except KeyboardInterrupt:
    stri = str(i)
    f = open("channel_count.txt", "w")
    f.write(stri)
    f.close()
    os.system("mpc stop")	
    print("Program stopped")			
    GPIO.cleanup()
    #os.system("sudo shutdown now")
