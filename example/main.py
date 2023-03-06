# Example main.py from picow_main_template_with_comments.py

# Example main providing a text displayed by button selection
# Button A - Displays the current weather. See get_weather()
# Button B - Displays the current time.
# Each display is held for a specific number of seconds.
# The LED is green when a button can be pushed. Blue when there is an active display
# I didn't get fancy with the disply. This was a proof of the main template I wrte.

# I'm using the Pico Display Pack https://shop.pimoroni.com/products/pico-display-pack

# IMPORTS
# From references to Python best practices, I use FROM to only import the functions
# needed to keep space down.

from time import sleep,localtime
from time import time as time_in_sec
#@from machine import reset
#@from network import WLAN, STA_IF
from sys import print_exception,exit
from gc import collect
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P4
from pimoroni import Button, RGBLED
from os import rename
# These are local files
from log_time import log_time
from set_rtc import set_rtc
from get_weather import get_weather
#https://www.tomshardware.com/how-to/hide-passwords-in-code-raspberry-pi-pico-w
# Hiding not implemented yet
import params

# CONSTANTS
# See https://docs.micropython.org/en/latest/reference/constrained.html#execution-phase

# FUNCTIONS
#=========== clear()
# Clear the current contents of the PICO Display

def clear():
    global last_line_displayed
    last_line_displayed = 0
    
    display.set_pen(BLACK)
    display.clear()
    display.update()

    return
    
#=========== display_line(text)
def display_line(line):

    # Write to a 6x25 text line display emulated on the Pico Display
    # Display the next line. Wrap to the top when the bottom is reached
    # All pixel addrs used in DISPLAY functions derived by trial and error.
    
    global last_line_displayed
    last_line_displayed = last_line_displayed + 1
    
    # Calculate the Y pixel coorindate of the next line. Each line is 22 pixels.
    if last_line_displayed > 6: last_line_displayed = 1
    y = 22*(last_line_displayed-1)
    
    # First clear the existing line since display.text is additive text on pixels
    # Clearing is done by creating a black rectangle around the line
    # rectangle(x,y,width,height)
    display.set_pen(BLACK)
    display.rectangle(0,y,240,22)
    # Clear the first 2 columns to clear previous "> "
    display.rectangle(0,0,15,135)

    # Display the line to a max of 21 characters. Current line shown by "> "
    # text(text, x, y, wordwrap, scale, angle, spacing)
    display.set_pen(GREEN)
    display.text("> "+line[:23], 0, y, 240, 2.7)

    display.update()
    
    return

#=========== display_weather()
# See display_weather.py for details

def display_weather(city):
    
    global weather,last_weather
    # In order to reduce the calls to the web service, and potential costs, limit the call
    # to every 15 minutes. I don't think the site is updated more frequently than that.
    # Also, do we care how much the temperature has changed in that time ;-)
    
    city_l = city.lower()
    weather=last_weather[city_l]
    display_line("For "+city)
    # The first time a call for a city comes in 'last_call' will be zero
    if time_in_sec() >=(weather["last_call"]+15*60):
        weather=get_weather(params.weather_url[city_l] )
        last_weather[city_l] = weather
        display_line("Weather info updated")

    display_line("As of "+weather["last_upd"])
    display_line("Temp "+weather["temp"])
    display_line("Feels like "+weather["feels"])
    display_line(weather["cond"])
    
    hold_display()
    
    return

#=========== display_time()

def display_time():
# Display current date and time.
    
    now = localtime() # RTC time set in set_rtc()
    display_line(pad(now[0])+"/"+pad(now[1])+"/"+pad(now[2]))
    display_line(pad(now[3])+":"+pad(now[4]))

    hold_display()
    return
# Companion to display_time. MP does not have a zero padding format 
def pad(val):
    return ("00"+str(val))[-2:]

#=========== hold_display()

def hold_display():
# Identify information is being displayed for x seconds with the blue light
    global led_intensity
    led.set_rgb(0, 0, led_intensity)   # Set the RGB LED to blue
    sleep(5)
    return
    

# ********** MAIN PROGRAM **********
# I'm not using the Python construct of testing __NAME__ for MAIN to all main().
# It doesn't seem to be needed for Pico W.

try:
    save_log_file=False # Set if exception to save log file
    
    # Log file was created in BOOT.PY.
    with open(params.log_file,"a") as f:
        f.write(log_time("main")+"MAIN.PY Started")
        
    # Init the LED. 6,7,8 are the PICO DISPLAY pins
    led = RGBLED(6, 7, 8)
        
    global weather, last_weather
    # This is the string returned from get_weather()
    weather={"temp": "-32000","feels": "-32000",\
                "last_upd":"Big Bang","cond":"Not good","last_call":0}
    last_weather={"toronto":weather,"barrie":weather,"muskoka":weather}
 
    # led.set_rgb(r,g,b) number values are for intensity
    global led_intensity
    led_intensity = 30
    
    global last_line_displayed
    last_line_displayed = 0
   
    # See https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/modules/picographics#readme
    display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_P4, rotate=0)
    display.set_backlight(0.5)
    # Font see https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/modules/picographics#changing-the-font
    display.set_font("bitmap8")

    GREEN = display.create_pen(0, 255, 0)
    BLACK = display.create_pen(0, 0, 0)
    
    # Define PICO DISPLAY Buttons
    button_a = Button(12)
    button_b = Button(13)
    button_x = Button(14)
    button_y = Button(15)
           
    # Clear Pico Display
    clear()
    
    # Check to make sure BOOT.PY ran successfully. If BOOT_OK not present, assume
    # test run from Thonny
    global boot_ok
    if "boot_ok" in globals():
        if not boot_ok:
            txt=" BOOT.PY failed. MAIN.PY exiting"
            display_line(txt)
            raise RuntimeError(txt)
    
    # Network Started in BOOT.PY. We test to see if it's active here
#@    global wlan
#@    wlan = WLAN(STA_IF)

    # Get Start Time for Calling set_rtc() to reset time in 5 hours
    next_rtc_call = time_in_sec()+5*60*60
    
    # I saw a note that the PICO DISPLAY only scans buttons every .1 seconds
    button_scan_time = .1
       
    # Main Program Loop
    while True:

        # This is a check at the start of every loop to make sure we still have wifi
        # If not, we need to perform a reset to rerun BOOT.PY
#@        if not wlan.isconnected():
#@            with open(params.log_file,"a") as f:
#@                f.write(log_time("main")+" WiFi lost. Restarting to run BOOT.PY")
#@            display_line("machine.reset()")
#@            # Reset used in case we are running from Thonny to make sure both BOOT+MAIN run
#@            machine.reset()
        
        # See set_rtc() but it is recommended to update the RTC peridically.
        if time_in_sec() >= next_rtc_call:
            set_rtc() # Update Time
            next_rtc_call = time_in_sec()+5*60*60
            with open(params.log_file,"a") as f:
                f.write(log_time("main")+"Refresh set_rtc() run")
                
        #----------------------------------------------------------------------------------------
        # Main code
        
        clear() # Clear previous display
        led.set_rgb(0, led_intensity, 0)   # Green=Ready to push a button
        
        if button_a.read():
            display_time()
            collect()
            
        elif button_b.read():
            display_weather("Toronto")
            collect()
            
        elif button_x.read():
            display_weather("Barrie")
            collect()
            
        elif button_y.read():
            display_weather("Muskoka")
            collect()

        #----------------------------------------------------------------------------------------
        # collect() was moved to after work is done by each button
        # No need to do it if no work was done.
        
        sleep(button_scan_time)
   
except Exception as err:
    with open(params.log_file,"a") as f:
        f.write(log_time("main")+"Exception caught\n")
        print_exception(err,f)
    save_log_file=True
    if "led" in locals():
        led.set_rgb(30,0,0) # RED
    
if save_log_file:
    rename(params.log_file,"Err_"+params.log_file)
    
exit(0)
    
