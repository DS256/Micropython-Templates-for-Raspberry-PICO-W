# Micropython Templates for Raspberry PICO W
_2023-03-06_

I am in debt to those who came before me in posting information on the web that helped me overcome issues as I explored the PICO W with PICO Display. Where possible, I've embedded links to those sources in the programs.

As part of the road traveled, I discovered that in the Micropython deployment on microcontrollers, there are two separate files used; BOOT.PY and MAIN.PY. BOOT is used for housekeeping chores like connecting Wi-Fi. Remember, the PICO W has limited memory. This approach seems to keep the usable space up. GLOBAL variables are shared between BOOT and MAIN so information can be passed. This is important since an error exit from BOOT does not prevent MAIN from running.

In my search, what I didn't find were any comprehensive templates to start a new project with. They are likely out there and I will now find them. In the interim I created this repository. I hope you find it useful.

## COMPONENTS

There are several constructs I've included. Some of are stored as separate PY files since they are shared between BOOT and MAIN.
* PICOW_BOOT_TEMPLATE_WITH_COMMENTS.PY - Template for BOOT.PY. The reference to _COMMENTS is that I plan to strip full line comments to reduce the size. 
* PICOW_MAIN_TEMPLATE_WITH_COMMENTS.PY - Template for MAIN.PY.
* PARAMS.PY - This is a revision of a link I found on being able to encrypt the SSID and PASSWORD (link in BOOT template). Handy place to store parameters. Also means if you need to share you code when solving problems, you don't have to worry about showing personal information.
* LOG_FILE.TXT - Log/Error file created by BOOT and appended to by BOOT, MAIN and supporting functions. Records information in the event of an error including trapped exceptions.
* SET_RTC() - PICO W has a Real Time Clock which is not maintained with a battery. This means at power on, it defaults back to '2021-01-01 00:00:00'. Micropython also does not handle Time Zones. This means that if use an NTP call to get the GMT, you have to mangle the time to set up your local time. I found a reference to a site with a RESTful call that returns  JSON payload with the time in the time zone for a specific city. This is used to set the RTC which Micropython uses. One other note if using Thonny with Micropython is that Thonny will optionally set the RTC. I found it useful to turn this off.
* LOG_TIME(module) - Common routine for prefixing a new entry to LOG_FILE.TXT

### PICOW_BOOT_TEMPLATE_WITH_COMMENTS.PY 

The main flow of this template are:
1. Create new LOG_FILE.TXT based on the parameter in PARAMS.PY
2. Disconnect the WiFi if connected to ensure all code is run
3. Connect the WiFi. While this in process, the LED on the PICO W will flash. Once a connection is made, the LED is left on. For the boot
module, this is RED+GREEN on the PICO Display. I found the first time I connected to my home WiFi, the connection took many attempts. Not sure the reason but others have reported the same experience. One tip was to set the 'COUNTRY' in PICO W to (theoretically) limit the country specific processing.
4. Set RTC with the new local time
5. Set the GLOBAL variable BOOT_OK for MAIN.PY to read.

### PICOW_MAIN_TEMPLATE_WITH_COMMENTS.PY

This template assumes a PICO DISPLAY is attached. Calls to the display are mostly isolated in functions.

The main flow of this template are:
1. Open, append mode, the LOG_FILE.TXT based on the parameter in PARAMS.PY
2. Initialize and clear the PICO DISPLAY. This initial configuration is to support a 6x23 text line display. Changes can be made to other modes.
3. Start main loop
* Optionally check if the WiFi is still connected. If not, perform a machine.soft_reset() to re-run BOOT.PY. The lines enabling this are commented out with #@
* Check to see if we need to refresh the Real Time Clock and if so, call set_rtc()
* <<< MAINLINE CODE FOR PROJECT >>>
* Perform Micropython garbage collection to maximize RAM.

## NOTES ON DEVELOPING FOR THE PICO W WITH MICROPYTHON

Some notes when working with PICO W, PICO DISPLAY, Micropython and Thonny

* I installed [the firmware](https://github.com/pimoroni/pimoroni-pico/releases) from PICO Display [pimoroni-picow-v1.19.15-micropython.uf2](https://github.com/pimoroni/pimoroni-pico/releases/download/v1.19.15/pimoroni-picow-v1.19.15-micropython.uf2)
* I have been advised that the team maintaining Micropython is small. They also port to many platforms with the PICO being just one. I've found in consistencies between the Micropython documentation and the actual behavior on the PICO W. One useful tip I found is to use 'help' to find out what is really implemented. For example, to find out what is exposed for RTC use >>> help(machine.RTC) this will list both the functions as well as variables to test. 
* PICO uses the Wake feature to implement the resets. This means the reset cause will always be 3 (WDT)
* I ran into a problem where MAIN was running after BOOT on a soft reset. Part of this is using Thonny. See this [forum post](https://github.com/orgs/micropython/discussions/10884) and [here](https://groups.google.com/g/thonny/c/g7IaeUeqKHE)
* When using an IDE, like Thonny, beware some of the features such as shared GLOBAL variables may not be shared by manual running.
