# picow_main_template_with_comments.py

# This is a template to start a Micropython Program from and include comments.
# I'm only using the hash comment to make it easier to strip comments to make
# a MAIN.PY to be loaded to the Raspberry PI Pico W.

# It is assumed a BOOT.PY, based on picow_boot_template_with_comments.py has been run
# to establish WiFi connectivity.
# If you find WiFi connectivity is frequently lost when running the MAIN.PY, find the
# commened lines starting with #@. These will load in WLAN module from the Network
# library and test for connectivity. If it has been lost, a machine.reset will be issued
# to restart the PICO and rerun BOOT.PY. It is commented out here to save space in MAIN.PY

# I'm also using the Pico Display Pack https://shop.pimoroni.com/products/pico-display-pack

# IMPORTS
# From references to Python best practices, I use FROM to only import the functions
# needed to keep space down.
from time import sleep
from time import time as time_in_sec
#@from machine import reset
#@from network import WLAN, STA_IF
from sys import print_exception,exit
from gc import collect
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P4
from pimoroni import RGBLED

# These are local files
from log_time import log_time
from set_rtc import set_rtc
from os import rename
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


# ********** MAIN PROGRAM **********
# I'm not using the Python construct of testing __NAME__ for MAIN to all main().
# It doesn't seem to be needed for Pico W.

save_log_file=False

try:
    # Log file was created in BOOT.PY.
    with open(params.log_file,"a") as f:
        f.write(log_time("main")+"MAIN.PY Started")
   
    loop_sleep_time = 10
    
    # Init the LED. 6,7,8 are the PICO DISPLAY pins
    led = RGBLED(6, 7, 8)
    led.set_rgb(0,0,0)

    # See https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/modules/picographics#readme
    display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_P4, rotate=0)
    display.set_backlight(0.5)
    # Font see https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/modules/picographics#changing-the-font
    display.set_font("bitmap8")

    GREEN = display.create_pen(0, 255, 0)
    BLACK = display.create_pen(0, 0, 0)
    
    global last_line_displayed
    last_line_displayed = 0
         
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
    # If space is short, drop defining WLAN and checking for a connection
    # another component will error out with the loss of an IP
#@    global wlan
#@    wlan = WLAN(STA_IF)
    
    loop_cnt = 0 # Caution on overflowing this integer. Drop if not needed.

    # Get Start Time for Calling set_rtc() to reset time in 5 hours
    next_rtc_call = time_in_sec()+5*60*60
       
    # Main Program Loop
    while True:

        loop_cnt=loop_cnt+1
        led.set_rgb(0,30,0) # Set green while processing
        sleep(1)
        
        display_line("Mainline Loop "+str(loop_cnt))
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
        # Main code here        
        #----------------------------------------------------------------------------------------
        
        # Force micropython garbage collection                
        collect()
        
        led.set_rgb(0,0,30) # Set Blue while asleep.
        sleep(loop_sleep_time)
   
except Exception as err:
    with open(params.log_file,"a") as f:
        f.write(log_time("main")+"Exception caught\n")
        print_exception(err,f)
    save_log_file=True
    if "led" in locals():
        led.set_rgb(30,0,0) # Set Red if error
    
if save_log_file:
    rename(params.log_file,"Err_"+params.log_file)
    
exit(0)
    
