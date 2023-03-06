# boot.py - Built from picow_boot_template_with_comments.py

# IMPORTS
# From references to Python best practices, I use FROM to only import the functions
# needed to keep space down.
from time import localtime, sleep
from pimoroni import RGBLED 
from machine import reset_cause, Pin
from sys import print_exception, exit
from rp2 import country
from network import WLAN, STA_IF
from log_time import log_time
from set_rtc import set_rtc
#https://www.tomshardware.com/how-to/hide-passwords-in-code-raspberry-pi-pico-w
#params is params.py on the Pico W
import params

# CONSTANTS
# See https://docs.micropython.org/en/latest/reference/constrained.html#execution-phase

# FUNCTIONS

#======= connnect()
# wlan is a global varible setup in the BOOTline code
# The Pico LED flashes when wifi connection is attempted. On solid when connected
def connect():
   
    # wlan.status() Return Value
    # STAT_IDLE -- 0
    # STAT_CONNECTING -- 1
    # Not sure what 2 is. Likely 'Connected to wifi, but no IP address'
    #    See https://github.com/georgerobotics/cyw43-driver/blob/9bfca61173a94432839cd39210f1d1afdf602c42/src/cyw43.h#L82
    # STAT_WRONG_PASSWORD -- -3
    # STAT_NO_AP_FOUND -- -2
    # STAT_CONNECT_FAIL -- -1
    # STAT_GOT_IP -- 3

    cnt=0
    global led, wlan

    try:
# Print a List of Local SSIDs
#         nets = wlan.scan()
#         for net in nets:
#             s_ssid_b, s_bssid_h, s_channel, s_RSSI, s_authmode, s_hidden = net
#             s_ssid = s_ssid_b.decode()
#             if s_ssid == params.ssid:
#                 print ("On Ch ",s_channel,"Sig ",s_RSSI)
# 
#         print("Status ",wlan.status() )
        set_leds("off")
        while not wlan.isconnected():
            cnt=cnt+1
            wlan.active(True)
            wlan.connect(params.ssid, params.pwd)
            sleep(3)
            # If the status is not 'connecting' (1) or 'connected but no ip' (2) or connected abort
            status = wlan.status() 
            if not wlan.isconnected():
                if not ((status == 1) or (status == 2)):
                    with open(params.log_file,"a") as f:
                        f.write(log_time("boot/connect"))
                        f.write("Wifi is not connecting to "+params.ssid+". Status "+str(status) )
                    set_leds("off")
                    raise RuntimeError('Wifi connect failed')
            
            set_leds("toggle")
            
            
        set_leds("on")
#        print("Connected to channel ",wlan.config('channel'))
           
        if cnt > 1:
            with open(params.log_file,"a") as f:
                f.write(log_time("boot/connect")+"Connection took "+str(cnt)+" attempts")
   
    except Exception as err:
        with open(params.log_file,"a") as f:
            f.write(log_time("boot/connect"))
            print_exception(err,f)
        raise RuntimeError('boot/connect() failed')
    
    return

#=================== toggle_leds
# Use the leds to indicate status of the boot program connecting to the network.

# There is one LED on the PICO W and an RGB LED on th PICO display.
# The single colour PICO LED supports a toggle function. The PICO DISPLAY does not.

def set_leds(setting):
    
    global pico_led, rgbled, rgb_on
    
    if setting == "on":
        pico_led.on()
        rgbled.set_rgb(20,10,0) # RED+GREEN can't make YELLOW.
        rgb_on = True
        
    elif setting == "off":
        pico_led.off()
        rgbled.set_rgb(0,0,0)
        rbg_on = False
        
    elif setting == "toggle":
        if rgb_on:
            set_leds("off")
        else:
            set_leds("on")

    return
        

# ********** BOOT PROGRAM **********
# I'm not using the Python construct of testing __NAME__ for BOOT to all BOOT().
# It doesn't seem to be needed for Pico W.

# boot_ok is a GLOBAL variale that MAIN can read to determine whether or not to run
# based on the success of failure of BOOT

try:
    # For development/debug, it is best to append to the existing log.
    # Existing logs will have to be manually cleared
    # For production, start a new file. This keeps down the space taken.
    
    global boot_ok
    boot_ok=False
    
    if params.debug:
        mode="a"
    else:
        mode="w"
        
    with open(params.log_file,mode) as f:
        f.write(log_time("boot")+"Started. Last reset cause recorded "+str(reset_cause()))
        
    global pico_led, rgbled, rgb_on
    pico_led = Pin("LED", Pin.OUT)
    # Init the LED. 6,7,8 are the PICO DISPLAY pins
    rgbled = RGBLED(6, 7, 8)
    set_leds("off")
    rgb_on=False

    # Set country for wlan connnection
    # See https://peppe8o.com/getting-started-with-wifi-on-raspberry-pi-pico-w-and-micropython/
    country('CA')

    global wlan
    wlan = WLAN(STA_IF)
    wlan.active(True)
    # If we are connected, disconnect to keep things clean and ensure all code executed.
    if wlan.isconnected():
        wlan.disconnect()

    # Turn off wireless power saving
    wlan.config(pm = 0xa11140)
  
    connect()
    ip = wlan.ifconfig()[0]
    
    # Set the Real Time Clock
    set_rtc()
    
    with open(params.log_file,"a") as f:
        f.write(log_time("boot")+"Connected to "+params.ssid+". IP "+str(ip))
        
    boot_ok=True
    set_leds("on")
            
except Exception as err:
    with open(params.log_file,"a") as f:
        f.write(log_time("boot")+"Exception caught\n")
        print_exception(err,f)
        f.write("\nboot_ok=False")
    boot_ok=False
    # Check to see if the rgb_led has been initialize and if so turn the light RED
    if "rgbled" in globals():
        rgbled.set_rgb(30,0,0) # Red

exit(0)
